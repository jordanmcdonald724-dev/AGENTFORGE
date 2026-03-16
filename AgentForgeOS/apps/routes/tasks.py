from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Optional
from engine.core.database import db
from services.utils import serialize_doc
from models.base import Task
from models.project import TaskCreate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("")
async def create_task(task_data: TaskCreate):
    task = Task(**task_data.model_dump())
    doc = task.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.tasks.insert_one(doc)
    return serialize_doc(doc)


@router.get("")
async def get_tasks(project_id: Optional[str] = None):
    query = {"project_id": project_id} if project_id else {}
    return await db.tasks.find(query, {"_id": 0}).to_list(500)


@router.patch("/{task_id}")
async def update_task(task_id: str, updates: dict):
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    await db.tasks.update_one({"id": task_id}, {"$set": updates})
    return {"success": True}


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    await db.tasks.delete_one({"id": task_id})
    return {"success": True}
