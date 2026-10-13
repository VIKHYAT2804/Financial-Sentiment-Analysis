import pandas as pd
import os
from datetime import datetime
from config import OUTPUT_DIR

class CSVGenerator:
    def __init__(self):
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

    def generate(self, query, analyzed_data):
        """Generate a CSV file from the analyzed data."""
        if not analyzed_data:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join([c if c.isalnum() else "_" for c in query])
        filename = f"results_{safe_query}_{timestamp}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Prepare data for DataFrame
        rows = []
        for item in analyzed_data:
            rows.append({
                "Source": item.get("source", ""),
                "Title": item.get("title", ""),
                "Content": item.get("content", ""),
                "Date": item.get("date", item.get("publishedAt", "")),
                "URL": item.get("url", ""),
                "Sentiment_Label": item.get("label", "neutral").upper(),
                "Sentiment_Score": round(item.get("score", 0.0), 4),
                "Confidence": round(item.get("confidence", 0.0), 4)
            })
            
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"💾 CSV Generator: Saved to {filepath}")
        
        return filename
