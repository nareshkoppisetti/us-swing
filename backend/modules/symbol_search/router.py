"""
File path: backend/modules/symbol_search/router.py
Purpose: FastAPI router for symbol search and lookup.
         Registered at prefix /api/v1/symbols in main.py (no prefix here per BUILD_PLAN Rule 10).

Endpoints:
  GET /symbols/search?q={query}&limit=10  — autocomplete symbol search
  GET /symbols/{ticker}                   — get symbol details
  GET /symbols/                           — list all symbols (paginated)
"""
import logging
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user
from modules.symbol_search.service import SymbolSearchService
from modules.symbol_search.schemas import SymbolSearchResponse, SymbolSearchResult

logger = logging.getLogger("app")

router = APIRouter(tags=["Symbol Search"])


def _build_meta() -> dict:
    return {"request_id": str(uuid4()), "timestamp": datetime.utcnow().isoformat() + "Z", "version": "1.0"}


@router.get("/search")
def search_symbols(
    q: str = Query(..., min_length=1, description="Search query: ticker or company name"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Search symbols by ticker prefix or company name (case-insensitive).
    Returns up to `limit` matching symbols, grouped by asset type.
    """
    svc = SymbolSearchService(db=db)
    results = svc.search(q, limit=limit)

    return {
        "success": True,
        "data": SymbolSearchResponse(
            query=q,
            results=[SymbolSearchResult(**r) for r in results],
            total=len(results),
        ).model_dump(),
        "meta": _build_meta(),
    }


@router.get("/")
def list_symbols(
    symbol_type: str = Query(None, description="Filter by type: stock | etf | futures | index"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """List all active symbols, optionally filtered by type, with pagination."""
    svc = SymbolSearchService(db=db)
    result = svc.list_symbols(symbol_type=symbol_type, page=page, page_size=page_size)
    return {
        "success": True,
        "data": result["items"],
        "meta": _build_meta(),
        "pagination": {
            "page": result["page"],
            "per_page": result["page_size"],
            "total": result["total"],
            "total_pages": max(1, (result["total"] + page_size - 1) // page_size),
        },
    }


@router.get("/{ticker}")
def get_symbol(
    ticker: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Get details for a specific ticker symbol."""
    svc = SymbolSearchService(db=db)
    symbol = svc.get_symbol(ticker.upper())
    if not symbol:
        raise HTTPException(status_code=404, detail=f"Symbol '{ticker}' not found")
    return {"success": True, "data": symbol, "meta": _build_meta()}
