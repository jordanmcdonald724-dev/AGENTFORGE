from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


class ProjectAutopsy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    source_type: str
    source_url: Optional[str] = None
    status: str = "pending"
    architecture: Dict[str, Any] = {}
    tech_stack: List[Dict[str, str]] = []
    dependencies: Dict[str, List[str]] = {}
    dependency_graph: Dict[str, Any] = {}
    design_patterns: List[Dict[str, Any]] = []
    weak_points: List[Dict[str, Any]] = []
    upgrade_plan: List[Dict[str, Any]] = []
    file_tree: Dict[str, Any] = {}
    stats: Dict[str, Any] = {}
    analyzed_by: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
