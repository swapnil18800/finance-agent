# Data Ingestion & Database Status

**Date:** 2026-04-28  
**Database:** Railway PostgreSQL (pgvector enabled)

---

## 📊 Database Tables Overview

| Table | Rows | Size | Purpose |
|---|---|---|---|
| `ten_k_chunks` | **28,029** | 126 MB | RAG text chunks from 10-K filings (primary RAG source) |
| `ten_k_tables` | **2,958** | 9.1 MB | Structured financial tables extracted from 10-Ks |
| `complete_sec_filings` | **47** | 11 MB | Full raw 10-K filing metadata + text |
| `transcript_chunks` | **75** | 360 KB | Quarterly financial summaries (via yfinance, substitute for earnings transcripts) |
| `complete_transcripts` | **0** | 16 KB | Earnings call transcripts — **EMPTY** |
| `chat_conversations` | 33 | 64 KB | User chat sessions |
| `chat_messages` | 53 | 184 KB | Chat message history |

---

## 📁 Ten-K Chunks (Primary RAG Data)

**28,029 chunks across 21 tickers** ✅

| Ticker | Chunks | Fiscal Years | Status |
|---|---|---|---|
| AAPL | 474 | 2025 | ✅ |
| AMAT | 484 | 2025 | ✅ |
| AMD | 1,260 | 2024–2025 | ✅ |
| AMZN | 626 | 2025 | ✅ |
| AVGO | 1,396 | 2024–2025 | ✅ |
| CRM | 1,449 | 2025–2026 | ✅ |
| GOOGL | 907 | 2025 | ✅ |
| IBM | 3,599 | 2024–2025 | ✅ (largest) |
| INTC | 1,992 | 2024–2025 | ✅ |
| LRCX | 410 | 2025 | ✅ |
| META | 1,703 | 2024–2025 | ✅ |
| MSFT | 738 | 2025 | ✅ |
| NFLX | 1,974 | 2024–2025 | ✅ |
| NOW | 1,388 | 2024–2025 | ✅ |
| NVDA | 1,445 | 2025–2026 | ✅ |
| ORCL | 1,582 | 2025 | ✅ |
| PANW | 1,634 | 2024–2025 | ✅ |
| PLTR | 1,048 | 2025 | ✅ |
| PYPL | 1,543 | 2024–2025 | ✅ |
| TSLA | 1,307 | 2024–2025 | ✅ |
| UBER | 1,070 | 2025 | ✅ |

**❌ Missing from 10-K (7 tickers):**

| Ticker | Notes |
|---|---|
| ADBE | Ingestion started but not indexed to ten_k_chunks |
| CSCO | Not yet run |
| MU | Not yet run |
| QCOM | Not yet run |
| TXN | Not yet run |
| KLAC | Not yet run |
| SNOW | Not yet run |

---

## 📝 Transcript Chunks (yfinance Quarterly Summaries)

**75 chunks across 15 tickers** — each ticker has ~5 quarters of data (Q1–Q4 spanning ~2 years)

| Ticker | Chunks | Year Range | Quarters |
|---|---|---|---|
| AAPL | 5 | 2024–2025 | Q1–Q4 |
| ADBE | 5 | 2025–2026 | Q1–Q4 |
| AMD | 5 | 2024–2025 | Q1–Q4 |
| AMZN | 5 | 2024–2025 | Q1–Q4 |
| AVGO | 5 | 2025–2026 | Q1–Q4 |
| CRM | 5 | 2025–2026 | Q1–Q4 |
| GOOGL | 5 | 2024–2025 | Q1–Q4 |
| INTC | 5 | 2025–2026 | Q1–Q4 |
| META | 5 | 2024–2025 | Q1–Q4 |
| MSFT | 5 | 2024–2025 | Q1–Q4 |
| NFLX | 5 | 2025–2026 | Q1–Q4 |
| NVDA | 5 | 2025–2026 | Q1–Q4 |
| ORCL | 5 | 2025–2026 | Q1–Q4 |
| TSLA | 5 | 2025–2026 | Q1–Q4 |
| UBER | 5 | 2024–2025 | Q1–Q4 |

**❌ Missing from Transcript Chunks (13 tickers):**

| Ticker | Has 10-K? | Priority |
|---|---|---|
| IBM | ✅ Yes | 🔴 High |
| PANW | ✅ Yes | 🔴 High |
| NOW | ✅ Yes | 🔴 High |
| PYPL | ✅ Yes | 🔴 High |
| PLTR | ✅ Yes | 🔴 High |
| LRCX | ✅ Yes | 🟡 Medium |
| AMAT | ✅ Yes | 🟡 Medium |
| CSCO | ❌ No (10-K also missing) | 🟡 Medium |
| MU | ❌ No | 🟡 Medium |
| QCOM | ❌ No | 🟡 Medium |
| TXN | ❌ No | 🟡 Medium |
| KLAC | ❌ No | 🟢 Low |
| SNOW | ❌ No | 🟢 Low |

