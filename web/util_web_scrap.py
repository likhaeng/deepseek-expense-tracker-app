# Python Library
from bs4 import BeautifulSoup
from urllib.parse import quote
from typing import List, Dict
import logging
import requests
# Custom Library
import config
# Spacy Library
import spacy

logging.basicConfig(format='%(asctime)s %(message)s', filename=config.log_path, level = config.log_level)

class WebScrap():
    def __init__(self):
        pass

    def extract_keywords_spacy(self, sentence):
        # Load the English language model
        nlp = spacy.load(config.spacy_language_model)
        #
        doc = nlp(sentence)
        keywords = [token.text for token in doc if not token.is_stop and not token.is_punct]
        keyword_string = " ".join(keywords)
        return keyword_string

class PubMed():
    def __init__(self):
        self.base_url = config.pubmed_base_url
        # tool and email is required as part of the PubMed API requirement
        self.tool = config.pubmed_tool_name
        self.email = config.pubmed_email
        # 
        self.webScapUtil = WebScrap()

    def search_pubmed_manual(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search PubMed and return article metadata
        """
        base_url = config.pubmed_base_url
        search_url = f"{base_url}?term={quote(query)}"
        logging.warning("PubMed Manual Web Scrapping on Search url: " + search_url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching search results: {e}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        # Extract article cards
        for card in soup.select('.docsum-content')[:max_results]:
            try:
                title_elem = card.select_one('a.docsum-title')
                title = title_elem.text.strip()
                pmid = title_elem.get('href').split('/')[-2]
                link = f"{base_url}{title_elem.get('href')}"
                
                authors = card.select_one('.docsum-authors').text.strip()
                citation = card.select_one('.docsum-journal-citation').text.strip()
                
                # Get abstract page
                abstract = self.get_abstract(pmid, headers)
                
                articles.append({
                    'pmid': pmid,
                    'title': title,
                    'authors': authors,
                    'citation': citation,
                    'abstract': abstract,
                    'url': link
                })
            except Exception as e:
                logging.error(f"Error processing article: {e}")
                continue
        
        return articles

    def get_abstract(self, pmid: str, headers: Dict) -> str:
        """
        Fetch abstract for a specific PMID
        """
        abstract_url = f"{config.pubmed_base_url}{pmid}/"
        try:
            response = requests.get(abstract_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different selectors for abstract
            abstract = ""
            if abstract_div := soup.find('div', class_='abstract-content selected'):
                abstract = abstract_div.get_text(separator=' ', strip=True)
            elif abstract_section := soup.find('div', id='enc-abstract'):
                abstract = abstract_section.get_text(separator=' ', strip=True)
            
            return abstract
        except Exception as e:
            logging.error(f"Error fetching abstract for PMID {pmid}: {e}")
            return ""
        
    def search_pubmed(self, query, is_pubmed_API=False, max_results=3):
        # User Query to searchable keywords
        keyword = self.webScapUtil.extract_keywords_spacy(query)
        # Conditional Handling to use pubmed API or manual web scrapping
        # log_remarks = ""
        if is_pubmed_API:
            logging.warning("PubMed Web Scrapping using API")
            pubmed = PubMed(tool=config.pubmed_tool_name, email=config.pubmed_email)
            # PubMed API integration
            results = pubmed.query(keyword, max_results=max_results)
            # results = pubmed.query(query)
            articles = []
            for article in results:
                formatted_pubmed_id = article.pubmed_id.splitlines()[0]
                article_data = {
                    "title": article.title,
                    "abstract": article.abstract,
                    "doi": article.doi,
                    "url": f"{config.pubmed_base_url}{formatted_pubmed_id}/",
                    "authors": ", ".join([author["lastname"] for author in article.authors]),
                    "journal": article.journal,
                    "year": article.publication_date.year if article.publication_date else None,
                }
                articles.append(article_data)
            # log_remarks = "pubmed API integration"
        else:
            # PubMed Manual Web Scrapping integration
            logging.warning("PubMed Web Scrapping using Manual Web Scrapping Logic")
            results = self.search_pubmed_manual(keyword, max_results=max_results)
            articles = []
            for article in results:
                article_data = {
                    "title": article['title'],
                    "abstract": article['abstract'],
                    # "doi": article.doi,
                    "url": article['url'],
                    "authors": article['authors'],
                    # "journal": article.journal,
                    # "year": article.publication_date.year if article.publication_date else None,
                }
                articles.append(article_data)
            # log_remarks = "pubmed manual web scrapping"
        # return articles, log_remarks
        return articles