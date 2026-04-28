"""Configuration settings for the trading agent."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Claude API
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    claude_model: str = "claude-sonnet-4-20250514"

    # Database
    db_path: str = str(BASE_DIR / "data" / "trading_agent.db")

    # News sources (RSS feeds) - free, reliable sources
    news_sources: dict[str, str] = {
        "reuters_business": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
        "cnbc_top": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
        "cnbc_world": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100727362",
        "google_news_markets": "https://news.google.com/rss/search?q=stock+market+trading&hl=en",
        "google_news_geopolitics": "https://news.google.com/rss/search?q=geopolitics+war+sanctions&hl=en",
        "marketwatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
        "ansa_economia": "https://www.ansa.it/sito/notizie/economia/economia_rss.xml",
        "yahoo_finance": "https://finance.yahoo.com/news/rssindex",
    }

    # Market settings - major tradeable assets
    watchlist: list[str] = [
        # Major ETFs
        "SPY", "QQQ", "DIA", "IWM",
        # Leveraged ETFs (for aggressive trading)
        "TQQQ", "SQQQ", "SPXL", "SPXS", "UVXY",
        # Big tech
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
        # Financials
        "JPM", "GS",
        # Energy
        "XOM", "CVX",
        # Commodities
        "GLD", "SLV", "USO",
        # Volatility
        "^VIX",
    ]

    # Swarm settings (MiroFish-inspired)
    swarm_agent_count: int = 12
    swarm_simulation_rounds: int = 3
    swarm_debate_enabled: bool = True

    # Signal settings
    signal_confidence_threshold: float = 0.65
    max_daily_signals: int = 5
    max_risk_per_trade_pct: float = 5.0  # max 5% of capital per trade
    default_capital: float = 3000.0  # €3,000 starting capital

    # Scheduler
    news_check_interval_minutes: int = 15
    full_analysis_cron: str = "0 6 * * 1-5"  # 6 AM UTC, weekdays (before US open)
    intraday_scan_cron: str = "30 13,15,17,19 * * 1-5"  # During US market hours

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
