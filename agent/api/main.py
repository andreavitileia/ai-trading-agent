"""FastAPI backend serving the trading agent dashboard."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from ..config import settings, BASE_DIR
from ..data.market import (
    build_market_context,
    fetch_recent,
    add_technical_indicators,
    detect_patterns,
    get_market_summary,
)
from ..data.news import build_news_context, fetch_all_news
from ..data.historical_events import get_events_summary, find_analogous_events
from ..swarm.engine import SwarmEngine
from ..analysis.claude_analyzer import ClaudeAnalyzer
from ..signals.generator import (
    extract_signals_from_consensus,
    save_signals,
    load_latest_signals,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Trading Agent",
    description="MiroFish-inspired swarm intelligence + Claude for market prediction",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# In-memory store for latest analysis
_latest_analysis: dict = {}
_analysis_running: bool = False


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the dashboard."""
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return index_path.read_text()
    return "<h1>AI Trading Agent</h1><p>Frontend not found. API is running.</p>"


@app.get("/api/status")
async def status():
    """Get system status."""
    return {
        "status": "running",
        "analysis_running": _analysis_running,
        "last_analysis": _latest_analysis.get("consensus", {}).get("generated_at"),
        "watchlist_count": len(settings.watchlist),
        "swarm_agents": settings.swarm_agent_count,
        "capital": settings.default_capital,
    }


@app.get("/api/market/summary")
async def market_summary():
    """Get current market summary for watchlist."""
    tickers = ["SPY", "QQQ", "DIA", "IWM", "^VIX", "GLD", "TQQQ"]
    summary = get_market_summary(tickers)
    return {"data": summary, "timestamp": datetime.now(tz=timezone.utc).isoformat()}


@app.get("/api/market/analysis/{ticker}")
async def ticker_analysis(ticker: str):
    """Get detailed technical analysis for a ticker."""
    df = fetch_recent(ticker, days=60)
    if df.empty:
        return {"error": f"No data for {ticker}"}

    df = add_technical_indicators(df)
    patterns = detect_patterns(df)
    latest = df.iloc[-1]

    return {
        "ticker": ticker,
        "price": round(float(latest["Close"]), 2),
        "daily_return": round(float(latest.get("Daily_Return", 0)) * 100, 2),
        "rsi": round(float(latest.get("RSI_14", 0)), 1),
        "macd": round(float(latest.get("MACD", 0)), 4),
        "volatility_20d": round(float(latest.get("Volatility_20d", 0)) * 100, 1),
        "sma_20": round(float(latest.get("SMA_20", 0)), 2),
        "sma_50": round(float(latest.get("SMA_50", 0)), 2),
        "sma_200": round(float(latest.get("SMA_200", 0)), 2),
        "bb_upper": round(float(latest.get("BB_upper", 0)), 2),
        "bb_lower": round(float(latest.get("BB_lower", 0)), 2),
        "atr": round(float(latest.get("ATR_14", 0)), 2),
        "adx": round(float(latest.get("ADX", 0)), 1),
        "patterns": patterns,
    }


@app.get("/api/news")
async def news():
    """Get latest news feed."""
    articles = fetch_all_news()
    return {
        "count": len(articles),
        "articles": [a.to_dict() for a in articles[:50]],
    }


@app.get("/api/signals")
async def get_signals():
    """Get current trading signals."""
    signals = load_latest_signals()
    if not signals and _latest_analysis:
        consensus = _latest_analysis.get("consensus", {})
        signals = extract_signals_from_consensus(consensus)

    return {
        "count": len(signals),
        "signals": [s.to_dict() for s in signals],
        "capital": settings.default_capital,
    }


@app.get("/api/analysis/latest")
async def latest_analysis():
    """Get the latest full swarm analysis."""
    if not _latest_analysis:
        return {"status": "no_analysis", "message": "Run /api/analysis/run first"}
    return _latest_analysis


@app.post("/api/analysis/run")
async def run_analysis(background_tasks: BackgroundTasks):
    """Trigger a full swarm analysis (runs in background)."""
    global _analysis_running
    if _analysis_running:
        return {"status": "already_running"}

    _analysis_running = True
    background_tasks.add_task(_run_full_analysis)
    return {"status": "started", "message": "Swarm analysis started in background"}


async def _run_full_analysis():
    """Execute the full swarm analysis pipeline."""
    global _latest_analysis, _analysis_running
    try:
        logger.info("Starting full swarm analysis...")

        # Gather all context
        market_ctx = build_market_context(settings.watchlist[:10])
        news_ctx = build_news_context(max_articles=30)
        historical_ctx = get_events_summary()

        # Run swarm
        engine = SwarmEngine()
        result = engine.run_full_analysis(market_ctx, news_ctx, historical_ctx)

        # Extract signals
        consensus = result.get("consensus", {})
        signals = extract_signals_from_consensus(consensus)
        save_signals(signals)

        _latest_analysis = result
        logger.info(f"Analysis complete. Generated {len(signals)} signals.")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        _latest_analysis = {"error": str(e)}
    finally:
        _analysis_running = False


@app.get("/api/analysis/quick")
async def quick_analysis():
    """Quick market outlook without full swarm (faster, cheaper)."""
    analyzer = ClaudeAnalyzer()
    market_ctx = build_market_context(["SPY", "QQQ", "^VIX", "GLD"])
    result = analyzer.quick_market_outlook(market_ctx)
    return result


@app.post("/api/chat")
async def chat(body: dict):
    """Chat with the AI about markets."""
    question = body.get("question", "")
    if not question:
        return {"error": "No question provided"}

    analyzer = ClaudeAnalyzer()
    market_ctx = ""
    if body.get("include_context", True):
        market_ctx = build_market_context(["SPY", "QQQ", "^VIX"])

    answer = analyzer.chat(question, context=market_ctx)
    return {"answer": answer}


@app.get("/api/history/events")
async def historical_events(query: Optional[str] = Query(None)):
    """Search historical market events."""
    if query:
        events = find_analogous_events(query)
    else:
        from ..data.historical_events import HISTORICAL_EVENTS
        events = HISTORICAL_EVENTS
    return {"events": events}
