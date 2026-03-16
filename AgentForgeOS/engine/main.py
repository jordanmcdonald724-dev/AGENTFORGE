"""
AgentForge API v4.5 - Modular Entry Point
==========================================

This is the new modular entry point for the AgentForge backend.
All routes are imported from the /routes directory.
All models are imported from the /models directory.
Core utilities are in /core directory.

Usage:
  uvicorn main:app --host 0.0.0.0 --port 8001 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure the AgentForgeOS layers are importable
ROOT_DIR = Path(__file__).parent
OS_ROOT = ROOT_DIR.parent
PY_PATHS = [
    ROOT_DIR,  # engine
    OS_ROOT / "services",
    OS_ROOT / "providers",
    OS_ROOT / "apps",
]
for path in PY_PATHS:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Load environment from centralized config
from dotenv import load_dotenv
load_dotenv(OS_ROOT / "config" / ".env")

# Import database
from engine.core.database import db, shutdown_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    yield
    await shutdown_db()


# Create app
app = FastAPI(
    title="AgentForgeOS",
    description="Layered runtime engine for AgentForgeOS",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
