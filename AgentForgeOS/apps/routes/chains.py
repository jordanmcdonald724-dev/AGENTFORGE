"""
Quick Actions & Agent Chains Routes
====================================
Routes for quick actions and multi-agent chain execution.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
from typing import List, Optional
from engine.core.database import db
from providers.clients import llm_client
from services.utils import serialize_doc, logger
from models.project import QuickActionRequest
import json
import re

router = APIRouter(tags=["chains"])

# Import QUICK_ACTIONS from server.py to maintain single source of truth
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import QUICK_ACTIONS


@router.get("/quick-actions")
async def get_quick_actions():
    """Get available quick actions"""
    return list(QUICK_ACTIONS.values())


@router.post("/quick-actions/execute")
async def execute_quick_action(project_id: str, action_id: str, parameters: dict = None):
    """Execute a quick action"""
    if action_id not in QUICK_ACTIONS:
        raise HTTPException(status_code=404, detail=f"Quick action {action_id} not found")
    
    action = QUICK_ACTIONS[action_id]
    prompt = action["prompt"]
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    engine_type = project.get("engine_version", "unreal")
    prompt = prompt.replace("{engine_type}", engine_type)
    
    if parameters:
        for key, value in parameters.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
    
    agents = await db.agents.find({}, {"_id": 0}).to_list(10)
    chain = action.get("chain", ["COMMANDER"])
    target_agent = next((a for a in agents if a["name"].upper() == chain[0].upper()), agents[0])
    
    context = await _build_context(project_id)
    
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
        code_blocks = _extract_code_blocks(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action failed: {str(e)}")
    
    return {
        "response": result,
        "code_blocks": code_blocks,
        "action": action["name"],
        "agent": target_agent["name"]
    }


@router.post("/quick-actions/execute/stream")
async def stream_quick_action(request: QuickActionRequest):
    """Execute a quick action with streaming"""
    project_id = request.project_id
    action_id = request.action_id
    parameters = request.parameters
    
    if action_id not in QUICK_ACTIONS:
        raise HTTPException(status_code=404, detail=f"Quick action {action_id} not found")
    
    action = QUICK_ACTIONS[action_id]
    prompt = action["prompt"]
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    engine_type = project.get("engine_version", "unreal") if project else "unreal"
    prompt = prompt.replace("{engine_type}", engine_type)
    
    agents = await db.agents.find({}, {"_id": 0}).to_list(10)
    chain = action.get("chain", ["COMMANDER"])
    target_agent = next((a for a in agents if a["name"].upper() == chain[0].upper()), agents[0])
    
    context = await _build_context(project_id)
    
    async def generate():
        yield f"data: {json.dumps({'type': 'start', 'agent': target_agent['name']})}\n\n"
        
        full_content = ""
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
                    content = chunk.choices[0].delta.content
                    full_content += content
                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
            
            code_blocks = _extract_code_blocks(full_content)
            yield f"data: {json.dumps({'type': 'done', 'code_blocks': code_blocks})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/chain")
async def execute_agent_chain(project_id: str, message: str, chain: List[str] = None, auto_execute: bool = True):
    """Execute a multi-agent chain"""
    agents = await db.agents.find({}, {"_id": 0}).to_list(10)
    chain = chain or ["COMMANDER", "FORGE", "SENTINEL"]
    
    context = await _build_context(project_id)
    results = []
    current_message = message
    
    for agent_name in chain:
        agent = next((a for a in agents if a["name"].upper() == agent_name.upper()), None)
        if not agent:
            continue
        
        try:
            response = llm_client.chat.completions.create(
                model=agent.get("model", "google/gemini-2.5-flash"),
                messages=[
                    {"role": "system", "content": agent["system_prompt"] + f"\n\nCONTEXT:\n{context}"},
                    {"role": "user", "content": current_message}
                ],
                max_tokens=8000,
                temperature=0.7
            )
            result = response.choices[0].message.content
            
            results.append({
                "agent": agent["name"],
                "response": result,
                "code_blocks": _extract_code_blocks(result)
            })
            
            if auto_execute:
                current_message = f"Previous agent ({agent['name']}) produced:\n{result}\n\nContinue with your part."
        except Exception as e:
            results.append({
                "agent": agent["name"],
                "error": str(e)
            })
            break
    
    return {"chain": chain, "results": results}


@router.post("/chain/stream")
async def stream_agent_chain(project_id: str, message: str, chain: List[str] = None):
    """Execute a multi-agent chain with streaming"""
    agents = await db.agents.find({}, {"_id": 0}).to_list(10)
    chain = chain or ["COMMANDER", "FORGE"]
    
    context = await _build_context(project_id)
    
    async def generate():
        current_message = message
        
        for agent_name in chain:
            agent = next((a for a in agents if a["name"].upper() == agent_name.upper()), None)
            if not agent:
                continue
            
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': agent['name']})}\n\n"
            
            full_content = ""
            try:
                stream = llm_client.chat.completions.create(
                    model=agent.get("model", "google/gemini-2.5-flash"),
                    messages=[
                        {"role": "system", "content": agent["system_prompt"] + f"\n\nCONTEXT:\n{context}"},
                        {"role": "user", "content": current_message}
                    ],
                    max_tokens=8000,
                    temperature=0.7,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_content += content
                        yield f"data: {json.dumps({'type': 'content', 'agent': agent['name'], 'content': content})}\n\n"
                
                code_blocks = _extract_code_blocks(full_content)
                yield f"data: {json.dumps({'type': 'agent_done', 'agent': agent['name'], 'code_blocks': code_blocks})}\n\n"
                
                current_message = f"Previous agent ({agent['name']}) produced:\n{full_content}\n\nContinue."
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'agent': agent['name'], 'error': str(e)})}\n\n"
                break
        
        yield f"data: {json.dumps({'type': 'chain_done'})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


def _extract_code_blocks(content: str) -> List[dict]:
    """Extract code blocks from response"""
    pattern = r'```(\w+)?(?::([^\n]+))?\n([\s\S]*?)```'
    matches = re.findall(pattern, content)
    blocks = []
    for match in matches:
        language = match[0] or "text"
        filepath = match[1] or ""
        code = match[2].strip()
        filename = filepath.split('/')[-1] if filepath else f"code.{language}"
        blocks.append({
            "language": language,
            "filepath": filepath,
            "filename": filename,
            "content": code
        })
    return blocks


async def _build_context(project_id: str) -> str:
    """Build project context"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        return ""
    
    parts = [
        f"PROJECT: {project['name']}",
        f"TYPE: {project['type']}",
        f"ENGINE: {project.get('engine_version', 'N/A')}",
        f"STATUS: {project['status']}"
    ]
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(20)
    if files:
        parts.append(f"\nFILES ({len(files)}):")
        for f in files[:10]:
            parts.append(f"  - {f.get('filepath')}")
    
    return "\n".join(parts)
