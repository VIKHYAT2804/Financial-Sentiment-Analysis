# Financial Sentiment Analysis System

An intelligent financial news sentiment analysis system that uses **FinBERT**, a transformer model designed for financial text, to classify news articles as positive, negative, or neutral. The system aggregates sentiment scores and generates BUY, SELL, or HOLD signals.

## Features

- **Financial News Scraping:** Collects news from sources such as Google News, Bing, and Reddit.
- **Smart Query Expansion:** Expands company names and stock-related queries to improve search results.
- **Data Preprocessing:** Cleans HTML content, removes duplicates, and prepares article text.
- **Sentiment Analysis:** Uses FinBERT to classify financial news with confidence scores.
- **Trading Signal Generation:** Aggregates article sentiment to generate BUY, SELL, or HOLD signals.
- **REST API:** Provides endpoints for searching, retrieving results, and downloading CSV reports.
- **Interactive Dashboard:** Visualizes sentiment distribution, article-level scores, and sentiment trends.
- **CLI Support:** Runs the analysis pipeline directly from the terminal.

## System Architecture

The system follows this pipeline:

1. User enters a company name or search query.
2. The query generator expands the search terms.
3. The scraper and data collector retrieve financial news.
4. The data cleaner preprocesses articles and removes duplicates.
5. FinBERT analyzes sentiment and produces confidence scores.
6. The signal generator aggregates sentiment and generates a trading signal.
7. Results are displayed through the CLI, REST API, or Streamlit dashboard.

## Project Structure

```text
financial-sentiment-analysis-main/
├── config.py
├── scraper.py
├── data_cleaner.py
├── csv_generator.py
├── api.py
├── data_collector.py
├── sentiment_analyzer.py
├── signal_generator.py
├── query_generator.py
├── dashboard.py
├── main.py
├── test_api.py
├── tests/
│   └── test_core.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Technologies Used

- Python
- FinBERT and Hugging Face Transformers
- PyTorch
- Pandas and NumPy
- Flask
- Streamlit
- Plotly
- BeautifulSoup
- Requests and feedparser
- TextBlob

## Installation

### Prerequisites

- Python 3.10 or later
- pip

### 1. Clone the repository

```bash
git clone https://github.com/VIKHYAT2804/Financial-Sentiment-Analysis.git
cd Financial-Sentiment-Analysis
```

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**Note:** The FinBERT model may download automatically from Hugging Face during the first run. This requires an internet connection and sufficient disk space.

## Running the Project

### Command-Line Interface

Run the main analysis pipeline:

```bash
python main.py
```

The program processes the collected financial news and displays a sentiment summary and trading signal.

### REST API

Start the Flask API:

```bash
python api.py
```

The API runs at:

`http://localhost:5000`

Available endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/search` | Starts a sentiment analysis job |
| GET | `/results?job_id=<job_id>` | Retrieves job status and analysis results |
| GET | `/download?job_id=<job_id>` | Downloads the generated CSV report |

Example request:

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"tesla\"}"
```

The search endpoint returns a job ID that can be used to retrieve the results.

### Streamlit Dashboard

Launch the dashboard:

```bash
python -m streamlit run dashboard.py
```

Open `http://localhost:8501` in your browser.

The dashboard provides sentiment distribution charts, article-level sentiment scores, sentiment trends, and individual article details.

## Running Tests

Run the offline unit tests:

```bash
python -m unittest discover -v
```

These tests cover core functionality, including query generation, sentiment-to-signal mapping, empty-input handling, and data cleaning.

For the API smoke test, start the API in one terminal and run the following in another:

```bash
python test_api.py
```

## Sentiment Classification

The primary model is **ProsusAI/finbert**, which classifies financial text into three categories:

- Positive
- Negative
- Neutral

If configured, the system can use TextBlob as a fallback sentiment analyzer when FinBERT is unavailable.

## Trading Signal Generation

The system uses an aggregate sentiment score to determine a signal.

| Aggregate Score | Signal |
|---|---|
| Score ≥ +0.15 | BUY |
| Score ≤ -0.15 | SELL |
| Between -0.15 and +0.15 | HOLD |

Article sentiment is aggregated using confidence-weighted scores. The thresholds can be adjusted in `config.py`.

## Configuration

The `config.py` file contains the system's configuration, including:

- Maximum scraper results per source
- API port
- FinBERT model identifier
- Sentiment model selection
- BUY and SELL thresholds

Configure any required API keys through the project's supported configuration settings. Do not commit API keys, passwords, or other secrets to GitHub.

## Limitations

- News availability depends on external websites, network access, and source restrictions.
- Initial FinBERT execution may require downloading a large model.
- Sentiment classifications are predictions and may not capture every financial nuance.
- BUY, SELL, and HOLD signals are analytical outputs, not guaranteed investment recommendations.

## Disclaimer

This project is intended for educational and research purposes only. Its sentiment scores and trading signals should not be treated as financial advice.

## License

No specific license is currently declared. Add a license file if you intend to permit reuse or redistribution under particular terms.
