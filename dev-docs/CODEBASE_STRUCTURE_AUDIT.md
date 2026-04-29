# Finance Agent Codebase Structure Audit & Cleanup Plan

**Date:** 2026-04-28  
**Scope:** Files created during data ingestion, error resolution, and testing phases (April 27-28)  
**Current Status:** ❌ **MESSY** — requires major reorganization

---

## 📋 Executive Summary

The codebase has significant structural issues introduced during the current work session:

1. **23 Ticker Directories** at project root (AAPL, MSFT, NVDA, etc.) — should be `data/raw/` or similar
2. **13 Loose Log/Error Files** at project root — should be `logs/` directory
3. **5 Test/Utility Scripts** at project root — should be `tests/` directory
4. **1 New Data Ingestion Script** correctly placed but not integrated into docs
5. **1 Launch Config** correctly placed in `.claude/launch.json`
6. **Missing Directories:** `data/`, `logs/`, `tests/` (no proper organization)

**Affected Files/Dirs:** ~40+ files/directories requiring reorganization
**Impact:** 
- Root directory cluttered and hard to navigate
- Unclear separation between source code, data, tests, and logs
- No clear data pipeline tracking (raw vs. processed vs. ingested)
- Makes onboarding and CI/CD harder

---

## 🔍 Detailed Inventory

### 1. **Ticker Directories at Root** (MUST MOVE)

**Current Location:** `/<TICKER>/` (23 directories)  
**Directories:** AAPL, ADBE, AMAT, AMD, AMZN, AVGO, CRM, CSCO, GOOGL, IBM, INTC, LRCX, META, MSFT, MU, NFLX, NOW, NVDA, ORCL, PANW, PLTR, PYPL, QCOM, TSLA, UBER

**Contents:** Each contains `.tar` files (EDGAR 10-K filing archives from datamule/SEC EDGAR)
- Example: `AAPL/000032019324000123.tar` (EDGAR accession numbers)
- Size: 9–10 MB per ticker directory
- Purpose: Raw archived 10-K documents awaiting processing/ingestion

**Issues:**
- ❌ Clogs root directory
- ❌ Not in `.gitignore` (if committed, will bloat repo)
- ❌ No clear separation from source code
- ❌ Hard to identify ingestion pipeline status at a glance

**Proposed Structure:**
```
data/
├── raw/
│   ├── sec_edgar/
│   │   ├── AAPL/
│   │   │   └── *.tar (EDGAR documents)
│   │   ├── MSFT/
│   │   └── ...
│   └── yfinance/  (for future quote data, if stored locally)
└── processed/
    ├── ten_k_chunks/
    ├── transcript_chunks/
    └── embeddings/
```

**Action:** Move all 23 ticker directories from `./` to `./data/raw/sec_edgar/`

---

### 2. **Loose Log Files at Root** (MUST MOVE)

**Current Location:** `/` (13 files)  
**Files:**
- `10k_db_ingestion.log` — 0 bytes (empty)
- `backend.log` — 15 KB
- `earnings_transcripts_fetch.log` — 2 KB
- `ingestion_err.txt` — 308 KB ⚠️ (LARGE — contains full error traces)
- `ingestion_log.txt` — 52 KB ⚠️ (LARGE — datamule 10-K ingestion output)
- `output.txt` — 84 KB ⚠️ (LARGE — old test output?)
- `sec_filings_ingestion.log` — 0 bytes (empty)
- `server.log` — 68 KB
- `yf_err.txt` — 21 KB ⚠️ (yfinance errors)
- `yf_log.txt` — 0 bytes
- `yfinance_err.txt` — 40 bytes
- `yfinance_log.txt` — 40 bytes
- `DATA_INGESTION_STATUS.md` — 2.6 KB (status doc, not a log)
- `STEP9_STATUS.md` — 3.8 KB (status doc)

**Issues:**
- ❌ Root cluttered with non-code files
- ❌ Multiple duplicates/similar purposes (`yf_*.txt` vs. `yfinance_*.txt`)
- ❌ Large error files (308 KB `ingestion_err.txt`) should be archived/compressed
- ❌ No clear timestamp/rotation strategy
- ❌ Status docs mixed with logs (should be in docs/)

