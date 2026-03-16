from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
from engine.core.database import db
from services.utils import serialize_doc
from models.collaboration import Blueprint, Collaborator, FileLock, CollaborationMessage
import uuid

router = APIRouter(tags=["collaboration"])


# Blueprint Routes
@router.post("/blueprints")
async def create_blueprint(data: dict):
    """Create a new blueprint"""
    blueprint = Blueprint(**data)
    doc = blueprint.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.blueprints.insert_one(doc)
    return serialize_doc(doc)


@router.get("/blueprints")
async def get_blueprints(project_id: str):
    """Get all blueprints for a project"""
    return await db.blueprints.find({"project_id": project_id}, {"_id": 0}).to_list(100)


@router.get("/blueprints/{blueprint_id}")
async def get_blueprint(blueprint_id: str):
    """Get a specific blueprint"""
    return await db.blueprints.find_one({"id": blueprint_id}, {"_id": 0})


@router.patch("/blueprints/{blueprint_id}")
async def update_blueprint(blueprint_id: str, updates: dict):
    """Update a blueprint"""
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    await db.blueprints.update_one({"id": blueprint_id}, {"$set": updates})
    return {"success": True}


@router.delete("/blueprints/{blueprint_id}")
async def delete_blueprint(blueprint_id: str):
    """Delete a blueprint"""
    await db.blueprints.delete_one({"id": blueprint_id})
    return {"success": True}


# Collaborator Routes
@router.post("/collab/{project_id}/join")
async def join_project(project_id: str, user_id: str, username: str):
    """Join a project as a collaborator"""
    existing = await db.collaborators.find_one({
        "project_id": project_id, 
        "user_id": user_id
    })
    
    if existing:
        await db.collaborators.update_one(
            {"id": existing['id']},
            {"$set": {"is_online": True, "last_seen": datetime.now(timezone.utc).isoformat()}}
        )
        return existing
    
    colors = ["blue", "green", "purple", "orange", "pink", "cyan"]
    count = await db.collaborators.count_documents({"project_id": project_id})
    
    collab = Collaborator(
        project_id=project_id,
        user_id=user_id,
        username=username,
        color=colors[count % len(colors)],
        is_online=True
    )
    doc = collab.model_dump()
    doc['last_seen'] = doc['last_seen'].isoformat()
    doc['joined_at'] = doc['joined_at'].isoformat()
    await db.collaborators.insert_one(doc)
    return serialize_doc(doc)


@router.post("/collab/{project_id}/leave")
async def leave_project(project_id: str, user_id: str):
    """Leave a project"""
    await db.collaborators.update_one(
        {"project_id": project_id, "user_id": user_id},
        {"$set": {"is_online": False, "last_seen": datetime.now(timezone.utc).isoformat()}}
    )
    await db.file_locks.delete_many({"project_id": project_id, "locked_by_user_id": user_id})
    return {"success": True}


@router.get("/collab/{project_id}/users")
async def get_collaborators(project_id: str):
    """Get all collaborators for a project"""
    return await db.collaborators.find({"project_id": project_id}, {"_id": 0}).to_list(50)


@router.patch("/collab/{project_id}/cursor")
async def update_cursor(project_id: str, user_id: str, cursor_position: dict, active_file_id: str = None):
    """Update user's cursor position"""
    await db.collaborators.update_one(
        {"project_id": project_id, "user_id": user_id},
        {"$set": {
            "cursor_position": cursor_position,
            "active_file_id": active_file_id,
            "last_seen": datetime.now(timezone.utc).isoformat()
        }}
    )
    return {"success": True}


# File Lock Routes
@router.post("/collab/{project_id}/lock/{file_id}")
async def lock_file(project_id: str, file_id: str, user_id: str, username: str):
    """Lock a file for editing"""
    existing = await db.file_locks.find_one({"project_id": project_id, "file_id": file_id})
    
    if existing:
        if existing['locked_by_user_id'] != user_id:
            return {"success": False, "locked_by": existing['locked_by_username']}
        return {"success": True, "already_locked": True}
    
    lock = FileLock(
        project_id=project_id,
        file_id=file_id,
        locked_by_user_id=user_id,
        locked_by_username=username,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30)
    )
    doc = lock.model_dump()
    doc['locked_at'] = doc['locked_at'].isoformat()
    doc['expires_at'] = doc['expires_at'].isoformat()
    await db.file_locks.insert_one(doc)
    return {"success": True}


@router.delete("/collab/{project_id}/lock/{file_id}")
async def unlock_file(project_id: str, file_id: str, user_id: str):
    """Unlock a file"""
    await db.file_locks.delete_one({
        "project_id": project_id, 
        "file_id": file_id, 
        "locked_by_user_id": user_id
    })
    return {"success": True}


@router.get("/collab/{project_id}/locks")
async def get_file_locks(project_id: str):
    """Get all file locks for a project"""
    return await db.file_locks.find({"project_id": project_id}, {"_id": 0}).to_list(100)


# Collaboration Chat
@router.post("/collab/{project_id}/chat")
async def send_collab_message(project_id: str, user_id: str, username: str, content: str):
    """Send a message in collaboration chat"""
    msg = CollaborationMessage(
        project_id=project_id,
        user_id=user_id,
        username=username,
        content=content
    )
    doc = msg.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.collab_messages.insert_one(doc)
    return serialize_doc(doc)


@router.get("/collab/{project_id}/chat")
async def get_collab_messages(project_id: str, limit: int = 50):
    """Get collaboration chat messages"""
    return await db.collab_messages.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("timestamp", -1).to_list(limit)
