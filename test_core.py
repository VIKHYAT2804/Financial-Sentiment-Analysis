"""Offline unit tests for core financial sentiment components."""
import unittest

from query_generator import SmartQueryGenerator
from signal_generator import SignalGenerator
from data_cleaner import DataCleaner


class QueryGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.generator = SmartQueryGenerator()

    def test_company_query_expansion(self):
        result = self.generator.generate("tesla stocks")
        self.assertEqual(result["original"], "tesla stocks")
        self.assertIn("TSLA", result["optimized"])
        self.assertTrue(result["entities"])

    def test_empty_query_has_fallback(self):
        result = self.generator.generate("   ")
        self.assertTrue(result["optimized"].strip())


class SignalGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.generator = SignalGenerator()

    def test_positive_articles_generate_buy(self):
        result = self.generator.aggregate_sentiment([
            {"label": "positive", "score": 0.9, "confidence": 0.9}
        ])
        self.assertEqual(result["signal"], "BUY")

    def test_negative_articles_generate_sell(self):
        result = self.generator.aggregate_sentiment([
            {"label": "negative", "score": -0.9, "confidence": 0.9}
        ])
        self.assertEqual(result["signal"], "SELL")

    def test_empty_articles_return_hold(self):
        result = self.generator.aggregate_sentiment([])
        self.assertEqual(result["signal"], "HOLD")
        self.assertEqual(result["article_count"], 0)


class DataCleanerTests(unittest.TestCase):
    def test_html_cleanup_and_duplicate_removal(self):
        cleaner = DataCleaner()
        result = cleaner.process_data([
            {"title": "<b>Markets rally</b>", "content": "Stocks rise"},
            {"title": "Markets rally", "content": "Duplicate"},
            {"title": "", "content": "No title"},
        ])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Markets rally")


if __name__ == "__main__":
    unittest.main()
