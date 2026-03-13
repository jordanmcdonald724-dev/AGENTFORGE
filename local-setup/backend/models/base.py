from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


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
    images: List[Dict[str, str]] = []
    delegated_to: Optional[str] = None
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
    category: str = "concept"
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


class AgentMemory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    agent_id: str
    agent_name: str
    memory_type: str = "context"
    content: str
    importance: int = 5
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


class CustomQuickAction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    icon: str = "sparkles"
    prompt: str
    chain: List[str] = ["COMMANDER", "FORGE"]
    category: str = "custom"
    is_global: bool = False
    project_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
