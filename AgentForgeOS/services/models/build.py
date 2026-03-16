from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


class SimulationRequest(BaseModel):
    """Request for build simulation/dry run"""
    project_id: str
    build_type: str = "full"
    target_engine: str = "unreal"
    include_systems: List[str] = []


class SimulationResult(BaseModel):
    """Result of build simulation"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    estimated_build_time: str
    estimated_build_minutes: int
    file_count: int
    total_size_kb: int
    required_assets: List[Dict[str, Any]] = []
    warnings: List[Dict[str, str]] = []
    architecture_summary: str
    phases: List[Dict[str, Any]] = []
    feasibility_score: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AutonomousBuild(BaseModel):
    """Autonomous overnight build job"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    status: str = "queued"
    build_type: str = "full"
    target_engine: str = "unreal"
    current_stage: int = 0
    total_stages: int = 0
    stages: List[Dict[str, Any]] = []
    progress_percent: int = 0
    estimated_completion: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WarRoomMessage(BaseModel):
    """Agent communication in war room"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    build_id: Optional[str] = None
    from_agent: str
    to_agent: Optional[str] = None
    message_type: str = "discussion"
    content: str
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StartBuildRequest(BaseModel):
    project_id: str
    build_type: str = "full"
    target_engine: str = "unreal"
    systems_to_build: List[str] = []
    estimated_hours: int = 12
    scheduled_at: Optional[str] = None
    category: str = "game"


class PlayableDemo(BaseModel):
    """Playable demo generated on build completion"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    build_id: str
    status: str = "generating"
    demo_type: str = "both"
    target_engine: str = "unreal"
    web_demo_url: Optional[str] = None
    web_demo_html: Optional[str] = None
    executable_url: Optional[str] = None
    executable_size_mb: float = 0
    platform: str = "windows"
    systems_included: List[str] = []
    demo_features: List[str] = []
    controls_guide: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_at: Optional[datetime] = None


class BuildWorker(BaseModel):
    """Distributed build worker"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    status: str = "idle"
    current_job: Optional[str] = None
    current_project_id: Optional[str] = None
    capabilities: List[str] = []
    max_concurrent: int = 1
    jobs_completed: int = 0
    total_build_time_hours: float = 0
    success_rate: float = 100.0
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BuildFarmJob(BaseModel):
    """Job in the build farm queue"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    project_name: str
    job_type: str
    priority: int = 5
    status: str = "queued"
    assigned_worker: Optional[str] = None
    progress: float = 0
    config: Dict[str, Any] = {}
    result: Dict[str, Any] = {}
    queued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class BuildQueueItem(BaseModel):
    """Item in the build queue"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    category: str
    build_config: Dict[str, Any] = {}
    status: str = "queued"
    position: int = 0
    scheduled_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DebugLoop(BaseModel):
    """AI self-debugging loop session"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    build_id: Optional[str] = None
    status: str = "idle"
    iterations: List[Dict[str, Any]] = []
    current_iteration: int = 0
    max_iterations: int = 10
    errors_detected: List[Dict[str, Any]] = []
    fixes_applied: List[Dict[str, Any]] = []
    tests_run: List[Dict[str, Any]] = []
    success: bool = False
    final_report: Dict[str, Any] = {}
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Checkpoint(BaseModel):
    """Development checkpoint for time machine"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    description: str = ""
    step_number: int
    files_snapshot: List[Dict[str, Any]] = []
    tasks_snapshot: List[Dict[str, Any]] = []
    build_state: Dict[str, Any] = {}
    agent_memories: List[Dict[str, Any]] = []
    auto_created: bool = False
    tags: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"


class IdeaConcept(BaseModel):
    """Generated project concept"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    category: str
    description: str
    unique_features: List[str] = []
    target_audience: str = ""
    tech_stack_suggestion: List[str] = []
    complexity: str = "medium"
    estimated_build_time: str = ""
    project_id: Optional[str] = None
    prototype_built: bool = False
    generated_by: str = "COMMANDER"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdeaBatch(BaseModel):
    """Batch of generated ideas"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str
    category_filter: Optional[str] = None
    count: int = 10
    ideas: List[Dict[str, Any]] = []
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SaaSBlueprint(BaseModel):
    """One-click SaaS generation blueprint"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    backend_api: Dict[str, Any] = {}
    database_schema: Dict[str, Any] = {}
    auth_system: Dict[str, Any] = {}
    frontend_ui: Dict[str, Any] = {}
    deployment_config: Dict[str, Any] = {}
    payment_integration: Dict[str, Any] = {}
    tech_stack: Dict[str, str] = {}
    estimated_cost: Dict[str, Any] = {}
    status: str = "draft"
    project_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SystemMap(BaseModel):
    """3D/2D system visualization data"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    clusters: List[Dict[str, Any]] = []
    agent_positions: Dict[str, Dict[str, float]] = {}
    active_connections: List[str] = []
    layout_type: str = "force"
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
