import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
import time
import csv
from typing import List, Dict

def search_pubmed(query: str, max_results: int = 10) -> List[Dict]:
    """
    Search PubMed and return article metadata
    """
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    search_url = f"{base_url}?term={quote(query)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching search results: {e}")
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
            abstract = get_abstract(pmid, headers)
            
            articles.append({
                'pmid': pmid,
                'title': title,
                'authors': authors,
                'citation': citation,
                'abstract': abstract,
                'url': link
            })
        except Exception as e:
            print(f"Error processing article: {e}")
            continue
    
    return articles

def get_abstract(pmid: str, headers: Dict) -> str:
    """
    Fetch abstract for a specific PMID
    """
    abstract_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
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
        print(f"Error fetching abstract for PMID {pmid}: {e}")
        return ""

def save_to_csv(articles: List[Dict], filename: str = "pubmed_articles.csv"):
    """
    Save scraped articles to CSV file
    """
    if not articles:
        return
    
    keys = articles[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(articles)
    print(f"Saved {len(articles)} articles to {filename}")

# Example usage
if __name__ == "__main__":
    search_query = "hydrogen water"
    articles = search_pubmed(search_query, max_results=5)
    
    for article in articles:
        print(f"\nPMID: {article['pmid']}")
        print(f"Title: {article['title']}")
        print(f"Authors: {article['authors']}")
        print(f"Citation: {article['citation']}")
        print(f"Abstract: {article['abstract'][:200]}...")  # Print first 200 chars
        print(f"URL: {article['url']}")
    
    save_to_csv(articles)