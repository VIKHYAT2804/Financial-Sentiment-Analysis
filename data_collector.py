"""
Data Collection Module
Fetches financial news articles using the multi-source web scraper.
"""

from query_generator import SmartQueryGenerator
from scraper import WebScraper
from data_cleaner import DataCleaner

# ── Date range presets ────────────────────────────────────────────────
# Kept for compatibility with dashboard.py
DATE_RANGE_PRESETS = {
    "Past 24 Hours": 1,
    "Past Week": 7,
    "Past 2 Weeks": 14,
    "Past Month": 30,
    "Past 3 Months": 90,
    "Past Year": 365,
}

class NewsCollector:
    """Collects financial news articles using WebScraper."""

    def __init__(self, api_key: str = ""):
        self.query_gen = SmartQueryGenerator()
        self.scraper = WebScraper()
        self.cleaner = DataCleaner()

    def fetch_articles(
        self,
        query: str = "stock market",
        max_articles: int = 50,
        days_back: int = 7,
        smart_query: bool = True,
    ) -> tuple[list[dict], dict | None]:
        """
        Fetch articles using WebScraper.

        Args:
            query: Raw user search query
            max_articles: Maximum number of articles to fetch (kept for compatibility)
            days_back: How many days back to search (kept for compatibility)
            smart_query: Whether to expand the query using SmartQueryGenerator

        Returns:
            Tuple of (articles_list, query_info_dict_or_None)
        """
        query_info = None

        if smart_query:
            query_info = self.query_gen.generate(query)
            search_query = query_info["optimized"]
        else:
            search_query = query

        print(f"ℹ  Using multi-source web scraper for: {search_query}\n")
        raw_data = self.scraper.scrape_all(search_query)
        cleaned_data = self.cleaner.process_data(raw_data)

        # For compatibility with older system, ensure description and publishedAt fields exist
        for item in cleaned_data:
            if 'description' not in item:
                item['description'] = item.get('content', '')
            if 'publishedAt' not in item:
                item['publishedAt'] = item.get('date', '')

        return cleaned_data, query_info

if __name__ == "__main__":
    collector = NewsCollector()
    articles, q_info = collector.fetch_articles("tesla stocks")
    if q_info:
        print(f"  Query:     {q_info['original']}")
        print(f"  Optimized: {q_info['optimized']}")
        print(f"  Entities:  {q_info['entities']}")
        print(f"  Strategy:  {q_info['strategy']}")
        print()
    for i, a in enumerate(articles, 1):
        print(f"{i:>2}. [{a['source']}] {a['title']}")
