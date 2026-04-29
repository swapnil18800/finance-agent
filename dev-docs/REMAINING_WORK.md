# Remaining Work & Project Status

**Date:** 2026-04-28  
**Project:** AlphaLens Finance Agent (forked from StrataLens)  
**Goal:** Job-hunt portfolio project — fully working RAG financial Q&A app

---

## 🚦 Overall Status: ~60% Complete

| Area | Status | % Done |
|---|---|---|
| Backend API (FastAPI) | ✅ Running | ~85% |
| RAG Pipeline (search + LLM) | ✅ Working | ~80% |
| Data — 10-K (annual filings) | ⚠️ Partial | 75% |
| Data — Transcripts (quarterly) | ⚠️ Partial | 54% |
| Frontend (React) | ✅ Running | ~70% |
| Test Suite | ✅ 25/27 tests | ~93% |
| Codebase Structure | ❌ Messy | 20% |
| Documentation | ❌ Scattered | 30% |
| Deployment (Railway) | ✅ Live | ~90% |

---

## 🔴 Critical / Blocking

### 1. Fix 2 Failing API Tests

**Tests failing:**
- `Demo got result` — `/chat/landing/demo/stream-v2` returns 1 event but not `"result"` type
- `Invalid question handled gracefully` — `/chat/message/stream-v2` with off-topic query hangs or crashes, never returns a result event

**Why it matters:** These are user-facing features. Demo endpoint is the first thing visitors see on landing page. Invalid question crash could expose error traces.

**Effort:** 1–2 hours  
**Files:** `app/routers/chat.py`, `agent/rag/search_planner.py`

---

### 2. Complete Data Ingestion

**10-K chunks — 7 tickers missing:** ADBE, CSCO, MU, QCOM, TXN, KLAC, SNOW  
**Transcript chunks — 13 tickers missing:** IBM, PANW, NOW, PYPL, PLTR, LRCX, AMAT, CSCO, MU, QCOM, TXN, KLAC, SNOW

**Why it matters:** RAG answers are only as good as the data. If someone asks about CSCO or SNOW, the agent has nothing to retrieve.

**Effort:** 
- yfinance transcripts (13 tickers): ~5 minutes, run a single command
- 10-K ingestion (7 tickers): 1–2 hours (EDGAR download intensive)

**Commands:**
```bash
# Fast — transcript chunks
python agent/rag/data_ingestion/ingest_yfinance_to_transcripts.py \
  --tickers IBM PANW NOW PYPL PLTR LRCX AMAT CSCO MU QCOM TXN KLAC SNOW

# Slow — 10-K chunks (run overnight or in background)
python agent/rag/data_ingestion/ingest_10k_filings_full.py \
  --tickers ADBE CSCO MU QCOM TXN KLAC SNOW
```

---

## 🟡 Important / Non-Blocking

### 3. Codebase Structure Cleanup

**See:** `dev-docs/CODEBASE_STRUCTURE_AUDIT.md` for full plan.

**Summary of mess:**
- 23 ticker directories (`AAPL/`, `MSFT/`, etc.) sitting at project root
- 13 log/error files at project root
- Test scripts (`test_apis.py`) at root instead of `tests/`
- No `data/`, `logs/`, `tests/` directories

**Why it matters:** Portfolio project — recruiters/interviewers may look at the repo structure. Messy root = bad impression.

**Effort:** ~35 minutes to move everything + update .gitignore

---

### 4. Transcripts Endpoint Returns 500

**Endpoint:** `GET /transcripts/transcript/AAPL/2025/1`  
**Status:** Returns 500 (test accepts this as "responded", but it should be 200 or 404)

**Likely cause:** `complete_transcripts` table is empty, and the endpoint doesn't handle empty gracefully — it probably crashes when trying to access data.

**Effort:** 30 min  
**File:** `app/routers/transcript.py`

---

### 5. Companies Endpoint Returns Empty Results

**Endpoint:** `GET /companies/companies/public/search?query=NVIDIA`  
**Status:** Returns 200 + `{"success": true, "companies": []}` — always empty  

**Root cause:** Missing data in `financial_data.company_profiles` table (or equivalent). The search query runs but finds no company profiles because none have been seeded.

**Effort:** 1–2 hours to understand schema + seed company data  
**Files:** `app/routers/companies.py` or equivalent

---

### 6. SEC Filings Sparse Coverage

**Current state:** `complete_sec_filings` has 47 rows (mostly just 1–4 per ticker)  
**Test:** `NVDA has filings in DB — 2 filings` ✅ (passes, but thin)

**The issue:** The SEC filings API (`/sec-filings/sec-filings/NVDA/available`) works and returns data, but users clicking through to read full filings may get limited options.

**Effort:** Low priority — current coverage sufficient for demo

---

## 🟢 Nice to Have / Polish

### 7. Frontend Polish

