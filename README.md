# Finance Agent

A GenAI-powered equity research platform. Ask questions and get answers grounded in 10-K filings and quarterly financials for S&P 500 tech companies.

**Stack:** FastAPI · PostgreSQL (pgvector) · Cerebras Qwen-3-235B · React · Railway

---

## What It Does

- **RAG over 10-K filings** — 42,023 chunks from 27 tickers (AAPL, NVDA, MSFT, META, etc.)
- **Quarterly financial summaries** — 140 chunks across 28 tickers via yfinance
- **Hybrid search** — BM25 + pgvector cosine similarity + cross-encoder rerank
- **Streaming responses** — SSE via FastAPI, real-time to the browser
- **Multi-company comparisons** — single question, parallel per-ticker retrieval
- **Auth** — Clerk JWT in production, dev fallback via `X-User-ID` header

---

## Agent Architecture

```
Question
  ↓
Question Analyzer          (extracts ticker, intent, time period)
  ↓
Search Planner             (generates keyword + vector queries per ticker)
  ↓
Hybrid Retrieval
  ├── ten_k_chunks         (42,023 rows — pgvector + BM25)
  └── transcript_chunks    (140 rows   — pgvector + BM25)
  ↓
Cross-Encoder Rerank       (sentence-transformers)
  ↓
LLM Generation             (Cerebras Qwen-3-235B → OpenAI gpt-4o-mini fallback)
  ↓
Streaming SSE Response
```

---

## Project Structure

```
finance-agent/
├── app/                        # FastAPI application
│   ├── main.py                 # Server entry point
│   ├── routers/                # chat, companies, sec_filings, transcripts
│   ├── auth/                   # Clerk JWT + dev fallback
│   ├── schemas/                # Pydantic request/response models
│   └── utils/                  # Logging, DB init, error handlers
├── agent/                      # RAG pipeline
│   ├── rag/
│   │   ├── rag_agent.py        # Main orchestration
│   │   ├── question_analyzer.py
│   │   ├── search_planner.py
│   │   ├── search_engine.py    # Hybrid BM25 + pgvector
│   │   ├── response_generator.py
│   │   ├── tavily_service.py   # Real-time news (optional)
│   │   └── data_ingestion/     # Ingestion scripts (10-K + transcripts)
│   └── screener/               # Financial screener (DuckDB, in development)
├── frontend/                   # React + Vite + TypeScript
├── tests/                      # Test suite (split by component)
│   ├── run_all.py              # Orchestrator
│   ├── test_health.py
│   ├── test_companies.py
│   ├── test_conversations.py
│   ├── test_sec_filings.py
│   ├── test_transcripts.py
│   ├── test_db_coverage.py
│   ├── test_chat_rag.py        # Slow — hits LLM
│   └── utils.py                # Shared helpers
├── data/
│   ├── raw/
│   │   ├── sec_edgar/          # EDGAR .tar archives (gitignored, re-downloadable)
│   │   └── earnings_transcripts/
│   └── processed/              # Local embedding cache (gitignored)
├── docs/                       # Project documentation
├── scripts/                    # Utility scripts
├── logs/                       # Application + ingestion logs (gitignored)
├── db/                         # SQL schema
├── config.py                   # Settings (reads from .env)
├── requirements.txt
└── test_apis.py                # Backward-compat shim → tests/run_all.py
```

---

## Quick Start

### Prerequisites
- Python 3.11
- PostgreSQL 14+ with pgvector extension (or use the Railway DB below)
- Node 18+ (frontend only)

### Backend

```bash
# 1. Clone and set up
git clone <your-repo-url>
cd finance-agent
python -m venv .venv
.venv/Scripts/activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Fill in your keys (see Environment Variables below)

# 4. Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host
# Runs on http://localhost:5173
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string (Railway) |
| `PG_VECTOR` | Yes | Same as DATABASE_URL (pgvector reads this) |
| `OPENAI_API_KEY` | Yes | OpenAI fallback for LLM generation |
| `CEREBRAS_API_KEY` | Yes | Primary LLM (Qwen-3-235B, fast + cheap) |
| `CLERK_SECRET_KEY` | Prod | Clerk auth backend key |
| `CLERK_PUBLISHABLE_KEY` | Prod | Clerk auth frontend key |
| `REDIS_URL` | Optional | Redis for WebSocket session caching |
| `TAVILY_API_KEY` | Optional | Real-time news search |
| `LOGFIRE_TOKEN` | Optional | Pydantic Logfire observability |
| `AUTH_DISABLED` | Dev | Set `true` to skip auth locally |

---

## Testing

```bash
# Fast tests only (no LLM calls, ~5s)
python tests/run_all.py --fast

# Full suite including LLM streaming (2-3 min)
python tests/run_all.py

# Run a single suite
python tests/test_health.py
python tests/test_sec_filings.py
python tests/test_chat_rag.py

# Backward-compat (same as tests/run_all.py)
python test_apis.py --fast
```

**Current results:** 19 fast tests passing · 13 LLM tests passing · 0 failing

---

## Data Coverage

| Source | Table | Rows | Tickers |
|--------|-------|------|---------|
| SEC 10-K filings | `ten_k_chunks` | 42,023 | 27/28 |
| Quarterly financials (yfinance) | `transcript_chunks` | 140 | 28/28 |

**Tickers with 10-K data:** AAPL · AMAT · AMD · AMZN · AVGO · CRM · CSCO · GOOGL · IBM · INTC · KLAC · LRCX · META · MSFT · MU · NFLX · NOW · NVDA · ORCL · PANW · PLTR · PYPL · QCOM · SNOW · TSLA · TXN · UBER

**Missing:** ADBE (PDF parsing failure during ingestion)

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Server health + DB/RAG status |
| `GET` | `/api` | API info |
| `POST` | `/chat/message/stream-v2` | Authenticated chat (SSE streaming) |
| `POST` | `/chat/landing/demo/stream-v2` | Public demo chat (SSE streaming) |
| `GET` | `/companies/companies/public/search` | Company search |
| `GET` | `/sec-filings/sec-filings/{ticker}/available` | Available 10-K filings |
| `GET` | `/transcripts/transcript/{ticker}/{year}/{quarter}` | Quarterly data |
| `POST` | `/chat/conversations` | Conversation management |

Swagger UI: `http://localhost:8000/docs`

### Example: RAG query

```bash
curl -X POST http://localhost:8000/chat/message/stream-v2 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 00000000-0000-0000-0000-000000000001" \
  -d '{"message": "What was NVIDIA total revenue in FY2025?", "use_rag": true}'
```

---

## Data Ingestion

### Re-ingest 10-K filings
```bash
# Single ticker
.venv/Scripts/python agent/rag/data_ingestion/ingest_10k_filings_full.py \
  --tickers ADBE --lookback-years 3

# Multiple tickers
.venv/Scripts/python agent/rag/data_ingestion/ingest_10k_filings_full.py \
  --tickers CSCO MU QCOM TXN KLAC SNOW
```

### Re-ingest quarterly financials
```bash
.venv/Scripts/python agent/rag/data_ingestion/ingest_yfinance_to_transcripts.py \
  --tickers AAPL MSFT NVDA --lookback-quarters 8
```

---

## Deployment (Railway)

1. Push code to GitHub
2. Connect repo in Railway → set environment variables
3. Railway auto-deploys on push (uses `Procfile`)
4. The PostgreSQL database is already on Railway — no migration needed

```
# Procfile
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## License

MIT
