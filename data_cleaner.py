import re
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

class DataCleaner:
    def __init__(self):
        pass

    def clean_html(self, text):
        """Remove HTML tags and decode entities."""
        if not text:
            return ""
        # Use BeautifulSoup to strip tags safely
        soup = BeautifulSoup(text, "lxml")
        cleaned_text = soup.get_text(separator=" ", strip=True)
        return cleaned_text

    def normalize_text(self, text):
        """Normalize text: remove extra whitespace, normalize quotes."""
        if not text:
            return ""
        # Replace multiple spaces/newlines with a single space
        text = re.sub(r'\s+', ' ', text)
        # Fix smart quotes
        text = text.replace('‘', "'").replace('’', "'").replace('“', '"').replace('”', '"')
        return text.strip()

    def is_similar(self, a, b, threshold=0.8):
        """Check if two strings are similar."""
        if not a or not b:
            return False
        return SequenceMatcher(None, a.lower(), b.lower()).ratio() > threshold

    def process_data(self, raw_data):
        """Clean and deduplicate data."""
        cleaned_data = []
        seen_titles = []
        
        print(f"🧹 Cleaner: Processing {len(raw_data)} raw items...")

        for item in raw_data:
            title = self.normalize_text(self.clean_html(item.get("title", "")))
            content = self.normalize_text(self.clean_html(item.get("content", "")))
            
            if not title:
                continue
                
            # Content might be empty (e.g., just a title link), use title as content if needed
            if not content:
                content = title

            # Check for duplicates based on title similarity
            is_duplicate = False
            for seen_title in seen_titles:
                if self.is_similar(title, seen_title):
                    is_duplicate = True
                    break
                    
            if not is_duplicate:
                seen_titles.append(title)
                cleaned_item = {
                    "source": item.get("source", "Unknown"),
                    "title": title,
                    "content": content,
                    "url": item.get("url", ""),
                    "date": item.get("date", "")
                }
                cleaned_data.append(cleaned_item)
                
        print(f"✓ Cleaner: Retained {len(cleaned_data)} unique items.")
        return cleaned_data
