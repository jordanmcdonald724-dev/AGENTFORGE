"""
Unreal Engine Integration - Generate complete game builds from prompts
Supports blueprint generation, asset creation, and build packaging
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
from core.database import db
import uuid
import asyncio

router = APIRouter(prefix="/unreal", tags=["unreal-engine"])


class GameProject(BaseModel):
    name: str
    description: str
    genre: str = "action"  # action, puzzle, rpg, platformer, shooter, racing
    art_style: str = "stylized"  # realistic, stylized, pixel, low_poly
    platforms: List[str] = ["windows"]  # windows, mac, linux, android, ios
    features: List[str] = []


class BlueprintRequest(BaseModel):
    project_id: str
    blueprint_type: str  # character, weapon, vehicle, ui, game_mode, level
    name: str
    properties: Dict = {}


# Game templates
GAME_TEMPLATES = {
    "fps_shooter": {
        "name": "First-Person Shooter",
        "description": "Complete FPS template with weapons, AI enemies, and multiplayer",
        "blueprints": ["BP_FPSCharacter", "BP_Weapon_Base", "BP_Enemy_AI", "BP_GameMode_FPS"],
        "assets": ["Weapons Pack", "Character Models", "Environment Kit"],
        "features": ["Multiplayer", "AI Enemies", "Weapon System", "Health System"]
    },
    "platformer_3d": {
        "name": "3D Platformer",
        "description": "Mario-style platformer with collectibles and power-ups",
        "blueprints": ["BP_PlatformCharacter", "BP_Collectible", "BP_MovingPlatform", "BP_Checkpoint"],
        "assets": ["Platform Kit", "Character Pack", "VFX Collection"],
        "features": ["Double Jump", "Collectibles", "Checkpoints", "Power-ups"]
    },
    "rpg_adventure": {
        "name": "RPG Adventure",
        "description": "Open-world RPG with quests, inventory, and combat",
        "blueprints": ["BP_RPGCharacter", "BP_Inventory", "BP_QuestSystem", "BP_DialogueManager"],
        "assets": ["Fantasy Characters", "Weapons & Armor", "Environment Pack"],
        "features": ["Quest System", "Inventory", "Dialogue", "Combat", "Leveling"]
    },
    "racing": {
        "name": "Racing Game",
        "description": "Arcade racing with AI opponents and track editor",
        "blueprints": ["BP_Vehicle", "BP_RaceManager", "BP_AIDriver", "BP_TrackSpline"],
        "assets": ["Vehicle Pack", "Track Components", "VFX Pack"],
        "features": ["Vehicle Physics", "AI Opponents", "Lap System", "Boost"]
    },
    "puzzle": {
        "name": "Puzzle Game",
        "description": "Physics-based puzzle game with level progression",
        "blueprints": ["BP_PuzzleManager", "BP_Interactable", "BP_PhysicsObject", "BP_LevelGate"],
        "assets": ["Puzzle Elements", "Environment Kit", "UI Pack"],
        "features": ["Physics Puzzles", "Level Progression", "Hints System", "Star Rating"]
    }
}

# Blueprint templates
BLUEPRINT_TEMPLATES = {
    "character": {
        "components": ["SkeletalMesh", "CapsuleCollider", "CharacterMovement", "Camera"],
        "events": ["BeginPlay", "Tick", "OnLanded", "OnJumped"],
        "variables": ["Health", "Speed", "JumpForce", "IsAlive"]
    },
    "weapon": {
        "components": ["StaticMesh", "BoxCollider", "AudioComponent", "ParticleSystem"],
        "events": ["Fire", "Reload", "Equip", "Unequip"],
        "variables": ["Damage", "FireRate", "AmmoCount", "MaxAmmo"]
    },
    "vehicle": {
        "components": ["SkeletalMesh", "WheeledVehicleMovement", "Camera", "AudioComponent"],
        "events": ["Accelerate", "Brake", "Steer", "Boost"],
        "variables": ["TopSpeed", "Acceleration", "Handling", "BoostAmount"]
    },
    "ui": {
        "components": ["WidgetComponent", "Canvas", "TextBlock", "ProgressBar"],
        "events": ["OnButtonClicked", "OnValueChanged", "UpdateUI"],
        "variables": ["IsVisible", "AnimationState"]
    },
    "game_mode": {
        "components": ["GameState", "PlayerController", "HUD"],
        "events": ["StartMatch", "EndMatch", "PlayerDied", "ScoreChanged"],
        "variables": ["MatchTime", "Score", "PlayerCount", "GameState"]
    },
    "level": {
        "components": ["LevelStreaming", "NavMesh", "LightingScenario"],
        "events": ["LevelLoaded", "LevelUnloaded", "CheckpointReached"],
        "variables": ["LevelName", "Difficulty", "Collectibles"]
    }
}


@router.get("/templates")
async def get_game_templates():
    """Get all available game templates"""
    return GAME_TEMPLATES


@router.get("/blueprint-types")
async def get_blueprint_types():
    """Get available blueprint types and their structure"""
    return BLUEPRINT_TEMPLATES


@router.post("/projects/create")
async def create_game_project(project: GameProject, background_tasks: BackgroundTasks):
    """Create a new Unreal Engine game project"""
    
    project_id = str(uuid.uuid4())
    
    game_project = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "genre": project.genre,
        "art_style": project.art_style,
        "platforms": project.platforms,
        "features": project.features,
        "status": "initializing",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "blueprints": [],
        "assets": [],
        "build_status": None,
        "unreal_version": "5.4"
    }
    
    await db.unreal_projects.insert_one(game_project)
    
    # Generate initial blueprints in background
    background_tasks.add_task(generate_initial_blueprints, project_id, project.genre, project.features)
    
    return {
        "project_id": project_id,
        "status": "initializing",
        "message": f"Creating {project.genre} game project '{project.name}'"
    }


async def generate_initial_blueprints(project_id: str, genre: str, features: List[str]):
    """Generate initial blueprints based on genre"""
    
    # Get template for genre
    template_key = {
        "action": "fps_shooter",
        "shooter": "fps_shooter",
        "platformer": "platformer_3d",
        "rpg": "rpg_adventure",
        "racing": "racing",
        "puzzle": "puzzle"
    }.get(genre, "platformer_3d")
    
    template = GAME_TEMPLATES.get(template_key, GAME_TEMPLATES["platformer_3d"])
    
    blueprints = []
    for bp_name in template["blueprints"]:
        blueprints.append({
            "id": str(uuid.uuid4()),
            "name": bp_name,
            "type": bp_name.split("_")[1].lower() if "_" in bp_name else "actor",
            "status": "generated",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    # Update project with blueprints
    await db.unreal_projects.update_one(
        {"id": project_id},
        {
            "$set": {
                "status": "ready",
                "blueprints": blueprints,
                "assets": template["assets"],
                "template_features": template["features"]
            }
        }
    )


@router.get("/projects")
async def list_game_projects():
    """List all Unreal Engine projects"""
    projects = await db.unreal_projects.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return projects


@router.get("/projects/{project_id}")
async def get_game_project(project_id: str):
    """Get game project details"""
    project = await db.unreal_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/blueprints/generate")
async def generate_blueprint(request: BlueprintRequest):
    """Generate a new blueprint for a project"""
    
    # Verify project exists
    project = await db.unreal_projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get blueprint template
    bp_template = BLUEPRINT_TEMPLATES.get(request.blueprint_type, BLUEPRINT_TEMPLATES["character"])
    
    blueprint = {
        "id": str(uuid.uuid4()),
        "project_id": request.project_id,
        "name": request.name,
        "type": request.blueprint_type,
        "components": bp_template["components"],
        "events": bp_template["events"],
        "variables": bp_template["variables"],
        "custom_properties": request.properties,
        "code": generate_blueprint_code(request.name, request.blueprint_type, bp_template),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Add to project
    await db.unreal_projects.update_one(
        {"id": request.project_id},
        {"$push": {"blueprints": blueprint}}
    )
    
    return blueprint


def generate_blueprint_code(name: str, bp_type: str, template: dict) -> str:
    """Generate pseudo Unreal Blueprint code"""
    
    code = f"""// Blueprint: {name}
