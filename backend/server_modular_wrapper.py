"""
AgentForge Development Studio API v4.5
=======================================

This file serves as the entry point for the FastAPI application.
The codebase has been refactored into a modular structure:

/app/backend/
├── core/
│   ├── database.py      # MongoDB connection
│   ├── clients.py       # LLM and TTS clients
│   ├── config.py        # Constants and configuration
│   └── utils.py         # Helper functions
├── models/
│   ├── base.py          # Core models (Agent, Project, Task, etc.)
│   ├── project.py       # Request models
│   ├── agent.py         # Dynamic agent models
│   ├── build.py         # Build-related models
│   ├── collaboration.py # Collaboration models
│   ├── sandbox.py       # Sandbox and asset models
│   ├── autopsy.py       # Project autopsy models
│   └── v45_features.py  # v4.5 feature models
├── routes/
│   ├── health.py        # Health check endpoints
│   ├── agents.py        # Agent CRUD
│   ├── projects.py      # Project CRUD
│   ├── chat.py          # Chat and streaming
│   ├── files.py         # File management
│   ├── tasks.py         # Task management
│   ├── images.py        # Image generation
│   ├── plans.py         # Project plans
│   ├── github.py        # GitHub integration
│   ├── builds.py        # Build management
│   ├── collaboration.py # Real-time collaboration
│   ├── sandbox.py       # Sandbox and assets
│   └── command_center.py # v4.0/v4.5 features
└── server.py            # This file (entry point)

For full backward compatibility, this file imports and re-exports
the FastAPI app from the modular main.py.
"""

import sys
from pathlib import Path

# Ensure the backend directory is in the path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import the app from the modular main.py
from main import app

# Re-export for uvicorn
__all__ = ["app"]
