"""
Autonomous Builds Routes
========================
Overnight builds, scheduled builds, and build stage management.
Extracted from server.py as part of refactoring.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from core.database import db
import uuid
import asyncio
import logging

router = APIRouter(prefix="/builds", tags=["builds"])
logger = logging.getLogger(__name__)


# Import required functions and data from server.py
def get_models():
    from server import StartBuildRequest, AutonomousBuild, ProjectFile
    return StartBuildRequest, AutonomousBuild, ProjectFile


def get_build_stages():
    from server import BUILD_STAGES
    return BUILD_STAGES


def serialize_doc(doc):
    from server import serialize_doc
    return serialize_doc(doc)


async def get_or_create_agents_fn():
    from server import get_or_create_agents
    return await get_or_create_agents()


async def call_agent_fn(agent, messages, context):
    from server import call_agent
    return await call_agent(agent, messages, context)


async def build_project_context_fn(project_id):
    from server import build_project_context
    return await build_project_context(project_id)


def extract_code_blocks_fn(content):
    from server import extract_code_blocks
    return extract_code_blocks(content)


async def broadcast_to_war_room(project_id: str, from_agent: str, content: str, message_type: str = "progress", build_id: str = None):
    """Broadcast to war room"""
    from server import broadcast_to_war_room as btwr
    return await btwr(project_id, from_agent, content, message_type, build_id)


async def generate_playable_demo_fn(build_id: str):
    """Call the playable demo generator in server.py"""
    from server import generate_playable_demo
    return await generate_playable_demo(build_id)


# ============ BUILD ROUTES ============

@router.post("/start")
async def start_autonomous_build(request: dict):
    """Start or schedule an autonomous overnight build"""
    StartBuildRequest, AutonomousBuild, _ = get_models()
    BUILD_STAGES = get_build_stages()
    
    project_id = request.get("project_id")
    build_type = request.get("build_type", "full")
    target_engine = request.get("target_engine", "unreal")
    scheduled_at = request.get("scheduled_at")
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check for existing running build
    existing = await db.builds.find_one({"project_id": project_id, "status": {"$in": ["running", "scheduled"]}})
    if existing:
        raise HTTPException(status_code=400, detail="A build is already running or scheduled for this project")
    
    # Get build stages
    base_stages = BUILD_STAGES.get(target_engine, BUILD_STAGES["unreal"])
    stages = []
    for i, stage in enumerate(base_stages):
        stages.append({
            "index": i,
            "name": stage["name"],
            "duration_minutes": stage["duration_minutes"],
            "tasks": stage["tasks"],
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "files_created": [],
            "test_results": None,
            "agent_notes": []
        })
    
    total_minutes = sum(s["duration_minutes"] for s in stages)
    hours = total_minutes // 60
    mins = total_minutes % 60
    
    # Parse scheduled time
    scheduled_time = None
    status = "queued"
    if scheduled_at:
        try:
            scheduled_time = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
            status = "scheduled"
        except Exception:
            pass
    
    build = AutonomousBuild(
        project_id=project_id,
        build_type=build_type,
        target_engine=target_engine,
        status=status,
        total_stages=len(stages),
        stages=stages,
        estimated_completion=f"{hours}h {mins}m",
        scheduled_at=scheduled_time
    )
    
    doc = build.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('scheduled_at'):
        doc['scheduled_at'] = doc['scheduled_at'].isoformat()
    await db.builds.insert_one(doc)
    
    # Post to war room
    if scheduled_time:
        scheduled_str = scheduled_time.strftime("%I:%M %p on %b %d")
        await broadcast_to_war_room(
            project_id,
            "COMMANDER",
            f"⏰ Build SCHEDULED for {scheduled_str}! Target: {target_engine.upper()}. Estimated time: {build.estimated_completion}. Get some rest, I'll handle this.",
            "progress",
            build.id
        )
    else:
        await broadcast_to_war_room(
            project_id,
            "COMMANDER",
            f"🚀 Autonomous build initiated! Target: {target_engine.upper()}. Estimated time: {build.estimated_completion}. {len(stages)} stages queued.",
            "progress",
            build.id
        )
    
    # Update project status
    await db.projects.update_one(
        {"id": project_id},
        {"$set": {"status": "scheduled" if scheduled_time else "building", "build_id": build.id}}
    )
    
    return serialize_doc(doc)


@router.get("/{project_id}")
async def get_project_builds(project_id: str):
    """Get all builds for a project"""
    builds = await db.builds.find({"project_id": project_id}, {"_id": 0}).sort("created_at", -1).to_list(20)
    return builds


@router.get("/{project_id}/current")
async def get_current_build(project_id: str):
    """Get the current/latest build for a project"""
    build = await db.builds.find_one(
        {"project_id": project_id, "status": {"$in": ["queued", "running"]}},
        {"_id": 0}
    )
    if not build:
        build = await db.builds.find_one(
            {"project_id": project_id},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
    return build


@router.post("/{build_id}/advance")
async def advance_build_stage(build_id: str):
    """Advance to the next build stage"""
    build = await db.builds.find_one({"id": build_id})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    
    current_stage = build["current_stage"]
    stages = build["stages"]
    
    if current_stage >= len(stages):
        return {"message": "Build already complete"}
    
    # Mark current stage as complete
    if build["status"] == "running":
        stages[current_stage]["status"] = "completed"
        stages[current_stage]["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    # Move to next stage
    next_stage = current_stage + 1
    progress = int((next_stage / len(stages)) * 100)
    
    if next_stage >= len(stages):
        # Build complete
        await db.builds.update_one(
            {"id": build_id},
            {"$set": {
                "status": "completed",
                "stages": stages,
                "current_stage": next_stage,
                "progress_percent": 100,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        await broadcast_to_war_room(
            build["project_id"],
            "COMMANDER",
            "✅ BUILD COMPLETE! All stages finished successfully.",
            "progress",
            build_id
        )
    else:
        # Start next stage
        stages[next_stage]["status"] = "in_progress"
        stages[next_stage]["started_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.builds.update_one(
            {"id": build_id},
            {"$set": {
                "status": "running",
                "stages": stages,
                "current_stage": next_stage,
                "progress_percent": progress,
                "started_at": build.get("started_at") or datetime.now(timezone.utc).isoformat()
            }}
        )
        
        stage_name = stages[next_stage]["name"]
        await broadcast_to_war_room(
            build["project_id"],
            "COMMANDER",
            f"📍 Stage {next_stage + 1}/{len(stages)}: {stage_name} starting... ({progress}% complete)",
            "progress",
            build_id
        )
    
    return await db.builds.find_one({"id": build_id}, {"_id": 0})


@router.post("/{build_id}/pause")
async def pause_build(build_id: str):
    """Pause a running build"""
    await db.builds.update_one({"id": build_id}, {"$set": {"status": "paused"}})
    build = await db.builds.find_one({"id": build_id}, {"_id": 0})
    await broadcast_to_war_room(build["project_id"], "COMMANDER", "⏸️ Build paused.", "progress", build_id)
    return {"success": True}


@router.post("/{build_id}/resume")
async def resume_build(build_id: str):
    """Resume a paused build"""
    await db.builds.update_one({"id": build_id}, {"$set": {"status": "running"}})
    build = await db.builds.find_one({"id": build_id}, {"_id": 0})
    await broadcast_to_war_room(build["project_id"], "COMMANDER", "▶️ Build resumed!", "progress", build_id)
    return {"success": True}


@router.post("/{build_id}/cancel")
async def cancel_build(build_id: str):
    """Cancel a build"""
    await db.builds.update_one({"id": build_id}, {"$set": {"status": "cancelled"}})
    build = await db.builds.find_one({"id": build_id}, {"_id": 0})
    await broadcast_to_war_room(build["project_id"], "COMMANDER", "❌ Build cancelled.", "progress", build_id)
    await db.projects.update_one({"id": build["project_id"]}, {"$set": {"status": "planning"}})
    return {"success": True}


@router.get("/scheduled/all")
async def get_scheduled_builds():
    """Get all scheduled builds that should start now"""
    now = datetime.now(timezone.utc)
    builds = await db.builds.find({
        "status": "scheduled",
        "scheduled_at": {"$lte": now.isoformat()}
    }, {"_id": 0}).to_list(100)
    return builds


@router.post("/{build_id}/start-scheduled")
async def start_scheduled_build(build_id: str, background_tasks: BackgroundTasks):
    """Start a scheduled build that is ready"""
    build = await db.builds.find_one({"id": build_id})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    
    if build["status"] != "scheduled":
        raise HTTPException(status_code=400, detail="Build is not in scheduled status")
    
    await db.builds.update_one(
        {"id": build_id},
        {"$set": {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await broadcast_to_war_room(
        build["project_id"],
        "COMMANDER",
        "⏰ Scheduled build starting NOW!",
        "progress",
        build_id
    )
    
    async def execute_all_stages():
        for i in range(len(build["stages"])):
            current_build = await db.builds.find_one({"id": build_id})
            if current_build["status"] in ["cancelled", "paused"]:
                break
            try:
                await execute_build_stage_internal(build_id, i)
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Build stage {i} failed: {e}")
                break
        
        final_build = await db.builds.find_one({"id": build_id})
        if final_build["status"] == "running":
            all_complete = all(s["status"] == "completed" for s in final_build["stages"])
            await db.builds.update_one(
                {"id": build_id},
                {"$set": {
                    "status": "completed" if all_complete else "partial",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "progress_percent": 100 if all_complete else final_build.get("progress_percent", 0)
                }}
            )
            if all_complete:
                await broadcast_to_war_room(
                    final_build["project_id"],
                    "COMMANDER",
                    "🎉 OVERNIGHT BUILD COMPLETE!",
                    "progress",
                    build_id
                )
    
    background_tasks.add_task(execute_all_stages)
    return {"success": True, "message": "Scheduled build started"}


@router.post("/{build_id}/stage/{stage_index}/execute")
async def execute_build_stage(build_id: str, stage_index: int):
    """Execute a specific build stage using the agent team"""
    return await execute_build_stage_internal(build_id, stage_index)


async def execute_build_stage_internal(build_id: str, stage_index: int):
    """Internal function to execute a build stage"""
    _, _, ProjectFile = get_models()
    
    build = await db.builds.find_one({"id": build_id})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    
    if stage_index >= len(build["stages"]):
        raise HTTPException(status_code=400, detail="Invalid stage index")
    
    stage = build["stages"][stage_index]
    project = await db.projects.find_one({"id": build["project_id"]}, {"_id": 0})
    agents = await get_or_create_agents_fn()
    
    stage_agent_map = {
        "Project Setup": "COMMANDER",
        "Core Framework": "ATLAS",
        "Game Systems": "FORGE",
        "AI & NPCs": "FORGE",
        "UI/UX": "PRISM",
        "World Building": "PRISM",
        "Audio Integration": "FORGE",
        "Polish & Testing": "PROBE"
    }
    
    agent_name = stage_agent_map.get(stage["name"], "FORGE")
    agent = next((a for a in agents if a['name'] == agent_name), agents[0])
    
    await broadcast_to_war_room(
        build["project_id"],
        agent_name,
        f"🔧 Taking over {stage['name']}. Tasks: {', '.join(stage['tasks'])}",
        "handoff",
        build_id
    )
    
    tasks_str = "\n".join([f"- {t}" for t in stage["tasks"]])
    prompt = f"""You are working on an autonomous build for a {build['target_engine']} {build['build_type']} game.

