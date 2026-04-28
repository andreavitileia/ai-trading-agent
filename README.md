# AI Trading Agent

**Agente AI per trading basato su Swarm Intelligence (ispirato a MiroFish) + Claude AI**

Sistema di analisi e generazione segnali di trading che simula 12 analisti finanziari AI con personalita', background e bias diversi. Gli agenti dibattono tra loro e raggiungono un consenso, generando segnali operativi con entry, stop-loss e take-profit.

## Architettura

```
News RSS (Reuters, CNBC, ANSA, ...) ─┐
                                      ├─> Swarm Engine (12 AI Analysts) ─> Consensus ─> Trading Signals
Yahoo Finance (100 anni di dati)  ────┤         │ Debate │ Challenge │ Revise
                                      │
Historical Events DB (1929-2025) ─────┘
                                            │
                                      Claude AI (Anthropic)
                                            │
                                    Dashboard Web ← FastAPI Backend
```

### Pipeline di Analisi

1. **Fase 1 - Analisi Indipendente**: Ogni agente analizza mercato + news + storia separatamente
2. **Fase 2 - Dibattito**: Gli agenti si sfidano, criticano le analisi deboli, identificano punti ciechi
3. **Fase 3 - Sintesi**: Un CIO virtuale sintetizza tutto in segnali operativi con probabilita'

### I 12 Agenti

| Agente | Ruolo | Specializzazione |
|--------|-------|-----------------|
| Marcus Chen | Macro Strategist | Tassi, yield curve, liquidita' globale |
| Sarah Volkov | Geopolitical Risk | Guerre, sanzioni, supply chain |
| Raj Patel | Quant Analyst | Indicatori tecnici, pattern statistici |
| Elena Rossi | Value Investor | Fondamentali, cash flow, contrarian |
| Jake Morrison | Options Trader | Volatilita', Greeks, tail risk |
| Li Wei | Tech Specialist | AI, semiconduttori, big tech |
| Omar Hassan | Commodities Trader | Oil, gas, metalli, OPEC |
| Anna Bergstrom | Fixed Income | Yield curve, politica monetaria |
| Diego Morales | EM Specialist | Mercati emergenti, valute |
| Yuki Tanaka | Sentiment Analyst | Psicologia di mercato, contrarian |
| Victoria Sterling | Event-Driven | M&A, earnings, catalysts |
| Nikolai Petrov | Risk Manager | Tail risk, hedging, worst-case |

## Quick Start

### Prerequisiti
- Python >= 3.11
- API Key Anthropic (Claude)

### Installazione

```bash
# Clona il repo
git clone https://github.com/Vitileiaandrea/ai-trading-agent.git
cd ai-trading-agent

# Crea virtual environment
python -m venv .venv
source .venv/bin/activate

# Installa dipendenze
pip install -e .

# Configura API key
cp .env.example .env
# Modifica .env con la tua ANTHROPIC_API_KEY
```

### Avvio

```bash
# Avvia il server (dashboard + API)
python -m agent.main
```

Apri il browser su `http://localhost:8000`

### API Endpoints

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/` | GET | Dashboard web |
| `/api/status` | GET | Stato del sistema |
| `/api/market/summary` | GET | Panoramica mercato |
| `/api/market/analysis/{ticker}` | GET | Analisi tecnica ticker |
| `/api/news` | GET | Feed notizie |
| `/api/signals` | GET | Segnali di trading attivi |
| `/api/analysis/run` | POST | Avvia analisi swarm completa |
| `/api/analysis/latest` | GET | Ultima analisi completa |
| `/api/analysis/quick` | GET | Outlook rapido (senza swarm) |
| `/api/chat` | POST | Chat con l'AI |
| `/api/history/events` | GET | Eventi storici |

## Fonti Dati (Gratuite)

- **Yahoo Finance**: Dati storici e in tempo reale (OHLCV)
- **Reuters RSS**: Notizie business/finanza
- **CNBC RSS**: Top news e mercati mondiali
- **Google News RSS**: Notizie mercati e geopolitica
- **MarketWatch RSS**: Top stories finanziarie
- **ANSA RSS**: Economia italiana
- **Database interno**: 40+ eventi storici dal 1929 al 2025

## Disclaimer

Questo sistema e' solo a scopo informativo e didattico.
Non costituisce consulenza finanziaria personalizzata ai sensi della normativa Consob/MiFID II.
Le performance passate non garantiscono risultati futuri.
Investire comporta rischi di perdita del capitale.
