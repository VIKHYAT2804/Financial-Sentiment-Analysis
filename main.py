"""
Financial Sentiment Analysis System — Main Entry Point
Orchestrates: Data Collection → Sentiment Analysis → Signal Generation
"""

import sys
import time
from data_collector import NewsCollector
from sentiment_analyzer import SentimentAnalyzer
from signal_generator import SignalGenerator


def main():
    print()
    print("=" * 55)
    print("  FINANCIAL SENTIMENT ANALYSIS SYSTEM")
    print("  Powered by FinBERT · transformer-based NLP")
    print("=" * 55)
    print()

    overall_start = time.time()

    # ── Step 1: Collect Data ──────────────────────────────────────
    print("─── STEP 1: Data Collection ───────────────────────────")
    collector = NewsCollector()
    articles, query_info = collector.fetch_articles()

    if query_info:
        print(f"  🧠 Smart Query Expansion:")
        print(f"     Original:  {query_info['original']}")
        print(f"     Optimized: {query_info['optimized']}")
        if query_info['entities']:
            ents = ", ".join(f"{e['name']} ({e['ticker']})" for e in query_info['entities'])
            print(f"     Detected:  {ents}")
        print(f"     Strategy:  {query_info['strategy']}")
        print()

    if not articles:
        print("✗ No articles found. Exiting.")
        sys.exit(1)

    # ── Step 2: Sentiment Analysis ────────────────────────────────
    print("─── STEP 2: Sentiment Analysis ────────────────────────")
    analyzer = SentimentAnalyzer()
    analyzed = analyzer.analyze_articles(articles)

    # ── Step 3: Signal Generation ─────────────────────────────────
    print("─── STEP 3: Signal Generation ─────────────────────────")
    generator = SignalGenerator()
    result = generator.aggregate_sentiment(analyzed)
    print(generator.format_report(result))

    # ── Step 4: Article Details ───────────────────────────────────
    print("\n─── ARTICLE DETAILS ───────────────────────────────────")
    for i, a in enumerate(analyzed, 1):
        label = a.get("label", "neutral")
        conf = a.get("confidence", 0)
        score = a.get("score", 0)

        icon = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}.get(label, "⚪")
        print(f" {i:>2}. {icon} {label.upper():<9} (score: {score:+.4f}, conf: {conf:.2%})")
        print(f"     {a.get('title', '')}")
        print(f"     [{a.get('source', '')}] {a.get('publishedAt', '')[:10]}")
        print()

    # ── Summary ──────────────────────────────────────────────────
    total_time = time.time() - overall_start
    print("─── SUMMARY ───────────────────────────────────────────")
    print(f"  Total Pipeline Time : {total_time:.2f}s")
    print(f"  Articles Processed  : {len(analyzed)}")
    print(f"  Aggregate Score     : {result['aggregate_score']:+.4f}")
    print(f"  Trading Signal      : {result['signal']}")
    print()
    print("  💡 Launch the dashboard for interactive visualization:")
    print("     streamlit run dashboard.py")
    print()


if __name__ == "__main__":
    main()
