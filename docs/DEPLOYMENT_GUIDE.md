 # Deployment Guide: Making This Project Your Own

This guide covers everything you need to deploy this codebase under your own identity — new branding, your own API keys, your own Railway deployment. Follow the sections in order.

---

## Table of Contents

1. [What You're Working With](#1-what-youre-working-with)
2. [Step 1 — Rebrand the Codebase](#2-step-1--rebrand-the-codebase)
3. [Step 2 — Create All Required Accounts & Keys](#3-step-2--create-all-required-accounts--keys)
4. [Step 3 — Set Up PostgreSQL with pgvector](#4-step-3--set-up-postgresql-with-pgvector)
5. [Step 4 — Configure Environment Variables](#5-step-4--configure-environment-variables)
6. [Step 5 — Ingest Data (Critical)](#6-step-5--ingest-data-critical)
7. [Step 6 — Build the Frontend](#7-step-6--build-the-frontend)
8. [Step 7 — Deploy on Railway](#8-step-7--deploy-on-railway)
9. [Step 8 — Post-Deployment Checklist](#9-step-8--post-deployment-checklist)
10. [Appendix — Full Environment Variable Reference](#10-appendix--full-environment-variable-reference)

---

## 1. What You're Working With

| Layer | Technology |
|---|---|
| Frontend | React 19 + TypeScript + Vite + Tailwind CSS |
| Backend | FastAPI (Python) + Uvicorn |
| Database | PostgreSQL with pgvector extension |
| Auth | Clerk (JWT-based) |
| LLM | Cerebras (primary) + OpenAI (fallback) |
| Vector Search | pgvector (384-dim embeddings via sentence-transformers) |
| News Search | Tavily API |
| Earnings Data | API Ninjas |
| Screener | DuckDB (local file — already in repo at `agent/screener/financial_data_new.duckdb`) |
| Deployment | Railway (Procfile + railway.toml already configured) |

---

## 2. Step 1 — Rebrand the Codebase

These are every place the original author's identity and product name appear. Change them all before pushing to GitHub.

### 2a. `frontend/src/components/AboutModal.tsx`

This is the most critical file — it renders a visible "Created by Hrishikesh Kamath" credit with a link to his site.

**Lines 75–86 — Replace with your own info:**
```tsx
// BEFORE
<p className="text-sm text-slate-500 mb-1">Created by</p>
<p className="text-lg font-semibold text-slate-900">Hrishikesh Kamath</p>
...
<a href="https://kamathhrishi.github.io" ...>
  Visit kamathhrishi.github.io
</a>
<div className="p-4 bg-slate-50 rounded-xl">
  <p className="text-sm text-slate-600 leading-relaxed">
    I spent several months building StrataLens as a product...
  </p>
</div>

// AFTER — replace with your name, your portfolio link, your description
<p className="text-sm text-slate-500 mb-1">Created by</p>
<p className="text-lg font-semibold text-slate-900">YOUR NAME</p>
...
<a href="https://YOUR-PORTFOLIO.com" ...>
  Visit YOUR-PORTFOLIO.com
</a>
<div className="p-4 bg-slate-50 rounded-xl">
  <p className="text-sm text-slate-600 leading-relaxed">
    Built this as a full-stack AI project combining RAG, vector search, and real-time 
    financial data to help analysts research SEC filings and earnings calls faster.
  </p>
</div>
```

**Line 57 — Change modal title:**
```tsx
// BEFORE
<h2 className="text-xl font-bold text-slate-900">About StrataLens</h2>
// AFTER
<h2 className="text-xl font-bold text-slate-900">About YOUR-APP-NAME</h2>
```

### 2b. `frontend/src/pages/LandingPage.tsx`

Search and replace all occurrences of `StrataLens` with your chosen app name. Key spots:

- Line 163: `<span className="...">StrataLens</span>` — navbar brand text
- Line 167: `<a href="#why" ...>Why StrataLens</a>` — nav link label
- Line 631: `id="why"` section heading: `"Primary Source Intelligence"` (fine as-is, but the H3 card at line 663 says `"StrataLens"` — replace it)
- Line 762: footer `<span>StrataLens</span>`

### 2c. `frontend/src/components/StrataLensLogo.tsx`

The component name references the original brand but the SVG itself is a generic FontAwesome `fa-layer-group` icon — perfectly fine to keep. Just rename the file and component if you want:

```bash
# Rename file
mv frontend/src/components/StrataLensLogo.tsx frontend/src/components/AppLogo.tsx
```

Then update all imports across `LandingPage.tsx`, `AboutModal.tsx`, and `Navbar.tsx`:
```tsx
// BEFORE
import StrataLensLogo from './StrataLensLogo'
// AFTER
import AppLogo from './AppLogo'
```

And inside the component itself, rename `StrataLensLogo` → `AppLogo`.

### 2d. `config.py`

**Line 64 — Admin email:**
```python
# BEFORE
ADMIN_EMAIL: str = "admin@stratalens.ai"
# AFTER
ADMIN_EMAIL: str = "admin@yourdomain.com"   # or just use your email
```

**Line 106 — DB application name (shows in PostgreSQL logs, not user-visible):**
```python
# BEFORE
APPLICATION_NAME: str = "stratalens_fastapi"
# AFTER
APPLICATION_NAME: str = "your_app_name_fastapi"
```

**Line 147 — Log file name:**
```python
# BEFORE
MAIN_LOG_FILE: str = "stratalens.log"
# AFTER
MAIN_LOG_FILE: str = "app.log"
```

**Lines 168–178 — CORS origins (update after you have your Railway URL):**
```python
DEFAULT_CORS_ORIGINS: str = (
    "https://YOUR-DOMAIN.com,"           # your custom domain if you have one
    "https://YOUR-APP.up.railway.app,"   # your Railway URL (get this after deploying)
    "http://localhost:3000,"
    "http://localhost:8000,"
    "http://127.0.0.1:3000,"
    "http://127.0.0.1:8000,"
    "http://localhost:5000,"
    "http://127.0.0.1:5000"
)
```

**Lines 237–239 — App title/description:**
```python
TITLE: str = "YOUR APP NAME API"
DESCRIPTION: str = "AI-powered financial research platform"
VERSION: str = "1.0.0"
```

**Line 373 — Default DB name:**
```python
return os.getenv("DATABASE_URL", "postgresql://postgres:changeme@localhost:5432/your_app_db")
```

### 2e. `README.md`

Remove or replace:
- Line 5: `**Live Platform:** [www.stratalens.ai](https://www.stratalens.ai)` — update to your URL
- Line 7: `**10K filings agent blogpost:** [Blogpost](...)` — remove or replace with your own writeup link

### 2f. `.env.example`

**Line 4 — Header comment:**
```
# BEFORE
# StrataLens AI - Environment Variables
# AFTER
# YOUR APP NAME - Environment Variables
```

**Line 28 — DB name:**
```
DATABASE_URL=postgresql://username:password@localhost:5432/your_db_name
```

### 2g. Git author config (local)

Before committing, make sure your git identity is set correctly so all future commits show your name:
```bash
git config user.name "Your Name"
git config user.email "you@youremail.com"
```

---

## 3. Step 2 — Create All Required Accounts & Keys

### Required (app won't work without these)

| Service | What For | Sign Up | Free Tier? |
|---|---|---|---|
| **Railway** | Hosting (backend + frontend) | railway.app | $5/mo hobby plan |
| **Railway PostgreSQL** | Database (add as Railway plugin) | via Railway dashboard | Included in hobby |
| **OpenAI** | LLM fallback + embeddings | platform.openai.com | Pay per use |
| **Cerebras** | Primary fast LLM inference | cloud.cerebras.ai | Free trial available |
| **API Ninjas** | Earnings transcript data | api-ninjas.com | Free tier: 10k calls/mo |
| **Clerk** | User authentication | clerk.com | Free up to 10k MAU |

### Optional (app degrades gracefully without these)

| Service | What For | Sign Up |
|---|---|---|
| **Tavily** | Real-time news search | tavily.com |
| **Logfire** | Structured logging/observability | logfire.pydantic.dev |
| **Redis** | Session caching (Railway plugin) | via Railway dashboard |

### Clerk Setup (most involved — do this carefully)

1. Create a new Clerk application at dashboard.clerk.com
2. Choose **Email + Password** as sign-in method (or add Google/GitHub OAuth)
3. In **API Keys** section, copy:
   - `Publishable key` → `CLERK_PUBLISHABLE_KEY` and `VITE_CLERK_PUBLISHABLE_KEY`
   - `Secret key` → `CLERK_SECRET_KEY`
4. In **Webhooks** (optional but recommended), create a webhook endpoint pointing to `https://YOUR-RAILWAY-URL/clerk/webhook` and copy the signing secret → `CLERK_WEBHOOK_SECRET`
5. In **Allowed origins**, add your Railway deployment URL and any custom domain

---

## 4. Step 3 — Set Up PostgreSQL with pgvector

The app requires PostgreSQL with the `pgvector` extension. Railway makes this easy.

### Option A: Railway PostgreSQL Plugin (recommended)

1. In your Railway project, click **+ New** → **Database** → **PostgreSQL**
2. Railway provisions a managed Postgres instance
3. Go to the PostgreSQL service → **Variables** tab → copy `DATABASE_URL`
4. Connect to the database and enable pgvector:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
   You can do this via Railway's built-in query interface or connect with `psql`.

### Option B: Supabase (free tier, also has pgvector)

1. Create project at supabase.com
2. Go to **SQL Editor** and run: `CREATE EXTENSION vector;`
3. Copy the connection string from **Settings → Database → Connection string (URI)**

### Database Tables

The app auto-creates tables on first startup via `app/utils/database_init.py`. You do **not** need to run migrations manually. Just ensure the `vector` extension is enabled before the first boot.

---

## 5. Step 4 — Configure Environment Variables

Create a `.env` file for local development (never commit this):

```bash
cp .env.example .env
```

Fill in every variable. Full reference is in the Appendix. Minimum required for local dev:

```env
OPENAI_API_KEY=sk-...
CEREBRAS_API_KEY=...
API_NINJAS_KEY=...
DATABASE_URL=postgresql://user:pass@host:5432/dbname
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_...
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
ENVIRONMENT=development
AUTH_DISABLED=true        # keep true during development
```

### Frontend `.env`

The Vite frontend needs its own env file:

```bash
# frontend/.env
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your-clerk-publishable-key
```

---

## 6. Step 5 — Ingest Data (Critical)

**This is the most important step.** Without data in PostgreSQL, the RAG system returns nothing.

The repo includes scripts in `agent/rag/data_ingestion/`. These scripts download financial documents, chunk them, generate embeddings, and store them in PostgreSQL.

### What data needs to be ingested

| Data Type | Script | Source |
|---|---|---|
| Earnings transcripts (Q1 2022 – present) | `download_transcripts.py` | API Ninjas |
| Embeddings for transcripts | `create_and_store_embeddings.py` | Runs locally |
| SEC 10-K filings | `ingest_sec_filings.py` | SEC EDGAR |

### How to run ingestion

```bash
# 1. Install Python dependencies first
pip install -r requirements.txt

# 2. Set your .env variables, then run from project root:

# Download earnings transcripts (takes 30-60 min, uses API Ninjas quota)
python agent/rag/data_ingestion/download_transcripts.py

# Generate embeddings and store in PostgreSQL
python agent/rag/data_ingestion/create_and_store_embeddings.py

# Ingest SEC 10-K filings
python agent/rag/data_ingestion/ingest_sec_filings.py
```

> **Note:** The embedding generation step is CPU/memory intensive and can take several hours for a full dataset. It uses `all-MiniLM-L6-v2` (384-dim) from sentence-transformers. Run it on a machine with at least 8GB RAM.

> **API Ninjas quota:** The free tier gives 10,000 API calls/month. Transcripts for ~500 companies across 12 quarters = potentially high usage. Monitor your quota.

### DuckDB screener (already in repo)

The file `agent/screener/financial_data_new.duckdb` ships with the repo and contains the screener financial data. No ingestion needed — just ensure the file is present when deploying to Railway (you'll need a Railway Volume for this — see deployment section).

---

## 7. Step 6 — Build the Frontend

```bash
cd frontend
npm install
npm run build   # outputs to frontend/dist/
```

The FastAPI backend serves the built frontend as static files. Every time you change the frontend, rebuild and commit `frontend/dist/`.

> **Important:** The `frontend/dist/` folder must be committed to git for Railway to serve it. If it's in `.gitignore`, remove it.

```bash
# Check if dist is ignored
grep "dist" .gitignore

# If it is, remove that line or add an exception:
echo "!frontend/dist" >> .gitignore
```

---

## 8. Step 7 — Deploy on Railway

The repo already has `railway.toml` and `Procfile` configured. Railway will detect these automatically.

### 7a. Connect your GitHub repo to Railway

1. Go to railway.app → **New Project** → **Deploy from GitHub repo**
2. Select your forked repository
3. Railway auto-detects `Procfile` and starts building

### 7b. Add environment variables in Railway

In your Railway service → **Variables** tab, add all backend variables from the Appendix. Key ones:

```
OPENAI_API_KEY=...
CEREBRAS_API_KEY=...
API_NINJAS_KEY=...
DATABASE_URL=<from Railway PostgreSQL plugin>
CLERK_SECRET_KEY=...
CLERK_PUBLISHABLE_KEY=...
ENVIRONMENT=production
AUTH_DISABLED=false       # enable auth in production
PORT=8000
```

### 7c. Update CORS origins

After Railway assigns your app a URL (e.g., `https://your-app.up.railway.app`), add it to `config.py` CORS origins list, rebuild and push.

Or set via environment variable (simpler):
```
CORS_ORIGINS=https://your-app.up.railway.app,http://localhost:3000
```

### 7d. Add Railway Volume for DuckDB (screener)

The DuckDB file needs persistent storage:

1. In Railway → your service → **Volumes** → **Add Volume**
2. Mount path: `/app/agent/screener`
3. Upload `agent/screener/financial_data_new.duckdb` to the volume via Railway shell or by keeping it in the git repo (file is ~50MB, may be fine to commit)

### 7e. Set up Clerk allowed origins

In Clerk dashboard → **Domains**, add your Railway URL: `https://your-app.up.railway.app`

### 7f. Verify deployment

```bash
# Health check
curl https://your-app.up.railway.app/health

# Should return 200 with {"status": "healthy"}
```

---

## 9. Step 8 — Post-Deployment Checklist

Work through these after first deploy:

- [ ] `/health` endpoint returns 200
- [ ] Landing page loads and shows your name in the About modal
- [ ] No references to `stratalens.ai` visible in UI (open browser devtools → Elements → search "stratalens")
- [ ] No references to `stratalens.ai` in page source or API responses
- [ ] Sign in with Clerk works (if `AUTH_DISABLED=false`)
- [ ] Chat page loads and you can ask a question
- [ ] A financial question (e.g., "What are NVDA's risk factors?") returns a real answer (requires data ingestion to be complete)
- [ ] CORS: frontend can reach the backend (no CORS errors in browser console)
- [ ] PostgreSQL has pgvector extension enabled (`SELECT * FROM pg_extension WHERE extname = 'vector';`)
- [ ] Log file shows no startup errors (Railway → Logs tab)

### Quick test for data ingestion

In the Railway shell or locally:
```bash
python -c "
import asyncio
from db.db_utils import get_db
# If this runs without error, DB connection is good
print('DB OK')
"
```

---

## 10. Appendix — Full Environment Variable Reference

Copy this into Railway's Variables tab. Remove comments before pasting.

```env
# === LLM KEYS ===
OPENAI_API_KEY=sk-...                     # Required
CEREBRAS_API_KEY=...                      # Required (primary LLM)
RAG_LLM_PROVIDER=auto                     # auto | cerebras | openai

# === DATA SOURCES ===
API_NINJAS_KEY=...                        # Required (earnings transcripts)
TAVILY_API_KEY=...                        # Optional (news search)

# === DATABASE ===
DATABASE_URL=postgresql://...             # Required — get from Railway PostgreSQL plugin

# === AUTHENTICATION ===
CLERK_SECRET_KEY=sk_live_...             # Required
CLERK_PUBLISHABLE_KEY=pk_live_...        # Required
CLERK_WEBHOOK_SECRET=whsec_...           # Optional but recommended
JWT_SECRET_KEY=<random-32-char-string>   # Required (legacy auth)

# === APP SETTINGS ===
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0
BASE_URL=https://YOUR-APP.up.railway.app
AUTH_DISABLED=false                       # Set false in production

# === CORS ===
CORS_ORIGINS=https://YOUR-APP.up.railway.app,https://YOUR-CUSTOM-DOMAIN.com

# === FEATURE FLAGS ===
ENABLE_REGULAR_AUTH=true
ENABLE_PREMIUM_ONBOARDING=false
ENABLE_LOGIN=true
ENABLE_SELF_SERVE_REGISTRATION=true

# === OPTIONAL ===
REDIS_URL=redis://...                     # Optional — Railway Redis plugin
LOGFIRE_TOKEN=...                         # Optional — structured logging
LOG_LEVEL=INFO
```

### Generating a secure JWT secret key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Common Issues

**Backend starts but chat returns empty answers**
→ Data ingestion hasn't been run. PostgreSQL tables exist but have no embeddings. Run the ingestion scripts from Step 5.

**CORS error in browser console**
→ Your Railway URL isn't in the `CORS_ORIGINS` env var. Add it and redeploy.

**Clerk auth fails with 401**
→ Confirm `CLERK_SECRET_KEY` and `CLERK_PUBLISHABLE_KEY` are set in Railway. Check that your Railway URL is added as an allowed origin in Clerk dashboard.

**pgvector error on startup**
→ The `vector` extension isn't installed in PostgreSQL. Connect to the database and run `CREATE EXTENSION IF NOT EXISTS vector;`

**DuckDB screener returns no results**
→ The `.duckdb` file isn't at `agent/screener/financial_data_new.duckdb`. Either commit it to git or mount it via Railway Volume.

**"StrataLens" still appears in browser**
→ You edited source files but didn't rebuild the frontend. Run `cd frontend && npm run build` and commit `frontend/dist/`.
