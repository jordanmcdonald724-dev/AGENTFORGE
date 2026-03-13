"""
Blueprint Editor Routes
=======================
Routes for visual blueprint scripting.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Dict, Any
from core.database import db
from core.utils import serialize_doc
import uuid

router = APIRouter(prefix="/blueprints", tags=["blueprints"])


BLUEPRINT_NODE_TEMPLATES = {
    "event_begin_play": {"type": "event", "name": "Event Begin Play", "color": "red", "outputs": [{"name": "exec", "type": "exec"}]},
    "event_tick": {"type": "event", "name": "Event Tick", "color": "red", "outputs": [{"name": "exec", "type": "exec"}, {"name": "delta_time", "type": "float"}]},
    "event_input": {"type": "event", "name": "Input Event", "color": "red", "properties": {"key": "Space"}, "outputs": [{"name": "pressed", "type": "exec"}, {"name": "released", "type": "exec"}]},
    "branch": {"type": "flow", "name": "Branch", "color": "zinc", "inputs": [{"name": "exec", "type": "exec"}, {"name": "condition", "type": "bool"}], "outputs": [{"name": "true", "type": "exec"}, {"name": "false", "type": "exec"}]},
    "sequence": {"type": "flow", "name": "Sequence", "color": "zinc", "inputs": [{"name": "exec", "type": "exec"}], "outputs": [{"name": "then_0", "type": "exec"}, {"name": "then_1", "type": "exec"}, {"name": "then_2", "type": "exec"}]},
    "for_loop": {"type": "flow", "name": "For Loop", "color": "zinc", "inputs": [{"name": "exec", "type": "exec"}, {"name": "start", "type": "int"}, {"name": "end", "type": "int"}], "outputs": [{"name": "loop_body", "type": "exec"}, {"name": "index", "type": "int"}, {"name": "completed", "type": "exec"}]},
    "delay": {"type": "flow", "name": "Delay", "color": "cyan", "inputs": [{"name": "exec", "type": "exec"}, {"name": "duration", "type": "float"}], "outputs": [{"name": "completed", "type": "exec"}]},
    "print_string": {"type": "function", "name": "Print String", "color": "blue", "inputs": [{"name": "exec", "type": "exec"}, {"name": "string", "type": "string"}], "outputs": [{"name": "exec", "type": "exec"}]},
    "spawn_actor": {"type": "function", "name": "Spawn Actor", "color": "emerald", "inputs": [{"name": "exec", "type": "exec"}, {"name": "class", "type": "class"}, {"name": "location", "type": "vector"}, {"name": "rotation", "type": "rotator"}], "outputs": [{"name": "exec", "type": "exec"}, {"name": "actor", "type": "actor"}]},
    "get_player": {"type": "function", "name": "Get Player Character", "color": "emerald", "inputs": [], "outputs": [{"name": "character", "type": "character"}]},
    "get_location": {"type": "function", "name": "Get Actor Location", "color": "amber", "inputs": [{"name": "target", "type": "actor"}], "outputs": [{"name": "location", "type": "vector"}]},
    "set_location": {"type": "function", "name": "Set Actor Location", "color": "amber", "inputs": [{"name": "exec", "type": "exec"}, {"name": "target", "type": "actor"}, {"name": "location", "type": "vector"}], "outputs": [{"name": "exec", "type": "exec"}]},
    "add_vectors": {"type": "math", "name": "Add (Vector)", "color": "emerald", "inputs": [{"name": "a", "type": "vector"}, {"name": "b", "type": "vector"}], "outputs": [{"name": "result", "type": "vector"}]},
    "multiply_float": {"type": "math", "name": "Multiply (Float)", "color": "emerald", "inputs": [{"name": "a", "type": "float"}, {"name": "b", "type": "float"}], "outputs": [{"name": "result", "type": "float"}]},
    "greater_than": {"type": "logic", "name": "Greater Than", "color": "emerald", "inputs": [{"name": "a", "type": "float"}, {"name": "b", "type": "float"}], "outputs": [{"name": "result", "type": "bool"}]},
}


@router.get("/templates")
async def get_blueprint_templates():
    """Get available blueprint node templates"""
    return BLUEPRINT_NODE_TEMPLATES


@router.post("")
async def create_blueprint(
    project_id: str,
    name: str,
    description: str = "",
    blueprint_type: str = "logic",
    target_engine: str = "unreal"
):
    """Create a new blueprint"""
    blueprint = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "name": name,
        "description": description,
        "blueprint_type": blueprint_type,
        "target_engine": target_engine,
        "nodes": [],
        "connections": [],
        "variables": [],
        "generated_code": None,
        "synced_file_id": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.blueprints.insert_one(blueprint)
    return serialize_doc(blueprint)


@router.get("")
async def get_blueprints(project_id: str):
    """Get all blueprints for a project"""
    return await db.blueprints.find({"project_id": project_id}, {"_id": 0}).to_list(100)


@router.get("/{blueprint_id}")
async def get_blueprint(blueprint_id: str):
    """Get a specific blueprint"""
    blueprint = await db.blueprints.find_one({"id": blueprint_id}, {"_id": 0})
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    return blueprint


@router.patch("/{blueprint_id}")
async def update_blueprint(blueprint_id: str, updates: dict):
    """Update a blueprint"""
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.blueprints.update_one({"id": blueprint_id}, {"$set": updates})
    return {"success": True}


@router.delete("/{blueprint_id}")
async def delete_blueprint(blueprint_id: str):
    """Delete a blueprint"""
    await db.blueprints.delete_one({"id": blueprint_id})
    return {"success": True}


@router.post("/{blueprint_id}/generate-code")
async def generate_code_from_blueprint(blueprint_id: str):
    """Generate code from a blueprint"""
    blueprint = await db.blueprints.find_one({"id": blueprint_id}, {"_id": 0})
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    nodes = blueprint.get("nodes", [])
    connections = blueprint.get("connections", [])
    target = blueprint.get("target_engine", "unreal")
    
    # Generate code based on nodes (simplified)
    code_lines = []
    
    if target == "unreal":
        code_lines.append("// Auto-generated from Blueprint")
        code_lines.append(f"// Blueprint: {blueprint['name']}")
        code_lines.append("")
        code_lines.append("void AMyActor::BeginPlay()")
        code_lines.append("{")
        code_lines.append("    Super::BeginPlay();")
        
        for node in nodes:
            if node.get("type") == "function":
                code_lines.append(f"    // {node.get('name', 'Node')}")
        
        code_lines.append("}")
    else:
        code_lines.append("// Auto-generated from Blueprint")
        code_lines.append(f"// Blueprint: {blueprint['name']}")
        code_lines.append("")
        code_lines.append("using UnityEngine;")
        code_lines.append("")
        code_lines.append("public class GeneratedScript : MonoBehaviour")
        code_lines.append("{")
        code_lines.append("    void Start()")
        code_lines.append("    {")
        
        for node in nodes:
            if node.get("type") == "function":
                code_lines.append(f"        // {node.get('name', 'Node')}")
        
        code_lines.append("    }")
        code_lines.append("}")
    
    generated_code = "\n".join(code_lines)
    
    await db.blueprints.update_one(
        {"id": blueprint_id},
        {"$set": {"generated_code": generated_code, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"code": generated_code, "language": "cpp" if target == "unreal" else "cs"}


@router.post("/{blueprint_id}/sync-from-code")
async def sync_blueprint_from_code(blueprint_id: str, file_id: str):
    """Sync a blueprint from code changes"""
    blueprint = await db.blueprints.find_one({"id": blueprint_id}, {"_id": 0})
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    file = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    await db.blueprints.update_one(
        {"id": blueprint_id},
        {"$set": {
            "synced_file_id": file_id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"success": True, "message": "Blueprint synced with code file"}
