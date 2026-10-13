"""
Signal Generator Module
Aggregates sentiment scores and generates trading signals (BUY / SELL / HOLD).
"""

import time
from datetime import datetime
from config import BUY_THRESHOLD, SELL_THRESHOLD, LABEL_SCORE_MAP


class SignalGenerator:
    """Generates trading signals from aggregated article sentiments."""

    def __init__(
        self,
        buy_threshold: float = BUY_THRESHOLD,
        sell_threshold: float = SELL_THRESHOLD,
    ):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    # ── Aggregation ───────────────────────────────────────────────────

    def aggregate_sentiment(self, analyzed_articles: list[dict]) -> dict:
        """
        Compute weighted-average sentiment across articles.

        Weights each article's numeric score by its confidence.

        Returns:
            dict with aggregate_score, signal, distribution, article_count, metrics
        """
        start = time.time()

        if not analyzed_articles:
            return self._empty_result()

        total_weight = 0.0
        weighted_sum = 0.0
        distribution = {"positive": 0, "negative": 0, "neutral": 0}

        for article in analyzed_articles:
            label = article.get("label", "neutral")
            confidence = article.get("confidence", 0.5)
            score = article.get("score", LABEL_SCORE_MAP.get(label, 0.0))

            weighted_sum += score * confidence
            total_weight += confidence
            distribution[label] = distribution.get(label, 0) + 1

        aggregate_score = weighted_sum / total_weight if total_weight else 0.0
        signal = self._score_to_signal(aggregate_score)
        latency = time.time() - start

        return {
            "aggregate_score": round(aggregate_score, 4),
            "signal": signal,
            "distribution": distribution,
            "article_count": len(analyzed_articles),
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "latency_ms": round(latency * 1000, 2),
                "buy_threshold": self.buy_threshold,
                "sell_threshold": self.sell_threshold,
            },
        }

    # ── Trading signal ────────────────────────────────────────────────

    def _score_to_signal(self, score: float) -> str:
        """Map aggregate score to a trading signal."""
        if score >= self.buy_threshold:
            return "BUY"
        elif score <= self.sell_threshold:
            return "SELL"
        else:
            return "HOLD"

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _empty_result() -> dict:
        return {
            "aggregate_score": 0.0,
            "signal": "HOLD",
            "distribution": {"positive": 0, "negative": 0, "neutral": 0},
            "article_count": 0,
            "timestamp": datetime.now().isoformat(),
            "metrics": {"latency_ms": 0.0},
        }

    def format_report(self, result: dict) -> str:
        """Return a human-readable report string."""
        dist = result["distribution"]
        total = result["article_count"]
        score = result["aggregate_score"]
        signal = result["signal"]

        signal_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal, "⚪")

        lines = [
            "╔══════════════════════════════════════════════════╗",
            "║        FINANCIAL SENTIMENT ANALYSIS REPORT       ║",
            "╠══════════════════════════════════════════════════╣",
            f"║  Articles Analyzed :  {total:<27}║",
            f"║  Positive          :  {dist.get('positive', 0):<27}║",
            f"║  Negative          :  {dist.get('negative', 0):<27}║",
            f"║  Neutral           :  {dist.get('neutral', 0):<27}║",
            "╠══════════════════════════════════════════════════╣",
            f"║  Aggregate Score   :  {score:<+27.4f}║",
            f"║  Trading Signal    :  {signal_emoji} {signal:<24}║",
            "╠══════════════════════════════════════════════════╣",
            f"║  Timestamp         :  {result['timestamp'][:19]:<27}║",
            f"║  Latency           :  {result['metrics']['latency_ms']:.2f} ms{' ' * 21}║",
            "╚══════════════════════════════════════════════════╝",
        ]
        return "\n".join(lines)


# ── Quick test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = [
        {"label": "positive", "score": 0.85, "confidence": 0.92},
        {"label": "negative", "score": -0.70, "confidence": 0.88},
        {"label": "positive", "score": 0.60, "confidence": 0.75},
        {"label": "neutral", "score": 0.05, "confidence": 0.65},
    ]

    gen = SignalGenerator()
    result = gen.aggregate_sentiment(sample)
    print(gen.format_report(result))
