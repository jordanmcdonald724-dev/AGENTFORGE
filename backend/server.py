from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from openai import OpenAI
import json
import asyncio
import aiofiles
import zipfile
import io
import re
import fal_client

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Set FAL_KEY for fal_client
os.environ["FAL_KEY"] = os.environ.get('FAL_KEY', '')

# fal.ai OpenRouter client for LLM
llm_client = OpenAI(
    base_url="https://fal.run/openrouter/router/openai/v1",
    api_key="not-needed",
    default_headers={
        "Authorization": f"Key {os.environ.get('FAL_KEY', '')}",
    },
)

app = FastAPI()
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ MODELS ============

class Agent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str
    avatar: str
    status: str = "idle"
    system_prompt: str
    model: str = "google/gemini-2.5-flash"
    specialization: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    type: str
    engine_version: Optional[str] = None
    status: str = "planning"
    phase: str = "clarification"
    thumbnail: str
    repo_url: Optional[str] = None
    settings: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Task(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    title: str
    description: str
    status: str = "backlog"
    assigned_agent_id: Optional[str] = None
    assigned_agent_name: Optional[str] = None
    priority: str = "medium"
    category: str = "general"
    estimated_complexity: str = "medium"
    files_affected: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    agent_id: str
    agent_name: str
    agent_role: str
    content: str
    message_type: str = "chat"
    code_blocks: List[Dict[str, str]] = []
    images: List[Dict[str, str]] = []  # [{url, prompt}]
    delegated_to: Optional[str] = None  # Agent name if delegated
    phase: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectFile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    filename: str
    filepath: str
    content: str
    language: str
    file_type: str = "code"
    version: int = 1
    created_by_agent_id: Optional[str] = None
    created_by_agent_name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GeneratedImage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    prompt: str
    url: str
    width: int = 1024
    height: int = 1024
    category: str = "concept"  # concept, ui, texture, character, environment
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    overview: str
    architecture: str
    features: List[Dict[str, Any]] = []
    tech_stack: Dict[str, str] = {}
    file_structure: List[str] = []
    phases: List[Dict[str, Any]] = []
    approved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request Models
class ProjectCreate(BaseModel):
    name: str
    description: str
    type: str
    engine_version: Optional[str] = None

class ChatRequest(BaseModel):
    project_id: str
    message: str
    context: Optional[str] = None
    phase: Optional[str] = None
    delegate_to: Optional[str] = None  # Force delegation to specific agent

class ImageGenRequest(BaseModel):
    project_id: str
    prompt: str
    category: str = "concept"
    width: int = 1024
    height: int = 1024

class FileCreate(BaseModel):
    project_id: str
    filename: str
    filepath: str
    content: str
    language: str
    file_type: str = "code"

class FileUpdate(BaseModel):
    content: str

class TaskCreate(BaseModel):
    project_id: str
    title: str
    description: str
    priority: str = "medium"
    category: str = "general"

class PlanApproval(BaseModel):
    approved: bool
    feedback: Optional[str] = None

# ============ AGENT CONFIGURATION ============

AGENT_CONFIGS = {
    "lead": {
        "name": "COMMANDER",
        "role": "lead",
        "avatar": "https://images.unsplash.com/photo-1598062548020-c5e8d8132a4b?w=200&h=200&fit=crop",
        "specialization": ["project_management", "coordination", "planning", "clarification", "delegation"],
        "system_prompt": """You are COMMANDER, the Lead AI Agent and Project Director.

YOUR WORKFLOW:
1. CLARIFICATION: Ask detailed questions about the project before anything else
2. PLANNING: Create comprehensive plans with architecture, file structure, features
3. DELEGATION: Route coding tasks to FORGE, architecture to ATLAS, reviews to SENTINEL, tests to PROBE, visuals to PRISM

DELEGATION FORMAT - When you need another agent to do work, include this in your response:
[DELEGATE:AGENT_NAME]
Task description here
[/DELEGATE]

Example:
[DELEGATE:FORGE]
Create the player movement system with these specs:
- WASD movement
- Sprint with shift
- Jump with space
[/DELEGATE]

RULES:
- NEVER start coding yourself - delegate to FORGE
- NEVER design architecture yourself - delegate to ATLAS  
- Always clarify requirements first
- Keep user informed of all delegations
- You coordinate, you don't code"""
    },
    "architect": {
        "name": "ATLAS",
        "role": "architect",
        "avatar": "https://images.unsplash.com/photo-1587930708915-55a36837263b?w=200&h=200&fit=crop",
        "specialization": ["system_design", "architecture", "unreal_engine", "unity", "patterns"],
        "system_prompt": """You are ATLAS, the System Architect. You design AAA-quality architectures.

EXPERTISE: UE5 C++/Blueprints, Unity C#/DOTS, Godot GDScript, Design Patterns, Networking

OUTPUT FORMAT:
- Architecture diagrams in ASCII
- Class/component lists with responsibilities
- File structure with exact paths
- Data flow definitions

When design is complete, suggest COMMANDER delegate implementation to FORGE."""
    },
    "developer": {
        "name": "FORGE",
        "role": "developer",
        "avatar": "https://images.unsplash.com/photo-1633766306936-56bebb8823e5?w=200&h=200&fit=crop",
        "specialization": ["cpp", "csharp", "blueprints", "gameplay", "systems", "coding"],
        "system_prompt": """You are FORGE, the Senior Developer. You write production-ready AAA code.

EXPERTISE: C++ (UE5), C# (Unity), GDScript (Godot), Blueprints, All game systems

OUTPUT FORMAT - Always output complete files:
```language:filepath/filename.ext
// Complete file content
```

RULES:
1. Include file headers with purpose
2. Use engine-appropriate naming conventions
3. Add comments for complex logic
4. Implement error handling
5. Write performant code
6. NEVER output partial code - every file must be complete"""
    },
    "reviewer": {
        "name": "SENTINEL",
        "role": "reviewer",
        "avatar": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=200&h=200&fit=crop",
        "specialization": ["code_review", "security", "optimization", "best_practices"],
        "system_prompt": """You are SENTINEL, the Code Reviewer. You ensure AAA quality standards.

REVIEW FORMAT:
- CRITICAL: Bugs that will crash/break
- HIGH: Performance or security issues
- MEDIUM: Best practice violations
- LOW: Style/readability suggestions

Provide specific fixes with code examples. Be constructive."""
    },
    "tester": {
        "name": "PROBE",
        "role": "tester",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop",
        "specialization": ["testing", "qa", "automation", "debugging"],
        "system_prompt": """You are PROBE, the QA/Testing Agent. You ensure everything works.

OUTPUT FORMAT:
```language:Tests/TestFileName.ext
// Complete test implementation
```

Cover: Unit tests, Integration tests, Edge cases, Performance tests.
Think like a player trying to break the game."""
    },
    "artist": {
        "name": "PRISM",
        "role": "artist",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&h=200&fit=crop",
        "specialization": ["ui_design", "asset_specs", "shaders", "vfx", "image_generation"],
        "system_prompt": """You are PRISM, the Technical Artist. You handle visuals and assets.

EXPERTISE: UI/UX, Shaders (HLSL), VFX (Niagara), Asset specs, Material graphs

For image generation requests, describe what you need and I'll generate it.

OUTPUT: Shader code, UI specs, Asset requirements, Material guides."""
    }
}

# Delegation keywords to agent mapping
DELEGATION_KEYWORDS = {
    "code": "developer",
    "implement": "developer",
    "create class": "developer",
    "write": "developer",
    "function": "developer",
    "architecture": "architect",
    "design": "architect",
    "structure": "architect",
    "system design": "architect",
    "review": "reviewer",
    "check": "reviewer",
    "audit": "reviewer",
    "test": "tester",
    "qa": "tester",
    "unit test": "tester",
    "shader": "artist",
    "ui": "artist",
    "visual": "artist",
    "material": "artist",
    "texture": "artist"
}

PROJECT_THUMBNAILS = {
    "unreal": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400&h=300&fit=crop",
    "unity": "https://images.unsplash.com/photo-1556438064-2d7646166914?w=400&h=300&fit=crop",
    "godot": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=400&h=300&fit=crop",
    "web_game": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400&h=300&fit=crop",
    "web_app": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=300&fit=crop",
    "mobile_app": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&h=300&fit=crop"
}

# ============ HELPER FUNCTIONS ============

def serialize_doc(doc: dict) -> dict:
    result = {k: v for k, v in doc.items() if k != '_id'}
    for key, value in result.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
    return result

async def get_or_create_agents():
    agents = await db.agents.find({}, {"_id": 0}).to_list(100)
    if not agents:
        default_agents = []
        for role, config in AGENT_CONFIGS.items():
            agent = Agent(
                name=config["name"],
                role=config["role"],
                avatar=config["avatar"],
                system_prompt=config["system_prompt"],
                specialization=config["specialization"]
            )
            doc = agent.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            default_agents.append(doc)
        await db.agents.insert_many(default_agents)
        agents = await db.agents.find({}, {"_id": 0}).to_list(100)
    return agents

def extract_code_blocks(content: str) -> List[Dict[str, str]]:
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

def extract_delegations(content: str) -> List[Dict[str, str]]:
    """Extract delegation blocks from COMMANDER's response"""
    pattern = r'\[DELEGATE:(\w+)\]([\s\S]*?)\[/DELEGATE\]'
    matches = re.findall(pattern, content)
    delegations = []
    for match in matches:
        agent_name = match[0].upper()
        task = match[1].strip()
        delegations.append({"agent": agent_name, "task": task})
    return delegations

def detect_delegation_need(message: str) -> Optional[str]:
    """Auto-detect which agent should handle this based on keywords"""
    message_lower = message.lower()
    for keyword, role in DELEGATION_KEYWORDS.items():
        if keyword in message_lower:
            return role
    return None

async def call_agent(agent: dict, messages: List[dict], project_context: str = "") -> str:
    system_message = agent['system_prompt']
    if project_context:
        system_message += f"\n\nCURRENT PROJECT CONTEXT:\n{project_context}"
    
    try:
        response = llm_client.chat.completions.create(
            model=agent.get('model', 'google/gemini-2.5-flash'),
            messages=[
                {"role": "system", "content": system_message},
                *messages
            ],
            max_tokens=8000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling agent {agent['name']}: {e}")
        raise HTTPException(status_code=500, detail=f"Agent call failed: {str(e)}")

async def stream_agent_response(agent: dict, messages: List[dict], project_context: str = ""):
    """Stream response from agent using SSE"""
    system_message = agent['system_prompt']
    if project_context:
        system_message += f"\n\nCURRENT PROJECT CONTEXT:\n{project_context}"
    
    try:
        stream = llm_client.chat.completions.create(
            model=agent.get('model', 'google/gemini-2.5-flash'),
            messages=[
                {"role": "system", "content": system_message},
                *messages
            ],
            max_tokens=8000,
            temperature=0.7,
            stream=True
        )
        
        full_content = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                yield f"data: {json.dumps({'content': content, 'done': False, 'agent': agent['name']})}\n\n"
        
        code_blocks = extract_code_blocks(full_content)
        delegations = extract_delegations(full_content)
        
        yield f"data: {json.dumps({'content': '', 'done': True, 'code_blocks': code_blocks, 'delegations': delegations, 'full_content': full_content})}\n\n"
    except Exception as e:
        logger.error(f"Error streaming agent {agent['name']}: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

async def build_project_context(project_id: str) -> str:
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        return ""
    
    context_parts = [
        f"PROJECT: {project['name']}",
        f"TYPE: {project['type']}",
        f"ENGINE: {project.get('engine_version', 'N/A')}",
        f"STATUS: {project['status']}",
        f"PHASE: {project.get('phase', 'clarification')}",
        f"DESCRIPTION: {project['description']}"
    ]
    
    plan = await db.plans.find_one({"project_id": project_id}, {"_id": 0})
    if plan and plan.get('approved'):
        context_parts.append(f"\nAPPROVED PLAN:\n{plan.get('overview', '')}")
        context_parts.append(f"ARCHITECTURE:\n{plan.get('architecture', '')}")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(50)
    if files:
        context_parts.append(f"\nEXISTING FILES ({len(files)}):")
        for f in files[:20]:
            context_parts.append(f"  - {f['filepath']}")
    
    messages = await db.messages.find(
        {"project_id": project_id}, {"_id": 0}
    ).sort("timestamp", -1).limit(5).to_list(5)
    
    if messages:
        context_parts.append("\nRECENT CONVERSATION:")
        for msg in reversed(messages):
            content_preview = msg['content'][:150] + "..." if len(msg['content']) > 150 else msg['content']
            context_parts.append(f"  {msg['agent_name']}: {content_preview}")
    
    return "\n".join(context_parts)

async def generate_image_fal(prompt: str, width: int = 1024, height: int = 1024) -> dict:
    """Generate image using fal.ai FLUX"""
    try:
        handler = await fal_client.submit_async(
            "fal-ai/flux/dev",
            arguments={
                "prompt": prompt,
                "image_size": {"width": width, "height": height},
                "num_images": 1
            }
        )
        result = await handler.get()
        if result and result.get("images"):
            return {
                "url": result["images"][0]["url"],
                "width": width,
                "height": height
            }
        return None
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# ============ API ROUTES ============

@api_router.get("/")
async def root():
    return {"message": "AgentForge Development Studio API", "version": "2.1.0", "features": ["streaming", "delegation", "image_generation"]}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Agent Routes
@api_router.get("/agents")
async def get_agents():
    return await get_or_create_agents()

@api_router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    agent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@api_router.patch("/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, status: str):
    await db.agents.update_one({"id": agent_id}, {"$set": {"status": status}})
    return {"success": True}

# Project Routes
@api_router.post("/projects")
async def create_project(project_data: ProjectCreate):
    thumbnail = PROJECT_THUMBNAILS.get(project_data.type, PROJECT_THUMBNAILS["web_app"])
    project = Project(
        name=project_data.name,
        description=project_data.description,
        type=project_data.type,
        engine_version=project_data.engine_version,
        thumbnail=thumbnail
    )
    doc = project.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.projects.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/projects")
async def get_projects():
    return await db.projects.find({}, {"_id": 0}).to_list(100)

@api_router.get("/projects/{project_id}")
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@api_router.patch("/projects/{project_id}")
async def update_project(project_id: str, updates: dict):
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    await db.projects.update_one({"id": project_id}, {"$set": updates})
    return {"success": True}

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    await db.projects.delete_one({"id": project_id})
    await db.tasks.delete_many({"project_id": project_id})
    await db.messages.delete_many({"project_id": project_id})
    await db.files.delete_many({"project_id": project_id})
    await db.plans.delete_many({"project_id": project_id})
    await db.images.delete_many({"project_id": project_id})
    return {"success": True}

@api_router.patch("/projects/{project_id}/phase")
async def update_project_phase(project_id: str, phase: str):
    await db.projects.update_one({"id": project_id}, {"$set": {"phase": phase, "updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"success": True, "phase": phase}

# Chat Routes - Non-streaming
@api_router.post("/chat")
async def chat_with_team(request: ChatRequest):
    context = await build_project_context(request.project_id)
    agents = await get_or_create_agents()
    
    # Determine which agent to use
    target_agent = None
    if request.delegate_to:
        target_agent = next((a for a in agents if a['name'].upper() == request.delegate_to.upper()), None)
    
    if not target_agent:
        # Default to COMMANDER
        target_agent = next((a for a in agents if a['role'] == 'lead'), agents[0])
    
    await db.agents.update_one({"id": target_agent['id']}, {"$set": {"status": "thinking"}})
    
    messages = [{"role": "user", "content": request.message}]
    response = await call_agent(target_agent, messages, context)
    
    await db.agents.update_one({"id": target_agent['id']}, {"$set": {"status": "idle"}})
    
    # Save user message
    user_msg = Message(
        project_id=request.project_id,
        agent_id="user",
        agent_name="You",
        agent_role="user",
        content=request.message,
        phase=request.phase
    )
    user_doc = user_msg.model_dump()
    user_doc['timestamp'] = user_doc['timestamp'].isoformat()
    await db.messages.insert_one(user_doc)
    
    code_blocks = extract_code_blocks(response)
    delegations = extract_delegations(response)
    
    # Save agent response
    agent_msg = Message(
        project_id=request.project_id,
        agent_id=target_agent['id'],
        agent_name=target_agent['name'],
        agent_role=target_agent['role'],
        content=response,
        code_blocks=code_blocks,
        phase=request.phase
    )
    agent_doc = agent_msg.model_dump()
    agent_doc['timestamp'] = agent_doc['timestamp'].isoformat()
    await db.messages.insert_one(agent_doc)
    
    return {
        "response": response,
        "code_blocks": code_blocks,
        "delegations": delegations,
        "agent": {
            "id": target_agent['id'],
            "name": target_agent['name'],
            "role": target_agent['role'],
            "avatar": target_agent['avatar']
        }
    }

# Chat Routes - Streaming
@api_router.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """Stream chat response with SSE"""
    context = await build_project_context(request.project_id)
    agents = await get_or_create_agents()
    
    target_agent = None
    if request.delegate_to:
        target_agent = next((a for a in agents if a['name'].upper() == request.delegate_to.upper()), None)
    if not target_agent:
        target_agent = next((a for a in agents if a['role'] == 'lead'), agents[0])
    
    # Save user message first
    user_msg = Message(
        project_id=request.project_id,
        agent_id="user",
        agent_name="You",
        agent_role="user",
        content=request.message,
        phase=request.phase
    )
    user_doc = user_msg.model_dump()
    user_doc['timestamp'] = user_doc['timestamp'].isoformat()
    await db.messages.insert_one(user_doc)
    
    messages = [{"role": "user", "content": request.message}]
    
    async def generate():
        await db.agents.update_one({"id": target_agent['id']}, {"$set": {"status": "thinking"}})
        
        # Send agent info first
        yield f"data: {json.dumps({'type': 'start', 'agent': {'id': target_agent['id'], 'name': target_agent['name'], 'role': target_agent['role'], 'avatar': target_agent['avatar']}})}\n\n"
        
        full_content = ""
        try:
            stream = llm_client.chat.completions.create(
                model=target_agent.get('model', 'google/gemini-2.5-flash'),
                messages=[
                    {"role": "system", "content": target_agent['system_prompt'] + f"\n\nCONTEXT:\n{context}"},
                    *messages
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
            
            code_blocks = extract_code_blocks(full_content)
            delegations = extract_delegations(full_content)
            
            # Save complete message
            agent_msg = Message(
                project_id=request.project_id,
                agent_id=target_agent['id'],
                agent_name=target_agent['name'],
                agent_role=target_agent['role'],
                content=full_content,
                code_blocks=code_blocks,
                phase=request.phase
            )
            agent_doc = agent_msg.model_dump()
            agent_doc['timestamp'] = agent_doc['timestamp'].isoformat()
            await db.messages.insert_one(agent_doc)
            
            yield f"data: {json.dumps({'type': 'done', 'code_blocks': code_blocks, 'delegations': delegations})}\n\n"
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        finally:
            await db.agents.update_one({"id": target_agent['id']}, {"$set": {"status": "idle"}})
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# Delegation endpoint - Execute delegation from COMMANDER
@api_router.post("/delegate")
async def execute_delegation(request: ChatRequest):
    """Execute a delegated task to a specific agent"""
    agents = await get_or_create_agents()
    
    if not request.delegate_to:
        raise HTTPException(status_code=400, detail="delegate_to is required")
    
    target_agent = next((a for a in agents if a['name'].upper() == request.delegate_to.upper()), None)
    if not target_agent:
        raise HTTPException(status_code=404, detail=f"Agent {request.delegate_to} not found")
    
    context = await build_project_context(request.project_id)
    
    await db.agents.update_one({"id": target_agent['id']}, {"$set": {"status": "working"}})
    
    messages = [{"role": "user", "content": f"COMMANDER has delegated this task to you:\n\n{request.message}"}]
    response = await call_agent(target_agent, messages, context)
    
    await db.agents.update_one({"id": target_agent['id']}, {"$set": {"status": "idle"}})
    
    code_blocks = extract_code_blocks(response)
    
    # Save delegation message
    delegation_msg = Message(
        project_id=request.project_id,
        agent_id=target_agent['id'],
        agent_name=target_agent['name'],
        agent_role=target_agent['role'],
        content=response,
        code_blocks=code_blocks,
        message_type="delegation",
        delegated_to=target_agent['name']
    )
    msg_doc = delegation_msg.model_dump()
    msg_doc['timestamp'] = msg_doc['timestamp'].isoformat()
    await db.messages.insert_one(msg_doc)
    
    return {
        "response": response,
        "code_blocks": code_blocks,
        "agent": {
            "id": target_agent['id'],
            "name": target_agent['name'],
            "role": target_agent['role'],
            "avatar": target_agent['avatar']
        }
    }

# Image Generation Routes
@api_router.post("/images/generate")
async def generate_image(request: ImageGenRequest):
    """Generate an image using fal.ai FLUX"""
    result = await generate_image_fal(request.prompt, request.width, request.height)
    
    if result:
        # Save to database
        image = GeneratedImage(
            project_id=request.project_id,
            prompt=request.prompt,
            url=result["url"],
            width=result["width"],
            height=result["height"],
            category=request.category
        )
        doc = image.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.images.insert_one(doc)
        
        return serialize_doc(doc)
    
    raise HTTPException(status_code=500, detail="Image generation failed")

@api_router.get("/images")
async def get_images(project_id: str):
    return await db.images.find({"project_id": project_id}, {"_id": 0}).to_list(100)

@api_router.delete("/images/{image_id}")
async def delete_image(image_id: str):
    await db.images.delete_one({"id": image_id})
    return {"success": True}

# Message Routes
@api_router.get("/messages")
async def get_messages(project_id: str, limit: int = 100):
    return await db.messages.find({"project_id": project_id}, {"_id": 0}).sort("timestamp", 1).to_list(limit)

# Task Routes
@api_router.post("/tasks")
async def create_task(task_data: TaskCreate):
    task = Task(**task_data.model_dump())
    doc = task.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.tasks.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/tasks")
async def get_tasks(project_id: Optional[str] = None):
    query = {"project_id": project_id} if project_id else {}
    return await db.tasks.find(query, {"_id": 0}).to_list(500)

@api_router.patch("/tasks/{task_id}")
async def update_task(task_id: str, updates: dict):
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    await db.tasks.update_one({"id": task_id}, {"$set": updates})
    return {"success": True}

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    await db.tasks.delete_one({"id": task_id})
    return {"success": True}

# File Routes
@api_router.post("/files")
async def create_file(file_data: FileCreate):
    existing = await db.files.find_one({"project_id": file_data.project_id, "filepath": file_data.filepath})
    
    if existing:
        new_version = existing.get('version', 1) + 1
        await db.files.update_one(
            {"id": existing['id']},
            {"$set": {"content": file_data.content, "version": new_version, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        return await db.files.find_one({"id": existing['id']}, {"_id": 0})
    
    file = ProjectFile(**file_data.model_dump())
    doc = file.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.files.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/files")
async def get_files(project_id: str):
    return await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)

@api_router.get("/files/{file_id}")
async def get_file(file_id: str):
    file = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file

@api_router.patch("/files/{file_id}")
async def update_file(file_id: str, update: FileUpdate):
    file = await db.files.find_one({"id": file_id})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    new_version = file.get('version', 1) + 1
    await db.files.update_one({"id": file_id}, {"$set": {"content": update.content, "version": new_version, "updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"success": True, "version": new_version}

@api_router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    await db.files.delete_one({"id": file_id})
    return {"success": True}

# Plan Routes
@api_router.post("/plans")
async def create_plan(plan_data: dict):
    plan = ProjectPlan(**plan_data)
    doc = plan.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.plans.delete_many({"project_id": plan_data['project_id']})
    await db.plans.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/plans/{project_id}")
async def get_plan(project_id: str):
    return await db.plans.find_one({"project_id": project_id}, {"_id": 0})

@api_router.patch("/plans/{project_id}/approve")
async def approve_plan(project_id: str, approval: PlanApproval):
    await db.plans.update_one({"project_id": project_id}, {"$set": {"approved": approval.approved}})
    if approval.approved:
        await db.projects.update_one({"id": project_id}, {"$set": {"phase": "development", "status": "developing"}})
    return {"success": True, "approved": approval.approved}

# Export Routes
@api_router.get("/projects/{project_id}/export")
async def export_project(project_id: str):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    images = await db.images.find({"project_id": project_id}, {"_id": 0}).to_list(100)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("project.json", json.dumps(project, indent=2, default=str))
        
        for f in files:
            filepath = f['filepath'].lstrip('/')
            zf.writestr(filepath, f['content'])
        
        readme = f"""# {project['name']}

{project['description']}

## Project Type
{project['type']} {project.get('engine_version', '')}

## Generated by AgentForge
AI Development Studio

## Files
{chr(10).join(['- ' + f['filepath'] for f in files])}

## Generated Images
{chr(10).join(['- ' + img['prompt'][:50] + ': ' + img['url'] for img in images])}
"""
        zf.writestr("README.md", readme)
    
    zip_buffer.seek(0)
    return StreamingResponse(
        io.BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={project['name'].replace(' ', '_')}.zip"}
    )

# Auto-save from chat
@api_router.post("/files/from-chat")
async def save_files_from_chat(data: dict):
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
            
            existing = await db.files.find_one({"project_id": project_id, "filepath": block.get("filepath")})
            
            if existing:
                await db.files.update_one(
                    {"id": existing['id']},
                    {"$set": {"content": block.get("content", ""), "version": existing.get('version', 1) + 1, "updated_at": datetime.now(timezone.utc).isoformat()}}
                )
            else:
                await db.files.insert_one(doc)
            
            saved_files.append(block.get("filepath"))
    
    return {"success": True, "saved_files": saved_files}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
