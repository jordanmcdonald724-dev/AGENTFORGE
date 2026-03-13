from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


class GoalLoop(BaseModel):
    """Autonomous goal-driven build loop"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    goal: str
    status: str = "idle"
    thresholds: Dict[str, Any] = {
        "tests_pass_rate": 90,
        "performance_score": 70,
        "code_quality": 70,
        "demo_playable": True
    }
    current_cycle: int = 0
    max_cycles: int = 50
    cycles: List[Dict[str, Any]] = []
    current_metrics: Dict[str, Any] = {}
    thresholds_met: Dict[str, bool] = {}
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeEntry(BaseModel):
    """Cross-project knowledge entry"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entry_type: str
    title: str
    description: str
    source_project_id: Optional[str] = None
    source_file: Optional[str] = None
    tags: List[str] = []
    category: str = "general"
    tech_stack: List[str] = []
    success_count: int = 0
    failure_count: int = 0
    reuse_count: int = 0
    rating: float = 0.0
    code_snippet: Optional[str] = None
    solution_steps: List[str] = []
    known_issues: List[str] = []
    created_by: str = "system"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectureVariant(BaseModel):
    """Parallel architecture exploration variant"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    exploration_id: str
    name: str
    architecture_type: str
    description: str
    files_generated: List[Dict[str, str]] = []
    metrics: Dict[str, float] = {
        "performance": 0,
        "maintainability": 0,
        "scalability": 0,
        "complexity": 0,
        "cost_estimate": 0
    }
    pros: List[str] = []
    cons: List[str] = []
    selected: bool = False
    evaluation_notes: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectureExploration(BaseModel):
    """Multi-future build exploration session"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    goal: str
    status: str = "exploring"
    variants: List[str] = []
    selected_variant_id: Optional[str] = None
    comparison_report: Dict[str, Any] = {}
    recommendation: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RefactorJob(BaseModel):
    """Autonomous refactoring job"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    job_type: str = "nightly"
    status: str = "pending"
    inefficiencies: List[Dict[str, Any]] = []
    outdated_deps: List[Dict[str, str]] = []
    performance_issues: List[Dict[str, Any]] = []
    code_smells: List[Dict[str, Any]] = []
    refactors_applied: List[Dict[str, Any]] = []
    deps_updated: List[Dict[str, str]] = []
    files_optimized: List[str] = []
    before_metrics: Dict[str, float] = {}
    after_metrics: Dict[str, float] = {}
    improvement_score: float = 0
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MissionControlEvent(BaseModel):
    """Real-time mission control event"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    event_type: str
    agent_name: Optional[str] = None
    title: str
    description: str
    details: Dict[str, Any] = {}
    reasoning_chain: List[str] = []
    metrics: Dict[str, float] = {}
    severity: str = "info"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DeploymentPipeline(BaseModel):
    """Autonomous deployment pipeline"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    trigger: str = "manual"
    status: str = "idle"
    stages: List[Dict[str, Any]] = [
        {"name": "lint", "status": "pending"},
        {"name": "test", "status": "pending"},
        {"name": "build", "status": "pending"},
        {"name": "deploy", "status": "pending"},
        {"name": "verify", "status": "pending"}
    ]
    current_stage: int = 0
    target_platform: str = "vercel"
    deploy_url: Optional[str] = None
    auto_deploy_enabled: bool = False
    test_threshold: float = 90
    logs: List[str] = []
    triggered_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SystemModule(BaseModel):
    """Self-created system module/tool"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    module_type: str
    description: str
    detected_need: str
    frequency_trigger: int = 1
    template_code: str = ""
    config_schema: Dict[str, Any] = {}
    usage_instructions: str = ""
    times_used: int = 0
    success_rate: float = 100.0
    active: bool = True
    auto_created: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RealityPipeline(BaseModel):
    """Full idea-to-deployed-product pipeline"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    idea: str
    idea_id: Optional[str] = None
    status: str = "intake"
    current_phase: int = 0
    phases: List[Dict[str, Any]] = [
        {"name": "Intake", "status": "pending", "agent": "COMMANDER"},
        {"name": "Clarification", "status": "pending", "agent": "COMMANDER"},
        {"name": "Architecture", "status": "pending", "agent": "ATLAS"},
        {"name": "Asset Generation", "status": "pending", "agent": "PRISM"},
        {"name": "Code Generation", "status": "pending", "agent": "FORGE"},
        {"name": "Code Review", "status": "pending", "agent": "SENTINEL"},
        {"name": "Testing", "status": "pending", "agent": "PROBE"},
        {"name": "Deployment", "status": "pending", "agent": "COMMANDER"},
        {"name": "Verification", "status": "pending", "agent": "PROBE"}
    ]
    project_id: Optional[str] = None
    clarification_notes: str = ""
    architecture_doc: Dict[str, Any] = {}
    assets_generated: List[str] = []
    files_created: List[str] = []
    test_results: Dict[str, Any] = {}
    deploy_url: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
