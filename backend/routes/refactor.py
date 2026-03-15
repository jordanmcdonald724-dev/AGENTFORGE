"""
Refactor Routes
===============
Routes for multi-file refactoring operations.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Optional
from core.database import db
from core.clients import llm_client
from core.utils import serialize_doc
import uuid
import re

router = APIRouter(prefix="/refactor", tags=["refactor"])


# NOTE: /preview, /apply, and /ai-suggest are intentionally removed here.
# They are implemented in routes/build_operations.py (registered after this router).
# Since FastAPI uses first-match routing, the implementations in build_operations.py
# would be shadowed if duplicate routes were defined here with query-param signatures.
# The frontend sends JSON body, so only build_operations.py's dict-body handlers work.

@router.post("/ai-suggest")
async def ai_suggest_refactoring(project_id: str):
    """Get AI suggestions for refactoring"""
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(50)
    
    suggestions = []
    
    for f in files:
        content = f.get("content", "")
        filepath = f.get("filepath", "")
        lines = content.split("\n")
        
        # Check for long files
        if len(lines) > 300:
            suggestions.append({
                "type": "split_file",
                "file": filepath,
                "severity": "medium",
                "message": f"File has {len(lines)} lines. Consider splitting into smaller modules.",
                "suggestion": "Extract related functions into separate files"
            })
        
        # Check for long functions (simplified)
        func_pattern = r'(def |function |async function |const \w+ = (?:async )?\()'
        matches = list(re.finditer(func_pattern, content))
        
        # Check for duplicate code patterns
        if content.count("console.log") > 10:
            suggestions.append({
                "type": "cleanup",
                "file": filepath,
                "severity": "low",
                "message": "Many console.log statements found",
                "suggestion": "Consider using a logging utility or removing debug statements"
            })
    
    return {
        "project_id": project_id,
        "suggestions": suggestions,
        "total": len(suggestions)
    }


@router.get("/systems/open-world")
async def get_open_world_systems():
    """Get available open-world game systems for generation"""
    return {
        "terrain": {"name": "Terrain & World", "files_estimate": 15, "time_estimate_minutes": 45},
        "npc_population": {"name": "NPC Population", "files_estimate": 20, "time_estimate_minutes": 60},
        "quest_system": {"name": "Quest System", "files_estimate": 25, "time_estimate_minutes": 75},
        "vehicle_system": {"name": "Vehicle System", "files_estimate": 30, "time_estimate_minutes": 90},
        "day_night_cycle": {"name": "Day/Night Cycle", "files_estimate": 12, "time_estimate_minutes": 35},
        "combat_system": {"name": "Combat System", "files_estimate": 35, "time_estimate_minutes": 100},
        "crafting_system": {"name": "Crafting System", "files_estimate": 18, "time_estimate_minutes": 50},
        "economy_system": {"name": "Economy System", "files_estimate": 15, "time_estimate_minutes": 40},
        "skill_tree": {"name": "Skill Tree", "files_estimate": 16, "time_estimate_minutes": 45},
        "fast_travel": {"name": "Fast Travel", "files_estimate": 10, "time_estimate_minutes": 25},
        "multiplayer": {"name": "Multiplayer", "files_estimate": 40, "time_estimate_minutes": 120}
    }


@router.get("/build-stages/{engine}")
async def get_build_stages(engine: str):
    """Get build stages for an engine"""
    stages = {
        "unreal": [
            {"name": "Project Setup", "duration_minutes": 30},
            {"name": "Core Framework", "duration_minutes": 90},
            {"name": "Game Systems", "duration_minutes": 180},
            {"name": "AI & NPCs", "duration_minutes": 150},
            {"name": "UI/UX", "duration_minutes": 120},
            {"name": "Polish & Testing", "duration_minutes": 120}
        ],
        "unity": [
            {"name": "Project Setup", "duration_minutes": 30},
            {"name": "Core Framework", "duration_minutes": 90},
            {"name": "Game Systems", "duration_minutes": 180},
            {"name": "AI & NPCs", "duration_minutes": 150},
            {"name": "UI/UX", "duration_minutes": 120},
            {"name": "Polish & Testing", "duration_minutes": 120}
        ]
    }
    
    return stages.get(engine.lower(), stages["unreal"])
