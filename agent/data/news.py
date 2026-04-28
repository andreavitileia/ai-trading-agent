"""News scraper using RSS feeds from major financial/geopolitical sources."""

import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

import feedparser
import httpx
from bs4 import BeautifulSoup

from ..config import settings


@dataclass
class NewsArticle:
    title: str
    summary: str
    url: str
    source: str
    published: datetime
    content: str = ""
    sentiment: str = ""  # filled later by analysis
    relevance_score: float = 0.0

    @property
    def uid(self) -> str:
        return hashlib.md5(self.url.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "uid": self.uid,
            "title": self.title,
            "summary": self.summary[:500],
            "url": self.url,
            "source": self.source,
            "published": self.published.isoformat(),
            "sentiment": self.sentiment,
            "relevance_score": self.relevance_score,
        }


def fetch_rss_feed(url: str, source_name: str) -> list[NewsArticle]:
    """Parse a single RSS feed and return articles."""
    articles = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:  # limit per source
            published = datetime.now(tz=timezone.utc)
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                except Exception:
                    pass

            summary = ""
            if hasattr(entry, "summary"):
                summary = BeautifulSoup(entry.summary, "lxml").get_text(strip=True)

            articles.append(
                NewsArticle(
                    title=entry.get("title", ""),
                    summary=summary[:1000],
                    url=entry.get("link", ""),
                    source=source_name,
                    published=published,
                )
            )
    except Exception:
        pass
    return articles


def fetch_all_news() -> list[NewsArticle]:
    """Fetch news from all configured RSS sources."""
    all_articles: list[NewsArticle] = []
    seen_urls: set[str] = set()

    for source_name, url in settings.news_sources.items():
        articles = fetch_rss_feed(url, source_name)
        for a in articles:
            if a.url not in seen_urls:
                seen_urls.add(a.url)
                all_articles.append(a)

    # Sort by recency
    all_articles.sort(key=lambda a: a.published, reverse=True)
    return all_articles


def fetch_article_content(url: str, timeout: float = 10.0) -> str:
    """Try to fetch the full text of an article."""
    try:
        resp = httpx.get(url, timeout=timeout, follow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 (compatible; TradingAgent/1.0)"
        })
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "lxml")
            # Remove script/style elements
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            # Truncate to avoid huge texts
            return text[:5000]
    except Exception:
        pass
    return ""


def build_news_context(max_articles: int = 30) -> str:
    """Build a news context string for LLM analysis."""
    articles = fetch_all_news()
    lines = [
        "# Latest Financial & Geopolitical News\n",
        f"Fetched at: {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n",
    ]

    for i, article in enumerate(articles[:max_articles], 1):
        lines.append(f"\n## [{i}] {article.title}")
        lines.append(f"Source: {article.source} | {article.published.strftime('%Y-%m-%d %H:%M')}")
        if article.summary:
            lines.append(f"Summary: {article.summary[:300]}")
        lines.append("")

    return "\n".join(lines)
