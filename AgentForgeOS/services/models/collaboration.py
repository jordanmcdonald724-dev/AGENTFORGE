from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


class BlueprintNode(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    name: str
    position: Dict[str, float] = {"x": 0, "y": 0}
    inputs: List[Dict[str, Any]] = []
    outputs: List[Dict[str, Any]] = []
    properties: Dict[str, Any] = {}
    color: str = "zinc"


class Blueprint(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    description: str = ""
    blueprint_type: str = "logic"
    target_engine: str = "unreal"
    nodes: List[Dict[str, Any]] = []
    connections: List[Dict[str, Any]] = []
    variables: List[Dict[str, Any]] = []
    generated_code: Optional[str] = None
    synced_file_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Collaborator(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    user_id: str
    username: str
    color: str = "blue"
    role: str = "editor"
    cursor_position: Dict[str, Any] = {}
    active_file_id: Optional[str] = None
    is_online: bool = False
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FileLock(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    file_id: str
    locked_by_user_id: str
    locked_by_username: str
    locked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CollaborationMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    user_id: str
    username: str
    content: str
    message_type: str = "chat"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
