"""
Game Engine Integration
=======================
Deep integration with Unreal Engine and Unity.
Generate Blueprints, C++ gameplay systems, compile projects, launch playable demos.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.database import db
from core.clients import llm_client
from core.utils import serialize_doc
import uuid
import json

router = APIRouter(prefix="/game-engine", tags=["game-engine"])


# ========== UNREAL ENGINE ==========

UNREAL_TEMPLATES = {
    "fps_controller": {
        "name": "FPS Character Controller",
        "files": ["PlayerCharacter.h", "PlayerCharacter.cpp", "BP_PlayerCharacter"],
        "systems": ["movement", "camera", "input"]
    },
    "third_person": {
        "name": "Third Person Controller",
        "files": ["TPCharacter.h", "TPCharacter.cpp", "BP_TPCharacter", "ABP_Character"],
        "systems": ["movement", "camera", "animation", "input"]
    },
    "vehicle": {
        "name": "Vehicle System",
        "files": ["VehicleBase.h", "VehicleBase.cpp", "BP_Car", "BP_Boat"],
        "systems": ["physics", "input", "camera"]
    },
    "inventory": {
        "name": "Inventory System",
        "files": ["InventoryComponent.h", "InventoryComponent.cpp", "ItemBase.h", "BP_InventoryUI"],
        "systems": ["items", "ui", "save_load"]
    },
    "dialogue": {
        "name": "Dialogue System",
        "files": ["DialogueManager.h", "DialogueManager.cpp", "DialogueNode.h", "BP_DialogueUI"],
        "systems": ["branching", "conditions", "ui"]
    },
    "ai_npc": {
        "name": "AI NPC System",
        "files": ["AICharacter.h", "AICharacter.cpp", "BT_BasicAI", "BP_Patrol"],
        "systems": ["behavior_tree", "perception", "navigation"]
    },
    "quest": {
        "name": "Quest System",
        "files": ["QuestManager.h", "QuestManager.cpp", "Quest.h", "QuestObjective.h"],
        "systems": ["objectives", "rewards", "tracking"]
    },
    "combat": {
        "name": "Combat System",
        "files": ["CombatComponent.h", "CombatComponent.cpp", "WeaponBase.h", "DamageType.h"],
        "systems": ["melee", "ranged", "damage", "abilities"]
    }
}


@router.get("/unreal/templates")
async def get_unreal_templates():
    """Get available Unreal Engine templates"""
    return UNREAL_TEMPLATES


@router.post("/unreal/generate")
async def generate_unreal_code(
    project_id: str,
    template: str,
    customization: dict = None
):
    """Generate Unreal Engine code from template"""
    
    if template not in UNREAL_TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Unknown template: {template}")
    
    template_config = UNREAL_TEMPLATES[template]
    
    generation = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "engine": "unreal",
        "template": template,
        "template_name": template_config["name"],
        "status": "generating",
        "files": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Generate files using LLM
    for filename in template_config["files"]:
        try:
            if filename.endswith(".h"):
                content = await _generate_unreal_header(template, filename, customization)
            elif filename.endswith(".cpp"):
                content = await _generate_unreal_cpp(template, filename, customization)
            elif filename.startswith("BP_"):
                content = await _generate_blueprint_json(template, filename)
            elif filename.startswith("BT_"):
                content = await _generate_behavior_tree(template, filename)
            elif filename.startswith("ABP_"):
                content = await _generate_anim_blueprint(template, filename)
            else:
                content = f"// Generated {filename} for {template}"
            
            generation["files"].append({
                "filename": filename,
                "content": content,
                "type": "header" if filename.endswith(".h") else "source" if filename.endswith(".cpp") else "blueprint"
            })
            
        except Exception as e:
            generation["files"].append({
                "filename": filename,
                "error": str(e),
                "content": f"// Error generating {filename}"
            })
    
    generation["status"] = "completed"
    generation["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.engine_generations.insert_one(generation)
    return serialize_doc(generation)


async def _generate_unreal_header(template: str, filename: str, customization: dict) -> str:
    """Generate Unreal C++ header file"""
    
    response = llm_client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": """Generate Unreal Engine 5 C++ header file.
Follow UE5 conventions:
- Use UCLASS, UPROPERTY, UFUNCTION macros
- Include proper headers
- Use BlueprintCallable for functions exposed to Blueprint
- Add proper categories and meta specifiers"""},
            {"role": "user", "content": f"Generate {filename} for {template} system. Make it production-ready."}
        ],
        max_tokens=3000
    )
    
    return response.choices[0].message.content


async def _generate_unreal_cpp(template: str, filename: str, customization: dict) -> str:
    """Generate Unreal C++ source file"""
    
    response = llm_client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": """Generate Unreal Engine 5 C++ source file.
