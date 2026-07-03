"""
File path: backend/modules/options/router.py
Endpoints (per API.md "Options Intelligence", mounted at /api/v1/options):
  GET /options/chain?symbol=            — full options chain
  GET /options/put-call-ratio?symbol=   — put/call OI ratio
  GET /options/gamma-exposure?symbol=   — dealer GEX by strike + gamma flip
  GET /options/max-pain?symbol=&expiry= — max pain strike
  GET /options/vix-structure            — VIX term structure
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user
from modules.options.service import OptionsIntelligenceService

router = APIRouter(tags=["Options Intelligence"])


@router.get("/chain")
def get_options_chain(symbol: str = Query(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    svc = OptionsIntelligenceService(db)
    chain = svc.fetch_options_chain(symbol.upper())
    return {"success": True, "data": chain, "meta": {"symbol": symbol.upper(), "count": len(chain)}}


@router.get("/put-call-ratio")
def get_put_call_ratio(symbol: str = Query(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    svc = OptionsIntelligenceService(db)
    ratio = svc.compute_put_call_ratio(symbol.upper())
    return {"success": True, "data": {"symbol": symbol.upper(), "put_call_ratio": ratio}, "meta": {}}


@router.get("/gamma-exposure")
def get_gamma_exposure(symbol: str = Query(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    svc = OptionsIntelligenceService(db)
    gex = svc.compute_gamma_exposure(symbol.upper())
    return {"success": True, "data": gex, "meta": {}}


@router.get("/max-pain")
def get_max_pain(symbol: str = Query(...), expiry: str = Query(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    svc = OptionsIntelligenceService(db)
    strike = svc.compute_max_pain(symbol.upper(), expiry)
    return {"success": True, "data": {"symbol": symbol.upper(), "expiry": expiry, "max_pain_strike": strike}, "meta": {}}


@router.get("/vix-structure")
def get_vix_structure(db: Session = Depends(get_db), _=Depends(get_current_user)):
    svc = OptionsIntelligenceService(db)
    return {"success": True, "data": svc.get_vix_term_structure(), "meta": {}}