---

## 🗃️ SEC Filings Metadata (`complete_sec_filings`)

47 raw filing records (10-K metadata/full text) across same 21 tickers as ten_k_chunks.  
Most tickers have 1–4 filing entries (reflects different annual filing versions ingested).

**Key note:** This is metadata about filings, not the RAG-ready chunks. The RAG pipeline uses `ten_k_chunks` (chunked + embedded), not this table directly.

---

## 📈 Coverage vs Target

**Target ticker universe:** 28 (from `us_tickers.txt`)

| Metric | Count | % Complete |
|---|---|---|
| Tickers with 10-K chunks | 21 / 28 | **75%** |
| Tickers with transcript chunks | 15 / 28 | **54%** |
| Tickers with BOTH data sources | 14 / 28 | **50%** |
| Tickers with NO data at all | 0 / 28 | **0%** (ADBE has transcripts) |

### Data Source Coverage Map

```
Ticker  | 10-K  | Transcripts | Status
--------|-------|-------------|-------
AAPL    |  ✅   |     ✅      | FULL
MSFT    |  ✅   |     ✅      | FULL
NVDA    |  ✅   |     ✅      | FULL
GOOGL   |  ✅   |     ✅      | FULL
AMZN    |  ✅   |     ✅      | FULL
META    |  ✅   |     ✅      | FULL
TSLA    |  ✅   |     ✅      | FULL
AVGO    |  ✅   |     ✅      | FULL
AMD     |  ✅   |     ✅      | FULL
INTC    |  ✅   |     ✅      | FULL
ORCL    |  ✅   |     ✅      | FULL
CRM     |  ✅   |     ✅      | FULL
NFLX    |  ✅   |     ✅      | FULL
UBER    |  ✅   |     ✅      | FULL
ADBE    |  ❌   |     ✅      | PARTIAL (no 10-K)
IBM     |  ✅   |     ❌      | PARTIAL (no transcripts)
PANW    |  ✅   |     ❌      | PARTIAL
NOW     |  ✅   |     ❌      | PARTIAL
PYPL    |  ✅   |     ❌      | PARTIAL
PLTR    |  ✅   |     ❌      | PARTIAL
LRCX    |  ✅   |     ❌      | PARTIAL
AMAT    |  ✅   |     ❌      | PARTIAL
CSCO    |  ❌   |     ❌      | MISSING
MU      |  ❌   |     ❌      | MISSING
QCOM    |  ❌   |     ❌      | MISSING
TXN     |  ❌   |     ❌      | MISSING
KLAC    |  ❌   |     ❌      | MISSING
SNOW    |  ❌   |     ❌      | MISSING
```

---

## 🔧 Pending Ingestion Tasks

### Task A: 10-K Ingestion for 7 missing tickers

**Script:** `agent/rag/data_ingestion/ingest_10k_filings_full.py` (via datamule)  
**Command:**
```bash
python agent/rag/data_ingestion/ingest_10k_filings_full.py --tickers ADBE CSCO MU QCOM TXN KLAC SNOW
```

**Estimated time:** 5–15 min per ticker (EDGAR download + chunking + embedding + DB insert)  
**Total estimate:** 1–2 hours

### Task B: yfinance Transcript Ingestion for 13 missing tickers

**Script:** `agent/rag/data_ingestion/ingest_yfinance_to_transcripts.py`  
**Command:**
```bash
python agent/rag/data_ingestion/ingest_yfinance_to_transcripts.py \
  --tickers IBM PANW NOW PYPL PLTR LRCX AMAT CSCO MU QCOM TXN KLAC SNOW \
  --lookback-quarters 8
```

**Estimated time:** 2–5 min total (yfinance is fast)  
**Total estimate:** ~5 minutes

### Task C: Real Earnings Transcripts (Optional / Future)

**Current state:** `complete_transcripts` table is **empty** (0 rows)  
**Original plan:** API Ninjas for real transcripts (requires premium subscription)  
**Current workaround:** yfinance quarterly financial summaries (cheaper, no real transcript dialogue)  
**Recommendation:** Keep yfinance approach for now; note in README that real transcripts would improve Q&A depth

---

## 📅 Ingestion Timeline

| Date | Activity | Result |
|---|---|---|
| 2026-04-27 | 10-K ingestion via datamule (NVDA first) | First chunks in DB |
| 2026-04-27 | Expanded 10-K ingestion (21 companies) | 22,980 → 28,029 chunks |
| 2026-04-27/28 | yfinance transcript ingestion (15 companies) | 75 transcript chunks |
| **Pending** | 10-K for 7 missing tickers | Target: 28 tickers |
| **Pending** | Transcripts for 13 missing tickers | Target: 28 tickers |
