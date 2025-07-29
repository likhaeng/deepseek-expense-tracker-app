import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import random

class ScienceDirectScraper:
    def __init__(self, headless=True):
        self.base_url = "https://www.sciencedirect.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.setup_selenium(headless)
        
    def setup_selenium(self, headless=True):
        """Configure Selenium WebDriver"""
        chrome_options = Options()
        # if headless:
        #     chrome_options.add_argument("--headless") # Root cause on causing TimeOutException during WebDriverWait
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set path to your chromedriver
        # service = Service(executable_path='D:/BOIT/MedicalAI/4_SourceCode_MedicalAI/chromedriver.exe') # Success
        service = Service(executable_path='chromedriver.exe') # Success
        self.driver = webdriver.Chrome(service=service, options=chrome_options) # Success
        
    def search_articles(self, query, max_results=5, wait_time=2):
        try:
            """Search ScienceDirect and return article links"""
            search_url = f"{self.base_url}/search?qs={quote(query)}"
            # search_url = "https://pubmed.ncbi.nlm.nih.gov/?term=hydrogen+reduce+stress"
            self.driver.get(search_url)
            
            # Wait for results to load
            # EC.presence_of_element_located((By.CSS_SELECTOR, ".docsum-title"))
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".js"))
            )
            # Scroll to load more results
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while len(self.driver.find_elements(By.CSS_SELECTOR, ".result-item")) < max_results:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(wait_time)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            # Get article links
            articles = []
            for item in self.driver.find_elements(By.CSS_SELECTOR, ".result-item")[:max_results]:
                try:
                    link = item.find_element(By.CSS_SELECTOR, "a.result-list-title-link").get_attribute("href")
                    title = item.find_element(By.CSS_SELECTOR, "a.result-list-title-link").text
                    articles.append({
                        'title': title,
                        'url': link
                    })
                except Exception as e:
                    print(f"Error processing search result: {e}")
            
            return articles
        except Exception as ex:
            print("Print exception to terminal")
            print(str(ex))
            return [str(ex)]
    
    def scrape_article(self, url):
        """Scrape detailed article information"""
        self.driver.get(url)
        try:
            # Wait for article to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".article-content")))
            
            # Get article metadata from JSON-LD
            article_data = {}
            try:
                script = self.driver.find_element(By.XPATH, '//script[@type="application/ld+json"]')
                metadata = json.loads(script.get_attribute("innerHTML"))
                article_data.update({
                    'doi': metadata.get('identifier', ''),
                    'publication_date': metadata.get('datePublished', ''),
                    'authors': [author['name'] for author in metadata.get('author', [])],
                    'publisher': metadata.get('publisher', {}).get('name', ''),
                    'citation_count': metadata.get('citationCount', '')
                })
            except Exception as e:
                print(f"Error parsing JSON-LD: {e}")
            
            # Get additional information
            article_data.update({
                'title': self.safe_extract(By.CSS_SELECTOR, "h1.article-title", ""),
                'abstract': self.safe_extract(By.CSS_SELECTOR, ".abstract.author p", ""),
                'keywords': self.safe_extract_multi(By.CSS_SELECTOR, ".keyword span"),
                'references': len(self.driver.find_elements(By.CSS_SELECTOR, ".references li")),
                'figures': len(self.driver.find_elements(By.CSS_SELECTOR, ".figure")),
                'tables': len(self.driver.find_elements(By.CSS_SELECTOR, ".table"))
            })
            
            return article_data
            
        except Exception as e:
            print(f"Error scraping article {url}: {e}")
            return None
    
    def safe_extract(self, by, selector, default=""):
        """Safely extract element text"""
        try:
            return self.driver.find_element(by, selector).text
        except:
            return default
    
    def safe_extract_multi(self, by, selector):
        """Safely extract multiple elements"""
        try:
            return [el.text for el in self.driver.find_elements(by, selector)]
        except:
            return []
    
    def save_to_csv(self, data, filename="sciencedirect_articles.csv"):
        """Save scraped data to CSV"""
        if not data:
            return
        
        keys = data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        print(f"Saved {len(data)} articles to {filename}")
    
    def close(self):
        """Close the Selenium driver"""
        self.driver.quit()

# Example usage
if __name__ == "__main__":
    scraper = ScienceDirectScraper(headless=True)
    
    try:
        # Search for articles
        query = "Effect of consuming hydrogen rich substance"
        search_results = scraper.search_articles(query, max_results=3)
        print(f"Found {len(search_results)} articles for '{query}'")
        
        # Scrape each article
        articles_data = []
        for article in search_results:
            print(f"\nScraping: {article['title']}")
            article_data = scraper.scrape_article(article['url'])
            if article_data:
                article_data['search_url'] = article['url']
                articles_data.append(article_data)
                time.sleep(random.uniform(1, 3))  # Random delay between requests
        
        # Save results
        if articles_data:
            scraper.save_to_csv(articles_data)
            print("\nSample article data:")
            print(json.dumps(articles_data[0], indent=2))
        else:
            print("No articles were scraped successfully")
            
    finally:
        scraper.close()