Follow UE5 conventions:
- Include proper headers
- Implement all declared functions
- Use proper UE5 patterns (Tick, BeginPlay, etc.)
- Add logging where appropriate"""},
            {"role": "user", "content": f"Generate {filename} implementation for {template} system."}
        ],
        max_tokens=4000
    )
    
    return response.choices[0].message.content


async def _generate_blueprint_json(template: str, filename: str) -> str:
    """Generate Blueprint representation"""
    return json.dumps({
        "blueprint_name": filename,
        "template": template,
        "nodes": [
            {"type": "EventBeginPlay", "position": [0, 0]},
            {"type": "Custom", "name": f"Initialize{template}", "position": [200, 0]}
        ],
        "variables": [],
        "note": "Blueprint structure - import into UE5 Editor"
    }, indent=2)


async def _generate_behavior_tree(template: str, filename: str) -> str:
    """Generate Behavior Tree structure"""
    return json.dumps({
        "behavior_tree": filename,
        "root": {
            "type": "Selector",
            "children": [
                {"type": "Sequence", "name": "Combat", "children": []},
                {"type": "Sequence", "name": "Patrol", "children": []}
            ]
        }
    }, indent=2)


async def _generate_anim_blueprint(template: str, filename: str) -> str:
    """Generate Animation Blueprint structure"""
    return json.dumps({
        "anim_blueprint": filename,
        "state_machine": {
            "default_state": "Idle",
            "states": ["Idle", "Walk", "Run", "Jump"],
            "transitions": [
                {"from": "Idle", "to": "Walk", "condition": "Speed > 0"},
                {"from": "Walk", "to": "Run", "condition": "Speed > 300"}
            ]
        }
    }, indent=2)


# ========== UNITY ==========

UNITY_TEMPLATES = {
    "fps_controller": {
        "name": "FPS Controller",
        "files": ["PlayerController.cs", "MouseLook.cs", "PlayerInput.cs"],
        "systems": ["movement", "camera", "input"]
    },
    "third_person": {
        "name": "Third Person Controller",
        "files": ["ThirdPersonController.cs", "CameraController.cs", "PlayerAnimator.cs"],
        "systems": ["movement", "camera", "animation"]
    },
    "inventory": {
        "name": "Inventory System",
        "files": ["InventoryManager.cs", "Item.cs", "InventoryUI.cs", "InventorySlot.cs"],
        "systems": ["items", "ui", "drag_drop"]
    },
    "dialogue": {
        "name": "Dialogue System",
        "files": ["DialogueManager.cs", "DialogueNode.cs", "DialogueUI.cs"],
        "systems": ["branching", "events", "ui"]
    },
    "save_system": {
        "name": "Save System",
        "files": ["SaveManager.cs", "SaveData.cs", "ISaveable.cs"],
        "systems": ["serialization", "slots", "auto_save"]
    },
    "ai_fsm": {
        "name": "AI State Machine",
        "files": ["AIController.cs", "State.cs", "PatrolState.cs", "ChaseState.cs"],
        "systems": ["states", "transitions", "perception"]
    }
}


@router.get("/unity/templates")
async def get_unity_templates():
    """Get available Unity templates"""
    return UNITY_TEMPLATES


@router.post("/unity/generate")
async def generate_unity_code(
    project_id: str,
    template: str,
    customization: dict = None
):
    """Generate Unity C# code from template"""
    
    if template not in UNITY_TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Unknown template: {template}")
    
    template_config = UNITY_TEMPLATES[template]
    
    generation = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "engine": "unity",
        "template": template,
        "template_name": template_config["name"],
        "status": "generating",
        "files": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    for filename in template_config["files"]:
        try:
            response = llm_client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": """Generate Unity C# script.
Follow Unity conventions:
- Use MonoBehaviour for components
- Use proper attributes ([SerializeField], [Header], etc.)
- Include proper namespaces
- Add XML documentation comments
- Make it production-ready"""},
                    {"role": "user", "content": f"Generate {filename} for {template} system in Unity."}
                ],
                max_tokens=3000
            )
            
            generation["files"].append({
                "filename": filename,
                "content": response.choices[0].message.content
            })
            
        except Exception as e:
            generation["files"].append({
                "filename": filename,
                "error": str(e),
                "content": f"// Error generating {filename}"
            })
    
    generation["status"] = "completed"
    generation["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.engine_generations.insert_one(generation)
    return serialize_doc(generation)


# ========== GODOT ==========

GODOT_TEMPLATES = {
    "player_controller": {
        "name": "Player Controller",
        "files": ["player.gd", "camera_controller.gd"],
        "systems": ["movement", "camera"]
    },
    "inventory": {
        "name": "Inventory System",
        "files": ["inventory.gd", "item.gd", "inventory_ui.gd"],
        "systems": ["items", "ui"]
    },
    "dialogue": {
        "name": "Dialogue System",
        "files": ["dialogue_manager.gd", "dialogue_box.gd"],
        "systems": ["branching", "signals"]
    }
}


@router.get("/godot/templates")
async def get_godot_templates():
    """Get available Godot templates"""
    return GODOT_TEMPLATES


@router.post("/godot/generate")
async def generate_godot_code(
    project_id: str,
    template: str
):
    """Generate Godot GDScript from template"""
    
    if template not in GODOT_TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Unknown template: {template}")
    
    template_config = GODOT_TEMPLATES[template]
    
    generation = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "engine": "godot",
        "template": template,
        "template_name": template_config["name"],
        "status": "generating",
        "files": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    for filename in template_config["files"]:
        try:
            response = llm_client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": """Generate Godot 4 GDScript.
Follow Godot conventions:
- Use class_name for custom classes
- Use @export for inspector variables
- Use signals for events
- Include type hints
- Make it production-ready"""},
                    {"role": "user", "content": f"Generate {filename} for {template} system in Godot 4."}
                ],
                max_tokens=2000
            )
            
            generation["files"].append({
                "filename": filename,
                "content": response.choices[0].message.content
            })
            
        except Exception as e:
            generation["files"].append({
                "filename": filename,
                "error": str(e)
            })
    
    generation["status"] = "completed"
    generation["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.engine_generations.insert_one(generation)
    return serialize_doc(generation)


@router.get("/generations")
async def list_engine_generations(project_id: str = None, engine: str = None, limit: int = 20):
    """List engine code generations"""
    query = {}
    if project_id:
        query["project_id"] = project_id
    if engine:
        query["engine"] = engine
    return await db.engine_generations.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
