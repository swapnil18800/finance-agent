"""
SEC Filings Router

Serves 10-K, 10-Q, and 8-K filing content from the bucket + database.
- Metadata (ticker, fiscal_year, etc.) lives in PostgreSQL
- Document markdown lives in the Railway S3 bucket
"""

import os
import asyncio
import logging
from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from typing import Optional, List
import asyncpg
import boto3
from botocore.config import Config
from app.utils.sec_highlight import inject_sec_highlights

router = APIRouter(prefix="/sec-filings", tags=["sec-filings"])

_pg_vector_url = os.getenv("PG_VECTOR", "").strip() or os.getenv("DATABASE_URL", "").strip()
_pool: asyncpg.Pool | None = None

# S3 client for Railway bucket (lazy-loaded)
_s3 = None
_BUCKET_NAME = os.getenv("RAILWAY_BUCKET_NAME", "").strip()

def _get_s3_client():
    """Lazy-load S3 client only when needed"""
    global _s3
    if _s3 is None:
        endpoint_url = os.getenv("RAILWAY_BUCKET_ENDPOINT", "").strip()
        access_key = os.getenv("RAILWAY_BUCKET_ACCESS_KEY_ID", "").strip()
        secret_key = os.getenv("RAILWAY_BUCKET_SECRET_KEY", "").strip()

        if not endpoint_url or not access_key or not secret_key:
            raise HTTPException(status_code=503, detail="Railway S3 bucket not configured")

        _s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="auto",
            config=Config(signature_version="s3v4"),
        )
    return _s3

# In-memory cache for recently fetched markdown
_markdown_cache: dict[str, str] = {}
_MAX_CACHE = 30


async def _get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        if not _pg_vector_url:
            raise HTTPException(status_code=503, detail="PG_VECTOR database not configured")
        url = _pg_vector_url
        pool_kwargs: dict = dict(min_size=1, max_size=4)
        if "supabase.co" in url or "supabase.com" in url:
            import ssl as _ssl
            ctx = _ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = _ssl.CERT_NONE
            pool_kwargs["ssl"] = ctx
            if "sslmode=" not in url:
                url = url + ("&" if "?" in url else "?") + "sslmode=require"
        _pool = await asyncpg.create_pool(url, **pool_kwargs)
    return _pool


async def _fetch_markdown_from_bucket(bucket_key: str) -> str:
    """Fetch markdown content from the Railway bucket (with in-memory cache)."""
    if bucket_key in _markdown_cache:
        return _markdown_cache[bucket_key]

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: _get_s3_client().get_object(Bucket=_BUCKET_NAME, Key=bucket_key)
    )
    markdown = response["Body"].read().decode("utf-8")

    # Evict oldest if full
    if len(_markdown_cache) >= _MAX_CACHE:
        _markdown_cache.pop(next(iter(_markdown_cache)))
    _markdown_cache[bucket_key] = markdown
    return markdown


class HighlightRequest(BaseModel):
    ticker: str
    filing_type: str
    fiscal_year: int
    quarter: Optional[int] = None
    filing_date: Optional[str] = None
    relevant_chunks: Optional[List[dict]] = None


async def _fetch_filing_meta(ticker: str, filing_type: str, fiscal_year: int) -> dict:
    """Fetch filing metadata row from DB."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT ticker, filing_type, fiscal_year, filing_date,
                   document_length, company_name, bucket_key
            FROM complete_sec_filings
            WHERE UPPER(ticker) = UPPER($1)
              AND filing_type = $2
              AND fiscal_year <= $3
            ORDER BY fiscal_year DESC, filing_date DESC NULLS LAST
            LIMIT 1
            """,
            ticker, filing_type, fiscal_year
        )

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"No {filing_type} filing found for {ticker.upper()} FY{fiscal_year}"
        )
    return dict(row)


def _inject_highlights(markdown: str, chunks: List[dict]) -> str:
    return inject_sec_highlights(markdown, chunks)


@router.get("/{ticker}/available")
async def get_available_filings(ticker: str):
    """List all available filings for a ticker."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT ticker, filing_type, fiscal_year, filing_date, document_length
            FROM complete_sec_filings
            WHERE UPPER(ticker) = UPPER($1)
            ORDER BY fiscal_year DESC, filing_date DESC
            """,
            ticker
        )
    return {
        "ticker": ticker.upper(),
        "filings": [dict(r) for r in rows]
    }


@router.get("/{ticker}/{filing_type}/{fiscal_year}")
async def get_filing(
    ticker: str,
    filing_type: str,
    fiscal_year: int,
    quarter: Optional[int] = Query(None),
    filing_date: Optional[str] = Query(None),
):
    """Fetch a filing — metadata from DB, content from bucket."""
    meta = await _fetch_filing_meta(ticker, filing_type, fiscal_year)

    bucket_key = meta.get("bucket_key")
    if not bucket_key:
        raise HTTPException(status_code=404, detail="Full SEC 10-K coming soon")

    markdown = await _fetch_markdown_from_bucket(bucket_key)

    return ORJSONResponse({
        "success": True,
        "ticker": meta["ticker"],
        "company_name": meta.get("company_name"),
        "filing_type": meta["filing_type"],
        "fiscal_year": meta["fiscal_year"],
        "filing_date": str(meta["filing_date"]) if meta.get("filing_date") else None,
        "document_text": "",
        "document_markdown": markdown,
        "document_length": meta.get("document_length"),
    })


@router.post("/with-highlights")
async def get_filing_with_highlights(req: HighlightRequest):
    """Fetch a filing and inject highlight marks around relevant chunks."""
    meta = await _fetch_filing_meta(req.ticker, req.filing_type, req.fiscal_year)

    bucket_key = meta.get("bucket_key")
    if not bucket_key:
        raise HTTPException(status_code=404, detail="Full SEC 10-K coming soon")

    markdown = await _fetch_markdown_from_bucket(bucket_key)
    highlighted = _inject_highlights(markdown, req.relevant_chunks or [])

    return ORJSONResponse({
        "success": True,
        "ticker": meta["ticker"],
        "company_name": meta.get("company_name"),
        "filing_type": meta["filing_type"],
        "fiscal_year": meta["fiscal_year"],
        "filing_date": str(meta["filing_date"]) if meta.get("filing_date") else None,
        "document_text": "",
        "document_markdown": markdown,
        "highlighted_markdown": highlighted,
        "document_length": meta.get("document_length"),
    })
