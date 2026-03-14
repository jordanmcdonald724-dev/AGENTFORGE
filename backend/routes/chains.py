"""
Quick Actions & Agent Chains Routes
====================================
Routes for quick actions and multi-agent chain execution.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
from typing import List, Optional
from core.database import db
from core.clients import llm_client
from core.utils import serialize_doc, logger
from models.project import QuickActionRequest
import json
import re

router = APIRouter(tags=["chains"])


QUICK_ACTIONS = {
    "landing_page": {
        "id": "landing_page",
        "name": "Landing Page",
        "description": "Generate a complete landing page with hero, features, contact",
        "icon": "layout",
        "chain": ["FORGE"],
        "prompt": """Generate a complete, modern React landing page. DO NOT ask questions, just build it.

Create these files:

1. src/App.js - Main app with routing
2. src/components/Hero.jsx - Hero section with headline, subtext, CTA button
3. src/components/Features.jsx - 3 feature cards with icons
4. src/components/Contact.jsx - Contact form (name, email, message)
5. src/components/Footer.jsx - Simple footer
6. src/index.css - Tailwind styles, dark modern theme

Use:
- React 18 with functional components
- Tailwind CSS for styling
- Lucide React for icons
- Dark theme with blue accents
- Responsive design
- Smooth animations

Generate ALL the code now. Include FULL file contents with ```javascript:filepath syntax."""
    },
    "player_controller": {
        "id": "player_controller",
        "name": "Player Controller",
        "description": "Generate a complete player movement system",
        "icon": "gamepad",
        "chain": ["FORGE"],
        "prompt": """Generate a COMPLETE player controller system for Unreal Engine 5. DO NOT ask questions, just build with these defaults.

Create ALL these files with full implementations:

1. Source/OceanCivilizationSimulator/Player/OCSPlayerController.h
2. Source/OceanCivilizationSimulator/Player/OCSPlayerController.cpp  
3. Source/OceanCivilizationSimulator/Player/OCSCharacterMovement.h
4. Source/OceanCivilizationSimulator/Player/OCSCharacterMovement.cpp

Include:
- WASD movement (walk: 300, run: 500, sprint: 700 units/s)
- Sprint (Shift key, 1.4x multiplier)
- Crouch (Ctrl key, 0.5x speed, reduced capsule to 44,48)
- Jump velocity 500, coyote time 0.15s
- Mouse look with 45 pitch clamp
- Ground detection with line traces

Use UPROPERTY/UFUNCTION macros, make BlueprintCallable.

Output with ```cpp:filepath format NOW."""
    },
    "inventory_system": {
        "id": "inventory_system",
        "name": "Inventory System",
        "description": "Generate a flexible inventory system",
        "icon": "package",
        "chain": ["COMMANDER", "ATLAS", "FORGE"],
        "prompt": """Design and implement a complete inventory system:
- Item base class with properties
- Inventory container with slots
- Add/remove/move items
- Save/load functionality
For {engine_type} with best practices."""
    },
    "save_system": {
        "id": "save_system",
        "name": "Save/Load System",
        "description": "Generate a save game system",
        "icon": "save",
        "chain": ["COMMANDER", "FORGE"],
        "prompt": """Create a robust save/load system:
- Serialization manager
- Auto-save functionality
- Multiple save slots
For {engine_type}."""
    },
    "health_system": {
        "id": "health_system",
        "name": "Health & Damage",
        "description": "Generate health and damage system",
        "icon": "heart",
        "chain": ["COMMANDER", "FORGE"],
        "prompt": """Create a health and damage system:
- Health component with max/current health
- Damage types and resistance
- Healing mechanics
- UI hooks for health bars
For {engine_type}."""
    },
    "ai_behavior": {
        "id": "ai_behavior",
        "name": "AI Behavior Tree",
        "description": "Generate enemy AI with behavior tree",
        "icon": "bot",
        "chain": ["COMMANDER", "ATLAS", "FORGE"],
        "prompt": """Create an AI system with behavior trees:
- Behavior tree base nodes
- Common behaviors (Patrol, Chase, Attack)
- Perception system
For {engine_type}."""
    }
}


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
