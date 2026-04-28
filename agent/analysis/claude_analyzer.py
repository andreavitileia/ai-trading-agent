"""Claude-powered deep analysis for individual queries and news sentiment."""

import json
import logging
from typing import Optional

import anthropic

from ..config import settings

logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    """Uses Claude for deep financial analysis beyond the swarm."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(
            api_key=api_key or settings.anthropic_api_key,
        )
        self.model = settings.claude_model

    def analyze_news_sentiment(self, articles: list[dict]) -> list[dict]:
        """Analyze sentiment and market impact of news articles in batch."""
        if not articles:
            return []

        news_text = "\n".join(
            f"[{i+1}] {a.get('title', '')} - {a.get('summary', '')[:200]}"
            for i, a in enumerate(articles[:20])
        )

        prompt = (
            "Analyze the market impact of these news articles.\n"
            "For each article, determine:\n"
            "1. Sentiment (very_negative, negative, neutral, positive, very_positive)\n"
            "2. Market impact score (-1.0 to +1.0)\n"
            "3. Affected sectors/tickers\n"
            "4. Urgency (low, medium, high, critical)\n\n"
            f"Articles:\n{news_text}\n\n"
            "Respond in JSON:\n"
            '{"articles": [\n'
            '  {"index": 1, "sentiment": "...", "impact_score": 0.0,\n'
            '   "affected_tickers": ["..."], "urgency": "...",\n'
            '   "brief_analysis": "..."}\n'
            "]}"
        )

        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                system="You are a financial news analyst. Be precise and quantitative.",
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.content[0].text
            return self._extract_json(text).get("articles", [])
        except Exception as e:
            logger.error(f"News sentiment analysis failed: {e}")
            return []

    def quick_market_outlook(self, market_context: str) -> dict:
        """Generate a quick market outlook from technical data."""
        prompt = (
            "Based on this market data, provide a quick outlook.\n\n"
            f"{market_context[:5000]}\n\n"
            "Respond in JSON:\n"
            "{\n"
            '  "overall_sentiment": "bullish|bearish|neutral",\n'
            '  "key_levels": {"SPY_support": ..., "SPY_resistance": ...},\n'
            '  "sector_rotation": "which sectors are leading/lagging",\n'
            '  "volatility_outlook": "low|normal|elevated|high",\n'
            '  "one_liner": "One sentence summary of market conditions"\n'
            "}"
        )

        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.3,
                system="You are a market technician. Be concise and data-driven.",
                messages=[{"role": "user", "content": prompt}],
            )
            return self._extract_json(resp.content[0].text)
        except Exception as e:
            logger.error(f"Quick outlook failed: {e}")
            return {"error": str(e)}

    def chat(self, question: str, context: str = "") -> str:
        """Interactive chat about markets and trading."""
        system = (
            "You are an expert financial advisor and trading analyst. "
            "You have access to real-time market data and 100 years of historical knowledge. "
            "Be specific, actionable, and honest about risks. "
            "Always mention that past performance doesn't guarantee future results. "
            "Respond in the same language as the question."
        )

        user_msg = question
        if context:
            user_msg = f"Current market context:\n{context[:3000]}\n\nQuestion: {question}"

        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.5,
                system=system,
                messages=[{"role": "user", "content": user_msg}],
            )
            return resp.content[0].text
        except Exception as e:
            return f"Error: {e}"

    def _extract_json(self, text: str) -> dict:
        import re
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                pass
        return {"raw": text}
