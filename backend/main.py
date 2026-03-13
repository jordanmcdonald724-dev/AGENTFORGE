"""
AgentForge Development Studio API v4.5
Modular FastAPI Application

This is the main entry point that imports all route modules.
The original server.py has been refactored into:
- /core/ - Database, clients, utilities, config
- /models/ - Pydantic models
- /routes/ - API route handlers
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create FastAPI app
app = FastAPI(
    title="AgentForge Development Studio",
    version="4.5.0",
    description="AI-powered development studio with autonomous build capabilities"
)

# Import database for shutdown handler
from core.database import shutdown_db

# Import all route modules
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

# Include all routers with /api prefix
app.include_router(health_router, prefix="/api")
app.include_router(agents_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(files_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(images_router, prefix="/api")
app.include_router(plans_router, prefix="/api")
app.include_router(github_router, prefix="/api")
app.include_router(builds_router, prefix="/api")
app.include_router(collaboration_router, prefix="/api")
app.include_router(sandbox_router, prefix="/api")
app.include_router(command_center_router, prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shutdown handler
@app.on_event("shutdown")
async def shutdown():
    await shutdown_db()
