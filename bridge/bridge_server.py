from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException

from bridge.bridge_security import BridgeSecurity
from engine.config import get_settings


def get_router(security: BridgeSecurity | None = None) -> APIRouter:
    router = APIRouter(prefix="/bridge", tags=["bridge"])
    security = security or BridgeSecurity()

    @router.post("/sync")
    def sync(payload: Dict[str, str], settings=Depends(get_settings)) -> Dict[str, str]:
        security.assert_token(payload.get("token"))
        return {"status": "synced", "target": payload.get("target"), "environment": settings.environment}

    @router.post("/launch")
    def launch(payload: Dict[str, str]) -> Dict[str, str]:
        security.assert_token(payload.get("token"))
        tool = payload.get("tool")
        if not tool:
            raise HTTPException(status_code=400, detail="tool is required")
        return {"status": "launched", "tool": tool}

    return router

