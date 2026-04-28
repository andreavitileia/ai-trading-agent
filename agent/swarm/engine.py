"""MiroFish-inspired swarm intelligence engine for financial prediction.

Instead of fitting a single model, we simulate a diverse group of AI analysts
who debate, challenge each other, and reach a consensus (or reveal divergence).
The collective signal is stronger than any individual prediction.

Pipeline:
1. Feed market data + news to all agents
2. Each agent provides independent analysis
3. Agents debate and challenge each other
4. Synthesize into final consensus with confidence scores
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

import anthropic

from ..config import settings
from .agents import ANALYST_PERSONAS, AgentPersona

logger = logging.getLogger(__name__)


class SwarmEngine:
    """Runs a multi-agent swarm simulation for market prediction."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(
            api_key=api_key or settings.anthropic_api_key,
        )
        self.model = settings.claude_model
        self.personas = ANALYST_PERSONAS[: settings.swarm_agent_count]

    def _call_claude(
        self,
        system: str,
        user_msg: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> str:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        return resp.content[0].text

    # ------------------------------------------------------------------
    # Phase 1: Independent Analysis
    # ------------------------------------------------------------------
    def gather_independent_views(
        self, market_context: str, news_context: str, historical_context: str
    ) -> list[dict]:
        """Each agent independently analyzes the situation."""
        prompt = (
            "Analyze the current market situation and provide your trading recommendation.\n\n"
            f"{market_context}\n\n"
            f"{news_context}\n\n"
            f"{historical_context}\n\n"
            "Respond in JSON format:\n"
            "{\n"
            '  "market_regime": "bull|bear|neutral|transition",\n'
            '  "top_opportunities": [\n'
            '    {"ticker": "...", "direction": "LONG|SHORT", "conviction": 0.0-1.0,\n'
            '     "entry_price": ..., "stop_loss": ..., "take_profit": ...,\n'
            '     "timeframe": "intraday|days|weeks",\n'
            '     "reasoning": "..."}\n'
            "  ],\n"
            '  "key_risks": ["..."],\n'
            '  "historical_analogy": "Which past event is most similar to now and why",\n'
            '  "overall_stance": "strongly_bullish|bullish|neutral|bearish|strongly_bearish",\n'
            '  "confidence": 0.0-1.0\n'
            "}"
        )

        views = []
        for persona in self.personas:
            try:
                raw = self._call_claude(
                    system=persona.to_system_prompt(),
                    user_msg=prompt,
                    temperature=0.8,
                )
                # Parse JSON from response
                parsed = self._extract_json(raw)
                parsed["agent_name"] = persona.name
                parsed["agent_role"] = persona.role
                views.append(parsed)
                logger.info(f"Agent {persona.name}: {parsed.get('overall_stance', '?')}")
            except Exception as e:
                logger.warning(f"Agent {persona.name} failed: {e}")
                views.append({
                    "agent_name": persona.name,
                    "agent_role": persona.role,
                    "error": str(e),
                    "overall_stance": "neutral",
                    "confidence": 0.0,
                })
        return views

    # ------------------------------------------------------------------
    # Phase 2: Debate & Challenge
    # ------------------------------------------------------------------
    def run_debate(
        self, views: list[dict], market_context: str, news_context: str
    ) -> list[dict]:
        """Agents debate each other's views, challenging assumptions."""
        if not settings.swarm_debate_enabled:
            return views

        # Summarize all views for the debate
        views_summary = self._summarize_views(views)

        debate_prompt = (
            "You have seen the following independent analyses from your fellow analysts:\n\n"
            f"{views_summary}\n\n"
            "Current market data:\n"
            f"{market_context[:3000]}\n\n"
            "Latest news:\n"
            f"{news_context[:3000]}\n\n"
            "Now, do the following:\n"
            "1. Challenge the weakest arguments from other analysts\n"
            "2. Identify blind spots in the group analysis\n"
            "3. Update your own view based on others' insights\n"
            "4. Provide your REVISED recommendation\n\n"
            "Respond in JSON:\n"
            "{\n"
            '  "challenges": ["specific critique of another analyst\'s view"],\n'
            '  "blind_spots": ["risks or opportunities the group missed"],\n'
            '  "revised_opportunities": [\n'
            '    {"ticker": "...", "direction": "LONG|SHORT", "conviction": 0.0-1.0,\n'
            '     "entry_price": ..., "stop_loss": ..., "take_profit": ...,\n'
            '     "timeframe": "intraday|days|weeks",\n'
            '     "reasoning": "..."}\n'
            "  ],\n"
            '  "revised_stance": "strongly_bullish|bullish|neutral|bearish|strongly_bearish",\n'
            '  "revised_confidence": 0.0-1.0\n'
            "}"
        )

        revised_views = []
        for persona in self.personas:
            try:
                raw = self._call_claude(
                    system=persona.to_system_prompt(),
                    user_msg=debate_prompt,
                    temperature=0.6,
                )
                parsed = self._extract_json(raw)
                parsed["agent_name"] = persona.name
                parsed["agent_role"] = persona.role
                revised_views.append(parsed)
            except Exception as e:
                logger.warning(f"Debate failed for {persona.name}: {e}")
                # Keep original view
                original = next((v for v in views if v.get("agent_name") == persona.name), {})
                revised_views.append(original)

        return revised_views

    # ------------------------------------------------------------------
    # Phase 3: Synthesis
    # ------------------------------------------------------------------
    def synthesize_consensus(
        self,
        initial_views: list[dict],
        debate_views: list[dict],
        market_context: str,
        news_context: str,
    ) -> dict:
        """Synthesize all agent views into a final consensus report with trading signals."""
        initial_summary = self._summarize_views(initial_views)
        debate_summary = self._summarize_views(debate_views)

        synthesis_prompt = (
            "You are the Chief Investment Officer synthesizing inputs from 12 expert analysts.\n\n"
            "## Initial Independent Analyses:\n"
            f"{initial_summary}\n\n"
            "## Post-Debate Revised Analyses:\n"
            f"{debate_summary}\n\n"
            "## Current Market Data:\n"
            f"{market_context[:4000]}\n\n"
            "## Latest News:\n"
            f"{news_context[:3000]}\n\n"
            "Synthesize everything into a FINAL actionable trading plan.\n"
            "Consider:\n"
            "- Where do analysts agree? (high conviction signals)\n"
            "- Where do they disagree? (controversial = more risk)\n"
            "- What is the consensus market regime?\n"
            "- Risk/reward of each trade\n"
            "- Position sizing for a €3,000 account with aggressive leverage\n\n"
            "Respond in JSON:\n"
            "{\n"
            '  "timestamp": "ISO timestamp",\n'
            '  "market_regime": "bull|bear|neutral|transition",\n'
            '  "regime_confidence": 0.0-1.0,\n'
            '  "consensus_stance": "strongly_bullish|bullish|neutral|bearish|strongly_bearish",\n'
            '  "signals": [\n'
            "    {\n"
            '      "rank": 1,\n'
            '      "ticker": "...",\n'
            '      "direction": "LONG|SHORT",\n'
            '      "conviction": 0.0-1.0,\n'
            '      "entry_price": ...,\n'
            '      "stop_loss": ...,\n'
            '      "take_profit": ...,\n'
            '      "risk_reward_ratio": ...,\n'
            '      "position_size_eur": ...,\n'
            '      "leverage_suggested": "1x|2x|3x|5x|10x",\n'
            '      "timeframe": "intraday|1-3 days|1-2 weeks",\n'
            '      "reasoning": "...",\n'
            '      "supporting_agents": ["names of agents who agree"],\n'
            '      "dissenting_agents": ["names of agents who disagree"],\n'
            '      "key_risk": "main risk for this trade"\n'
            "    }\n"
            "  ],\n"
            '  "portfolio_allocation": {\n'
            '    "cash_pct": ...,\n'
            '    "long_pct": ...,\n'
            '    "short_pct": ...,\n'
            '    "hedge_pct": ...\n'
            "  },\n"
            '  "top_risks": ["ordered list of biggest risks to watch"],\n'
            '  "events_to_watch": ["upcoming events that could change the analysis"],\n'
            '  "historical_parallel": "The historical event most analogous to current conditions",\n'
            '  "next_review": "When this analysis should be updated",\n'
            '  "executive_summary": "2-3 paragraph summary for the trader"\n'
            "}"
        )

        raw = self._call_claude(
            system=(
                "You are the Chief Investment Officer of an elite hedge fund. "
                "You must synthesize diverse analyst views into clear, actionable trading signals. "
                "Be decisive. Every signal must have exact entry, stop-loss, and take-profit levels. "
                "Capital: €3,000 with access to leveraged instruments. "
                "Target: maximize risk-adjusted returns aggressively."
            ),
            user_msg=synthesis_prompt,
            max_tokens=4000,
            temperature=0.3,
        )

        result = self._extract_json(raw)
        result["generated_at"] = datetime.now(tz=timezone.utc).isoformat()
        result["agent_count"] = len(self.personas)
        result["debate_rounds"] = 1 if settings.swarm_debate_enabled else 0
        return result

    # ------------------------------------------------------------------
    # Full Pipeline
    # ------------------------------------------------------------------
    def run_full_analysis(
        self,
        market_context: str,
        news_context: str,
        historical_context: str,
    ) -> dict:
        """Run the complete swarm analysis pipeline."""
        logger.info("Phase 1: Gathering independent views...")
        initial_views = self.gather_independent_views(
            market_context, news_context, historical_context
        )

        logger.info("Phase 2: Running debate...")
        debate_views = self.run_debate(initial_views, market_context, news_context)

        logger.info("Phase 3: Synthesizing consensus...")
        consensus = self.synthesize_consensus(
            initial_views, debate_views, market_context, news_context
        )

        return {
            "initial_views": initial_views,
            "debate_views": debate_views,
            "consensus": consensus,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from LLM response, handling markdown code blocks."""
        import re
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()

        # Try to find JSON object in the text
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                pass

        # Fallback: try the whole string
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"raw_response": text, "parse_error": True}

    def _summarize_views(self, views: list[dict]) -> str:
        """Create a readable summary of agent views."""
        lines = []
        for v in views:
            name = v.get("agent_name", "Unknown")
            role = v.get("agent_role", "")
            stance = v.get("overall_stance") or v.get("revised_stance", "?")
            confidence = v.get("confidence") or v.get("revised_confidence", "?")
            lines.append(f"\n### {name} ({role})")
            lines.append(f"Stance: {stance} (confidence: {confidence})")

            opps = v.get("top_opportunities") or v.get("revised_opportunities", [])
            if isinstance(opps, list):
                for opp in opps[:3]:
                    if isinstance(opp, dict):
                        lines.append(
                            f"  - {opp.get('ticker', '?')} {opp.get('direction', '?')} "
                            f"(conviction: {opp.get('conviction', '?')}): {opp.get('reasoning', '')[:200]}"
                        )

            risks = v.get("key_risks", [])
            if isinstance(risks, list) and risks:
                lines.append(f"  Risks: {', '.join(str(r) for r in risks[:3])}")

            analogy = v.get("historical_analogy", "")
            if analogy:
                lines.append(f"  Historical parallel: {str(analogy)[:200]}")

        return "\n".join(lines)
