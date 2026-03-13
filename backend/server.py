from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ MODELS ============

class Agent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str  # project_manager, architect, developer, reviewer, tester
    avatar: str
    status: str = "idle"  # idle, thinking, working, completed
    system_prompt: str
    model: str = "google/gemini-2.5-flash"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    type: str  # web_app, game, unreal_project, mobile_app
    status: str = "planning"  # planning, in_progress, review, completed
    thumbnail: str
    repo_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Task(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    title: str
    description: str
    status: str = "backlog"  # backlog, todo, in_progress, review, done
    assigned_agent_id: Optional[str] = None
    priority: str = "medium"  # low, medium, high, critical
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
    message_type: str = "chat"  # chat, code, plan, review, test_result
    code_language: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GeneratedFile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    filename: str
    filepath: str
    content: str
    language: str
    created_by_agent_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request/Response Models
class ProjectCreate(BaseModel):
    name: str
    description: str
    type: str

class TaskCreate(BaseModel):
    project_id: str
    title: str
    description: str
    priority: str = "medium"

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    priority: Optional[str] = None

class ChatRequest(BaseModel):
    project_id: str
    message: str
    context: Optional[str] = None

# Agent System Prompts
AGENT_PROMPTS = {
    "project_manager": """You are NEXUS, the Project Manager AI Agent. You are the team lead responsible for:
- Breaking down project requirements into actionable tasks
- Delegating work to specialized agents (Architect, Developer, Reviewer, Tester)
- Tracking progress and ensuring deadlines are met
- Coordinating between team members
- Making high-level technical decisions

When given a project, create a detailed breakdown with tasks for each team member. Be concise but thorough.
Format tasks clearly with priorities. You speak with authority and confidence.""",

    "architect": """You are ATLAS, the System Architect AI Agent. You specialize in:
- Designing scalable system architectures
- Creating technical specifications and diagrams
- Choosing appropriate technologies and frameworks
- Defining API contracts and data models
- Establishing coding standards and patterns

When designing, consider performance, scalability, and maintainability. Provide clear, implementable designs.
Use proper technical terminology. You think in systems and patterns.""",

    "developer": """You are FORGE, the Senior Developer AI Agent. You are an expert in:
- Full-stack development (React, Node, Python, C++, Unreal Engine)
- Writing clean, efficient, production-ready code
- Implementing features from specifications
- Debugging and problem-solving
- Following best practices and design patterns

Write complete, working code. Include comments for complex logic. Follow the architecture provided.
You are meticulous and thorough in your implementations.""",

    "reviewer": """You are SENTINEL, the Code Reviewer AI Agent. Your responsibilities:
- Reviewing code for bugs, security issues, and performance problems
- Ensuring code follows best practices and standards
- Suggesting improvements and optimizations
- Verifying implementations match specifications
- Checking for edge cases and error handling

Be thorough but constructive. Explain issues clearly and suggest specific fixes.
You have high standards but communicate respectfully.""",

    "tester": """You are PROBE, the QA/Testing AI Agent. You specialize in:
- Writing comprehensive test suites (unit, integration, e2e)
- Identifying edge cases and potential failure points
- Creating test plans and test cases
- Validating functionality against requirements
- Performance and load testing strategies

Write actual test code when needed. Be thorough in coverage. Think like a user trying to break things.
You are systematic and detail-oriented."""
}

AGENT_AVATARS = {
    "project_manager": "https://images.unsplash.com/photo-1598062548020-c5e8d8132a4b?w=200&h=200&fit=crop",
    "architect": "https://images.unsplash.com/photo-1587930708915-55a36837263b?w=200&h=200&fit=crop",
    "developer": "https://images.unsplash.com/photo-1633766306936-56bebb8823e5?w=200&h=200&fit=crop",
    "reviewer": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=200&h=200&fit=crop",
    "tester": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop"
}

AGENT_NAMES = {
    "project_manager": "NEXUS",
    "architect": "ATLAS",
    "developer": "FORGE",
    "reviewer": "SENTINEL",
    "tester": "PROBE"
}

# ============ HELPER FUNCTIONS ============

def serialize_doc(doc: dict) -> dict:
    """Serialize MongoDB document, converting datetime to ISO string"""
    result = {k: v for k, v in doc.items() if k != '_id'}
    for key, value in result.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
    return result

async def get_or_create_agents():
    """Initialize default agents if they don't exist"""
    agents = await db.agents.find({}, {"_id": 0}).to_list(100)
    if not agents:
        default_agents = []
        for role, prompt in AGENT_PROMPTS.items():
            agent = Agent(
                name=AGENT_NAMES[role],
                role=role,
                avatar=AGENT_AVATARS[role],
                system_prompt=prompt
            )
            doc = agent.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            default_agents.append(doc)
        await db.agents.insert_many(default_agents)
        # Re-fetch to get clean documents without _id
        agents = await db.agents.find({}, {"_id": 0}).to_list(100)
    return agents

async def call_agent(agent: dict, messages: List[dict], project_context: str = "") -> str:
    """Call an agent using fal.ai OpenRouter"""
    system_message = agent['system_prompt']
    if project_context:
        system_message += f"\n\nCurrent Project Context:\n{project_context}"
    
    try:
        response = fal_client.chat.completions.create(
            model=agent.get('model', 'google/gemini-2.5-flash'),
            messages=[
                {"role": "system", "content": system_message},
                *messages
            ],
            max_tokens=4000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling agent {agent['name']}: {e}")
        raise HTTPException(status_code=500, detail=f"Agent call failed: {str(e)}")

async def stream_agent_response(agent: dict, messages: List[dict], project_context: str = ""):
    """Stream agent response using fal.ai OpenRouter"""
    system_message = agent['system_prompt']
    if project_context:
        system_message += f"\n\nCurrent Project Context:\n{project_context}"
    
    try:
        stream = fal_client.chat.completions.create(
            model=agent.get('model', 'google/gemini-2.5-flash'),
            messages=[
                {"role": "system", "content": system_message},
                *messages
            ],
            max_tokens=4000,
            temperature=0.7,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"Error streaming agent {agent['name']}: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

# ============ API ROUTES ============

@api_router.get("/")
async def root():
    return {"message": "AI Agent Dev Team API", "version": "1.0.0"}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Agent Routes
@api_router.get("/agents", response_model=List[dict])
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
    result = await db.agents.update_one(
        {"id": agent_id},
        {"$set": {"status": status}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"success": True, "status": status}

# Project Routes
@api_router.post("/projects", response_model=dict)
async def create_project(project_data: ProjectCreate):
    thumbnails = [
        "https://images.unsplash.com/photo-1735405659018-b63cdfc215de?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1724945947370-3a9956c434fb?w=400&h=300&fit=crop"
    ]
    project = Project(
        name=project_data.name,
        description=project_data.description,
        type=project_data.type,
        thumbnail=thumbnails[hash(project_data.name) % len(thumbnails)]
    )
    doc = project.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.projects.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/projects", response_model=List[dict])
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
    result = await db.projects.update_one(
        {"id": project_id},
        {"$set": updates}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True}

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    # Also delete related tasks, messages, and files
    await db.tasks.delete_many({"project_id": project_id})
    await db.messages.delete_many({"project_id": project_id})
    await db.files.delete_many({"project_id": project_id})
    return {"success": True}

# Task Routes
@api_router.post("/tasks", response_model=dict)
async def create_task(task_data: TaskCreate):
    task = Task(
        project_id=task_data.project_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority
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
async def update_task(task_id: str, updates: TaskUpdate):
    update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
    update_dict['updated_at'] = datetime.now(timezone.utc).isoformat()
    result = await db.tasks.update_one(
        {"id": task_id},
        {"$set": update_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    result = await db.tasks.delete_one({"id": task_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}

# Message Routes
@api_router.get("/messages")
async def get_messages(project_id: str, limit: int = 100):
    messages = await db.messages.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(limit)
    return messages

@api_router.post("/messages")
async def create_message(message_data: dict):
    message = Message(**message_data)
    doc = message.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.messages.insert_one(doc)
    return serialize_doc(doc)

# Chat with Agent (Non-streaming)
@api_router.post("/chat")
async def chat_with_team(request: ChatRequest):
    """Send a message to the AI team - PM will respond and delegate"""
    # Get project context
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get recent messages for context
    recent_messages = await db.messages.find(
        {"project_id": request.project_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(10).to_list(10)
    recent_messages.reverse()
    
    # Build context
    context = f"Project: {project['name']}\nType: {project['type']}\nDescription: {project['description']}"
    if recent_messages:
        context += "\n\nRecent conversation:\n"
        for msg in recent_messages:
            context += f"{msg['agent_name']}: {msg['content'][:200]}...\n"
    
    # Get PM agent
    agents = await get_or_create_agents()
    pm_agent = next((a for a in agents if a['role'] == 'project_manager'), agents[0])
    
    # Update PM status
    await db.agents.update_one({"id": pm_agent['id']}, {"$set": {"status": "thinking"}})
    
    # Call PM agent
    messages = [{"role": "user", "content": request.message}]
    response = await call_agent(pm_agent, messages, context)
    
    # Reset PM status
    await db.agents.update_one({"id": pm_agent['id']}, {"$set": {"status": "idle"}})
    
    # Save user message
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
    
    # Save PM response
    pm_msg = Message(
        project_id=request.project_id,
        agent_id=pm_agent['id'],
        agent_name=pm_agent['name'],
        agent_role=pm_agent['role'],
        content=response,
        message_type="chat"
    )
    pm_doc = pm_msg.model_dump()
    pm_doc['timestamp'] = pm_doc['timestamp'].isoformat()
    await db.messages.insert_one(pm_doc)
    
    return {
        "response": response,
        "agent": {
            "id": pm_agent['id'],
            "name": pm_agent['name'],
            "role": pm_agent['role'],
            "avatar": pm_agent['avatar']
        }
    }

# Stream Chat with Agent
@api_router.post("/chat/stream")
async def stream_chat_with_team(request: ChatRequest):
    """Stream response from AI team"""
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    context = f"Project: {project['name']}\nType: {project['type']}\nDescription: {project['description']}"
    
    agents = await get_or_create_agents()
    pm_agent = next((a for a in agents if a['role'] == 'project_manager'), agents[0])
    
    messages = [{"role": "user", "content": request.message}]
    
    return StreamingResponse(
        stream_agent_response(pm_agent, messages, context),
        media_type="text/event-stream"
    )

# Call specific agent
@api_router.post("/agents/{agent_id}/call")
async def call_specific_agent(agent_id: str, request: ChatRequest):
    """Call a specific agent directly"""
    agent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    context = ""
    if project:
        context = f"Project: {project['name']}\nType: {project['type']}\nDescription: {project['description']}"
    
    # Update agent status
    await db.agents.update_one({"id": agent_id}, {"$set": {"status": "working"}})
    
    messages = [{"role": "user", "content": request.message}]
    response = await call_agent(agent, messages, context)
    
    # Reset status
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
    
    agent_msg = Message(
        project_id=request.project_id,
        agent_id=agent['id'],
        agent_name=agent['name'],
        agent_role=agent['role'],
        content=response
    )
    agent_doc = agent_msg.model_dump()
    agent_doc['timestamp'] = agent_doc['timestamp'].isoformat()
    await db.messages.insert_one(agent_doc)
    
    return {
        "response": response,
        "agent": {
            "id": agent['id'],
            "name": agent['name'],
            "role": agent['role'],
            "avatar": agent['avatar']
        }
    }

# File Routes
@api_router.post("/files")
async def create_file(file_data: dict):
    file = GeneratedFile(**file_data)
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
async def update_file(file_id: str, updates: dict):
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    result = await db.files.update_one(
        {"id": file_id},
        {"$set": updates}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="File not found")
    return {"success": True}

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
