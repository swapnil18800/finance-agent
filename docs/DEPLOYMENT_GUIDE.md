# Complete Deployment Guide — Finance Agent

> **Goal:** Take this forked repo, rebrand it as your own, and deploy it live on Railway so recruiters can see a fully working AI equity research platform under your name.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Clone & Local Setup](#2-clone--local-setup)
3. [Create All Required Accounts](#3-create-all-required-accounts)
4. [Set Up PostgreSQL with pgvector](#4-set-up-postgresql-with-pgvector)
5. [Configure Environment Variables](#5-configure-environment-variables)
6. [Rebrand the Codebase](#6-rebrand-the-codebase)
7. [Build the Frontend](#7-build-the-frontend)
8. [Test Locally](#8-test-locally)
9. [Run Data Ingestion](#9-run-data-ingestion)
10. [Deploy to Railway](#10-deploy-to-railway)
11. [Post-Deployment Verification](#11-post-deployment-verification)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Prerequisites

Install these on your machine before anything else.

### Python 3.11

Download from python.org/downloads — pick **Python 3.11.x** (not 3.12+, some ML packages still lag).

During install on Windows:
- Check **"Add Python to PATH"**
- Check **"pip"**

Verify:
```powershell
python --version
# Expected: Python 3.11.x

pip --version
# Expected: pip 23.x or higher
```

### Node.js 18+

Download from nodejs.org — pick the **LTS version**.

Verify:
```powershell
node --version
# Expected: v18.x or v20.x

npm --version
# Expected: 9.x or 10.x
```

### Git

Download from git-scm.com if not installed.

```powershell
git --version
# Expected: git version 2.x
```

### Railway CLI (for deployment later)

```powershell
npm install -g @railway/cli
railway --version
```

---

## 2. Clone & Local Setup

### 2a. Clone your forked repo

```powershell
cd C:\Users\HP\Desktop\ai-projects
git clone https://github.com/swapnil18800/finance-agent.git
cd finance-agent
```

### 2b. Create a Python virtual environment

Always use a venv — never install packages globally.

```powershell
python -m venv venv
```

### 2c. Activate the virtual environment

```powershell
# Windows PowerShell:
venv\Scripts\activate

# You should see (venv) at the start of your prompt:
# (venv) PS C:\Users\HP\Desktop\ai-projects\finance-agent>
```

> Every time you open a new terminal to work on this project, run the activate command first.

### 2d. Install Python dependencies

```powershell
pip install -r requirements.txt
```

This will take 5–10 minutes — sentence-transformers pulls PyTorch.

> If you get errors on Windows about `psycopg2-binary`, run:
> ```powershell
> pip install psycopg2-binary --only-binary :all:
> ```

### 2e. Verify install

```powershell
pip list | findstr "fastapi langchain openai"
# Should show all three with version numbers
```

---

## 3. Create All Required Accounts

Do these in parallel while waiting for installs. Open all in separate tabs.

### 3a. OpenAI — LLM fallback + embeddings

1. Go to **platform.openai.com**
2. Sign up / Log in
3. Go to **API Keys** → **Create new secret key**
4. Name it `finance-agent`
5. Copy the key — it starts with `sk-proj-...` or `sk-...`
6. Save it somewhere — **you can only see it once**
7. Add billing at **Settings → Billing** (add $5–10 to start)

### 3b. Cerebras — Primary LLM (fast inference)

1. Go to **cloud.cerebras.ai**
2. Sign up with GitHub or email
3. Go to **API Keys** → **Create API Key**
4. Copy the key

> Cerebras is the primary LLM (Qwen-3-235B) — much faster than OpenAI for this use case. Has a free tier.

### 3c. API Ninjas — Earnings transcripts

1. Go to **api-ninjas.com**
2. Sign up → go to **My Account**
3. Your API key is shown on the dashboard
4. Copy it

> Free tier: 10,000 API calls/month. Transcripts for ~500 companies need significant quota — plan accordingly.

### 3d. Clerk — User authentication

1. Go to **dashboard.clerk.com**
2. Click **Create application**
3. Name it (e.g., `Finance Agent`)
4. Choose sign-in options: check **Email** and optionally **Google**
5. Click **Create application**
6. You'll land on the **API Keys** page — copy both:
   - **Publishable key** → starts with `pk_test_...`
   - **Secret key** → starts with `sk_test_...`
7. Keep this tab open — you'll need to add your Railway URL later

### 3e. Tavily — Real-time news search (optional)

1. Go to **tavily.com**
2. Sign up → go to **API Keys**
3. Copy your API key

> Without Tavily, the news search feature is disabled but everything else works.

### 3f. Railway — Hosting

1. Go to **railway.app**
2. Sign up with GitHub (recommended — easier repo linking)
3. You'll need the **Hobby plan ($5/mo)** for the memory required

> Do NOT set up your Railway project yet — you'll do that in Step 10. Just create the account now.

---

## 4. Set Up PostgreSQL with pgvector

The app needs PostgreSQL with the `pgvector` extension for storing embeddings. Two options:

### Option A: Supabase (recommended — free tier, easy)

#### 4a. Create project

1. Go to **supabase.com** → **New Project**
2. Name it `finance-agent`
3. Set a database password — **save this password**
4. Select the region closest to you
5. Wait ~2 minutes for provisioning

#### 4b. Enable pgvector

1. Go to your project → **SQL Editor** (left sidebar)
2. Click **New query**
3. Paste and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. Click **Run** — should show "Success"

#### 4c. Get connection string

1. Go to **Settings** (gear icon) → **Database**
2. Scroll to **Connection string**
3. Select **URI** tab
4. Copy the string — looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with the password you set in step 4a

> **Save this** — this is your `DATABASE_URL`

---

### Option B: Railway PostgreSQL (if you prefer everything in one place)

Skip this if using Supabase. Come back here after setting up Railway in Step 10.

1. In your Railway project → click **+ New** → **Database** → **Add PostgreSQL**
2. Once provisioned, click the PostgreSQL service → **Variables** tab
3. Copy the `DATABASE_URL` value
4. Connect via Railway shell and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

---

## 5. Configure Environment Variables

### 5a. Create your .env file

```powershell
copy .env.example .env
```

### 5b. Open and fill it in

Open `.env` in VS Code or Notepad:

```powershell
code .env
# or
notepad .env
```

Fill in every value:

```env
# === LLM ===
OPENAI_API_KEY=sk-proj-your-key-here
CEREBRAS_API_KEY=your-cerebras-key-here
RAG_LLM_PROVIDER=auto

# === DATA ===
API_NINJAS_KEY=your-api-ninjas-key-here
TAVILY_API_KEY=your-tavily-key-here

# === DATABASE ===
DATABASE_URL=postgresql://postgres:yourpassword@db.xxxx.supabase.co:5432/postgres

# === AUTH ===
CLERK_SECRET_KEY=sk_test_your-clerk-secret-key
CLERK_PUBLISHABLE_KEY=pk_test_your-clerk-publishable-key
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your-clerk-publishable-key
JWT_SECRET_KEY=run-python-command-below-to-generate

# === APP ===
ENVIRONMENT=development
PORT=8000
HOST=0.0.0.0
BASE_URL=http://localhost:8000
AUTH_DISABLED=true

# === LOGGING ===
LOG_LEVEL=INFO
```

### 5c. Generate a JWT secret key

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as `JWT_SECRET_KEY` in your `.env`.

### 5d. Create frontend .env

```powershell
# Create the file
echo VITE_CLERK_PUBLISHABLE_KEY=pk_test_your-clerk-publishable-key > frontend\.env
```

Or create `frontend/.env` manually with:
```env
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your-clerk-publishable-key
```

---

## 6. Rebrand the Codebase

**Do this before pushing to GitHub.** These are every place the original author's name and brand appear.

### 6a. AboutModal.tsx — most visible, do this first

Open `frontend/src/components/AboutModal.tsx`

**Find and replace lines 74–93:**

```tsx
// FIND THIS:
              <div className="mb-6">
                <p className="text-sm text-slate-500 mb-1">Created by</p>
                <p className="text-lg font-semibold text-slate-900">Hrishikesh Kamath</p>
              </div>

              <a
                href="https://kamathhrishi.github.io"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-[#0a1628] hover:text-[#1e293b] font-medium transition-colors mb-6"
              >
                Visit kamathhrishi.github.io
                <ExternalLink className="w-4 h-4" />
              </a>

              <div className="p-4 bg-slate-50 rounded-xl">
                <p className="text-sm text-slate-600 leading-relaxed">
                  I spent several months building StrataLens as a product, learning extensively about the financial industry and working with analysts. While I've decided to open source it rather than continue commercial development, it was an incredibly valuable journey. Feel free to use and contribute!
                </p>
              </div>

// REPLACE WITH (fill in YOUR details):
              <div className="mb-6">
                <p className="text-sm text-slate-500 mb-1">Created by</p>
                <p className="text-lg font-semibold text-slate-900">YOUR FULL NAME</p>
              </div>

              <a
                href="https://your-portfolio.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-[#0a1628] hover:text-[#1e293b] font-medium transition-colors mb-6"
              >
                Visit your-portfolio.com
                <ExternalLink className="w-4 h-4" />
              </a>

              <div className="p-4 bg-slate-50 rounded-xl">
                <p className="text-sm text-slate-600 leading-relaxed">
                  Built as a full-stack AI project combining RAG, pgvector semantic search, and
                  real-time financial data APIs to help analysts research SEC filings and earnings
                  calls faster. Stack: FastAPI, React, PostgreSQL, LangChain, Cerebras.
                </p>
              </div>
```

**Also change the modal title on line 57:**
```tsx
// FIND:
<h2 className="text-xl font-bold text-slate-900">About StrataLens</h2>
// REPLACE:
<h2 className="text-xl font-bold text-slate-900">About YOUR APP NAME</h2>
```

### 6b. LandingPage.tsx — brand name in UI

Open `frontend/src/pages/LandingPage.tsx`

Do a **Find & Replace** (Ctrl+H in VS Code):
- Find: `StrataLens`
- Replace with: `YOUR APP NAME`

Key spots to verify after replacing:
- Line ~163: navbar brand text
- Line ~167: nav link `Why StrataLens`
- Line ~663: comparison card heading
- Line ~762: footer text

### 6c. Rename the logo component (optional but clean)

```powershell
# Rename the file
ren frontend\src\components\StrataLensLogo.tsx AppLogo.tsx
```

Then in the renamed file, change the function name:
```tsx
// FIND:
export default function StrataLensLogo(
// REPLACE:
export default function AppLogo(
```

Update all 3 files that import it:
- `frontend/src/components/AboutModal.tsx`
- `frontend/src/pages/LandingPage.tsx`
- `frontend/src/components/Navbar.tsx`

In each, change:
```tsx
// FIND:
import StrataLensLogo from './StrataLensLogo'
// REPLACE:
import AppLogo from './AppLogo'
```

And change all usages from `<StrataLensLogo` to `<AppLogo`.

### 6d. config.py — backend config

Open `config.py` and make these changes:

**Line 64 — admin email:**
```python
ADMIN_EMAIL: str = "your-email@gmail.com"
```

**Line 106 — DB app name:**
```python
APPLICATION_NAME: str = "finance_agent_fastapi"
```

**Line 147 — log file:**
```python
MAIN_LOG_FILE: str = "app.log"
```

**Lines 168–178 — CORS (update after you get Railway URL):**
```python
DEFAULT_CORS_ORIGINS: str = (
    "https://YOUR-APP.up.railway.app,"
    "http://localhost:3000,"
    "http://localhost:8000,"
    "http://127.0.0.1:3000,"
    "http://127.0.0.1:8000,"
    "http://localhost:5000,"
    "http://127.0.0.1:5000"
)
```

**Lines 237–239 — app title:**
```python
TITLE: str = "Finance Agent API"
DESCRIPTION: str = "AI-powered financial research platform"
VERSION: str = "1.0.0"
```

### 6e. README.md — remove original author links

Open `README.md` and remove/replace:
```markdown
# FIND AND REMOVE these lines:
**Live Platform:** [www.stratalens.ai](https://www.stratalens.ai)
**10K filings agent blogpost:** [Blogpost](https://substack.com/home/post/p-181608263)

# REPLACE WITH:
**Live Platform:** [your-app.up.railway.app](https://your-app.up.railway.app)
```

### 6f. Set your git identity

```powershell
git config user.name "Your Name"
git config user.email "your-email@gmail.com"
```

### 6g. Commit all rebranding changes

```powershell
git add .
git commit -m "Rebrand: update author info, app name, CORS config"
```

---

## 7. Build the Frontend

### 7a. Install Node dependencies

```powershell
cd frontend
npm install
```

This takes 1–2 minutes.

### 7b. Build

```powershell
npm run build
```

Expected output:
```
✓ built in Xs
dist/index.html
dist/assets/index-[hash].js
dist/assets/index-[hash].css
```

### 7c. Go back to root

```powershell
cd ..
```

### 7d. Make sure frontend/dist is committed to git

Check `.gitignore`:
```powershell
type .gitignore | findstr "dist"
```

If `dist` is ignored, add an exception:
```powershell
echo !frontend/dist >> .gitignore
```

Commit the built frontend:
```powershell
git add frontend/dist
git add .gitignore
git commit -m "Build frontend, ensure dist is tracked"
```

---

## 8. Test Locally

### 8a. Start the backend

```powershell
# Make sure venv is activated first
venv\Scripts\activate

uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Watch the startup logs. Expected sequence:
```
INFO: Database pool initialized
INFO: Admin user verified
INFO: RAG agent initialized
INFO: Application startup complete
INFO: Uvicorn running on http://0.0.0.0:8000
```

If you see any ERROR lines, check the Troubleshooting section.

### 8b. Verify health endpoint

Open a new terminal and run:
```powershell
curl http://localhost:8000/health
```

Expected:
```json
{"status": "healthy"}
```

Or just open `http://localhost:8000/health` in your browser.

### 8c. Open the app

Go to `http://localhost:8000` in your browser.

You should see:
- Landing page with your new app name
- About modal showing your name
- No "StrataLens" references visible

### 8d. Test the chat (basic)

1. Click **Open Platform** or navigate to `/chat`
2. Type a question like: `What are NVDA's risk factors?`
3. It will return empty or say no data found — **this is expected** until data ingestion (Step 9)

---

## 9. Run Data Ingestion

**This is the most time-consuming step.** This populates your PostgreSQL database with earnings transcripts and SEC filings so the RAG system has data to search.

> Make sure your `DATABASE_URL` and `API_NINJAS_KEY` are set in `.env` before running these.

### 9a. Download earnings transcripts

```powershell
python agent/rag/data_ingestion/download_transcripts.py
```

- Downloads earnings call transcripts for ~500 tech companies
- Uses your API Ninjas key
- Takes **30–60 minutes**
- Stores raw transcripts locally

> Monitor your API Ninjas quota at api-ninjas.com/profile — free tier is 10k calls/month.

### 9b. Generate embeddings and store in PostgreSQL

```powershell
python agent/rag/data_ingestion/create_and_store_embeddings.py
```

- Generates 384-dimensional vector embeddings using `all-MiniLM-L6-v2`
- Stores chunks + embeddings in your PostgreSQL database
- Takes **1–4 hours** depending on your CPU/RAM
- Needs at least **8GB RAM** — close other apps

> If this crashes or runs out of memory, re-run it — it resumes from where it stopped.

### 9c. Ingest SEC 10-K filings

```powershell
python agent/rag/data_ingestion/ingest_sec_filings.py
```

- Downloads 10-K filings from SEC EDGAR (free, no key needed)
- Processes and stores them in PostgreSQL
- Takes **30–90 minutes**

### 9d. Verify data is in the database

Connect to your Supabase project → **Table Editor** and check:
- `transcript_chunks` table has rows
- `ten_k_chunks` table has rows

Or run in the terminal:
```powershell
python -c "
import asyncio, asyncpg, os
from dotenv import load_dotenv
load_dotenv()
async def check():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    t = await conn.fetchval('SELECT COUNT(*) FROM transcript_chunks')
    k = await conn.fetchval('SELECT COUNT(*) FROM ten_k_chunks')
    print(f'Transcripts: {t} chunks')
    print(f'10-K filings: {k} chunks')
    await conn.close()
asyncio.run(check())
"
```

### 9e. Test RAG is working

Start the backend and ask a real question:
```
What are NVDA's main risk factors from their latest 10-K?
```

You should now get a real answer with citations.

---

## 10. Deploy to Railway

### 10a. Push your repo to GitHub

Make sure all your changes are committed and pushed:
```powershell
git push origin main
```

### 10b. Create Railway project

1. Go to **railway.app** → **New Project**
2. Click **Deploy from GitHub repo**
3. Authorize Railway to access your GitHub
4. Select `swapnil18800/finance-agent`
5. Railway detects `Procfile` automatically and starts building

### 10c. Note your Railway URL

After the first deploy starts, Railway assigns you a URL like:
`https://finance-agent-production-xxxx.up.railway.app`

Copy this URL — you need it for CORS and Clerk config.

### 10d. Add PostgreSQL (if not using Supabase)

If using Supabase, skip this. If using Railway PostgreSQL:
1. In your project → **+ New** → **Database** → **PostgreSQL**
2. Railway links it automatically and sets `DATABASE_URL`
3. Connect via Railway shell → run `CREATE EXTENSION IF NOT EXISTS vector;`

### 10e. Set environment variables in Railway

In your Railway service → **Variables** tab → click **Raw Editor** and paste:

```env
OPENAI_API_KEY=sk-proj-your-key
CEREBRAS_API_KEY=your-cerebras-key
RAG_LLM_PROVIDER=auto
API_NINJAS_KEY=your-api-ninjas-key
TAVILY_API_KEY=your-tavily-key
DATABASE_URL=your-supabase-or-railway-db-url
CLERK_SECRET_KEY=sk_live_your-clerk-secret
CLERK_PUBLISHABLE_KEY=pk_live_your-clerk-publishable
VITE_CLERK_PUBLISHABLE_KEY=pk_live_your-clerk-publishable
JWT_SECRET_KEY=your-generated-jwt-secret
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0
BASE_URL=https://your-app.up.railway.app
AUTH_DISABLED=false
CORS_ORIGINS=https://your-app.up.railway.app
LOG_LEVEL=INFO
ENABLE_REGULAR_AUTH=true
ENABLE_LOGIN=true
ENABLE_SELF_SERVE_REGISTRATION=true
```

> Replace all placeholder values with your actual keys.

> **Important:** Use `pk_live_` and `sk_live_` Clerk keys for production (not `pk_test_`). Get them from Clerk dashboard → **API Keys** → switch to **Production** instance.

### 10f. Update CORS in config.py

Now that you have your Railway URL, update `config.py` line 168:
```python
DEFAULT_CORS_ORIGINS: str = (
    "https://your-app-name.up.railway.app,"
    "http://localhost:3000,"
    "http://localhost:8000,"
    "http://127.0.0.1:3000,"
    "http://127.0.0.1:8000"
)
```

Commit and push:
```powershell
git add config.py
git commit -m "Update CORS for Railway deployment URL"
git push origin main
```

### 10g. Add Clerk allowed origin

1. Go to **Clerk Dashboard** → your app
2. Go to **Domains** (or **Allowed Origins**)
3. Add: `https://your-app.up.railway.app`
4. Save

### 10h. Add Railway Volume for DuckDB

The screener needs the DuckDB file on persistent storage:

1. Railway → your service → **Volumes** → **Mount a Volume**
2. Set mount path: `/app/agent/screener`
3. In Railway shell, copy the file:
   ```bash
   # The file should already be there if committed to git
   ls /app/agent/screener/financial_data_new.duckdb
   ```

If the file is under 100MB, the easiest approach is to just commit it to your repo:
```powershell
git add -f agent/screener/financial_data_new.duckdb
git commit -m "Include DuckDB screener data"
git push origin main
```

### 10i. Watch the deployment logs

In Railway → your service → **Deployments** → click the latest → **View Logs**

Wait for:
```
INFO: Application startup complete
INFO: Uvicorn running on http://0.0.0.0:8000
```

If you see errors, check the Troubleshooting section.

---

## 11. Post-Deployment Verification

Work through this checklist after Railway shows the deployment is live.

### 11a. Health check
```powershell
curl https://your-app.up.railway.app/health
# Expected: {"status": "healthy"}
```

### 11b. Landing page
- Go to `https://your-app.up.railway.app`
- Verify your name shows in the About modal
- Open browser DevTools → Elements → search "stratalens" or "Hrishikesh"
- There should be zero results

### 11c. Auth flow
1. Click Sign Up
2. Create a test account
3. Verify you can log in and reach the chat page

### 11d. Chat works with data
Ask: `What are the risk factors for NVDA?`
- Should return an answer with citations
- Should NOT say "no data found"

### 11e. CORS check
- Open browser DevTools → Console
- Look for any red CORS errors
- If you see them, your `CORS_ORIGINS` env var is missing the production URL

### 11f. Screener works
- Navigate to `/screener`
- Should load financial data from DuckDB
- If blank, the DuckDB file isn't on the Railway Volume

---

## 12. Troubleshooting

### "pgvector extension not found"
```sql
-- Run this in Supabase SQL Editor or Railway shell:
CREATE EXTENSION IF NOT EXISTS vector;
```

### "CORS error" in browser console
In Railway Variables, set:
```
CORS_ORIGINS=https://your-app.up.railway.app
```

### "401 Unauthorized" on all requests
- `AUTH_DISABLED` is set to `false` but Clerk keys are wrong
- Verify `CLERK_SECRET_KEY` and `CLERK_PUBLISHABLE_KEY` are the **production** keys (not test)
- Verify your Railway URL is added to Clerk's allowed origins

### Chat returns empty answers
Data ingestion hasn't been run, or it ran against a different database.
- Check `DATABASE_URL` points to the same DB in both `.env` (local) and Railway Variables
- Run `python agent/rag/data_ingestion/create_and_store_embeddings.py` locally pointing to the production DB

### Railway build fails
Check logs for the error. Common causes:
- Missing environment variable (Railway shows which one)
- `frontend/dist` not committed — rebuild and commit it
- Memory limit during build — upgrade Railway plan

### "Module not found" errors on startup
```powershell
pip install -r requirements.txt
```
Some package was missed. Check the error for which module is missing and add it to requirements.txt.

### Screener page is blank
The DuckDB file isn't found. Either:
1. Commit it directly: `git add -f agent/screener/financial_data_new.duckdb`
2. Or mount a Railway Volume at `/app/agent/screener`

### Frontend shows old "StrataLens" branding
You edited the source files but didn't rebuild:
```powershell
cd frontend
npm run build
cd ..
git add frontend/dist
git commit -m "Rebuild frontend with rebranding"
git push origin main
```

---

## Quick Reference — All Keys You Need

| Key | Where | Required? |
|---|---|---|
| `OPENAI_API_KEY` | platform.openai.com → API Keys | Yes |
| `CEREBRAS_API_KEY` | cloud.cerebras.ai → API Keys | Yes |
| `API_NINJAS_KEY` | api-ninjas.com → My Account | Yes |
| `DATABASE_URL` | Supabase → Settings → Database → URI | Yes |
| `CLERK_SECRET_KEY` | dashboard.clerk.com → API Keys | Yes (prod) |
| `CLERK_PUBLISHABLE_KEY` | dashboard.clerk.com → API Keys | Yes (prod) |
| `JWT_SECRET_KEY` | Generate with python command | Yes |
| `TAVILY_API_KEY` | tavily.com → API Keys | No |
| `LOGFIRE_TOKEN` | logfire.pydantic.dev | No |
| `REDIS_URL` | Railway Redis plugin | No |

---

*Estimated total time from zero to live: 4–8 hours (mostly data ingestion)*
