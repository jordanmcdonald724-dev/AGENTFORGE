from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from engine.core.database import db
from services.utils import serialize_doc
from models.base import ProjectFile
from models.project import FileCreate, FileUpdate

router = APIRouter(prefix="/files", tags=["files"])


@router.post("")
async def create_file(file_data: FileCreate):
    existing = await db.files.find_one({
        "project_id": file_data.project_id, 
        "filepath": file_data.filepath
    })
    
    if existing:
        new_version = existing.get('version', 1) + 1
        await db.files.update_one(
            {"id": existing['id']},
            {"$set": {
                "content": file_data.content, 
                "version": new_version, 
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        return await db.files.find_one({"id": existing['id']}, {"_id": 0})
    
    file = ProjectFile(**file_data.model_dump())
    doc = file.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.files.insert_one(doc)
    return serialize_doc(doc)


@router.get("")
async def get_files(project_id: str):
    return await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)


@router.get("/{file_id}")
async def get_file(file_id: str):
    file = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file


@router.patch("/{file_id}")
async def update_file(file_id: str, update: FileUpdate):
    file = await db.files.find_one({"id": file_id})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    new_version = file.get('version', 1) + 1
    await db.files.update_one(
        {"id": file_id}, 
        {"$set": {
            "content": update.content, 
            "version": new_version, 
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    return {"success": True, "version": new_version}


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    await db.files.delete_one({"id": file_id})
    return {"success": True}


@router.post("/from-chat")
async def save_files_from_chat(data: dict):
    """Auto-save files from chat code blocks"""
    project_id = data.get("project_id")
    code_blocks = data.get("code_blocks", [])
    agent_id = data.get("agent_id")
    agent_name = data.get("agent_name")
    
    saved_files = []
    for block in code_blocks:
        if block.get("filepath"):
            file = ProjectFile(
                project_id=project_id,
                filename=block.get("filename", ""),
                filepath=block.get("filepath"),
                content=block.get("content", ""),
                language=block.get("language", "text"),
                created_by_agent_id=agent_id,
                created_by_agent_name=agent_name
            )
            doc = file.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            doc['updated_at'] = doc['updated_at'].isoformat()
            
            existing = await db.files.find_one({
                "project_id": project_id, 
                "filepath": block.get("filepath")
            })
            
            if existing:
                await db.files.update_one(
                    {"id": existing['id']},
                    {"$set": {
                        "content": block.get("content", ""), 
                        "version": existing.get('version', 1) + 1, 
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
            else:
                await db.files.insert_one(doc)
            
            saved_files.append(block.get("filepath"))
    
    return {"success": True, "saved_files": saved_files}
