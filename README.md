# 📈 Financial Sentiment Analysis System

An intelligent system that analyzes financial news to determine stock market sentiment using **FinBERT** — a transformer model trained specifically on financial text. It classifies articles as positive, negative, or neutral, generates trading signals, and provides access via a CLI, an interactive dashboard, and a **REST API with dynamic Web Scraping**.

---

## 🏗️ Architecture

```
┌──────────────┐      ┌───────────────────┐        ┌──────────────────┐     ┌─────────────┐
│ Web Scraping │      │ Data Preprocessing│        │    Sentiment     │     │   Signal    │
│(Google, Bing,│────▶ │  & Deduplication  │ ────▶  │    Analysis      │────▶│ Generation  │
│ Reddit)      │      │  (Cleaner)        │        │   (FinBERT)      │     │(BUY/SELL)   │
└──────────────┘      └───────────────────┘        └──────────────────┘     └─────────────┘
                                                                                   │
             ┌─────────────────────────┬─────────────────────────┬─────────────────┘
             ▼                         ▼                         ▼
    ┌────────────────┐        ┌────────────────┐        ┌────────────────┐
    │ REST API       │        │ CLI Pipeline   │        │ Dashboard      │
    │ (Flask + CSV)  │        │ (Terminal)     │        │ (Streamlit)    │
    └────────────────┘        └────────────────┘        └────────────────┘
```

The system follows a modular pipeline:

1. **Smart Query Expansion** — Enhances user queries by detecting companies and tickers (e.g., "tesla" -> "Tesla TSLA stock earnings revenue")
2. **Data Collection** — Fetches financial news via NewsAPI or dynamic web scraping (Google News, Bing, Reddit)
3. **Preprocessing** — Cleans HTML, deduplicates, and formats article text
4. **Sentiment Analysis** — Classifies each article using FinBERT with confidence scores
5. **Aggregation** — Computes weighted-average sentiment across all articles
6. **Signal Generation** — Produces BUY / SELL / HOLD trading signals

---

## 📂 Project Structure

```
sentimental-analysis/
├── config.py               # Configuration, API keys, scraper settings
├── scraper.py              # Multi-source concurrent web scraper
├── data_cleaner.py         # HTML stripping and deduplication
├── csv_generator.py        # Pandas-based CSV export
├── api.py                  # Flask REST API server
├── data_collector.py       # NewsAPI data collection (Legacy/CLI)
├── sentiment_analyzer.py   # FinBERT sentiment engine
├── signal_generator.py     # Aggregation + trading signal logic
├── query_generator.py      # Smart query expansion logic
├── dashboard.py            # Streamlit visualization dashboard
├── main.py                 # CLI pipeline entry point
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# 1. Navigate to the project directory
cd financial-sentiment-analysis-main

# 2. Install dependencies
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

> **Note:** FinBERT (~500 MB) downloads automatically on first run. No GPU required — it runs on CPU as well.

---

### Running the REST API

The system provides a background-processed REST API with CSV export.

```bash
python api.py
```

The server runs on `http://localhost:5000`.

**Endpoints:**
1. `POST /search`
   ```bash
   curl -X POST http://localhost:5000/search -H "Content-Type: application/json" -d "{\"query\": \"tesla\"}"
   # Returns a job_id immediately
   ```
2. `GET /results?job_id=<job_id>`
   Poll this endpoint to get the processing status. Once complete, it returns the sentiment summary and analyzed articles.
3. `GET /download?job_id=<job_id>`
   Downloads the generated CSV file containing all scraped and analyzed data.

---

### Running Tests

Run the offline unit tests (no live API server or network access required):

```bash
python -m unittest discover -v
```

The manual API smoke test requires the server to be running in a separate terminal:

```bash
python test_api.py
```

### Running the CLI Pipeline

```bash
python main.py
```

This runs the full pipeline and prints a formatted report to the terminal:

```
╔══════════════════════════════════════════════════╗
║        FINANCIAL SENTIMENT ANALYSIS REPORT       ║
╠══════════════════════════════════════════════════╣
║  Articles Analyzed :  15                         ║
║  Positive          :  9                          ║
║  Negative          :  6                          ║
╠══════════════════════════════════════════════════╣
║  Aggregate Score   :  +0.1246                    ║
║  Trading Signal    :  🟡 HOLD                    ║
╚══════════════════════════════════════════════════╝
```

---

### Launching the Dashboard

```bash
python -m streamlit run dashboard.py
```

Opens an interactive dashboard at `http://localhost:8501` with:

- **Trading Signal Card** — BUY / SELL / HOLD with aggregate score
- **Sentiment Distribution** — Pie chart of positive / negative / neutral
- **Scores by Article** — Horizontal bar chart of per-article sentiment
- **Sentiment Over Time** — Timeline scatter plot
- **Article Details** — Individual cards with source, label, confidence

---

## 🔧 Configuration

All settings are in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `SCRAPER_MAX_RESULTS_PER_SOURCE` | `20` | Max results to scrape per source |
| `API_PORT` | `5000` | Flask API port |
| `FINBERT_MODEL` | `ProsusAI/finbert` | Hugging Face model identifier |
| `USE_FINBERT` | `True` | Set `False` to use TextBlob fallback |
| `BUY_THRESHOLD` | `0.15` | Aggregate score above this → BUY |
| `SELL_THRESHOLD` | `-0.15` | Aggregate score below this → SELL |

---

## 🧠 Models

### FinBERT (Primary)

- **Model**: [ProsusAI/finbert](https://huggingface.co/ProsusAI/finbert)
- **Training**: Pre-trained on financial text corpus
- **Labels**: `positive`, `negative`, `neutral`
- **Strengths**: Understands finance-specific language and context

### TextBlob (Fallback)

- Lightweight, rule-based sentiment analysis
- Automatically used if FinBERT fails to load

---

## 📊 Signal Generation

Trading signals are generated from confidence-weighted sentiment aggregation:

| Condition | Signal |
|-----------|--------|
| Aggregate Score ≥ +0.15 | 🟢 **BUY** |
| Aggregate Score ≤ -0.15 | 🔴 **SELL** |
| Between -0.15 and +0.15 | 🟡 **HOLD** |

Each article's sentiment score is weighted by its confidence value before averaging.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Sentiment Model | FinBERT (Hugging Face Transformers) |
| Web Scraping | BeautifulSoup, feedparser, requests |
| REST API | Flask |
| Visualization | Streamlit + Plotly |
| Data Processing | Pandas |
| Deep Learning | PyTorch |
| Fallback NLP | TextBlob |

---

## 📄 License

This project is for educational and research purposes.