PROJECT: {project['name']}
DESCRIPTION: {project['description']}
ENGINE: {build['target_engine'].upper()}

CURRENT STAGE: {stage['name']} ({stage_index + 1}/{len(build['stages'])})

YOUR TASKS FOR THIS STAGE:
{tasks_str}

Generate all the necessary files for this stage now. Format: ```language:filepath/filename.ext"""

    context = await build_project_context_fn(build["project_id"])
    
    try:
        response = await call_agent_fn(agent, [{"role": "user", "content": prompt}], context)
        code_blocks = extract_code_blocks_fn(response)
        
        files_created = []
        for block in code_blocks:
            if block.get("filepath"):
                file = ProjectFile(
                    project_id=build["project_id"],
                    filename=block.get("filename", ""),
                    filepath=block.get("filepath"),
                    content=block.get("content", ""),
                    language=block.get("language", "text"),
                    created_by_agent_name=agent_name
                )
                doc = file.model_dump()
                doc['created_at'] = doc['created_at'].isoformat()
                doc['updated_at'] = doc['updated_at'].isoformat()
                
                existing = await db.files.find_one({"project_id": build["project_id"], "filepath": block.get("filepath")})
                if existing:
                    await db.files.update_one(
                        {"id": existing['id']},
                        {"$set": {"content": block.get("content", ""), "version": existing.get('version', 1) + 1}}
                    )
                else:
                    await db.files.insert_one(doc)
                
                files_created.append(block.get("filepath"))
        
        build["stages"][stage_index]["status"] = "completed"
        build["stages"][stage_index]["completed_at"] = datetime.now(timezone.utc).isoformat()
        build["stages"][stage_index]["files_created"] = files_created
        build["stages"][stage_index]["agent_notes"].append({
            "agent": agent_name,
            "note": f"Generated {len(files_created)} files",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        await db.builds.update_one({"id": build_id}, {"$set": {"stages": build["stages"]}})
        
        await broadcast_to_war_room(
            build["project_id"],
            agent_name,
            f"✅ {stage['name']} complete! Generated {len(files_created)} files.",
            "progress",
            build_id
        )
        
        return {"success": True, "stage": stage["name"], "files_created": files_created, "agent": agent_name}
        
    except Exception as e:
        logger.error(f"Stage execution failed: {e}")
        build["stages"][stage_index]["status"] = "failed"
        build["stages"][stage_index]["agent_notes"].append({
            "agent": agent_name,
            "note": f"Error: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        await db.builds.update_one({"id": build_id}, {"$set": {"stages": build["stages"], "status": "failed"}})
        
        await broadcast_to_war_room(
            build["project_id"],
            agent_name,
            f"❌ {stage['name']} failed: {str(e)}",
            "warning",
            build_id
        )
        
        raise HTTPException(status_code=500, detail=f"Stage execution failed: {str(e)}")


@router.post("/{build_id}/run-full")
async def run_full_build(build_id: str, background_tasks: BackgroundTasks):
    """Run all build stages sequentially"""
    build = await db.builds.find_one({"id": build_id})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    
    await db.builds.update_one(
        {"id": build_id},
        {"$set": {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    async def execute_all_stages():
        for i in range(len(build["stages"])):
            current_build = await db.builds.find_one({"id": build_id})
            if current_build["status"] in ["cancelled", "paused"]:
                break
            try:
                await execute_build_stage_internal(build_id, i)
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Build stage {i} failed: {e}")
                break
        
        final_build = await db.builds.find_one({"id": build_id})
        if final_build["status"] == "running":
            all_complete = all(s["status"] == "completed" for s in final_build["stages"])
            await db.builds.update_one(
                {"id": build_id},
                {"$set": {
                    "status": "completed" if all_complete else "partial",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "progress_percent": 100 if all_complete else final_build.get("progress_percent", 0)
                }}
            )
            
            if all_complete:
                await broadcast_to_war_room(
                    final_build["project_id"],
                    "COMMANDER",
                    "🎮 BUILD COMPLETE! Now generating playable demo...",
                    "progress",
                    build_id
                )
                try:
                    await generate_playable_demo_fn(build_id)
                except Exception as e:
                    logger.error(f"Demo generation failed: {e}")
    
    background_tasks.add_task(execute_all_stages)
    return {"success": True, "message": "Build started in background", "build_id": build_id}