**Proposed Structure:**
```
logs/
├── 2026-04-28/
│   ├── 10k_ingestion/
│   │   ├── datamule.log (or ingestion_log.txt renamed)
│   │   └── errors.log (or ingestion_err.txt renamed)
│   ├── yfinance_ingestion/
│   │   ├── yfinance.log
│   │   └── errors.log
│   ├── backend.log
│   └── server.log
docs/
├── DATA_INGESTION_STATUS.md
├── STEP9_STATUS.md
└── API_TEST_RESULTS.md (for test_apis.py output)
```

**Action:** 
- Move all `.log` and `.txt` files to `logs/2026-04-28/` (or similar dated subdirs)
- Move status/progress docs (`DATA_INGESTION_STATUS.md`, `STEP9_STATUS.md`) to `docs/`
- Consolidate duplicate yfinance logs (`yfinance_*.txt` + `yf_*.txt` → `logs/yfinance/`)

---

### 3. **Root-Level Test/Utility Scripts** (SHOULD MOVE)

**Current Location:** `/` (5 files)  
**Files:**
- `test_apis.py` — 13.4 KB ✅ **NEW** (comprehensive API test suite)
- `test_db_connection.py` — 1.4 KB (DB connection test)
- `config.py` — 15.1 KB (configuration loader)
- `create_mock_data.py` — 2.2 KB (mock data generator)
- `fastapi_server.py` — 0.5 KB (simple FastAPI entry point)

**Issues:**
- ❌ `test_*.py` should be in `tests/` directory, not root
- ❌ `config.py` and `create_mock_data.py` purpose unclear (test helpers? utilities?)
- ❌ `fastapi_server.py` is deprecated (main entry point is `app/main.py`)
- ✅ `test_apis.py` is **correctly** written but in wrong location

**Proposed Structure:**
```
tests/
├── __init__.py
├── test_apis.py (move from root)
├── test_db_connection.py (move from root)
├── unit/
│   └── (unit tests for individual modules)
├── integration/
│   └── (integration tests)
└── fixtures/
    └── (test data, mocks)

utils/  (or scripts/)
├── config.py (move from root)
├── create_mock_data.py (move from root)
└── fastapi_server.py (delete? or move to scripts/ if needed for development)
```

