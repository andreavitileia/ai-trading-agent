"""Historical market events database.

A curated list of major events that moved markets over the last 100 years,
used by the swarm agents to find analogies with current situations.
"""

HISTORICAL_EVENTS = [
    # 1929-1940s
    {"year": 1929, "event": "Wall Street Crash", "impact": "S&P -86% over 3 years", "category": "financial_crisis",
     "lesson": "Excessive speculation and leverage lead to catastrophic crashes. Markets can take 25 years to recover."},
    {"year": 1933, "event": "FDR New Deal & Gold Confiscation", "impact": "Market rallied 50%+ off lows", "category": "policy",
     "lesson": "Massive government intervention can reverse market declines. Currency devaluation benefits equities."},
    {"year": 1939, "event": "World War II begins", "impact": "Initial selloff, then war economy boom", "category": "war",
     "lesson": "Wars initially cause panic selling but defense/industrial stocks surge. War economies drive inflation."},

    # 1950s-1960s
    {"year": 1953, "event": "Korean War end", "impact": "Bull market through 1960s", "category": "war",
     "lesson": "Post-war periods often bring extended bull markets as economies rebuild."},
    {"year": 1962, "event": "Cuban Missile Crisis", "impact": "S&P dropped 22%, recovered within months", "category": "geopolitical",
     "lesson": "Geopolitical crises cause sharp but temporary drops. Buy the fear if nuclear war is avoided."},

    # 1970s
    {"year": 1971, "event": "Nixon ends gold standard", "impact": "Dollar devaluation, inflation spike", "category": "policy",
     "lesson": "Monetary regime changes cause massive asset repricing. Gold and commodities surge."},
    {"year": 1973, "event": "OPEC Oil Embargo", "impact": "S&P -48%, oil prices 4x", "category": "energy",
     "lesson": "Energy supply shocks cause stagflation. Energy stocks outperform, tech underperforms."},
    {"year": 1979, "event": "Iranian Revolution & Second Oil Crisis", "impact": "Oil doubled, inflation hit 14%", "category": "geopolitical",
     "lesson": "Middle East instability directly impacts energy prices and global inflation."},
    {"year": 1979, "event": "Volcker Rate Hikes", "impact": "Rates to 20%, deep recession, then 18-year bull", "category": "policy",
     "lesson": "Aggressive rate hikes crush inflation but cause severe short-term pain. The cure enables long bull markets."},

    # 1980s
    {"year": 1987, "event": "Black Monday Crash", "impact": "Dow -22.6% in single day", "category": "financial_crisis",
     "lesson": "Program trading and portfolio insurance can cause flash crashes. Markets recovered within 2 years."},
    {"year": 1989, "event": "Fall of Berlin Wall", "impact": "European markets surged", "category": "geopolitical",
     "lesson": "End of geopolitical tensions opens new markets and drives optimism."},

    # 1990s
    {"year": 1990, "event": "Gulf War / Iraq invades Kuwait", "impact": "Oil spiked 70%, S&P -20%", "category": "war",
     "lesson": "Oil-related conflicts cause immediate energy price spikes and market drops."},
    {"year": 1994, "event": "Fed Rate Hike Surprise (Tequila Crisis)", "impact": "Bond market crash, EM selloff", "category": "policy",
     "lesson": "Unexpected rate hikes devastate bonds and emerging markets."},
    {"year": 1997, "event": "Asian Financial Crisis", "impact": "Asian markets -50-80%", "category": "financial_crisis",
     "lesson": "Currency crises in one region can cascade globally. Flight to US dollar/bonds."},
    {"year": 1998, "event": "LTCM Collapse / Russian Default", "impact": "S&P -19%, VIX spiked", "category": "financial_crisis",
     "lesson": "Hedge fund leverage can create systemic risk. Fed bailouts prevent total collapse."},
    {"year": 1999, "event": "Dot-com Bubble Peak", "impact": "NASDAQ +85% in 1999 alone", "category": "bubble",
     "lesson": "Speculative manias can persist longer than expected. New paradigm narratives are dangerous."},

    # 2000s
    {"year": 2000, "event": "Dot-com Crash", "impact": "NASDAQ -78% over 2 years", "category": "financial_crisis",
     "lesson": "Technology bubbles burst violently. Valuations matter eventually. Cash-burning companies go bankrupt."},
    {"year": 2001, "event": "9/11 Attacks", "impact": "Markets closed 4 days, S&P -12% on reopen", "category": "geopolitical",
     "lesson": "Terror attacks cause sharp drops but markets recover. Defense stocks surge, airlines crash."},
    {"year": 2003, "event": "Iraq War Begins", "impact": "Market bottomed, then rallied", "category": "war",
     "lesson": "Markets often rally once war uncertainty resolves. 'Buy the invasion.'"},
    {"year": 2007, "event": "Subprime Crisis Begins", "impact": "Housing collapse, banks fail", "category": "financial_crisis",
     "lesson": "Real estate bubbles and financial engineering create systemic risk. Watch credit spreads."},
    {"year": 2008, "event": "Lehman Brothers Collapse", "impact": "S&P -57% from peak, global financial crisis", "category": "financial_crisis",
     "lesson": "Bank failures cause credit freezes and market panics. Government intervention eventually stabilizes."},
    {"year": 2009, "event": "Fed QE1 / TARP", "impact": "S&P bottomed March 2009, began 11-year bull", "category": "policy",
     "lesson": "Massive central bank intervention (QE) inflates asset prices. Don't fight the Fed."},

    # 2010s
    {"year": 2010, "event": "Flash Crash", "impact": "Dow -9% in minutes, recovered same day", "category": "financial_crisis",
     "lesson": "Algorithmic trading can cause extreme intraday volatility. Limit orders protect against flash crashes."},
    {"year": 2011, "event": "European Debt Crisis", "impact": "Greek bonds crashed, S&P -19%", "category": "financial_crisis",
     "lesson": "Sovereign debt crises in one country can threaten entire currency unions."},
    {"year": 2014, "event": "Russia Annexes Crimea", "impact": "Russian stocks -50%, oil dropped", "category": "geopolitical",
     "lesson": "Sanctions and geopolitical aggression destroy local markets but global impact can be contained."},
    {"year": 2015, "event": "China Stock Market Crash", "impact": "Shanghai -45%, global contagion", "category": "financial_crisis",
     "lesson": "Chinese market instability creates global volatility. Yuan devaluation fears hurt EM."},
    {"year": 2016, "event": "Brexit Referendum", "impact": "GBP -11%, FTSE -8% then recovered", "category": "geopolitical",
     "lesson": "Political shocks cause currency crashes. Equity markets recover faster than expected."},
    {"year": 2018, "event": "US-China Trade War Escalation", "impact": "S&P -20% in Q4", "category": "geopolitical",
     "lesson": "Trade wars hurt exporters and tech. Tariff escalation creates persistent uncertainty."},

    # 2020s
    {"year": 2020, "event": "COVID-19 Pandemic", "impact": "S&P -34% in 23 days, then V-recovery", "category": "pandemic",
     "lesson": "Pandemics cause fastest crashes in history. Massive fiscal/monetary response drives equally fast recovery."},
    {"year": 2021, "event": "GameStop / Meme Stock Mania", "impact": "GME +1600%, short squeezes", "category": "bubble",
     "lesson": "Retail trading and social media can create extreme short squeezes. Most gains are temporary."},
    {"year": 2022, "event": "Russia Invades Ukraine", "impact": "Oil +60%, wheat +50%, EU gas 10x", "category": "war",
     "lesson": "European land wars cause energy and food price spikes. Defense stocks surge, European markets suffer."},
    {"year": 2022, "event": "Fed Aggressive Rate Hikes", "impact": "S&P -25%, NASDAQ -33%, bonds -13%", "category": "policy",
     "lesson": "Fastest rate hike cycle in decades crushes growth stocks and bonds simultaneously."},
    {"year": 2023, "event": "SVB / Banking Crisis", "impact": "Regional banks -40%, flight to big banks", "category": "financial_crisis",
     "lesson": "Rate hikes expose duration risk in bank portfolios. Depositors flee small banks for big banks and money markets."},
    {"year": 2023, "event": "AI / ChatGPT Boom", "impact": "NVDA +240%, Magnificent 7 dominance", "category": "technology",
     "lesson": "Transformative technology creates massive concentration in few stocks. AI infrastructure providers benefit most."},
    {"year": 2024, "event": "Middle East Tensions / Red Sea", "impact": "Oil +10%, shipping costs up", "category": "geopolitical",
     "lesson": "Regional conflicts affecting trade routes cause supply chain disruption and inflation fears."},
    {"year": 2025, "event": "Trump Tariffs / Trade War 2.0", "impact": "Global market volatility, S&P correction", "category": "geopolitical",
     "lesson": "Renewed tariff escalation creates uncertainty. Companies with domestic revenue outperform exporters."},
]


def find_analogous_events(current_situation: str, top_k: int = 5) -> list[dict]:
    """Find historical events that may be analogous to the current situation.

    Simple keyword-based matching. The swarm LLM agents will do deeper analysis.
    """
    keywords = current_situation.lower().split()
    scored = []
    for event in HISTORICAL_EVENTS:
        score = 0
        event_text = f"{event['event']} {event['category']} {event['lesson']}".lower()
        for kw in keywords:
            if len(kw) > 3 and kw in event_text:
                score += 1
        if score > 0:
            scored.append((score, event))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:top_k]]


def get_events_summary() -> str:
    """Build a text summary of all historical events for LLM context."""
    lines = ["# Historical Market Events (100 Years)\n"]
    current_decade = None
    for e in HISTORICAL_EVENTS:
        decade = (e["year"] // 10) * 10
        if decade != current_decade:
            current_decade = decade
            lines.append(f"\n## {decade}s")
        lines.append(
            f"- **{e['year']} - {e['event']}** ({e['category']}): "
            f"{e['impact']}. Lesson: {e['lesson']}"
        )
    return "\n".join(lines)
