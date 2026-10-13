"""
Smart Query Generator
Expands user queries into optimized financial search terms for better article relevance.

Example: "tesla stocks" → "Tesla TSLA stock price earnings revenue"
"""

# ── Known Ticker / Company Mappings ──────────────────────────────────
COMPANY_TICKERS = {
    # Tech
    "tesla": ("Tesla", "TSLA"),
    "apple": ("Apple", "AAPL"),
    "google": ("Google Alphabet", "GOOGL"),
    "alphabet": ("Google Alphabet", "GOOGL"),
    "microsoft": ("Microsoft", "MSFT"),
    "amazon": ("Amazon", "AMZN"),
    "meta": ("Meta Platforms Facebook", "META"),
    "facebook": ("Meta Platforms Facebook", "META"),
    "nvidia": ("NVIDIA", "NVDA"),
    "netflix": ("Netflix", "NFLX"),
    "amd": ("AMD Advanced Micro Devices", "AMD"),
    "intel": ("Intel", "INTC"),
    "ibm": ("IBM", "IBM"),
    "uber": ("Uber", "UBER"),
    "airbnb": ("Airbnb", "ABNB"),
    "spotify": ("Spotify", "SPOT"),
    "twitter": ("Twitter X Corp", "X"),
    "snapchat": ("Snap Inc", "SNAP"),
    "salesforce": ("Salesforce", "CRM"),
    "oracle": ("Oracle", "ORCL"),
    "adobe": ("Adobe", "ADBE"),
    "palantir": ("Palantir", "PLTR"),
    # Finance
    "jpmorgan": ("JPMorgan Chase", "JPM"),
    "goldman": ("Goldman Sachs", "GS"),
    "goldman sachs": ("Goldman Sachs", "GS"),
    "morgan stanley": ("Morgan Stanley", "MS"),
    "visa": ("Visa", "V"),
    "mastercard": ("Mastercard", "MA"),
    "paypal": ("PayPal", "PYPL"),
    # Healthcare
    "pfizer": ("Pfizer", "PFE"),
    "johnson": ("Johnson & Johnson", "JNJ"),
    "moderna": ("Moderna", "MRNA"),
    # Retail / Consumer
    "walmart": ("Walmart", "WMT"),
    "costco": ("Costco", "COST"),
    "nike": ("Nike", "NKE"),
    "starbucks": ("Starbucks", "SBUX"),
    "mcdonalds": ("McDonald's", "MCD"),
    "coca cola": ("Coca-Cola", "KO"),
    "pepsi": ("PepsiCo", "PEP"),
    # Energy
    "exxon": ("ExxonMobil", "XOM"),
    "chevron": ("Chevron", "CVX"),
    # Crypto
    "bitcoin": ("Bitcoin", "BTC"),
    "ethereum": ("Ethereum", "ETH"),
}

# ── Financial context keywords for topic-based queries ────────────────
SECTOR_KEYWORDS = {
    "tech": "technology stocks NASDAQ software AI semiconductor",
    "technology": "technology stocks NASDAQ software AI semiconductor",
    "banking": "banks financial sector interest rates loans JPMorgan Goldman",
    "bank": "banks financial sector interest rates loans JPMorgan Goldman",
    "oil": "crude oil prices energy OPEC petroleum Brent WTI",
    "energy": "energy oil gas renewable solar wind stocks",
    "crypto": "cryptocurrency Bitcoin Ethereum blockchain digital assets",
    "cryptocurrency": "cryptocurrency Bitcoin Ethereum blockchain digital assets",
    "pharma": "pharmaceutical drugs FDA biotech healthcare stocks",
    "healthcare": "healthcare pharmaceutical biotech medical stocks",
    "real estate": "real estate housing market mortgage REIT property",
    "housing": "housing market mortgage rates home sales real estate",
    "retail": "retail consumer spending shopping e-commerce stocks",
    "ev": "electric vehicles EV Tesla charging battery stocks",
    "electric vehicles": "electric vehicles EV Tesla charging battery stocks",
    "semiconductor": "semiconductor chips NVIDIA AMD Intel TSMC shortage",
    "chips": "semiconductor chips NVIDIA AMD Intel TSMC shortage",
    "ai": "artificial intelligence AI machine learning stocks investment",
    "artificial intelligence": "artificial intelligence AI machine learning stocks investment",
}

# ── Words to strip (noise) ────────────────────────────────────────────
NOISE_WORDS = {
    "stocks", "stock", "share", "shares", "price", "prices",
    "market", "markets", "trading", "trade", "invest",
    "investing", "investment", "the", "a", "an", "of",
    "in", "for", "and", "or", "is", "are", "will", "how",
    "what", "why", "about", "show", "me", "analyze", "analysis",
    "get", "find", "search", "news", "latest", "recent",
    "tell", "give", "check",
}


class SmartQueryGenerator:
    """Expands user queries into optimized financial search terms."""

    def generate(self, raw_query: str) -> dict:
        """
        Process a raw user query and return an optimized search query.

        Returns:
            dict with keys:
                - original: the raw input
                - optimized: the expanded search string
                - entities: list of detected companies/tickers
                - strategy: description of what was done
        """
        original = raw_query.strip()
        lower = original.lower()
        tokens = lower.split()

        entities = []
        extra_terms = []
        matched_keys = set()

        # 1. Check for company/ticker matches (multi-word first, then single)
        for key, (name, ticker) in COMPANY_TICKERS.items():
            if key in lower and key not in matched_keys:
                entities.append({"name": name, "ticker": ticker})
                extra_terms.extend([name, ticker, "stock", "earnings", "revenue"])
                matched_keys.add(key)

        # 2. Check for sector/topic matches
        for key, keywords in SECTOR_KEYWORDS.items():
            if key in lower and key not in matched_keys:
                extra_terms.append(keywords)
                matched_keys.add(key)

        # 3. Build optimized query
        if entities or extra_terms:
            # Remove noise words from original, keep meaningful words
            meaningful = [w for w in tokens if w not in NOISE_WORDS and w not in matched_keys]
            combined = meaningful + extra_terms
            # Deduplicate while preserving order
            seen = set()
            optimized_parts = []
            for part in combined:
                for word in part.split():
                    w_lower = word.lower()
                    if w_lower not in seen:
                        seen.add(w_lower)
                        optimized_parts.append(word)
            optimized = " ".join(optimized_parts)
            strategy = f"Expanded: detected {len(entities)} company/ticker(s) and enriched with financial terms"
        else:
            # No known entities — append generic financial context
            meaningful = [w for w in tokens if w not in NOISE_WORDS]
            if meaningful:
                optimized = " ".join(meaningful) + " stock market financial news"
                strategy = "Generic: added financial context to unknown query"
            else:
                optimized = "stock market financial news today"
                strategy = "Fallback: using default financial query"

        return {
            "original": original,
            "optimized": optimized,
            "entities": entities,
            "strategy": strategy,
        }


# ── Quick test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    gen = SmartQueryGenerator()

    test_queries = [
        "tesla stocks",
        "show me apple news",
        "oil prices",
        "banking sector",
        "nvidia and amd chips",
        "how is the stock market doing",
        "crypto trading",
        "walmart retail",
    ]

    for q in test_queries:
        result = gen.generate(q)
        print(f"\n  Input:     {result['original']}")
        print(f"  Optimized: {result['optimized']}")
        print(f"  Entities:  {result['entities']}")
        print(f"  Strategy:  {result['strategy']}")
