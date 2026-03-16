"""
Build Operations Routes
=======================
Multi-file refactoring, simulation, war room, and playable demos.
Extracted from server.py as part of refactoring.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from engine.core.database import db
import uuid
import json
import re
import logging

router = APIRouter(tags=["build-operations"])
logger = logging.getLogger(__name__)


# Import required functions from server.py
def get_llm_client():
    from server import llm_client
    return llm_client


async def get_or_create_agents_fn():
    from server import get_or_create_agents
    return await get_or_create_agents()


def serialize_doc(doc):
    from server import serialize_doc
    return serialize_doc(doc)


def extract_code_blocks(content):
    from server import extract_code_blocks
    return extract_code_blocks(content)


def get_models():
    from server import RefactorRequest, SimulationRequest, WarRoomMessage, PlayableDemo, ProjectFile, Blueprint
    return RefactorRequest, SimulationRequest, WarRoomMessage, PlayableDemo, ProjectFile, Blueprint


def get_systems():
    from server import OPEN_WORLD_SYSTEMS, BUILD_STAGES, BLUEPRINT_NODE_TEMPLATES
    return OPEN_WORLD_SYSTEMS, BUILD_STAGES, BLUEPRINT_NODE_TEMPLATES


async def call_agent_fn(agent, messages, context):
    from server import call_agent
    return await call_agent(agent, messages, context)


async def broadcast_to_war_room_fn(project_id, from_agent, content, message_type="progress", build_id=None):
    """Helper to broadcast to war room"""
    _, _, WarRoomMessage, _, _, _ = get_models()
    message = WarRoomMessage(
        project_id=project_id,
        build_id=build_id,
        from_agent=from_agent,
        message_type=message_type,
        content=content
    )
    doc = message.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.war_room.insert_one(doc)
    return doc


# ============ MULTI-FILE REFACTORING ============

@router.post("/refactor/preview")
async def preview_refactor(request: dict):
    """Preview what a refactor would change without applying"""
    project = await db.projects.find_one({"id": request.get("project_id")}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    file_ids = request.get("file_ids", [])
    if file_ids:
        files = await db.files.find({"id": {"$in": file_ids}}, {"_id": 0}).to_list(500)
    else:
        files = await db.files.find({"project_id": request.get("project_id")}, {"_id": 0}).to_list(500)
    
    changes = []
    target = request.get("target", "")
    new_value = request.get("new_value", "")
    refactor_type = request.get("refactor_type", "find_replace")
    
    for f in files:
        original_content = f['content']
        new_content = original_content
        
        if refactor_type == "find_replace":
            if target in original_content:
                new_content = original_content.replace(target, new_value)
        elif refactor_type == "rename":
            patterns = [
                (rf'\bclass\s+{re.escape(target)}\b', f'class {new_value}'),
                (rf'\bdef\s+{re.escape(target)}\b', f'def {new_value}'),
                (rf'\bfunction\s+{re.escape(target)}\b', f'function {new_value}'),
                (rf'\bvoid\s+{re.escape(target)}\s*\(', f'void {new_value}('),
                (rf'\b{re.escape(target)}\s*\(', f'{new_value}('),
                (rf'\b{re.escape(target)}\b', new_value),
            ]
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, new_content)
        
        if new_content != original_content:
            changes.append({
                "file_id": f['id'],
                "filepath": f['filepath'],
                "occurrences": original_content.count(target),
                "preview": {
                    "before": original_content[:500] + ("..." if len(original_content) > 500 else ""),
                    "after": new_content[:500] + ("..." if len(new_content) > 500 else "")
                }
            })
    
    return {
        "refactor_type": refactor_type,
        "target": target,
        "new_value": new_value,
        "files_affected": len(changes),
        "total_files_scanned": len(files),
        "changes": changes
    }


@router.post("/refactor/apply")
async def apply_refactor(request: dict):
    """Apply a refactor across multiple files"""
    preview = await preview_refactor(request)
    
    if preview["files_affected"] == 0:
        return {"success": True, "files_updated": 0, "message": "No changes needed"}
    
    target = request.get("target", "")
    new_value = request.get("new_value", "")
    refactor_type = request.get("refactor_type", "find_replace")
    
    updated_files = []
    for change in preview["changes"]:
        file = await db.files.find_one({"id": change["file_id"]})
        if not file:
            continue
        
        original_content = file['content']
        new_content = original_content
        
        if refactor_type == "find_replace":
            new_content = original_content.replace(target, new_value)
        elif refactor_type == "rename":
            patterns = [
                (rf'\bclass\s+{re.escape(target)}\b', f'class {new_value}'),
                (rf'\bdef\s+{re.escape(target)}\b', f'def {new_value}'),
                (rf'\bfunction\s+{re.escape(target)}\b', f'function {new_value}'),
                (rf'\b{re.escape(target)}\b', new_value),
            ]
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, new_content)
        
        new_version = file.get('version', 1) + 1
        await db.files.update_one(
            {"id": change["file_id"]},
            {"$set": {
                "content": new_content,
                "version": new_version,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        updated_files.append(change["filepath"])
    
    return {
        "success": True,
        "files_updated": len(updated_files),
        "updated_files": updated_files,
        "refactor_type": refactor_type
    }


@router.post("/refactor/ai-suggest")
async def ai_suggest_refactor(project_id: str, description: str):
    """Use AI to suggest refactoring based on natural language"""
    llm_client = get_llm_client()
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(50)
    if not files:
        raise HTTPException(status_code=400, detail="No files to refactor")
    
    agents = await get_or_create_agents_fn()
    lead = next((a for a in agents if a['role'] == 'lead'), agents[0])
    
    file_list = "\n".join([f"- {f['filepath']}: {f['language']}" for f in files])
    
    prompt = f"""Analyze this refactoring request and suggest specific changes:

