"""
Sentiment Analysis Engine
Uses FinBERT (ProsusAI/finbert) for financial-domain sentiment classification.
Falls back to TextBlob if transformer model is unavailable.
"""

import time
from config import FINBERT_MODEL, USE_FINBERT, LABEL_SCORE_MAP


class SentimentAnalyzer:
    """Analyzes sentiment of financial text using FinBERT or TextBlob."""

    def __init__(self, use_finbert: bool = USE_FINBERT):
        self.use_finbert = use_finbert
        self.model_name = FINBERT_MODEL
        self.pipeline = None
        self._load_model()

    # ── Model loading ─────────────────────────────────────────────────

    def _load_model(self):
        """Load the sentiment analysis model."""
        if self.use_finbert:
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline as hf_pipeline

                print(f"⏳ Loading FinBERT model ({self.model_name})...")
                tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
                self.pipeline = hf_pipeline(
                    "sentiment-analysis",
                    model=model,
                    tokenizer=tokenizer,
                    top_k=None,           # return all label scores
                    truncation=True,
                    max_length=512,
                )
                print("✓  FinBERT model loaded successfully.\n")
            except Exception as e:
                print(f"⚠  Failed to load FinBERT: {e}")
                print("   Falling back to TextBlob.\n")
                self.use_finbert = False

    # ── Single-text analysis ──────────────────────────────────────────

    def analyze(self, text: str) -> dict:
        """
        Analyze sentiment of a single text string.

        Returns:
            dict with keys: label, score, confidence, scores_detail
        """
        if not text or not text.strip():
            return {"label": "neutral", "score": 0.0, "confidence": 0.0, "scores_detail": {}}

        if self.use_finbert and self.pipeline:
            return self._analyze_finbert(text)
        else:
            return self._analyze_textblob(text)

    def _analyze_finbert(self, text: str) -> dict:
        """Run FinBERT inference."""
        results = self.pipeline(text[:512])  # FinBERT max length

        # pipeline with top_k=None returns list of list of dicts
        scores = results[0] if isinstance(results[0], list) else results

        # Build detail dict and find best label
        scores_detail = {}
        best_label, best_score = "neutral", 0.0
        for item in scores:
            label = item["label"].lower()
            conf = item["score"]
            scores_detail[label] = round(conf, 4)
            if conf > best_score:
                best_label = label
                best_score = conf

        numeric_score = LABEL_SCORE_MAP.get(best_label, 0.0) * best_score

        return {
            "label": best_label,
            "score": round(numeric_score, 4),
            "confidence": round(best_score, 4),
            "scores_detail": scores_detail,
        }

    @staticmethod
    def _analyze_textblob(text: str) -> dict:
        """Fallback analysis using TextBlob."""
        from textblob import TextBlob

        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1

        if polarity > 0.05:
            label = "positive"
        elif polarity < -0.05:
            label = "negative"
        else:
            label = "neutral"

        confidence = min(abs(polarity) * 2, 1.0)  # rough approximation

        return {
            "label": label,
            "score": round(polarity, 4),
            "confidence": round(confidence, 4),
            "scores_detail": {"positive": max(polarity, 0), "negative": abs(min(polarity, 0)), "neutral": 1 - confidence},
        }

    # ── Batch analysis ────────────────────────────────────────────────

    def analyze_articles(self, articles: list[dict]) -> list[dict]:
        """
        Analyze a batch of articles.

        Each article dict must have 'title' and optionally 'description'.
        Returns list of article dicts augmented with sentiment fields.
        """
        results = []
        total = len(articles)
        start_time = time.time()

        print(f"📊 Analyzing sentiment for {total} articles...")

        for i, article in enumerate(articles, 1):
            # Combine title + description for richer context
            text = f"{article.get('title', '')}. {article.get('description', '')}"
            sentiment = self.analyze(text)

            enriched = {**article, **sentiment}
            results.append(enriched)

            # Progress indicator every 5 articles
            if i % 5 == 0 or i == total:
                elapsed = time.time() - start_time
                print(f"   Processed {i}/{total}  ({elapsed:.1f}s)")

        elapsed = time.time() - start_time
        throughput = total / elapsed if elapsed > 0 else 0
        print(f"\n✓  Sentiment analysis complete.")
        print(f"   Total time: {elapsed:.2f}s | Throughput: {throughput:.1f} articles/s\n")

        return results


# ── Quick test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()

    test_texts = [
        "Stocks surged today on strong earnings reports from tech giants.",
        "Markets crashed as trade war fears intensified.",
        "The company reported quarterly results in line with expectations.",
    ]

    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"  {result['label']:>8} ({result['confidence']:.2f})  →  {text[:60]}")