// Type: {bp_type}
// Generated by AgentForge

UCLASS()
class {name.upper()} : public A{'Character' if bp_type == 'character' else 'Actor'}
{{
    GENERATED_BODY()
    
public:
    // Components
"""
    
    for comp in template["components"]:
        code += f"    UPROPERTY(VisibleAnywhere)\n    U{comp}* {comp}Component;\n\n"
    
    code += "\n    // Variables\n"
    for var in template["variables"]:
        code += f"    UPROPERTY(EditAnywhere, BlueprintReadWrite)\n    float {var};\n\n"
    
    code += "\nprotected:\n    // Events\n"
    for event in template["events"]:
        code += f"    UFUNCTION(BlueprintCallable)\n    void {event}();\n\n"
    
    code += "};"
    
    return code


@router.post("/projects/{project_id}/build")
async def build_game(project_id: str, platform: str = "windows", background_tasks: BackgroundTasks = None):
    """Build game for specified platform"""
    
    project = await db.unreal_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    build_id = str(uuid.uuid4())
    
    build_info = {
        "id": build_id,
        "project_id": project_id,
        "platform": platform,
        "status": "building",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "progress": 0,
        "stages": [
            {"name": "Compiling Blueprints", "status": "pending"},
            {"name": "Cooking Content", "status": "pending"},
            {"name": "Packaging", "status": "pending"},
            {"name": "Optimizing", "status": "pending"}
        ]
    }
    
    await db.unreal_builds.insert_one(build_info)
    
    # Simulate build in background
    if background_tasks:
        background_tasks.add_task(simulate_build, build_id)
    
    return {
        "build_id": build_id,
        "status": "building",
        "platform": platform,
        "message": f"Building {project['name']} for {platform}"
    }


async def simulate_build(build_id: str):
    """Simulate build process"""
    stages = ["Compiling Blueprints", "Cooking Content", "Packaging", "Optimizing"]
    
    for i, stage in enumerate(stages):
        await db.unreal_builds.update_one(
            {"id": build_id},
            {
                "$set": {
                    f"stages.{i}.status": "running",
                    "progress": (i / len(stages)) * 100
                }
            }
        )
        
        await asyncio.sleep(2)  # Simulate work
        
        await db.unreal_builds.update_one(
            {"id": build_id},
            {"$set": {f"stages.{i}.status": "completed"}}
        )
    
    await db.unreal_builds.update_one(
        {"id": build_id},
        {
            "$set": {
                "status": "completed",
                "progress": 100,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "download_url": f"/downloads/game_{build_id}.zip"
            }
        }
    )


@router.get("/builds/{build_id}")
async def get_build_status(build_id: str):
    """Get build status"""
    build = await db.unreal_builds.find_one({"id": build_id}, {"_id": 0})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    return build


@router.get("/projects/{project_id}/builds")
async def get_project_builds(project_id: str):
    """Get all builds for a project"""
    builds = await db.unreal_builds.find(
        {"project_id": project_id}, 
        {"_id": 0}
    ).sort("started_at", -1).to_list(20)
    return builds
