from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


class DynamicAgent(BaseModel):
    """Dynamically created specialized agent"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    name: str
    role: str
    specialty: str
    description: str
    
    capabilities: List[str] = []
    triggers: List[str] = []
    
    created_by: str
    creation_reason: str
    
    tasks_handled: int = 0
    success_rate: float = 100.0
    active: bool = True
    
    system_prompt: str = ""
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
