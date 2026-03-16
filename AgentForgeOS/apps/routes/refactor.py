"""
Refactor Routes
===============
Routes for multi-file refactoring operations.

NOTE: /preview, /apply are implemented in routes/build_operations.py (JSON-body versions).
      They are intentionally NOT duplicated here to avoid FastAPI first-match shadowing.
"""

from fastapi import APIRouter
from engine.core.database import db
import re

router = APIRouter(prefix="/refactor", tags=["refactor"])


@router.get("/ai-suggest")
async def ai_suggest_refactoring(project_id: str):
    """Heuristic code suggestions for a project (fast, no LLM).
    For AI-powered suggestions use POST /refactor/ai-suggest in build_operations router."""
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(50)
    suggestions = []

    for f in files:
        content  = f.get("content", "")
        filepath = f.get("filepath", "")
        lines    = content.split("\n")

        if len(lines) > 300:
            suggestions.append({
                "type": "split_file", "file": filepath, "severity": "medium",
                "message": f"File has {len(lines)} lines — consider splitting into smaller modules.",
                "suggestion": "Extract related functions into separate files"
            })

        if content.count("console.log") > 10:
            suggestions.append({
                "type": "cleanup", "file": filepath, "severity": "low",
                "message": "Many console.log statements found",
                "suggestion": "Remove debug statements or use a logging utility"
            })

        # Detect TODO/FIXME density
        todo_count = len(re.findall(r'\b(TODO|FIXME|HACK|XXX)\b', content))
        if todo_count > 5:
            suggestions.append({
                "type": "tech_debt", "file": filepath, "severity": "low",
                "message": f"{todo_count} TODO/FIXME markers found",
                "suggestion": "Address outstanding technical debt items"
            })

    return {"project_id": project_id, "suggestions": suggestions, "total": len(suggestions)}
