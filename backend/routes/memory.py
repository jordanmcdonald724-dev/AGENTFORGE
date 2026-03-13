"""
Memory & Custom Actions Routes
==============================
Routes for agent memory and custom quick actions.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
from typing import List, Optional
from core.database import db
from core.clients import llm_client
from core.utils import serialize_doc
import uuid
import json

router = APIRouter(tags=["memory"])


# ========== AGENT MEMORY ENDPOINTS ==========

@router.post("/memory")
async def create_memory(
    project_id: str,
    agent_name: str,
    content: str,
    memory_type: str = "context",
    importance: int = 5
):
    """Create an agent memory entry"""
    agents = await db.agents.find({}, {"_id": 0}).to_list(10)
    agent = next((a for a in agents if a["name"].upper() == agent_name.upper()), None)
    
    memory = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "agent_id": agent["id"] if agent else None,
        "agent_name": agent_name.upper(),
        "memory_type": memory_type,
        "content": content,
        "importance": min(10, max(1, importance)),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": None
    }
    
    await db.memories.insert_one(memory)
    return serialize_doc(memory)


@router.get("/memory")
async def get_memories(project_id: str, agent_name: str = None, limit: int = 50):
    """Get agent memories for a project"""
    query = {"project_id": project_id}
    if agent_name:
        query["agent_name"] = agent_name.upper()
    
    return await db.memories.find(query, {"_id": 0}).sort("importance", -1).to_list(limit)


@router.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a memory entry"""
    await db.memories.delete_one({"id": memory_id})
    return {"success": True}


@router.post("/memory/auto-extract")
async def auto_extract_memories(project_id: str, from_messages: int = 10):
    """Auto-extract important memories from recent messages"""
    messages = await db.messages.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(from_messages).to_list(from_messages)
    
    extracted = []
    for msg in messages:
        content = msg.get("content", "")
        
        # Simple extraction: look for key phrases
        if any(phrase in content.lower() for phrase in ["important:", "remember:", "note:", "decision:"]):
            memory = {
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "agent_id": msg.get("agent_id"),
                "agent_name": msg.get("agent_name", "UNKNOWN"),
                "memory_type": "decision",
                "content": content[:500],
                "importance": 7,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.memories.insert_one(memory)
            extracted.append(memory)
    
    return {"extracted": len(extracted), "memories": extracted}


# ========== CUSTOM ACTIONS ENDPOINTS ==========

@router.post("/custom-actions")
async def create_custom_action(
    name: str,
    description: str,
    prompt: str,
    chain: List[str] = None,
    icon: str = "sparkles",
    category: str = "custom",
    is_global: bool = False,
    project_id: str = None
):
    """Create a custom quick action"""
    action = {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "prompt": prompt,
        "chain": chain or ["COMMANDER", "FORGE"],
        "icon": icon,
        "category": category,
        "is_global": is_global,
        "project_id": project_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.custom_actions.insert_one(action)
    return serialize_doc(action)


@router.get("/custom-actions")
async def get_custom_actions(project_id: str = None):
    """Get custom actions"""
    query = {"$or": [{"is_global": True}]}
    if project_id:
        query["$or"].append({"project_id": project_id})
    
    return await db.custom_actions.find(query, {"_id": 0}).to_list(100)


@router.delete("/custom-actions/{action_id}")
async def delete_custom_action(action_id: str):
    """Delete a custom action"""
    await db.custom_actions.delete_one({"id": action_id})
    return {"success": True}


@router.post("/custom-actions/{action_id}/execute")
async def execute_custom_action(action_id: str, project_id: str, parameters: dict = None):
    """Execute a custom action"""
    action = await db.custom_actions.find_one({"id": action_id}, {"_id": 0})
    if not action:
        raise HTTPException(status_code=404, detail="Custom action not found")
    
    prompt = action["prompt"]
    if parameters:
        for key, value in parameters.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
    
    # Get first agent in chain
    chain = action.get("chain", ["COMMANDER"])
    agents = await db.agents.find({}, {"_id": 0}).to_list(10)
    target_agent = next((a for a in agents if a["name"].upper() == chain[0].upper()), agents[0])
    
    context = await _build_project_context(project_id)
    
    try:
        response = llm_client.chat.completions.create(
            model=target_agent.get("model", "google/gemini-2.5-flash"),
            messages=[
                {"role": "system", "content": target_agent["system_prompt"] + f"\n\nCONTEXT:\n{context}"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000,
            temperature=0.7
        )
        result = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action execution failed: {str(e)}")
    
    return {
        "response": result,
        "action": action["name"],
        "agent": target_agent["name"]
    }


@router.post("/custom-actions/{action_id}/execute/stream")
async def execute_custom_action_stream(action_id: str, project_id: str, parameters: dict = None):
    """Execute a custom action with streaming"""
    action = await db.custom_actions.find_one({"id": action_id}, {"_id": 0})
    if not action:
        raise HTTPException(status_code=404, detail="Custom action not found")
    
    prompt = action["prompt"]
    if parameters:
        for key, value in parameters.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
    
    chain = action.get("chain", ["COMMANDER"])
    agents = await db.agents.find({}, {"_id": 0}).to_list(10)
    target_agent = next((a for a in agents if a["name"].upper() == chain[0].upper()), agents[0])
    
    context = await _build_project_context(project_id)
    
    async def generate():
        yield f"data: {json.dumps({'type': 'start', 'agent': target_agent['name']})}\n\n"
        
        try:
            stream = llm_client.chat.completions.create(
                model=target_agent.get("model", "google/gemini-2.5-flash"),
                messages=[
                    {"role": "system", "content": target_agent["system_prompt"] + f"\n\nCONTEXT:\n{context}"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=8000,
                temperature=0.7,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk.choices[0].delta.content})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


async def _build_project_context(project_id: str) -> str:
    """Build context string for a project"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        return ""
    
    parts = [
        f"PROJECT: {project['name']}",
        f"TYPE: {project['type']}",
        f"STATUS: {project['status']}"
    ]
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(20)
    if files:
        parts.append(f"\nFILES ({len(files)}):")
        for f in files[:10]:
            parts.append(f"  - {f.get('filepath', 'unknown')}")
    
    return "\n".join(parts)
