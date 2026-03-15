from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone, timedelta
from core.database import db
from core.utils import serialize_doc
from models.build import (
    SimulationResult, AutonomousBuild, WarRoomMessage, PlayableDemo,
    BuildQueueItem, StartBuildRequest
)
import uuid
import json
import asyncio

router = APIRouter(tags=["builds"])


@router.post("/builds/simulate")
async def simulate_build(project_id: str, build_type: str = "full", target_engine: str = "unreal"):
    """Simulate a build to estimate time and requirements"""
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    base_time = {"prototype": 120, "demo": 240, "full": 720}.get(build_type, 720)
    file_multiplier = 1 + (len(files) * 0.1)
    estimated_minutes = int(base_time * file_multiplier)
    
    hours = estimated_minutes // 60
    mins = estimated_minutes % 60
    
    simulation = SimulationResult(
        project_id=project_id,
        estimated_build_time=f"{hours}h {mins}m",
        estimated_build_minutes=estimated_minutes,
        file_count=len(files),
        total_size_kb=sum(len(f.get('content', '')) for f in files) // 1024,
        feasibility_score=min(95, 70 + len(files)),
        architecture_summary=f"Project has {len(files)} files ready for {target_engine} build"
    )
    
    doc = simulation.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.simulations.insert_one(doc)
    
    return serialize_doc(doc)


@router.get("/builds/{project_id}")
async def get_builds(project_id: str):
    """Get all builds for a project"""
    return await db.builds.find({"project_id": project_id}, {"_id": 0}).sort("created_at", -1).to_list(50)


@router.get("/builds/{project_id}/latest")
async def get_latest_build(project_id: str):
    """Get the latest build for a project"""
    return await db.builds.find_one({"project_id": project_id}, {"_id": 0}, sort=[("created_at", -1)])


@router.post("/builds/start")
async def start_autonomous_build(request: StartBuildRequest):
    """Start an autonomous build (scheduled or immediate)"""
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    stages = [
        {"name": "Setup", "status": "pending", "tasks": []},
        {"name": "Core Framework", "status": "pending", "tasks": []},
        {"name": "Systems", "status": "pending", "tasks": []},
        {"name": "AI/NPCs", "status": "pending", "tasks": []},
        {"name": "UI/UX", "status": "pending", "tasks": []},
        {"name": "Polish", "status": "pending", "tasks": []}
    ]
    
    build = AutonomousBuild(
        project_id=request.project_id,
        build_type=request.build_type,
        target_engine=request.target_engine,
        status="scheduled" if request.scheduled_at else "running",
        total_stages=len(stages),
        stages=stages,
        estimated_completion=(datetime.now(timezone.utc) + timedelta(hours=request.estimated_hours)).isoformat()
    )
    
    if request.scheduled_at:
        build.scheduled_at = datetime.fromisoformat(request.scheduled_at.replace('Z', '+00:00'))
    else:
        build.started_at = datetime.now(timezone.utc)
    
    doc = build.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('scheduled_at'):
        doc['scheduled_at'] = doc['scheduled_at'].isoformat()
    if doc.get('started_at'):
        doc['started_at'] = doc['started_at'].isoformat()
    
    await db.builds.insert_one(doc)
    
    await db.projects.update_one(
        {"id": request.project_id},
        {"$set": {"status": "building", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return serialize_doc(doc)


@router.post("/builds/{build_id}/pause")
async def pause_build(build_id: str):
    """Pause a running build"""
    await db.builds.update_one({"id": build_id}, {"$set": {"status": "paused"}})
    return {"success": True}


@router.post("/builds/{build_id}/resume")
async def resume_build(build_id: str):
    """Resume a paused build"""
    await db.builds.update_one({"id": build_id}, {"$set": {"status": "running"}})
    return {"success": True}


@router.get("/war-room/{project_id}/stream")
async def stream_war_room(project_id: str):
    """Stream war room updates via SSE"""
    async def generate():
        while True:
            messages = await db.war_room.find(
                {"project_id": project_id},
                {"_id": 0}
            ).sort("timestamp", -1).limit(10).to_list(10)
            
            build = await db.builds.find_one(
                {"project_id": project_id, "status": {"$in": ["running", "scheduled"]}},
                {"_id": 0}
            )
            
            yield f"data: {json.dumps({'messages': messages, 'build': build})}\n\n"
            await asyncio.sleep(2)
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/war-room/{project_id}/message")
async def post_war_room_message(project_id: str, from_agent: str, content: str, message_type: str = "discussion"):
    """Post a message to the war room"""
    msg = WarRoomMessage(
        project_id=project_id,
        from_agent=from_agent,
        content=content,
        message_type=message_type
    )
    doc = msg.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.war_room.insert_one(doc)
    return serialize_doc(doc)


@router.get("/war-room/{project_id}/messages")
async def get_war_room_messages(project_id: str, limit: int = 50):
    """Get war room messages"""
    return await db.war_room.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("timestamp", -1).to_list(limit)


@router.get("/demos/{project_id}")
async def get_demos(project_id: str):
    """Get playable demos for a project"""
    return await db.demos.find({"project_id": project_id}, {"_id": 0}).to_list(20)


@router.get("/demos/{project_id}/latest")
async def get_latest_demo(project_id: str):
    """Get the latest playable demo"""
    return await db.demos.find_one(
        {"project_id": project_id, "status": "ready"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )


@router.post("/queue/add")
async def add_to_queue(project_id: str, category: str, build_config: dict = None):
    """Add a project to the build queue"""
    position = await db.build_queue.count_documents({"status": "queued"})
    
    item = BuildQueueItem(
        project_id=project_id,
        category=category,
        build_config=build_config or {},
        position=position + 1
    )
    doc = item.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.build_queue.insert_one(doc)
    return serialize_doc(doc)


@router.get("/queue")
async def get_queue():
    """Get the build queue"""
    return await db.build_queue.find({}, {"_id": 0}).sort("position", 1).to_list(100)


@router.patch("/queue/{item_id}/status")
async def update_queue_status(item_id: str, status: str):
    """Update queue item status"""
    await db.build_queue.update_one({"id": item_id}, {"$set": {"status": status}})
    return {"success": True}
