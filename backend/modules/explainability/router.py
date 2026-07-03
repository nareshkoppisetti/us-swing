"""
File: backend/modules/explainability/router.py
Phase 3 stub — returns 501 with phase info. Implemented in Phase 4/5.
"""
from fastapi import APIRouter, Depends
from dependencies import get_current_user
router = APIRouter(tags=["Explainability"])

@router.get("/")
def explainability_root(_=Depends(get_current_user)):
    return {"success": False, "error": {"code": "NOT_IMPLEMENTED",
        "message": "This module will be implemented in a future phase."}}
