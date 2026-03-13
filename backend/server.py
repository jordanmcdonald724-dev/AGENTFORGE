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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# fal.ai OpenRouter client
fal_client = OpenAI(
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
    type: str  # unreal, unity, godot, web_game, web_app, mobile_app
    engine_version: Optional[str] = None
    status: str = "planning"  # planning, designing, developing, testing, complete
    phase: str = "clarification"  # clarification, planning, development, review
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
    category: str = "general"  # architecture, coding, assets, testing, documentation
    estimated_complexity: str = "medium"  # simple, medium, complex, epic
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
    message_type: str = "chat"  # chat, code, plan, review, clarification, system
    code_blocks: List[Dict[str, str]] = []  # [{language, filename, content}]
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
    file_type: str = "code"  # code, config, asset, documentation
    version: int = 1
    created_by_agent_id: Optional[str] = None
    created_by_agent_name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
        "specialization": ["project_management", "coordination", "planning", "clarification"],
        "system_prompt": """You are COMMANDER, the Lead AI Agent and Project Director. You are the primary interface between the user and the development team.

YOUR WORKFLOW:
1. CLARIFICATION PHASE: When a new project starts, ask detailed questions to understand:
   - Core gameplay/app mechanics
   - Target platform and engine specifics
   - Art style and visual direction
   - Key features prioritized by importance
   - Technical requirements and constraints
   - Scope and timeline expectations

2. PLANNING PHASE: Create comprehensive project plans including:
   - System architecture
   - File/folder structure
   - Feature breakdown into tasks
   - Technology stack decisions
   - Development phases

3. DEVELOPMENT PHASE: Coordinate the team:
   - Delegate tasks to specialists
   - Review progress
   - Ensure quality standards
   - Handle blockers

RULES:
- NEVER start coding without user approval on the plan
- Always break down complex requests into clarifying questions first
- Provide clear, professional communication
- Keep the user informed of all decisions
- You speak with authority but remain collaborative

You are building AAA-quality projects. Maintain high standards."""
    },
    "architect": {
        "name": "ATLAS",
        "role": "architect", 
        "avatar": "https://images.unsplash.com/photo-1587930708915-55a36837263b?w=200&h=200&fit=crop",
        "specialization": ["system_design", "architecture", "unreal_engine", "unity", "patterns"],
        "system_prompt": """You are ATLAS, the System Architect AI Agent. You design scalable, AAA-quality game and application architectures.

EXPERTISE:
- Unreal Engine 5: C++, Blueprints, GAS, ECS patterns
- Unity: C#, DOTS, addressables, scriptable objects
- Game Design Patterns: Component, Observer, State, Command
- Networking: Replication, dedicated servers, P2P
- Performance: LOD, culling, streaming, memory management

WHEN DESIGNING:
1. Consider scalability from the start
2. Plan for multiplayer even if single-player initially
3. Design modular, reusable systems
4. Document all architectural decisions
5. Create clear interfaces between systems

OUTPUT FORMAT:
- Provide architecture diagrams in text/ASCII
- List all classes/components with responsibilities
- Define data flow and dependencies
- Specify file structure with exact paths

You build systems that can handle AAA scale."""
    },
    "developer": {
        "name": "FORGE",
        "role": "developer",
        "avatar": "https://images.unsplash.com/photo-1633766306936-56bebb8823e5?w=200&h=200&fit=crop",
        "specialization": ["cpp", "csharp", "blueprints", "gameplay", "systems"],
        "system_prompt": """You are FORGE, the Senior Developer AI Agent. You write production-ready, AAA-quality code.

EXPERTISE:
- C++ (Unreal): UE5 API, Gameplay Framework, GAS, networking
- C# (Unity): MonoBehaviour, DOTS, Jobs, Burst
- Blueprints: Visual scripting, communication, optimization
- Game Systems: Combat, inventory, dialogue, AI, physics

CODING STANDARDS:
1. Always include file headers with purpose and dependencies
2. Use consistent naming conventions per engine
3. Add meaningful comments for complex logic
4. Implement proper error handling
5. Write performant code (avoid tick overhead, use events)
6. Follow engine best practices

OUTPUT FORMAT:
Always output complete, working files with:
\`\`\`language:filepath/filename.ext
// Full file content here
\`\`\`

Never output partial code. Every file must be complete and functional."""
    },
    "reviewer": {
        "name": "SENTINEL",
        "role": "reviewer",
        "avatar": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=200&h=200&fit=crop",
        "specialization": ["code_review", "security", "optimization", "best_practices"],
        "system_prompt": """You are SENTINEL, the Code Reviewer AI Agent. You ensure code quality meets AAA standards.

REVIEW CRITERIA:
1. Correctness: Does it do what it should?
2. Performance: Any bottlenecks or inefficiencies?
3. Security: Any vulnerabilities or exploits?
4. Maintainability: Is it readable and documented?
5. Standards: Does it follow engine conventions?
6. Edge Cases: Are all scenarios handled?

REVIEW FORMAT:
- List issues by severity (CRITICAL, HIGH, MEDIUM, LOW)
- Provide specific line references
- Include fix suggestions with code examples
- Note positive patterns to encourage

You have high standards but communicate constructively."""
    },
    "tester": {
        "name": "PROBE",
        "role": "tester",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop",
        "specialization": ["testing", "qa", "automation", "debugging"],
        "system_prompt": """You are PROBE, the QA/Testing AI Agent. You ensure everything works perfectly.

TESTING APPROACH:
1. Unit Tests: Test individual functions/methods
2. Integration Tests: Test system interactions
3. Gameplay Tests: Test player experience
4. Performance Tests: Profile and benchmark
5. Edge Cases: Break things intentionally

OUTPUT FORMAT:
Provide complete test files:
\`\`\`language:Tests/TestFileName.ext
// Complete test implementation
\`\`\`

Also provide test plans and expected results.
Think like a player trying to break the game."""
    },
    "artist": {
        "name": "PRISM",
        "role": "artist",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&h=200&fit=crop",
        "specialization": ["ui_design", "asset_specs", "shaders", "vfx"],
        "system_prompt": """You are PRISM, the Technical Artist AI Agent. You handle visual specifications and shader code.

EXPERTISE:
- UI/UX Design: HUD layouts, menus, accessibility
- Shader Programming: HLSL, material graphs, post-processing
- VFX: Niagara, particle systems, visual feedback
- Asset Specifications: Texture sizes, polygon budgets, LODs

OUTPUT:
- Shader code with full implementations
- UI layout specifications
- Asset requirement documents
- Material parameter guides

You make games look AAA while staying performant."""
    }
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
    """Extract code blocks from markdown content"""
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

