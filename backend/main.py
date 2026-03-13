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

# Ensure the backend directory is in path
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Load environment
from dotenv import load_dotenv
load_dotenv(ROOT_DIR / '.env')

# Import database
from core.database import db, shutdown_db

# Import all routers
from routes.health import router as health_router
from routes.agents import router as agents_router
from routes.projects import router as projects_router
from routes.chat import router as chat_router
from routes.files import router as files_router
from routes.tasks import router as tasks_router
from routes.images import router as images_router
from routes.plans import router as plans_router
from routes.github import router as github_router
from routes.builds import router as builds_router
from routes.collaboration import router as collaboration_router
from routes.sandbox import router as sandbox_router
from routes.command_center import router as command_center_router
from routes.celery_routes import router as celery_router
from routes.k8s import router as k8s_router
from routes.notifications import router as notifications_router
from routes.audio import router as audio_router
from routes.deploy import router as deploy_router
from routes.assets import router as assets_router
from routes.blueprints import router as blueprints_router
from routes.memory import router as memory_router
from routes.chains import router as chains_router
from routes.preview import router as preview_router
from routes.refactor import router as refactor_router
from routes.exploration import router as exploration_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    yield
    await shutdown_db()


# Create app
app = FastAPI(
    title="AgentForge Development Studio",
    description="AI-powered development studio with autonomous build capabilities",
    version="4.5.0",
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

# Include all routers
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(agents_router, prefix="/api", tags=["agents"])
app.include_router(projects_router, prefix="/api", tags=["projects"])
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(files_router, prefix="/api", tags=["files"])
app.include_router(tasks_router, prefix="/api", tags=["tasks"])
app.include_router(images_router, prefix="/api", tags=["images"])
app.include_router(plans_router, prefix="/api", tags=["plans"])
app.include_router(github_router, prefix="/api", tags=["github"])
app.include_router(builds_router, prefix="/api", tags=["builds"])
app.include_router(collaboration_router, prefix="/api", tags=["collaboration"])
app.include_router(sandbox_router, prefix="/api", tags=["sandbox"])
app.include_router(command_center_router, prefix="/api", tags=["command_center"])
app.include_router(celery_router, prefix="/api", tags=["celery"])
app.include_router(k8s_router, prefix="/api", tags=["kubernetes"])
app.include_router(notifications_router, prefix="/api", tags=["notifications"])
app.include_router(audio_router, prefix="/api", tags=["audio"])
app.include_router(deploy_router, prefix="/api", tags=["deploy"])
app.include_router(assets_router, prefix="/api", tags=["assets"])
app.include_router(blueprints_router, prefix="/api", tags=["blueprints"])
app.include_router(memory_router, prefix="/api", tags=["memory"])
app.include_router(chains_router, prefix="/api", tags=["chains"])
app.include_router(preview_router, prefix="/api", tags=["preview"])
app.include_router(refactor_router, prefix="/api", tags=["refactor"])
app.include_router(exploration_router, prefix="/api", tags=["exploration"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
