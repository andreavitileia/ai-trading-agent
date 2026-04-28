"""Main entry point for the AI Trading Agent."""

import logging
import os
import sys

import uvicorn

from .config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def main():
    """Start the trading agent server."""
    # Ensure API key is set
    if not settings.anthropic_api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY", "") or os.getenv("Claude", "")
        if api_key:
            settings.anthropic_api_key = api_key
        else:
            logger.error("ANTHROPIC_API_KEY not set. Please set it in .env or environment.")
            sys.exit(1)

    logger.info("=" * 60)
    logger.info("  AI Trading Agent - MiroFish Swarm + Claude")
    logger.info("=" * 60)
    logger.info(f"  Capital: €{settings.default_capital:,.0f}")
    logger.info(f"  Watchlist: {len(settings.watchlist)} tickers")
    logger.info(f"  Swarm agents: {settings.swarm_agent_count}")
    logger.info(f"  Model: {settings.claude_model}")
    logger.info(f"  Dashboard: http://localhost:{settings.api_port}")
    logger.info("=" * 60)

    uvicorn.run(
        "agent.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
