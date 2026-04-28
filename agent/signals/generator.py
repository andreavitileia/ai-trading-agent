"""Trading signal generator - processes swarm output into actionable signals."""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

from ..config import settings

logger = logging.getLogger(__name__)


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class Timeframe(str, Enum):
    INTRADAY = "intraday"
    DAYS = "1-3 days"
    WEEKS = "1-2 weeks"


@dataclass
class TradingSignal:
    ticker: str
    direction: str
    conviction: float
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    position_size_eur: float
    leverage: str
    timeframe: str
    reasoning: str
    supporting_agents: list[str] = field(default_factory=list)
    dissenting_agents: list[str] = field(default_factory=list)
    key_risk: str = ""
    generated_at: str = ""
    status: str = "active"  # active, triggered, stopped_out, target_hit, expired

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def risk_amount(self) -> float:
        if self.direction == "LONG":
            return abs(self.entry_price - self.stop_loss) / self.entry_price * self.position_size_eur
        else:
            return abs(self.stop_loss - self.entry_price) / self.entry_price * self.position_size_eur

    @property
    def potential_profit(self) -> float:
        if self.direction == "LONG":
            return abs(self.take_profit - self.entry_price) / self.entry_price * self.position_size_eur
        else:
            return abs(self.entry_price - self.take_profit) / self.entry_price * self.position_size_eur


def extract_signals_from_consensus(consensus: dict) -> list[TradingSignal]:
    """Extract and validate trading signals from swarm consensus."""
    raw_signals = consensus.get("signals", [])
    if not isinstance(raw_signals, list):
        return []

    signals = []
    for raw in raw_signals[: settings.max_daily_signals]:
        try:
            # Validate required fields
            ticker = raw.get("ticker", "")
            if not ticker:
                continue

            entry = float(raw.get("entry_price", 0))
            stop = float(raw.get("stop_loss", 0))
            target = float(raw.get("take_profit", 0))

            if entry <= 0 or stop <= 0 or target <= 0:
                continue

            conviction = float(raw.get("conviction", 0))
            if conviction < settings.signal_confidence_threshold:
                logger.info(f"Skipping {ticker}: conviction {conviction} below threshold")
                continue

            # Calculate risk/reward
            direction = raw.get("direction", "LONG").upper()
            if direction == "LONG":
                risk = abs(entry - stop)
                reward = abs(target - entry)
            else:
                risk = abs(stop - entry)
                reward = abs(entry - target)

            rr_ratio = reward / risk if risk > 0 else 0

            # Position sizing based on risk management
            max_risk_eur = settings.default_capital * (settings.max_risk_per_trade_pct / 100)
            position_size = float(raw.get("position_size_eur", 0))
            if position_size <= 0 or position_size > settings.default_capital:
                # Auto-calculate based on risk
                risk_pct = risk / entry if entry > 0 else 0.05
                position_size = min(max_risk_eur / risk_pct, settings.default_capital) if risk_pct > 0 else max_risk_eur

            signal = TradingSignal(
                ticker=ticker,
                direction=direction,
                conviction=conviction,
                entry_price=entry,
                stop_loss=stop,
                take_profit=target,
                risk_reward_ratio=round(rr_ratio, 2),
                position_size_eur=round(position_size, 2),
                leverage=raw.get("leverage_suggested", raw.get("leverage", "1x")),
                timeframe=raw.get("timeframe", "1-3 days"),
                reasoning=raw.get("reasoning", ""),
                supporting_agents=raw.get("supporting_agents", []),
                dissenting_agents=raw.get("dissenting_agents", []),
                key_risk=raw.get("key_risk", ""),
                generated_at=datetime.now(tz=timezone.utc).isoformat(),
            )
            signals.append(signal)
        except Exception as e:
            logger.warning(f"Failed to parse signal: {e}")
            continue

    # Sort by conviction
    signals.sort(key=lambda s: s.conviction, reverse=True)
    return signals


def save_signals(signals: list[TradingSignal], output_dir: Optional[str] = None) -> str:
    """Save signals to a JSON file."""
    if output_dir is None:
        output_dir = str(Path(settings.db_path).parent)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = Path(output_dir) / f"signals_{timestamp}.json"

    data = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "signal_count": len(signals),
        "signals": [s.to_dict() for s in signals],
    }

    filepath.write_text(json.dumps(data, indent=2, default=str))
    logger.info(f"Saved {len(signals)} signals to {filepath}")
    return str(filepath)


def load_latest_signals(data_dir: Optional[str] = None) -> list[TradingSignal]:
    """Load the most recent signals file."""
    if data_dir is None:
        data_dir = str(Path(settings.db_path).parent)

    data_path = Path(data_dir)
    if not data_path.exists():
        return []

    signal_files = sorted(data_path.glob("signals_*.json"), reverse=True)
    if not signal_files:
        return []

    try:
        data = json.loads(signal_files[0].read_text())
        signals = []
        for s in data.get("signals", []):
            signals.append(TradingSignal(**{
                k: v for k, v in s.items()
                if k in TradingSignal.__dataclass_fields__
            }))
        return signals
    except Exception as e:
        logger.error(f"Failed to load signals: {e}")
        return []
