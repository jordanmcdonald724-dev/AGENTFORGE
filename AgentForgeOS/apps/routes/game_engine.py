"""
Game Engine Builder - Real Unreal Engine 5 & Unity Build Integration
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
from engine.core.database import db
import uuid
import asyncio
import os
import subprocess
import platform

router = APIRouter(prefix="/game-engine", tags=["game-engine"])

CURRENT_OS = platform.system().lower()

ENGINE_CONFIG = {
    "unreal": {
        "name": "Unreal Engine 5",
        "versions": ["5.4", "5.3", "5.2", "5.1", "5.0"],
        "install_paths": {
            "windows": ["C:/Program Files/Epic Games/UE_{version}", "D:/Epic Games/UE_{version}"],
            "darwin": ["/Users/Shared/Epic Games/UE_{version}"],
            "linux": ["/opt/unreal-engine/UE_{version}"]
        },
        "build_tool": {"windows": "Engine/Build/BatchFiles/RunUAT.bat", "darwin": "Engine/Build/BatchFiles/RunUAT.sh", "linux": "Engine/Build/BatchFiles/RunUAT.sh"},
        "platforms": ["Win64", "Mac", "Linux", "Android", "iOS"]
    },
    "unity": {
        "name": "Unity",
        "versions": ["2023.2", "2023.1", "2022.3 LTS", "2022.2"],
        "install_paths": {
            "windows": ["C:/Program Files/Unity/Hub/Editor/{version}/Editor/Unity.exe"],
            "darwin": ["/Applications/Unity/Hub/Editor/{version}/Unity.app/Contents/MacOS/Unity"],
            "linux": ["/opt/unity/Editor/Unity"]
        },
        "platforms": ["StandaloneWindows64", "StandaloneOSX", "StandaloneLinux64", "Android", "iOS", "WebGL"]
    }
}

class GameProjectCreate(BaseModel):
    name: str
    description: str
    engine: str
    template: str = "blank"
    platforms: List[str] = ["Win64"]

class BuildRequest(BaseModel):
    project_id: str
    platform: str = "Win64"
    configuration: str = "Development"

@router.get("/detect")
async def detect_engines():
    """Detect installed game engines"""
    detected = {"os": CURRENT_OS, "unreal": [], "unity": []}
    
    for version in ENGINE_CONFIG["unreal"]["versions"]:
        for path_template in ENGINE_CONFIG["unreal"]["install_paths"].get(CURRENT_OS, []):
            path = os.path.expanduser(path_template.replace("{version}", version))
            if os.path.exists(path):
                detected["unreal"].append({"version": version, "path": path})
    
    for version in ENGINE_CONFIG["unity"]["versions"]:
        for path_template in ENGINE_CONFIG["unity"]["install_paths"].get(CURRENT_OS, []):
            path = os.path.expanduser(path_template.replace("{version}", version))
            if os.path.exists(path):
                detected["unity"].append({"version": version, "path": path})
    
    return detected

@router.post("/config")
async def set_engine_paths(paths: Dict[str, str]):
    """Set engine installation paths"""
    config = {
        "id": "engine_config",
        "unreal_path": paths.get("unreal_path"),
        "unity_path": paths.get("unity_path"),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.game_engine_config.update_one({"id": "engine_config"}, {"$set": config}, upsert=True)
    return {"message": "Paths saved", "config": config}

@router.get("/config")
async def get_engine_config():
    """Get engine configuration"""
    config = await db.game_engine_config.find_one({"id": "engine_config"}, {"_id": 0})
    return config or {}

@router.get("/templates/{engine}")
async def get_templates(engine: str):
    """Get project templates"""
    templates = {
        "unreal": {
            "blank": "Empty project",
            "first_person": "FPS template",
            "third_person": "Third person template",
            "top_down": "Top-down game",
            "side_scroller": "2D side-scroller",
            "vehicle": "Vehicle game",
            "vr": "VR template"
        },
        "unity": {
            "blank": "Empty project",
            "2d": "2D game",
            "3d": "3D game",
            "urp": "Universal Render Pipeline",
            "hdrp": "HD Render Pipeline",
            "vr": "VR project"
        }
    }
    return templates.get(engine, {})

@router.post("/projects")
async def create_project(project: GameProjectCreate, background_tasks: BackgroundTasks):
    """Create game project"""
    project_id = str(uuid.uuid4())
    
    game_project = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "engine": project.engine,
        "template": project.template,
        "platforms": project.platforms,
        "status": "created",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": []
    }
    
    await db.game_engine_projects.insert_one(game_project)
    background_tasks.add_task(generate_project_files, project_id, project)
    
    return {"project_id": project_id, "status": "created"}

async def generate_project_files(project_id: str, project: GameProjectCreate):
    """Generate project configuration files"""
    files = []
    
    if project.engine == "unreal":
        files.append({
            "name": f"{project.name}.uproject",
            "content": f'{{"FileVersion": 3, "EngineAssociation": "5.4", "Modules": [{{"Name": "{project.name}", "Type": "Runtime"}}]}}'
        })
    elif project.engine == "unity":
        files.append({
            "name": "ProjectSettings.asset",
            "content": f"productName: {project.name}"
        })
    
    await db.game_engine_projects.update_one(
        {"id": project_id},
        {"$set": {"status": "ready", "files": files}}
    )

@router.get("/projects")
async def list_projects():
    """List all game projects"""
    projects = await db.game_engine_projects.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return projects

@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    project = await db.game_engine_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/build")
async def start_build(request: BuildRequest, background_tasks: BackgroundTasks):
    """Start a build"""
    project = await db.game_engine_projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    build_id = str(uuid.uuid4())
    
    build = {
        "id": build_id,
        "project_id": request.project_id,
        "project_name": project["name"],
        "engine": project["engine"],
        "platform": request.platform,
        "configuration": request.configuration,
        "status": "queued",
        "progress": 0,
        "logs": [],
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.game_engine_builds.insert_one(build)
    background_tasks.add_task(execute_build, build_id, project, request)
    
    return {"build_id": build_id, "status": "queued"}

async def execute_build(build_id: str, project: dict, request: BuildRequest):
    """Execute the build"""
    engine = project["engine"]
    
    # Get configured path
    config = await db.game_engine_config.find_one({"id": "engine_config"}, {"_id": 0})
    engine_path = None
    
    if config:
        engine_path = config.get(f"{engine}_path")
    
    # Check if engine exists
    if engine_path and os.path.exists(engine_path):
        await run_real_build(build_id, engine, engine_path, project, request)
    else:
        await run_simulated_build(build_id, engine)

async def run_real_build(build_id: str, engine: str, engine_path: str, project: dict, request: BuildRequest):
    """Run actual engine build"""
    await update_build(build_id, "building", 10, "Starting real build...")
    
    try:
        if engine == "unreal":
            uat_path = os.path.join(engine_path, ENGINE_CONFIG["unreal"]["build_tool"].get(CURRENT_OS, ""))
            cmd = [uat_path, "BuildCookRun", f"-platform={request.platform}", "-cook", "-stage", "-pak"]
        else:
            cmd = [engine_path, "-quit", "-batchmode", f"-buildTarget={request.platform}"]
        
        await update_build(build_id, "building", 30, f"Executing: {' '.join(cmd[:3])}...")
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in iter(process.stdout.readline, ''):
            if line:
                await db.game_engine_builds.update_one(
                    {"id": build_id},
                    {"$push": {"logs": line.strip()[:200]}}
                )
        
        return_code = process.wait()
        
        if return_code == 0:
            await update_build(build_id, "completed", 100, "Build completed successfully!")
        else:
            await update_build(build_id, "failed", 0, f"Build failed with code {return_code}")
            
    except Exception as e:
        await update_build(build_id, "failed", 0, str(e))

async def run_simulated_build(build_id: str, engine: str):
    """Simulate build when engine not installed"""
    stages = [
        (20, "Preparing build environment..."),
        (40, "Compiling shaders..." if engine == "unreal" else "Compiling scripts..."),
        (60, "Cooking content..." if engine == "unreal" else "Building assets..."),
        (80, "Packaging..."),
        (100, "Build complete (simulated - engine not installed)")
    ]
    
    for progress, message in stages:
        await update_build(build_id, "building", progress, message)
        await asyncio.sleep(2)
    
    await db.game_engine_builds.update_one(
        {"id": build_id},
        {"$set": {"status": "completed", "simulated": True}}
    )

async def update_build(build_id: str, status: str, progress: int, message: str):
    """Update build status"""
    await db.game_engine_builds.update_one(
        {"id": build_id},
        {"$set": {"status": status, "progress": progress}, "$push": {"logs": message}}
    )

@router.get("/builds")
async def list_builds():
    """List all builds"""
    builds = await db.game_engine_builds.find({}, {"_id": 0}).sort("started_at", -1).to_list(50)
    return builds

@router.get("/builds/{build_id}")
async def get_build(build_id: str):
    """Get build status"""
    build = await db.game_engine_builds.find_one({"id": build_id}, {"_id": 0})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    return build
