from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


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
    delegate_to: Optional[str] = None


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


class GitHubPushRequest(BaseModel):
    project_id: str
    github_token: str
    repo_name: str
    commit_message: str = "Update from AgentForge"
    branch: str = "main"
    create_repo: bool = False


class AgentChainRequest(BaseModel):
    project_id: str
    message: str
    chain: List[str] = ["COMMANDER", "FORGE", "SENTINEL"]
    auto_execute: bool = True


class RefactorRequest(BaseModel):
    """Multi-file refactoring request"""
    project_id: str
    refactor_type: str
    target: str
    new_value: Optional[str] = None
    file_ids: List[str] = []
    preview_only: bool = False


class ProjectDuplicateRequest(BaseModel):
    project_id: str
    new_name: str
    include_files: bool = True
    include_tasks: bool = False
    include_messages: bool = False


class CustomActionCreate(BaseModel):
    name: str
    description: str
    prompt: str
    chain: List[str] = ["COMMANDER", "FORGE"]
    icon: str = "sparkles"
    category: str = "custom"
    is_global: bool = False
    project_id: Optional[str] = None


class MemoryCreate(BaseModel):
    project_id: str
    agent_name: str
    memory_type: str = "context"
    content: str
    importance: int = 5


class QuickActionRequest(BaseModel):
    project_id: str
    action_id: str
    parameters: Dict[str, Any] = {}