Request: {description}

Project files:
{file_list}

Respond with a JSON object:
{{
    "refactor_type": "rename|find_replace|extract|reorganize",
    "target": "what to change",
    "new_value": "what to change it to",
    "explanation": "why this change",
    "affected_files": ["list of filepaths"]
}}"""

    try:
        response = llm_client.chat.completions.create(
            model=lead.get('model', 'google/gemini-2.5-flash'),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            suggestion = json.loads(json_match.group())
            return {"success": True, "suggestion": suggestion}
    except Exception as e:
        logger.error(f"AI refactor suggestion failed: {e}")
    
    return {"success": False, "error": "Could not generate suggestion"}


# ============ WAR ROOM ============

@router.get("/war-room/{project_id}")
async def get_war_room_messages(project_id: str, limit: int = 100):
    """Get war room messages for a project"""
    messages = await db.war_room.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    return list(reversed(messages))


@router.post("/war-room/message")
async def post_war_room_message(project_id: str, from_agent: str, content: str, message_type: str = "discussion", to_agent: Optional[str] = None):
    """Post a message to the war room"""
    _, _, WarRoomMessage, _, _, _ = get_models()
    message = WarRoomMessage(
        project_id=project_id,
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=message_type,
        content=content
    )
    doc = message.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.war_room.insert_one(doc)
    return serialize_doc(doc)


@router.delete("/war-room/{project_id}")
async def clear_war_room(project_id: str):
    """Clear war room messages for a project"""
    await db.war_room.delete_many({"project_id": project_id})
    return {"success": True}


# ============ SIMULATION MODE ============

@router.get("/systems/open-world")
async def get_open_world_systems():
    """Get available open world game systems"""
    OPEN_WORLD_SYSTEMS, _, _ = get_systems()
    return list(OPEN_WORLD_SYSTEMS.values())


@router.get("/build-stages/{engine}")
async def get_build_stages(engine: str):
    """Get build stages for an engine"""
    _, BUILD_STAGES, _ = get_systems()
    stages = BUILD_STAGES.get(engine, BUILD_STAGES["unreal"])
    return stages


@router.post("/simulate")
async def run_simulation(request: dict):
    """Dry-run build simulation — estimates time, file count, and feasibility"""
    project_id = request.get("project_id")
    target_engine = request.get("target_engine", "unreal")
    include_systems = request.get("include_systems", [])

    OPEN_WORLD_SYSTEMS, _, _ = get_systems()
    warnings = []
    total_files = 0
    total_minutes = 0

    selected = [OPEN_WORLD_SYSTEMS[s] for s in include_systems if s in OPEN_WORLD_SYSTEMS]

    for system in selected:
        total_files += system.get("files_estimate", 10)
        total_minutes += system.get("time_estimate_minutes", 30)

        # Dependency warnings
        for dep in system.get("dependencies", []):
            dep_included = dep in include_systems
            if not dep_included:
                warnings.append({
                    "severity": "medium",
                    "message": f"{system['name']} depends on {dep} which is not selected",
                    "suggestion": f"Consider adding {dep} to ensure full functionality"
                })

    # Engine-specific warnings
    if target_engine == "unreal" and total_files > 100:
        warnings.append({
            "severity": "low",
            "message": "Large project: consider enabling Incredibuild or distributed compilation",
            "suggestion": "Enable parallel compilation in Build.cs files"
        })
    if len(include_systems) == 0:
        warnings.append({
            "severity": "high",
            "message": "No systems selected",
            "suggestion": "Select at least one game system to simulate"
        })

    # Build time estimate (hours and minutes)
    hours = total_minutes // 60
    mins = total_minutes % 60
    time_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

    # Feasibility score (0-100)
    critical_warnings = [w for w in warnings if w["severity"] == "high"]
    feasibility = max(0, 100 - len(critical_warnings) * 30 - len(warnings) * 5)

    # Architecture summary
    system_names = [s["name"] for s in selected]
    arch_summary = (
        f"{'Unreal Engine 5' if target_engine == 'unreal' else 'Unity'} project with "
        f"{len(selected)} integrated systems: {', '.join(system_names) or 'none selected'}. "
        f"Estimated {total_files} source files across all subsystems."
    )

    return {
        "project_id": project_id,
        "target_engine": target_engine,
        "systems_selected": include_systems,
        "estimated_build_time": time_str,
        "file_count": total_files,
        "total_size_kb": total_files * 12,  # rough estimate: ~12KB per file
        "feasibility_score": feasibility,
        "warnings": warnings,
        "architecture_summary": arch_summary,
        "ready_to_build": len(critical_warnings) == 0 and len(selected) > 0
    }


# ============ PLAYABLE DEMOS ============

@router.get("/demos/{project_id}")
async def get_project_demos(project_id: str):
    """Get all demos for a project"""
    demos = await db.demos.find({"project_id": project_id}, {"_id": 0}).sort("created_at", -1).to_list(10)
    return demos


@router.get("/demos/{project_id}/latest")
async def get_latest_demo(project_id: str):
    """Get the latest demo for a project"""
    demo = await db.demos.find_one(
        {"project_id": project_id, "status": "ready"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    return demo


@router.get("/demos/{project_id}/web")
async def get_web_demo(project_id: str):
    """Get the web demo HTML for embedding"""
    demo = await db.demos.find_one(
        {"project_id": project_id, "status": "ready"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    if not demo or not demo.get("web_demo_html"):
        raise HTTPException(status_code=404, detail="No web demo available")
    
    return HTMLResponse(content=demo["web_demo_html"])


# ============ BLUEPRINTS ============

@router.get("/blueprints/templates")
async def get_blueprint_templates():
    """Get available blueprint node templates"""
    _, _, BLUEPRINT_NODE_TEMPLATES = get_systems()
    return BLUEPRINT_NODE_TEMPLATES


@router.post("/blueprints")
async def create_blueprint(project_id: str, name: str, blueprint_type: str = "logic", target_engine: str = "unreal"):
    """Create a new blueprint"""
    _, _, _, _, _, Blueprint = get_models()
    blueprint = Blueprint(
        project_id=project_id,
        name=name,
        blueprint_type=blueprint_type,
        target_engine=target_engine,
        nodes=[],
        connections=[]
    )
    doc = blueprint.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.blueprints.insert_one(doc)
    return serialize_doc(doc)


@router.get("/blueprints")
async def get_blueprints(project_id: str):
    """Get all blueprints for a project"""
    blueprints = await db.blueprints.find({"project_id": project_id}, {"_id": 0}).to_list(100)
    return blueprints


@router.get("/blueprints/{blueprint_id}")
async def get_blueprint(blueprint_id: str):
    """Get a specific blueprint"""
    blueprint = await db.blueprints.find_one({"id": blueprint_id}, {"_id": 0})
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    return blueprint
