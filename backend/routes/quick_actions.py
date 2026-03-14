"""
Quick Actions & Preview Routes
==============================
Quick actions, custom actions, live preview, and project utilities.
Extracted from server.py as part of refactoring.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from core.database import db
import uuid
import logging

router = APIRouter(tags=["quick-actions"])
logger = logging.getLogger(__name__)


# Import required functions from server.py
def get_quick_actions():
    """Get QUICK_ACTIONS from server.py"""
    from server import QUICK_ACTIONS
    return QUICK_ACTIONS


async def execute_agent_chain_fn(request):
    """Execute agent chain from server.py"""
    from server import execute_agent_chain
    return await execute_agent_chain(request)


async def stream_agent_chain_fn(request):
    """Stream agent chain from server.py"""
    from server import stream_agent_chain
    return await stream_agent_chain(request)


def get_agent_chain_request():
    """Get AgentChainRequest model from server.py"""
    from server import AgentChainRequest
    return AgentChainRequest


def serialize_doc(doc):
    """Serialize document from server.py"""
    from server import serialize_doc
    return serialize_doc(doc)


# ============ MODELS ============

class QuickActionRequest(BaseModel):
    action_id: str
    project_id: str
    parameters: Dict[str, Any] = {}


class CustomActionCreate(BaseModel):
    name: str
    description: str
    prompt: str
    chain: List[str]
    icon: str = "zap"
    category: str = "custom"
    is_global: bool = False
    project_id: Optional[str] = None


class CustomQuickAction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    prompt: str
    chain: List[str]
    icon: str = "zap"
    category: str = "custom"
    is_global: bool = False
    project_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProjectDuplicateRequest(BaseModel):
    new_name: str


# ============ QUICK ACTIONS ============

@router.get("/quick-actions")
async def get_quick_actions_list():
    """Get available quick actions"""
    QUICK_ACTIONS = get_quick_actions()
    return list(QUICK_ACTIONS.values())


@router.post("/quick-actions/execute")
async def execute_quick_action(request: QuickActionRequest):
    """Execute a quick action"""
    QUICK_ACTIONS = get_quick_actions()
    AgentChainRequest = get_agent_chain_request()
    
    action = QUICK_ACTIONS.get(request.action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Quick action not found")
    
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    prompt = action['prompt'].format(
        engine_type=project.get('type', 'game'),
        engine_version=project.get('engine_version', ''),
        **request.parameters
    )
    
    chain_request = AgentChainRequest(
        project_id=request.project_id,
        message=prompt,
        chain=action['chain']
    )
    
    return await execute_agent_chain_fn(chain_request)


@router.post("/quick-actions/execute/stream")
async def stream_quick_action(request: QuickActionRequest):
    """Stream execute a quick action"""
    QUICK_ACTIONS = get_quick_actions()
    AgentChainRequest = get_agent_chain_request()
    
    action = QUICK_ACTIONS.get(request.action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Quick action not found")
    
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    prompt = action['prompt'].format(
        engine_type=project.get('type', 'game'),
        engine_version=project.get('engine_version', ''),
        **request.parameters
    )
    
    chain_request = AgentChainRequest(
        project_id=request.project_id,
        message=prompt,
        chain=action['chain']
    )
    
    return await stream_agent_chain_fn(chain_request)


# ============ LIVE PREVIEW ============

@router.get("/projects/{project_id}/preview")
async def get_project_preview(project_id: str):
    """Get live preview HTML for web projects"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project['type'] not in ['web_app', 'web_game']:
        raise HTTPException(status_code=400, detail="Preview only available for web projects")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    html_file = next((f for f in files if f['filepath'].endswith('.html') or f['filename'] == 'index.html'), None)
    css_files = [f for f in files if f['filepath'].endswith('.css')]
    js_files = [f for f in files if f['filepath'].endswith('.js')]
    
    if not html_file:
        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview</title>
    <style>{css}</style>
</head>
<body>
    <div id="app">
        <h1>Project Preview</h1>
        <p>No index.html found. Create an HTML file to see your preview.</p>
    </div>
    <script>{js}</script>