**Action:**
- Move `test_*.py` → `tests/`
- Move `config.py` and `create_mock_data.py` → `utils/` or `scripts/`
- Delete or archive `fastapi_server.py` (check if it's still used; likely superseded by `app/main.py`)

---

### 4. **New Data Ingestion Script** (CORRECTLY PLACED ✅)

**Location:** `agent/rag/data_ingestion/ingest_yfinance_to_transcripts.py` ✅

**Status:** ✅ Correctly placed in data ingestion pipeline directory

**Issue:** 
- ⚠️ Not documented in `agent/rag/data_ingestion/README.md`
- ⚠️ Not tracked in data ingestion status docs

**Action:**
- Add entry to `agent/rag/data_ingestion/README.md`
- Document in `docs/DATA_INGESTION_PIPELINE.md` or update `DATA_INGESTION_STATUS.md`

---

### 5. **Configuration Files** (CORRECTLY PLACED ✅)

**Location:** `.claude/launch.json` ✅  
**Purpose:** Dev server launch configuration (frontend + backend)

**Status:** ✅ Correctly placed and properly structured

**No action needed.**

---

### 6. **Missing/Under-Documented** 

**What should exist but doesn't:**

| Item | Purpose | Current State |
|---|---|---|
| `tests/` | Test suite directory | ❌ Missing (tests scattered at root) |
| `logs/` | Centralized logs | ❌ Missing (logs at root) |
| `data/` | Data pipeline (raw/processed) | ❌ Missing (ticker dirs at root) |
| `docs/` | Project documentation | ⚠️ Partial (README.md exists, but scattered docs) |
| `scripts/` | Utility scripts | ❌ Missing (scattered at root) |
| `.gitignore` | Git ignores | ⚠️ Needs update for logs/, data/raw/ |

---

## 📐 Proposed Final Directory Structure

```
finance-agent/
├── .claude/                          # Claude Code config (✅ OK)
│   ├── launch.json
│   ├── settings.json
│   └── settings.local.json
├── .git/                             # Git repo
├── .venv/                            # Python virtual env
├── .vscode/                          # VSCode settings
├── app/                              # Main FastAPI application (✅ OK)
│   ├── __init__.py
│   ├── main.py
│   ├── auth/
│   ├── routers/
│   ├── schemas/
│   ├── utils/
│   └── websocket/
├── agent/                            # Agent logic (✅ OK)
│   ├── rag/
│   │   ├── data_ingestion/
│   │   │   ├── ingest_10k_filings_full.py
│   │   │   ├── ingest_yfinance_to_transcripts.py    (✅ NEW)
│   │   │   ├── README.md (⚠️ needs update)
│   │   │   └── ...
│   │   └── ...
│   └── ...
├── data/                             # ⚠️ NEW — Data pipeline (RAW/PROCESSED)
│   ├── raw/
│   │   └── sec_edgar/                (⚠️ MOVE 23 ticker dirs here)
│   │       ├── AAPL/
│   │       ├── MSFT/
│   │       └── ...
│   └── processed/                    (future: ingested chunks, embeddings)
│       ├── ten_k_chunks/
│       └── transcript_chunks/
├── docs/                             # ⚠️ NEW — Documentation
│   ├── API_REFERENCE.md
│   ├── DATA_INGESTION_STATUS.md      (⚠️ MOVE from root)
│   ├── DATA_INGESTION_PIPELINE.md    (new: detailed pipeline docs)
│   ├── ARCHITECTURE.md
│   └── ...
├── logs/                             # ⚠️ NEW — Application logs
│   ├── 2026-04-28/                   (dated subdirectories)
│   │   ├── 10k_ingestion/
│   │   │   ├── datamule.log          (⚠️ MOVE from root: ingestion_log.txt)
│   │   │   └── errors.log            (⚠️ MOVE from root: ingestion_err.txt)
│   │   ├── yfinance_ingestion/
│   │   │   ├── yfinance.log          (⚠️ MOVE from root: yf_log.txt)
│   │   │   └── errors.log            (⚠️ MOVE from root: yf_err.txt)
│   │   └── ...
│   └── README.md                     (log rotation/retention policy)
├── tests/                            # ⚠️ NEW — Test suite
│   ├── __init__.py
│   ├── test_apis.py                  (⚠️ MOVE from root)
│   ├── test_db_connection.py         (⚠️ MOVE from root)
│   ├── unit/
│   └── integration/
├── scripts/                          # ⚠️ NEW — Utility scripts
│   ├── config.py                     (⚠️ MOVE from root)
│   ├── create_mock_data.py           (⚠️ MOVE from root)
│   └── README.md                     (document each script)
├── .env                              # (✅ OK, but in .gitignore)
├── .env.example
├── .cursorignore                     # (✅ OK)
├── .cursorrules
├── .gitignore                        # (⚠️ NEEDS UPDATE — add logs/, data/raw/, etc.)
├── Procfile
├── README.md                         # (✅ OK, but may need update for new structure)
├── pyproject.toml                    # (✅ OK)
├── requirements.txt                  # (✅ OK)
└── requirements-minimal.txt          # (✅ OK)
```

---

## 🔧 Cleanup Action Plan

### Phase 1: Create New Directories (Safe — no file moves)

```bash
mkdir -p data/raw/sec_edgar
mkdir -p data/processed
mkdir -p logs/2026-04-28
mkdir -p docs
mkdir -p tests/unit tests/integration tests/fixtures
mkdir -p scripts
```

### Phase 2: Move Ticker Directories

```bash
# Move 23 ticker directories from root to data/raw/sec_edgar/
mv AAPL ADBE AMAT AMD AMZN AVGO CRM CSCO GOOGL IBM INTC LRCX META MSFT MU NFLX NOW NVDA ORCL PANW PLTR PYPL QCOM TSLA UBER data/raw/sec_edgar/
```

**Verify:** `ls data/raw/sec_edgar/` should show 23 directories

### Phase 3: Move Log Files

```bash
# Move log/error/status files
mv *.log logs/2026-04-28/
mv ingestion_err.txt ingestion_log.txt logs/2026-04-28/
mv yf_*.txt yfinance_*.txt logs/2026-04-28/
mv output.txt logs/2026-04-28/

# Move status docs to docs/
mv DATA_INGESTION_STATUS.md STEP9_STATUS.md docs/
```

### Phase 4: Move Test/Utility Scripts

```bash
# Move tests
mv test_apis.py test_db_connection.py tests/

# Move utilities/scripts
mv config.py create_mock_data.py scripts/

# Decide on fastapi_server.py (check if used)
# If not used: rm fastapi_server.py
# If used: mv fastapi_server.py scripts/
```

### Phase 5: Update Documentation

**Files to create/update:**

1. **`docs/DATA_INGESTION_PIPELINE.md`** — New file
   - Overview of RAG data pipeline
   - Where raw data comes from (SEC EDGAR, yfinance)
   - Where processed data goes (ten_k_chunks, transcript_chunks)
   - New script: `ingest_yfinance_to_transcripts.py`

2. **`agent/rag/data_ingestion/README.md`** — Update
   - Add entry for `ingest_yfinance_to_transcripts.py`
   - Document usage: `python ingest_yfinance_to_transcripts.py --tickers AAPL MSFT NVDA`

3. **`docs/PROJECT_STRUCTURE.md`** — New file
   - Visual guide to directory layout
   - Where to find tests, logs, data

4. **`.gitignore`** — Update
   ```
   # Add or update:
   logs/
   data/raw/
   *.log
   *.tar
   .DS_Store
   ```

5. **`logs/README.md`** — New file
   - Log rotation policy
   - How to read log files from each pipeline
   - Retention/cleanup guidelines

### Phase 6: Verify No Breakage

After moves:

1. ✅ `python -m pytest tests/` — ensure tests run from new location
2. ✅ `python tests/test_apis.py` — ensure test_apis.py imports/runs from new location
3. ✅ Check `app/main.py` imports — ensure any imports of `config.py` updated to `scripts.config` or `from scripts import config`
4. ✅ Git status — ensure no files accidentally deleted
5. ✅ Backend server still runs: `python -m uvicorn app.main:app --reload`

---

## 📊 Summary Table

| Category | Current | Issue | Proposed | Status |
|---|---|---|---|---|
| **Ticker Directories** | Root (23 dirs) | Clutters root | `data/raw/sec_edgar/` | 🔴 MOVE |
| **Log Files** | Root (13 files) | Clutters root, duplicates | `logs/YYYY-MM-DD/` | 🔴 MOVE |
| **Status Docs** | Root (2 files) | Should be in docs/ | `docs/` | 🔴 MOVE |
| **Test Scripts** | Root (2 files) | Should be in tests/ | `tests/` | 🔴 MOVE |
| **Utility Scripts** | Root (3 files) | Should be in scripts/ | `scripts/` | 🔴 MOVE |
| **Data Ingestion (yfinance)** | `agent/rag/data_ingestion/` ✅ | Needs documentation | Update docs | 🟡 DOC UPDATE |
| **Launch Config** | `.claude/launch.json` ✅ | None | Keep as-is | 🟢 OK |
| **App Structure** | `app/` ✅ | None | Keep as-is | 🟢 OK |

---

## 🎯 Effort Estimate

| Phase | Task | Time |
|---|---|---|
| 1 | Create directories | 2 min |
| 2 | Move ticker dirs (23) | 3 min |
| 3 | Move logs/status docs | 3 min |
| 4 | Move test/utility scripts | 2 min |
| 5 | Update documentation | 15 min |
| 6 | Verify + test | 10 min |
| **Total** | | **~35 minutes** |

---

## ⚠️ Risks & Mitigation

| Risk | Severity | Mitigation |
|---|---|---|
| Import paths break after moves | 🔴 High | Run `python -m pytest tests/` after moves; check app/main.py imports |
| Logs lost during cleanup | 🔴 High | Archive old logs before deleting: `tar -czf logs/archive-2026-04-28.tar.gz logs/2026-04-28/` |
| Git tracks moved files as deletes + adds | 🟡 Medium | Use `git mv old new` instead of shell `mv` (if already committed) |
| Ingestion scripts fail if paths hardcoded | 🟡 Medium | Search for hardcoded paths like `./AAPL/` or `./ingestion_log.txt` in ingestion scripts |

---

## 📝 Next Steps (Do NOT Execute Yet)

1. ✅ Review this audit (what you're doing now)
2. ⏳ **Next session:** Execute Phase 1–6 systematically
3. ⏳ **After moves:** Run full test suite to verify nothing broke
4. ⏳ **After verification:** Create PR/commit with "refactor: reorganize codebase structure"

---

**Document Version:** 1.0  
**Last Updated:** 2026-04-28 01:10 UTC  
**Prepared for:** Start of new chat session
