"""
Configuration for Financial Sentiment Analysis System
"""

from dotenv import load_dotenv
import os

# ─── API Configuration ───────────────────────────────────────────────
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
# NEWS_API_KEY = "d1a1596b0fe0487cbc76ffed2e390b55"  # Set your NewsAPI key here (https://newsapi.org/)
NEWS_API_URL = "https://newsapi.org/v2/everything"

# ─── Scraper Configuration ───────────────────────────────────────────
SCRAPER_DELAY_MIN = 1.0    # Minimum delay between requests (seconds)
SCRAPER_DELAY_MAX = 3.0    # Maximum delay between requests (seconds)
SCRAPER_MAX_RESULTS_PER_SOURCE = 20
SCRAPER_TIMEOUT = 15       # Request timeout (seconds)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
]

# ─── REST API Configuration ──────────────────────────────────────────
API_HOST = "0.0.0.0"
API_PORT = 5000
OUTPUT_DIR = "output"
# ─── Model Configuration ─────────────────────────────────────────────
# Primary: FinBERT (best accuracy for financial text)
FINBERT_MODEL = "ProsusAI/finbert"

# Fallback: TextBlob (lightweight, no GPU required)
USE_FINBERT = True  # Set to False to use TextBlob fallback

# ─── Sentiment Thresholds ────────────────────────────────────────────
# Trading signal generation thresholds
BUY_THRESHOLD = 0.15       # Aggregate score above this → BUY
SELL_THRESHOLD = -0.15     # Aggregate score below this → SELL
# Between SELL_THRESHOLD and BUY_THRESHOLD → HOLD

# ─── Data Collection Settings ────────────────────────────────────────
DEFAULT_QUERY = "stock market"
MAX_ARTICLES = 50
LANGUAGE = "en"
SORT_BY = "relevancy"

# ─── Sentiment Label Mapping ─────────────────────────────────────────
# Maps FinBERT labels to numeric scores
LABEL_SCORE_MAP = {
    "positive": 1.0,
    "negative": -1.0,
    "neutral": 0.0,
}

# ─── Sample Data ─────────────────────────────────────────────────────
SAMPLE_ARTICLES = [
    {
        "title": "Tech Stocks Surge as AI Investments Drive Market Rally",
        "description": "Major technology companies saw significant gains today as investors poured billions into artificial intelligence ventures, pushing the NASDAQ to new all-time highs.",
        "source": "Financial Times",
        "publishedAt": "2026-04-02T10:30:00Z",
    },
    {
        "title": "Federal Reserve Signals Potential Rate Cut Amid Cooling Inflation",
        "description": "The Federal Reserve hinted at possible interest rate reductions in the coming months as inflation data shows signs of sustained cooling, boosting market optimism.",
        "source": "Reuters",
        "publishedAt": "2026-04-02T09:15:00Z",
    },
    {
        "title": "Oil Prices Plummet on Weak Global Demand Forecasts",
        "description": "Crude oil prices dropped sharply after OPEC revised its global demand outlook downward, raising concerns about economic slowdown in major economies.",
        "source": "Bloomberg",
        "publishedAt": "2026-04-02T08:45:00Z",
    },
    {
        "title": "Banking Sector Faces Headwinds as Loan Defaults Rise",
        "description": "Several major banks reported increasing loan default rates, particularly in commercial real estate, leading to declining share prices across the sector.",
        "source": "Wall Street Journal",
        "publishedAt": "2026-04-02T11:00:00Z",
    },
    {
        "title": "Cryptocurrency Market Remains Volatile After Regulatory Uncertainty",
        "description": "Bitcoin and other major cryptocurrencies experienced wild swings as regulators worldwide continue to debate the framework for digital asset oversight.",
        "source": "CoinDesk",
        "publishedAt": "2026-04-02T07:30:00Z",
    },
    {
        "title": "Electric Vehicle Sales Exceed Expectations in Q1 2026",
        "description": "Global electric vehicle sales surpassed analyst expectations in the first quarter, driven by strong demand in China and Europe, boosting EV manufacturer stocks.",
        "source": "CNBC",
        "publishedAt": "2026-04-01T14:20:00Z",
    },
    {
        "title": "Retail Sector Struggles as Consumer Spending Slows",
        "description": "Major retailers reported disappointing quarterly results as consumers tighten budgets amid persistent cost-of-living pressures, sending retail stocks lower.",
        "source": "MarketWatch",
        "publishedAt": "2026-04-01T16:45:00Z",
    },
    {
        "title": "Pharmaceutical Giants Announce Breakthrough Drug Approvals",
        "description": "Two leading pharmaceutical companies received FDA approval for groundbreaking treatments, driving their stock prices up significantly in after-hours trading.",
        "source": "Reuters",
        "publishedAt": "2026-04-01T18:00:00Z",
    },
    {
        "title": "Supply Chain Disruptions Ease, Manufacturing Stocks Recover",
        "description": "Global supply chain bottlenecks showed significant improvement, with shipping delays returning to pre-pandemic levels and manufacturing activity picking up pace.",
        "source": "Financial Times",
        "publishedAt": "2026-04-01T12:10:00Z",
    },
    {
        "title": "Trade Tensions Between US and China Escalate Over Tariffs",
        "description": "Markets fell sharply as the United States announced new tariffs on Chinese imports, sparking fears of a renewed trade war and global economic disruption.",
        "source": "Bloomberg",
        "publishedAt": "2026-04-01T09:30:00Z",
    },
    {
        "title": "Green Energy Investments Hit Record High in 2026",
        "description": "Renewable energy investments surged to unprecedented levels as governments and corporations accelerate their net-zero commitments, benefiting clean energy stocks.",
        "source": "The Guardian",
        "publishedAt": "2026-03-31T15:00:00Z",
    },
    {
        "title": "Housing Market Shows Signs of Recovery After Prolonged Slump",
        "description": "Home sales picked up for the third consecutive month as mortgage rates stabilized, providing a much-needed boost to real estate and construction stocks.",
        "source": "CNBC",
        "publishedAt": "2026-03-31T11:25:00Z",
    },
    {
        "title": "Hedge Funds Report Mixed Results in First Quarter",
        "description": "Major hedge funds delivered varied performance in Q1, with some benefiting from equity rallies while others suffered losses from commodity bets gone wrong.",
        "source": "Wall Street Journal",
        "publishedAt": "2026-03-31T13:40:00Z",
    },
    {
        "title": "Global Semiconductor Shortage Finally Coming to an End",
        "description": "Chip manufacturers reported significant increases in production capacity, signaling the end of the prolonged semiconductor shortage that plagued industries worldwide.",
        "source": "TechCrunch",
        "publishedAt": "2026-03-30T10:15:00Z",
    },
    {
        "title": "Corporate Earnings Season Kicks Off With Strong Results",
        "description": "Early earnings reports from major corporations exceeded Wall Street expectations, with revenue and profit growth surpassing forecasts across multiple sectors.",
        "source": "MarketWatch",
        "publishedAt": "2026-03-30T08:50:00Z",
    },
]