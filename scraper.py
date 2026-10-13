import requests
import random
import time
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import (
    SCRAPER_DELAY_MIN,
    SCRAPER_DELAY_MAX,
    SCRAPER_MAX_RESULTS_PER_SOURCE,
    SCRAPER_TIMEOUT,
    USER_AGENTS
)
from datetime import datetime
import json

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        
    def _get_headers(self):
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
    def _delay(self):
        time.sleep(random.uniform(SCRAPER_DELAY_MIN, SCRAPER_DELAY_MAX))

    def fetch_google_news(self, query):
        print(f"🔄 Scraper: Fetching Google News for '{query}'...")
        self._delay()
        encoded_query = quote_plus(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        results = []
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:SCRAPER_MAX_RESULTS_PER_SOURCE]:
                date_str = entry.get('published', '')
                try:
                    # Google News RSS format: Tue, 19 Apr 2026 12:00:00 GMT
                    dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
                    iso_date = dt.isoformat() + "Z"
                except:
                    iso_date = datetime.utcnow().isoformat() + "Z"

                results.append({
                    "source": "Google News",
                    "title": entry.get('title', ''),
                    "content": entry.get('summary', ''),
                    "url": entry.get('link', ''),
                    "date": iso_date
                })
            print(f"✓ Scraper: Found {len(results)} items from Google News")
        except Exception as e:
            print(f"⚠ Scraper error Google News: {e}")
            
        return results

    def fetch_bing_news(self, query):
        print(f"🔄 Scraper: Fetching Bing News for '{query}'...")
        self._delay()
        encoded_query = quote_plus(query)
        url = f"https://www.bing.com/news/search?q={encoded_query}"
        
        results = []
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=SCRAPER_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            cards = soup.find_all('div', class_='news-card')
            for card in cards[:SCRAPER_MAX_RESULTS_PER_SOURCE]:
                title_elem = card.find('a', class_='title')
                desc_elem = card.find('div', class_='snippet')
                
                if title_elem:
                    title = title_elem.text.strip()
                    link = title_elem.get('href', '')
                    content = desc_elem.text.strip() if desc_elem else ""
                    
                    results.append({
                        "source": "Bing News",
                        "title": title,
                        "content": content,
                        "url": link,
                        "date": datetime.utcnow().isoformat() + "Z"
                    })
            print(f"✓ Scraper: Found {len(results)} items from Bing News")
        except Exception as e:
            print(f"⚠ Scraper error Bing News: {e}")
            
        return results

    def fetch_reddit(self, query):
        print(f"🔄 Scraper: Fetching Reddit for '{query}'...")
        self._delay()
        encoded_query = quote_plus(query)
        url = f"https://www.reddit.com/search.json?q={encoded_query}&sort=new&limit={SCRAPER_MAX_RESULTS_PER_SOURCE}"
        
        results = []
        try:
            # Reddit requires a custom User-Agent to avoid 429 Too Many Requests
            headers = self._get_headers()
            headers["User-Agent"] = "python:financial_sentiment_bot:v1.0 (by /u/anonymous)"
            
            response = self.session.get(url, headers=headers, timeout=SCRAPER_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            children = data.get('data', {}).get('children', [])
            for child in children:
                post = child.get('data', {})
                title = post.get('title', '')
                content = post.get('selftext', '')
                if not content:
                    content = title
                    
                timestamp = post.get('created_utc')
                if timestamp:
                    iso_date = datetime.utcfromtimestamp(timestamp).isoformat() + "Z"
                else:
                    iso_date = datetime.utcnow().isoformat() + "Z"
                    
                results.append({
                    "source": "Reddit",
                    "title": title,
                    "content": content,
                    "url": f"https://www.reddit.com{post.get('permalink', '')}",
                    "date": iso_date
                })
            print(f"✓ Scraper: Found {len(results)} items from Reddit")
        except Exception as e:
            print(f"⚠ Scraper error Reddit: {e}")
            
        return results

    def scrape_all(self, query):
        """Scrape all sources concurrently."""
        all_results = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self.fetch_google_news, query),
                executor.submit(self.fetch_bing_news, query),
                executor.submit(self.fetch_reddit, query)
            ]
            
            for future in as_completed(futures):
                try:
                    all_results.extend(future.result())
                except Exception as e:
                    print(f"⚠ Scraper error in worker thread: {e}")
                    
        return all_results
