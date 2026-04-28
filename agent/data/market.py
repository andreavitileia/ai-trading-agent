"""Market data fetcher using Yahoo Finance (free)."""

import datetime as dt
from typing import Optional

import numpy as np
import pandas as pd
import ta
import yfinance as yf


def fetch_historical(
    ticker: str,
    period: str = "max",
    interval: str = "1d",
) -> pd.DataFrame:
    """Download full historical OHLCV data for a ticker."""
    t = yf.Ticker(ticker)
    df = t.history(period=period, interval=interval, auto_adjust=True)
    if df.empty:
        return df
    df.index = df.index.tz_localize(None)
    return df


def fetch_recent(
    ticker: str,
    days: int = 60,
    interval: str = "1d",
) -> pd.DataFrame:
    """Download recent OHLCV data."""
    end = dt.datetime.now()
    start = end - dt.timedelta(days=days)
    t = yf.Ticker(ticker)
    df = t.history(start=start, end=end, interval=interval, auto_adjust=True)
    if df.empty:
        return df
    df.index = df.index.tz_localize(None)
    return df


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add key technical analysis indicators to a DataFrame."""
    if df.empty or len(df) < 30:
        return df

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # Moving averages
    df["SMA_20"] = ta.trend.sma_indicator(close, window=20)
    df["SMA_50"] = ta.trend.sma_indicator(close, window=50)
    df["SMA_200"] = ta.trend.sma_indicator(close, window=200)
    df["EMA_12"] = ta.trend.ema_indicator(close, window=12)
    df["EMA_26"] = ta.trend.ema_indicator(close, window=26)

    # MACD
    macd = ta.trend.MACD(close)
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()
    df["MACD_hist"] = macd.macd_diff()

    # RSI
    df["RSI_14"] = ta.momentum.rsi(close, window=14)

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    df["BB_upper"] = bb.bollinger_hband()
    df["BB_lower"] = bb.bollinger_lband()
    df["BB_mid"] = bb.bollinger_mavg()
    df["BB_width"] = (df["BB_upper"] - df["BB_lower"]) / df["BB_mid"]

    # ATR (Average True Range)
    df["ATR_14"] = ta.volatility.average_true_range(high, low, close, window=14)

    # Volume indicators
    df["Volume_SMA_20"] = ta.trend.sma_indicator(volume.astype(float), window=20)
    df["Volume_ratio"] = volume / df["Volume_SMA_20"]

    # Stochastic
    stoch = ta.momentum.StochasticOscillator(high, low, close)
    df["Stoch_K"] = stoch.stoch()
    df["Stoch_D"] = stoch.stoch_signal()

    # ADX
    adx = ta.trend.ADXIndicator(high, low, close)
    df["ADX"] = adx.adx()

    # Percentage changes
    df["Daily_Return"] = close.pct_change()
    df["Return_5d"] = close.pct_change(5)
    df["Return_20d"] = close.pct_change(20)
    df["Volatility_20d"] = df["Daily_Return"].rolling(20).std() * np.sqrt(252)

    return df


def get_market_summary(tickers: list[str]) -> dict:
    """Get a quick summary of current market conditions."""
    summary = {}
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            info = t.fast_info
            hist = t.history(period="5d")
            if hist.empty:
                continue

            last_close = hist["Close"].iloc[-1]
            prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else last_close
            change_pct = ((last_close - prev_close) / prev_close) * 100

            summary[ticker] = {
                "price": round(last_close, 2),
                "change_pct": round(change_pct, 2),
                "volume": int(hist["Volume"].iloc[-1]),
                "high_5d": round(hist["High"].max(), 2),
                "low_5d": round(hist["Low"].min(), 2),
            }
        except Exception:
            continue
    return summary


def detect_patterns(df: pd.DataFrame) -> list[dict]:
    """Detect basic chart patterns and conditions."""
    if df.empty or len(df) < 50:
        return []

    patterns = []
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # Golden Cross / Death Cross
    if len(df) >= 200:
        if (
            prev.get("SMA_50", 0) <= prev.get("SMA_200", 0)
            and latest.get("SMA_50", 0) > latest.get("SMA_200", 0)
        ):
            patterns.append({"pattern": "Golden Cross", "signal": "BULLISH", "strength": 0.8})
        elif (
            prev.get("SMA_50", 0) >= prev.get("SMA_200", 0)
            and latest.get("SMA_50", 0) < latest.get("SMA_200", 0)
        ):
            patterns.append({"pattern": "Death Cross", "signal": "BEARISH", "strength": 0.8})

    # RSI extremes
    rsi = latest.get("RSI_14", 50)
    if rsi < 30:
        patterns.append({"pattern": "RSI Oversold", "signal": "BULLISH", "strength": 0.7})
    elif rsi > 70:
        patterns.append({"pattern": "RSI Overbought", "signal": "BEARISH", "strength": 0.7})

    # MACD crossover
    if (
        prev.get("MACD", 0) <= prev.get("MACD_signal", 0)
        and latest.get("MACD", 0) > latest.get("MACD_signal", 0)
    ):
        patterns.append({"pattern": "MACD Bullish Cross", "signal": "BULLISH", "strength": 0.65})
    elif (
        prev.get("MACD", 0) >= prev.get("MACD_signal", 0)
        and latest.get("MACD", 0) < latest.get("MACD_signal", 0)
    ):
        patterns.append({"pattern": "MACD Bearish Cross", "signal": "BEARISH", "strength": 0.65})

    # Bollinger Band squeeze / breakout
    bb_width = latest.get("BB_width", 0)
    if bb_width and bb_width < 0.05:
        patterns.append({"pattern": "BB Squeeze", "signal": "NEUTRAL", "strength": 0.6})
    close = latest["Close"]
    bb_upper = latest.get("BB_upper", 0)
    bb_lower = latest.get("BB_lower", 0)
    if bb_upper and close > bb_upper:
        patterns.append({"pattern": "BB Breakout Up", "signal": "BULLISH", "strength": 0.6})
    elif bb_lower and close < bb_lower:
        patterns.append({"pattern": "BB Breakout Down", "signal": "BEARISH", "strength": 0.6})

    # Volume spike
    vol_ratio = latest.get("Volume_ratio", 1)
    if vol_ratio and vol_ratio > 2.0:
        patterns.append({"pattern": "Volume Spike", "signal": "ATTENTION", "strength": 0.5})

    # Strong trend (ADX)
    adx = latest.get("ADX", 0)
    if adx and adx > 25:
        direction = "BULLISH" if latest["Close"] > latest.get("SMA_20", latest["Close"]) else "BEARISH"
        patterns.append({"pattern": f"Strong Trend (ADX={adx:.0f})", "signal": direction, "strength": 0.65})

    return patterns


def build_market_context(tickers: list[str]) -> str:
    """Build a comprehensive market context string for LLM analysis."""
    lines = ["# Current Market Context\n"]

    for ticker in tickers[:10]:  # Limit to avoid too much data
        try:
            df = fetch_recent(ticker, days=60)
            if df.empty:
                continue
            df = add_technical_indicators(df)
            patterns = detect_patterns(df)
            latest = df.iloc[-1]

            lines.append(f"\n## {ticker}")
            lines.append(f"Price: ${latest['Close']:.2f}")
            lines.append(f"Daily Return: {latest.get('Daily_Return', 0)*100:.2f}%")
            lines.append(f"RSI(14): {latest.get('RSI_14', 'N/A')}")
            lines.append(f"MACD: {latest.get('MACD', 'N/A')}")
            lines.append(f"20d Volatility: {latest.get('Volatility_20d', 'N/A')}")
            lines.append(f"Volume Ratio: {latest.get('Volume_ratio', 'N/A')}")

            if patterns:
                lines.append("Patterns detected:")
                for p in patterns:
                    lines.append(f"  - {p['pattern']} ({p['signal']}, strength={p['strength']})")
        except Exception as e:
            lines.append(f"\n## {ticker}: Error fetching data: {e}")

    return "\n".join(lines)
