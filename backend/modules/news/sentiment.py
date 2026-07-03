"""
File: backend/modules/news/sentiment.py
Purpose: Sentiment scoring engine for financial news articles.
         Uses VADER (primary) + TextBlob (fallback) + keyword boosting.
         Called by NewsIntelligenceEngine for each article.
         Per SPEC Section 9.2.

Scoring:
  1. VADER compound score on headline + body snippet
  2. TextBlob polarity as secondary signal
  3. Financial keyword boosting (domain-specific)
  4. Composite = vader*0.55 + textblob*0.25 + keyword*0.20
  5. Clamped to [-1.0, +1.0]; converted to bullish/bearish/neutral decomposition
"""
import logging

logger = logging.getLogger("app")

# Domain-specific financial keyword boosters: word → impact on composite (-1 to +1)
_BULL_KEYWORDS = {
    "beat": 0.3, "beats": 0.3, "record": 0.25, "surge": 0.35, "surges": 0.35,
    "rally": 0.3, "rallied": 0.3, "upgrade": 0.3, "upgraded": 0.3, "outperform": 0.25,
    "strong": 0.2, "strength": 0.2, "growth": 0.15, "profit": 0.2, "dividend": 0.2,
    "buyback": 0.25, "bullish": 0.4, "breakout": 0.3, "all-time high": 0.4,
    "exceeds": 0.2, "exceed": 0.2, "positive": 0.15, "expansion": 0.15,
}
_BEAR_KEYWORDS = {
    "miss": -0.3, "misses": -0.3, "crash": -0.45, "plunge": -0.4, "plunges": -0.4,
    "decline": -0.2, "declines": -0.2, "cut": -0.2, "cuts": -0.2, "loss": -0.25,
    "losses": -0.25, "downgrade": -0.3, "downgraded": -0.3, "underperform": -0.25,
    "weak": -0.2, "weakness": -0.2, "recession": -0.4, "default": -0.45,
    "bankruptcy": -0.5, "bearish": -0.4, "breakdown": -0.35, "warning": -0.2,
    "layoff": -0.3, "layoffs": -0.3, "investigation": -0.25, "lawsuit": -0.2,
}


class SentimentAnalyzer:
    """
    Lexicon-based sentiment scoring for financial news.
    Uses VADER (primary) + TextBlob (fallback) + financial keyword boosting.
    Fully self-contained — no external API calls.
    """

    def __init__(self):
        self._vader = None
        self._vader_tried = False

    def _get_vader(self):
        """Lazy-load VADER, downloading lexicon if needed."""
        if self._vader_tried:
            return self._vader
        self._vader_tried = True
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self._vader = SentimentIntensityAnalyzer()
            logger.info("SentimentAnalyzer: VADER loaded")
        except ImportError:
            try:
                import nltk
                from nltk.sentiment.vader import SentimentIntensityAnalyzer
                try:
                    nltk.data.find("sentiment/vader_lexicon.zip")
                except LookupError:
                    nltk.download("vader_lexicon", quiet=True)
                self._vader = SentimentIntensityAnalyzer()
                logger.info("SentimentAnalyzer: NLTK VADER loaded")
            except Exception as e:
                logger.warning(f"SentimentAnalyzer: VADER unavailable ({e}), using keyword fallback")
                self._vader = None
        return self._vader

    def _vader_score(self, text: str) -> float:
        """Return VADER compound score (-1.0 to +1.0), or 0.0 if unavailable."""
        vader = self._get_vader()
        if vader is None or not text:
            return 0.0
        try:
            return float(vader.polarity_scores(text)["compound"])
        except Exception:
            return 0.0

    def _textblob_score(self, text: str) -> float:
        """Return TextBlob polarity (-1.0 to +1.0), or 0.0 if unavailable."""
        if not text:
            return 0.0
        try:
            from textblob import TextBlob
            return float(TextBlob(text).sentiment.polarity)
        except Exception:
            return 0.0

    def _keyword_score(self, text: str) -> float:
        """Domain-specific financial keyword boosting score (-1.0 to +1.0)."""
        if not text:
            return 0.0
        text_lower = text.lower()
        score = 0.0
        for kw, val in _BULL_KEYWORDS.items():
            if kw in text_lower:
                score += val
        for kw, val in _BEAR_KEYWORDS.items():
            if kw in text_lower:
                score += val  # already negative
        return max(-1.0, min(1.0, score))

    def analyze(self, headline: str, body: str = "") -> dict:
        """
        Score a news article for sentiment.

        Args:
            headline: Article headline text
            body: Optional article body text (may be truncated)

        Returns:
            {
                "bullish_score": float,    # 0.0–1.0
                "bearish_score": float,    # 0.0–1.0
                "neutral_score": float,    # 0.0–1.0
                "composite_score": float,  # -1.0 to +1.0 (positive=bullish)
            }
        """
        headline = (headline or "").strip()
        body = (body or "").strip()

        # Use full text for VADER; headline-only for keywords (less noise)
        full_text = f"{headline}. {body[:300]}" if body else headline

        vader_val  = self._vader_score(full_text)
        blob_val   = self._textblob_score(full_text)
        kw_val     = self._keyword_score(headline)

        # If VADER is unavailable, weight keyword scoring higher
        if self._vader is None:
            composite = blob_val * 0.55 + kw_val * 0.45
        else:
            composite = vader_val * 0.55 + blob_val * 0.25 + kw_val * 0.20

        composite = max(-1.0, min(1.0, composite))

        # Decompose into bull/bear/neutral probabilities (sum to 1.0)
        if composite > 0:
            bullish = 0.5 + composite * 0.5
            bearish = 0.5 - composite * 0.5
        else:
            bearish = 0.5 + abs(composite) * 0.5
            bullish = 0.5 - abs(composite) * 0.5
        neutral = 1.0 - abs(composite)
        # Normalize to sum = 1
        total = bullish + bearish + neutral
        if total > 0:
            bullish /= total
            bearish /= total
            neutral /= total

        return {
            "bullish_score":   round(bullish, 4),
            "bearish_score":   round(bearish, 4),
            "neutral_score":   round(neutral, 4),
            "composite_score": round(composite, 4),
        }

    def analyze_batch(self, articles: list) -> list:
        """
        Score a list of article dicts [{title, content/body/description}].
        Returns list of sentiment result dicts in same order.
        """
        results = []
        for art in articles:
            headline = art.get("title") or art.get("headline") or ""
            body = art.get("content") or art.get("body") or art.get("description") or art.get("summary") or ""
            results.append(self.analyze(headline, body))
        return results
