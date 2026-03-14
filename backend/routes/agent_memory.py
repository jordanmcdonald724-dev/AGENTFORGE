"""
Agent Memory & Project Utilities Routes
========================================
Agent memory persistence and project duplication.
Extracted from server.py as part of refactoring.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from core.database import db
import uuid
import json
import re
import logging

router = APIRouter(tags=["agent-memory"])
logger = logging.getLogger(__name__)


# Import required functions from server.py
def get_llm_client():
    """Get LLM client from server.py"""
    from server import llm_client
    return llm_client


async def get_or_create_agents_fn():
    """Get agents from server.py"""
    from server import get_or_create_agents
    return await get_or_create_agents()


def serialize_doc(doc):
    """Serialize document from server.py"""
    from server import serialize_doc
    return serialize_doc(doc)


def get_models():
    """Get models from server.py"""
    from server import AgentMemory, MemoryCreate, Project, ProjectFile, Task
    return AgentMemory, MemoryCreate, Project, ProjectFile, Task


# ============ MODELS ============

class ProjectDuplicateRequest(BaseModel):
    new_name: str
    include_files: bool = True
    include_tasks: bool = True


# ============ AGENT MEMORY ROUTES ============

@router.post("/memory")
async def create_memory(memory_data: dict):
    """Store agent memory for persistence across sessions"""
    AgentMemory, MemoryCreate, _, _, _ = get_models()
    
    agents = await get_or_create_agents_fn()
    agent = next((a for a in agents if a['name'].upper() == memory_data.get('agent_name', '').upper()), None)
    
    memory = AgentMemory(
        project_id=memory_data.get('project_id', ''),
        agent_id=agent['id'] if agent else "",
        agent_name=memory_data.get('agent_name', ''),
        memory_type=memory_data.get('memory_type', 'context'),
        content=memory_data.get('content', ''),
        importance=memory_data.get('importance', 5)
    )
    doc = memory.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('expires_at'):
        doc['expires_at'] = doc['expires_at'].isoformat()
    await db.memories.insert_one(doc)
    return serialize_doc(doc)


@router.get("/memory")
async def get_memories(project_id: str, agent_name: Optional[str] = None, limit: int = 50):
    """Get agent memories for a project"""
    query = {"project_id": project_id}
    if agent_name:
        query["agent_name"] = agent_name.upper()
    memories = await db.memories.find(query, {"_id": 0}).sort("importance", -1).limit(limit).to_list(limit)
    return memories


@router.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str):
    await db.memories.delete_one({"id": memory_id})
    return {"success": True}


@router.post("/memory/auto-extract")
async def auto_extract_memories(project_id: str):
    """Auto-extract important memories from recent messages"""
    AgentMemory, _, _, _, _ = get_models()
    llm_client = get_llm_client()
    
    messages = await db.messages.find(
        {"project_id": project_id, "agent_role": {"$ne": "user"}},
        {"_id": 0}
    ).sort("timestamp", -1).limit(20).to_list(20)
    
    if not messages:
        return {"extracted": 0, "memories": []}
    
    agents = await get_or_create_agents_fn()
    lead = next((a for a in agents if a['role'] == 'lead'), agents[0])
    
    conversation = "\n".join([f"{m['agent_name']}: {m['content'][:500]}" for m in messages])
    
    extract_prompt = f"""Review this conversation and extract 3-5 key facts, decisions, or learnings that should be remembered for future sessions.

Conversation:
{conversation}

Output as JSON array:
[{{"agent": "AGENT_NAME", "type": "decision|context|preference|learned", "content": "What to remember", "importance": 1-10}}]"""

    try:
        response = llm_client.chat.completions.create(
            model=lead.get('model', 'google/gemini-2.5-flash'),
            messages=[{"role": "user", "content": extract_prompt}],
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        json_match = re.search(r'\[[\s\S]*\]', content)
        if json_match:
            extracted = json.loads(json_match.group())
            saved_memories = []
            
            for mem in extracted:
                memory = AgentMemory(
                    project_id=project_id,
                    agent_id="",
                    agent_name=mem.get('agent', 'COMMANDER'),
                    memory_type=mem.get('type', 'context'),
                    content=mem.get('content', ''),
                    importance=mem.get('importance', 5)
                )
                doc = memory.model_dump()
                doc['created_at'] = doc['created_at'].isoformat()
                await db.memories.insert_one(doc)
                saved_memories.append(serialize_doc(doc))
            
            return {"extracted": len(saved_memories), "memories": saved_memories}
    except Exception as e:
        logger.error(f"Memory extraction failed: {e}")
    
    return {"extracted": 0, "memories": []}


# ============ PROJECT DUPLICATION ============

@router.post("/projects/{project_id}/duplicate")
async def duplicate_project(project_id: str, request: ProjectDuplicateRequest):
    """Duplicate a project with all its files"""
    _, _, Project, ProjectFile, Task = get_models()
    
    original = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not original:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_project = Project(
        name=request.new_name,
        description=original['description'] + " (Copy)",
        type=original['type'],
        engine_version=original.get('engine_version'),
        thumbnail=original['thumbnail'],
        phase="clarification",
        status="planning"
    )
    new_doc = new_project.model_dump()
    new_doc['created_at'] = new_doc['created_at'].isoformat()
    new_doc['updated_at'] = new_doc['updated_at'].isoformat()
    await db.projects.insert_one(new_doc)
    
    duplicated = {"project": serialize_doc(new_doc), "files": 0, "tasks": 0, "messages": 0}
    
    # Duplicate files
    if request.include_files:
        files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
        for f in files:
            new_file = ProjectFile(
                project_id=new_project.id,
                filename=f['filename'],
                filepath=f['filepath'],
                content=f['content'],
                language=f['language'],
                file_type=f.get('file_type', 'code')
            )
            file_doc = new_file.model_dump()
            file_doc['created_at'] = file_doc['created_at'].isoformat()
            file_doc['updated_at'] = file_doc['updated_at'].isoformat()
            await db.files.insert_one(file_doc)
        duplicated["files"] = len(files)
    
    # Duplicate tasks
    if request.include_tasks:
        tasks = await db.tasks.find({"project_id": project_id}, {"_id": 0}).to_list(500)
        for t in tasks:
            new_task = Task(
                project_id=new_project.id,
                title=t['title'],
                description=t['description'],
                status="backlog",
                priority=t['priority'],
                category=t.get('category', 'general')
            )
            task_doc = new_task.model_dump()
            task_doc['created_at'] = task_doc['created_at'].isoformat()
            task_doc['updated_at'] = task_doc['updated_at'].isoformat()
            await db.tasks.insert_one(task_doc)
        duplicated["tasks"] = len(tasks)
    
    return duplicated
