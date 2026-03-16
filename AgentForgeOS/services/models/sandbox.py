from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


class NotificationSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    email_enabled: bool = False
    email_address: Optional[str] = None
    discord_enabled: bool = False
    discord_webhook_url: Optional[str] = None
    notify_on_complete: bool = True
    notify_on_milestones: bool = True
    notify_on_errors: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AudioAsset(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    audio_type: str
    prompt: str
    provider: str
    url: Optional[str] = None
    duration_seconds: float = 0
    format: str = "mp3"
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Deployment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    platform: str
    status: str = "pending"
    project_name: str
    deploy_url: Optional[str] = None
    admin_url: Optional[str] = None
    config: Dict[str, Any] = {}
    logs: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deployed_at: Optional[datetime] = None


class SandboxSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    status: str = "idle"
    environment: str = "web"
    console_output: List[Dict[str, Any]] = []
    variables: Dict[str, Any] = {}
    breakpoints: List[int] = []
    current_line: Optional[int] = None
    execution_time_ms: float = 0
    memory_usage_mb: float = 0
    started_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SandboxConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    timeout_seconds: int = 30
    max_memory_mb: int = 256
    enable_network: bool = False
    enable_filesystem: bool = False
    environment_vars: Dict[str, str] = {}
    entry_file: Optional[str] = None


class PipelineAsset(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    asset_type: str
    category: str = "general"
    file_path: Optional[str] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    file_size_bytes: int = 0
    format: str = ""
    dimensions: Optional[Dict[str, int]] = None
    duration_seconds: Optional[float] = None
    tags: List[str] = []
    dependencies: List[str] = []
    dependents: List[str] = []
    metadata: Dict[str, Any] = {}
    source: str = "generated"
    status: str = "ready"
    version: int = 1
    created_by: str = "system"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AssetImportRequest(BaseModel):
    project_id: str
    name: str
    asset_type: str
    category: str = "general"
    url: Optional[str] = None
    tags: List[str] = []
