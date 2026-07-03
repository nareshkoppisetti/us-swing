"""
File path: backend/modules/institutional/router.py
Endpoints (per API.md "Institutional Flows", mounted at /api/v1/institutional):
  GET /institutional/dark-pool?symbol=&weeks=
  GET /institutional/13f?symbol=&quarters=
  GET /institutional/insider?symbol=&days=
  GET /institutional/etf-flows?symbol=
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user
from modules.institutional.service import InstitutionalFlowService

router = APIRouter(tags=["Institutional Flows"])


@router.get("/dark-pool")
def get_dark_pool(symbol: str = Query(...), weeks: int = Query(4), db: Session = Depends(get_db), _=Depends(get_current_user)):
    svc = InstitutionalFlowService(db)
    data = svc.get_dark_pool_activity(symbol.upper(), weeks=weeks)
    return {"success": True, "data": data, "meta": {}}


@router.get("/13f")
def get_13f(symbol: str = Query(...), quarters: int = Query(4), db: Session = Depends(get_db), _=Depends(get_current_user)):
    svc = InstitutionalFlowService(db)
    holdings = svc.get_thirteen_f_holdings(symbol.upper(), quarters=quarters)
    return {"success": True, "data": holdings, "meta": {"count": len(holdings)}}


@router.get("/insider")
def get_insider(symbol: str = Query(...), days: int = Query(90), db: Session = Depends(get_db), _=Depends(get_current_user)):
    svc = InstitutionalFlowService(db)
    txns = svc.get_insider_transactions(symbol.upper(), days=days)
    return {"success": True, "data": txns, "meta": {"count": len(txns)}}


@router.get("/etf-flows")
def get_etf_flows(symbol: str = Query(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    svc = InstitutionalFlowService(db)
    data = svc.get_etf_flow_summary(symbol.upper())
    return {"success": True, "data": data, "meta": {}}