**Current state:** React frontend running, core chat UI works  
**Missing:**
- Logo (`StrataLensLogo.tsx` was deleted, replaced by `AppLogo.tsx`)
- `AboutModal.tsx` may have broken links/old branding
- Landing page still has StrataLens copy in places

**Effort:** 2–4 hours  
**Files:** `frontend/src/components/AboutModal.tsx`, `frontend/src/pages/LandingPage.tsx`

---

### 8. Real Earnings Transcripts

**Current:** Replaced with yfinance quarterly financial summaries (75 rows, 15 tickers)  
**Problem:** Summaries lack the Q&A, management commentary, and forward-looking statements that real transcripts contain  
**Options:**
- API Ninjas (premium) — requires paid plan
- Scrape/find free public transcripts
- Use Motley Fool / Seeking Alpha public pages
- Accept yfinance as good enough for demo

**Recommendation:** Accept yfinance for now; mark as "v2 enhancement" in README

---

### 9. Streaming Test for Demo Endpoint

**Test `test_chat_stream_demo`** hits `/chat/landing/demo/stream-v2` and expects a `"result"` event.  
**Currently failing** because event schema differs — needs either test fix or endpoint fix.

---

### 10. Documentation for Portfolio

**Missing docs (for recruiter/interview purposes):**
- `docs/ARCHITECTURE.md` — system diagram: user → frontend → FastAPI → RAG pipeline → Cerebras LLM → pgvector
- `docs/DATA_PIPELINE.md` — how 10-K data flows from SEC EDGAR → datamule → ten_k_chunks → RAG
- README update — rebrand from StrataLens → AlphaLens, add demo GIF, update tech stack section

**Effort:** 2–3 hours  
**Why it matters:** This is the #1 thing that makes or breaks a portfolio project for GenAI roles

---

## 📋 Prioritized Task Queue

### Phase 1: Data Complete (do first — running in background is fine)

| # | Task | Effort | Priority |
|---|---|---|---|
| 1 | Run yfinance ingestion for 13 missing tickers | 5 min | 🔴 |
| 2 | Run 10-K ingestion for 7 missing tickers | 1–2 hr (background) | 🔴 |

### Phase 2: Code Fixes

| # | Task | Effort | Priority |
|---|---|---|---|
| 3 | Fix invalid question handling (graceful no-result response) | 1 hr | 🔴 |
| 4 | Fix demo endpoint event schema / test assertion | 30 min | 🔴 |
| 5 | Fix transcripts endpoint 500 error | 30 min | 🟡 |
| 6 | Fix companies endpoint returning empty | 1–2 hr | 🟡 |

### Phase 3: Structure Cleanup

| # | Task | Effort | Priority |
|---|---|---|---|
| 7 | Move ticker dirs → `data/raw/sec_edgar/` | 5 min | 🟡 |
| 8 | Move logs → `logs/` | 5 min | 🟡 |
| 9 | Move tests → `tests/` | 5 min | 🟡 |
| 10 | Update `.gitignore` for `data/`, `logs/` | 5 min | 🟡 |

### Phase 4: Documentation & Polish

| # | Task | Effort | Priority |
|---|---|---|---|
| 11 | Write `docs/ARCHITECTURE.md` | 1 hr | 🟡 |
| 12 | Update README (rebrand + tech stack + demo) | 1–2 hr | 🟡 |
| 13 | Frontend branding polish | 2 hr | 🟢 |
| 14 | Add demo GIF / screenshot to README | 30 min | 🟢 |

---

## ✅ Completed Work (This Session)

| Done | Details |
|---|---|
| ✅ RAG pipeline fixes | 4-layer patch to `search_planner.py` — FY2025 regex, 10-K fallback, availability check |
| ✅ 10-K ingestion (21 tickers) | 28,029 chunks, 126 MB in DB |
| ✅ yfinance transcript ingestion (15 tickers) | 75 chunks, quarterly financial summaries |
| ✅ Ticker list cleanup | 28 clean tickers in `us_tickers.txt` |
| ✅ Test suite (`test_apis.py`) | Comprehensive API test script, 25/27 passing |
| ✅ Streaming timeout fix | `socket.setdefaulttimeout(300)` for LLM streaming tests |
| ✅ RAG answer verified | NVIDIA FY2025 revenue returns `$130B` correctly |
| ✅ Multi-company comparison | Apple vs Microsoft works |
| ✅ Dev docs folder created | `dev-docs/` with audit, ingestion status, remaining work |

---

## 🕐 Total Remaining Effort Estimate

| Category | Effort |
|---|---|
| Data ingestion (remaining) | 2–3 hours |
| Code fixes (4 issues) | 3–4 hours |
| Structure cleanup | 35 minutes |
| Docs + portfolio polish | 3–4 hours |
| **TOTAL** | **~9–12 hours** |

> At current pace (~3–4 hr/day sessions), this is **2–3 more work sessions** to get to a job-ready portfolio state.