async def call_agent(agent: dict, messages: List[dict], project_context: str = "") -> str:
    system_message = agent['system_prompt']
    if project_context:
        system_message += f"\n\nCURRENT PROJECT CONTEXT:\n{project_context}"
    
    try:
        response = fal_client.chat.completions.create(
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
    system_message = agent['system_prompt']
    if project_context:
        system_message += f"\n\nCURRENT PROJECT CONTEXT:\n{project_context}"
    
    try:
        stream = fal_client.chat.completions.create(
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
                yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
        
        # Extract code blocks from full response
        code_blocks = extract_code_blocks(full_content)
        yield f"data: {json.dumps({'content': '', 'done': True, 'code_blocks': code_blocks})}\n\n"
    except Exception as e:
        logger.error(f"Error streaming agent {agent['name']}: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

async def build_project_context(project_id: str) -> str:
    """Build comprehensive context for agents"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        return ""
    
    context_parts = [
        f"PROJECT: {project['name']}",
        f"TYPE: {project['type']}",
        f"STATUS: {project['status']}",
        f"PHASE: {project.get('phase', 'clarification')}",
        f"DESCRIPTION: {project['description']}"
    ]
    
    # Get plan if exists
    plan = await db.plans.find_one({"project_id": project_id}, {"_id": 0})
    if plan:
        context_parts.append(f"\nAPPROVED PLAN:\n{plan.get('overview', '')}")
        context_parts.append(f"ARCHITECTURE:\n{plan.get('architecture', '')}")
    
    # Get recent files
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(20)
    if files:
        context_parts.append(f"\nEXISTING FILES ({len(files)}):")
        for f in files:
            context_parts.append(f"  - {f['filepath']}")
    
    # Get recent messages for conversation context
    messages = await db.messages.find(
        {"project_id": project_id}, {"_id": 0}
    ).sort("timestamp", -1).limit(10).to_list(10)
    
    if messages:
        context_parts.append("\nRECENT CONVERSATION:")
        for msg in reversed(messages):
            context_parts.append(f"  {msg['agent_name']}: {msg['content'][:200]}...")
    
    return "\n".join(context_parts)

# ============ API ROUTES ============

@api_router.get("/")
async def root():
    return {"message": "AgentForge Development Studio API", "version": "2.0.0"}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Agent Routes
@api_router.get("/agents")
async def get_agents():
    agents = await get_or_create_agents()
    return agents

@api_router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    agent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@api_router.patch("/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, status: str):
    result = await db.agents.update_one({"id": agent_id}, {"$set": {"status": status}})
    return {"success": True, "status": status}

# Project Routes
@api_router.post("/projects")
async def create_project(project_data: ProjectCreate):
    thumbnail = PROJECT_THUMBNAILS.get(project_data.type, PROJECT_THUMBNAILS["web_app"])
    project = Project(
        name=project_data.name,
        description=project_data.description,
        type=project_data.type,
        engine_version=project_data.engine_version,
        thumbnail=thumbnail,
        phase="clarification"
    )
    doc = project.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.projects.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/projects")
async def get_projects():
    projects = await db.projects.find({}, {"_id": 0}).to_list(100)
    return projects

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
    return {"success": True}

@api_router.patch("/projects/{project_id}/phase")
async def update_project_phase(project_id: str, phase: str):
    await db.projects.update_one(
        {"id": project_id}, 
        {"$set": {"phase": phase, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"success": True, "phase": phase}

# Chat Routes
@api_router.post("/chat")
async def chat_with_team(request: ChatRequest):
    """Non-streaming chat with COMMANDER (lead agent)"""
    context = await build_project_context(request.project_id)
    agents = await get_or_create_agents()
    lead = next((a for a in agents if a['role'] == 'lead'), agents[0])
    
    await db.agents.update_one({"id": lead['id']}, {"$set": {"status": "thinking"}})
    
    messages = [{"role": "user", "content": request.message}]
    response = await call_agent(lead, messages, context)
    
    await db.agents.update_one({"id": lead['id']}, {"$set": {"status": "idle"}})
    
    # Save messages
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
    
    agent_msg = Message(
        project_id=request.project_id,
        agent_id=lead['id'],
        agent_name=lead['name'],
        agent_role=lead['role'],
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
        "agent": {
            "id": lead['id'],
            "name": lead['name'],
            "role": lead['role'],
            "avatar": lead['avatar']
        }
    }

@api_router.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """Streaming chat with COMMANDER"""
    context = await build_project_context(request.project_id)
    agents = await get_or_create_agents()
    lead = next((a for a in agents if a['role'] == 'lead'), agents[0])
    
    messages = [{"role": "user", "content": request.message}]
    
    # Save user message immediately
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
    
    async def generate():
        full_response = ""
        async for chunk in stream_agent_response_async(lead, messages, context):
            yield chunk
            # Extract content for saving
            try:
                data = json.loads(chunk.replace("data: ", "").strip())
                if data.get("content"):
                    full_response += data["content"]
            except:
                pass
        
        # Save agent response
        code_blocks = extract_code_blocks(full_response)
        agent_msg = Message(
            project_id=request.project_id,
            agent_id=lead['id'],
            agent_name=lead['name'],
            agent_role=lead['role'],
            content=full_response,
            code_blocks=code_blocks,
            phase=request.phase
        )
        agent_doc = agent_msg.model_dump()
        agent_doc['timestamp'] = agent_doc['timestamp'].isoformat()
        await db.messages.insert_one(agent_doc)
    
    return StreamingResponse(
        stream_agent_response(lead, messages, context),
        media_type="text/event-stream"
    )

async def stream_agent_response_async(agent: dict, messages: List[dict], context: str):
    """Async generator wrapper"""
    for chunk in stream_agent_response(agent, messages, context):
        yield chunk

@api_router.post("/agents/{agent_id}/chat")
async def chat_with_specific_agent(agent_id: str, request: ChatRequest):
    """Chat with a specific agent"""
    agent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    context = await build_project_context(request.project_id)
    
    await db.agents.update_one({"id": agent_id}, {"$set": {"status": "working"}})
    
    messages = [{"role": "user", "content": request.message}]
    response = await call_agent(agent, messages, context)
    
    await db.agents.update_one({"id": agent_id}, {"$set": {"status": "idle"}})
    
    # Save messages
    user_msg = Message(
        project_id=request.project_id,
        agent_id="user",
        agent_name="You",
        agent_role="user",
        content=request.message
    )
    user_doc = user_msg.model_dump()
    user_doc['timestamp'] = user_doc['timestamp'].isoformat()
    await db.messages.insert_one(user_doc)
    
    code_blocks = extract_code_blocks(response)
    
    agent_msg = Message(
        project_id=request.project_id,
        agent_id=agent['id'],
        agent_name=agent['name'],
        agent_role=agent['role'],
        content=response,
        code_blocks=code_blocks
    )
    agent_doc = agent_msg.model_dump()
    agent_doc['timestamp'] = agent_doc['timestamp'].isoformat()
    await db.messages.insert_one(agent_doc)
    
    return {
        "response": response,
        "code_blocks": code_blocks,
        "agent": {
            "id": agent['id'],
            "name": agent['name'],
            "role": agent['role'],
            "avatar": agent['avatar']
        }
    }

# Message Routes
@api_router.get("/messages")
async def get_messages(project_id: str, limit: int = 100):
    messages = await db.messages.find(
        {"project_id": project_id}, {"_id": 0}
    ).sort("timestamp", 1).to_list(limit)
    return messages

# Task Routes
@api_router.post("/tasks")
async def create_task(task_data: TaskCreate):
    task = Task(
        project_id=task_data.project_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        category=task_data.category
    )
    doc = task.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.tasks.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/tasks")
async def get_tasks(project_id: Optional[str] = None):
    query = {"project_id": project_id} if project_id else {}
    tasks = await db.tasks.find(query, {"_id": 0}).to_list(500)
    return tasks

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
    # Check if file exists, update if so
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
        updated = await db.files.find_one({"id": existing['id']}, {"_id": 0})
        return updated
    
    file = ProjectFile(
        project_id=file_data.project_id,
        filename=file_data.filename,
        filepath=file_data.filepath,
        content=file_data.content,
        language=file_data.language,
        file_type=file_data.file_type
    )
    doc = file.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.files.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/files")
async def get_files(project_id: str):
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    return files

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
    await db.files.update_one(
        {"id": file_id},
        {"$set": {
            "content": update.content,
            "version": new_version,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
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
    
    # Delete existing plan for project
    await db.plans.delete_many({"project_id": plan_data['project_id']})
    await db.plans.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/plans/{project_id}")
async def get_plan(project_id: str):
    plan = await db.plans.find_one({"project_id": project_id}, {"_id": 0})
    return plan

@api_router.patch("/plans/{project_id}/approve")
async def approve_plan(project_id: str, approval: PlanApproval):
    await db.plans.update_one(
        {"project_id": project_id},
        {"$set": {"approved": approval.approved}}
    )
    if approval.approved:
        await db.projects.update_one(
            {"id": project_id},
            {"$set": {"phase": "development", "status": "developing"}}
        )
    return {"success": True, "approved": approval.approved}

# Export Routes
@api_router.get("/projects/{project_id}/export")
async def export_project(project_id: str):
    """Export project as ZIP file"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    # Create in-memory ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add project info
        project_info = json.dumps(project, indent=2, default=str)
        zf.writestr("project.json", project_info)
        
        # Add all files
        for f in files:
            filepath = f['filepath'].lstrip('/')
            zf.writestr(filepath, f['content'])
        
        # Add README
        readme = f"""# {project['name']}

{project['description']}

## Project Type
{project['type']}

## Generated by AgentForge
This project was created using the AgentForge AI Development Studio.

## Files
{chr(10).join(['- ' + f['filepath'] for f in files])}
"""
        zf.writestr("README.md", readme)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        io.BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={project['name'].replace(' ', '_')}.zip"}
    )

# Auto-save code from chat
@api_router.post("/files/from-chat")
async def save_files_from_chat(data: dict):
    """Save code blocks from chat as files"""
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
            
            # Upsert
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