</body>
</html>"""
        css_content = "\n".join([f['content'] for f in css_files])
        js_content = "\n".join([f['content'] for f in js_files])
        html_content = html_content.format(css=css_content, js=js_content)
    else:
        html_content = html_file['content']
        
        if css_files and '<style>' not in html_content:
            css_content = "\n".join([f['content'] for f in css_files])
            html_content = html_content.replace('</head>', f'<style>{css_content}</style></head>')
        
        if js_files and '</body>' in html_content:
            js_content = "\n".join([f['content'] for f in js_files])
            html_content = html_content.replace('</body>', f'<script>{js_content}</script></body>')
    
    return HTMLResponse(content=html_content)


@router.get("/projects/{project_id}/preview-data")
async def get_preview_data(project_id: str):
    """Get preview data including HTML, CSS, JS separately"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    html_files = [f for f in files if f['filepath'].endswith('.html')]
    css_files = [f for f in files if f['filepath'].endswith('.css')]
    js_files = [f for f in files if f['filepath'].endswith('.js')]
    
    return {
        "html": [{"path": f['filepath'], "content": f['content']} for f in html_files],
        "css": [{"path": f['filepath'], "content": f['content']} for f in css_files],
        "js": [{"path": f['filepath'], "content": f['content']} for f in js_files],
        "project_type": project['type']
    }


# ============ CUSTOM QUICK ACTIONS ============

@router.post("/custom-actions")
async def create_custom_action(action_data: CustomActionCreate):
    """Create a custom quick action"""
    action = CustomQuickAction(
        name=action_data.name,
        description=action_data.description,
        prompt=action_data.prompt,
        chain=action_data.chain,
        icon=action_data.icon,
        category=action_data.category,
        is_global=action_data.is_global,
        project_id=action_data.project_id
    )
    doc = action.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.custom_actions.insert_one(doc)
    return serialize_doc(doc)


@router.get("/custom-actions")
async def get_custom_actions(project_id: Optional[str] = None):
    """Get custom quick actions (global + project-specific)"""
    query = {"$or": [{"is_global": True}]}
    if project_id:
        query["$or"].append({"project_id": project_id})
    
    actions = await db.custom_actions.find(query, {"_id": 0}).to_list(100)
    return actions


@router.delete("/custom-actions/{action_id}")
async def delete_custom_action(action_id: str):
    await db.custom_actions.delete_one({"id": action_id})
    return {"success": True}


@router.post("/custom-actions/{action_id}/execute")
async def execute_custom_action(action_id: str, project_id: str):
    """Execute a custom quick action"""
    AgentChainRequest = get_agent_chain_request()
    
    action = await db.custom_actions.find_one({"id": action_id}, {"_id": 0})
    if not action:
        raise HTTPException(status_code=404, detail="Custom action not found")
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    prompt = action['prompt'].replace('{engine_type}', project.get('type', 'game'))
    prompt = prompt.replace('{engine_version}', project.get('engine_version', ''))
    prompt = prompt.replace('{project_name}', project.get('name', ''))
    
    chain_request = AgentChainRequest(
        project_id=project_id,
        message=prompt,
        chain=action['chain']
    )
    
    return await execute_agent_chain_fn(chain_request)


@router.post("/custom-actions/{action_id}/execute/stream")
async def stream_custom_action(action_id: str, project_id: str):
    """Stream execute a custom quick action"""
    AgentChainRequest = get_agent_chain_request()
    
    action = await db.custom_actions.find_one({"id": action_id}, {"_id": 0})
    if not action:
        raise HTTPException(status_code=404, detail="Custom action not found")
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    prompt = action['prompt'].replace('{engine_type}', project.get('type', 'game'))
    prompt = prompt.replace('{engine_version}', project.get('engine_version', ''))
    
    chain_request = AgentChainRequest(
        project_id=project_id,
        message=prompt,
        chain=action['chain']
    )
    
    return await stream_agent_chain_fn(chain_request)
