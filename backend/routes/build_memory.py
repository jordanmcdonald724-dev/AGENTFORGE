"""
Project Memory System
=====================
Stores and learns from build history:
- Successful architectures
- Bug fixes
- Performance optimizations
- UI improvements
- Agent performance

The system gets smarter over time.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from core.database import db
import uuid

router = APIRouter(prefix="/memory", tags=["memory"])


# ============ MODELS ============

class BuildMemory(BaseModel):
    """Memory of a single build"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    project_type: str  # game, web, api, etc
    
    # What was built
    architecture_used: str
    modules_built: List[str]
    tech_stack: Dict[str, str]
    
    # Quality metrics
    final_score: int
    iterations_needed: int
    
    # Issues encountered
    bugs_found: List[Dict[str, Any]] = []
    fixes_applied: List[Dict[str, Any]] = []
    
    # Performance data
    build_time_seconds: int
    files_generated: int
    
    # Success indicators
    successful: bool
    deployment_ready: bool
    
    # Learning data
    patterns_that_worked: List[str] = []
    patterns_to_avoid: List[str] = []
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentPerformance(BaseModel):
    """Track agent performance over time"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    agent_role: str
    
    # Metrics
    total_tasks: int = 0
    successful_tasks: int = 0
    average_quality_score: float = 0.0
    average_time_seconds: float = 0.0
    
    # Best work
    best_outputs: List[Dict[str, Any]] = []
    
    # Areas to improve
    common_issues: List[str] = []
    
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LearningInsight(BaseModel):
    """Insights learned from builds"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str  # architecture, performance, ui, security, etc
    insight: str
    confidence: float  # 0-1
    evidence_count: int  # How many builds support this
    examples: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ============ API ENDPOINTS ============

@router.post("/build/record")
async def record_build_memory(memory: BuildMemory):
    """Record memory of a completed build"""
    await db.build_memories.insert_one(memory.model_dump())
    
    # Update learning insights
    await update_learning_insights(memory)
    
    return {"success": True, "id": memory.id}


@router.get("/build/history/{project_type}")
async def get_build_history(project_type: str, limit: int = 10):
    """Get successful builds of a specific type for learning"""
    memories = await db.build_memories.find(
        {"project_type": project_type, "successful": True},
        {"_id": 0}
    ).sort("final_score", -1).limit(limit).to_list(limit)
    
    return memories


@router.get("/agent/performance/{agent_name}")
async def get_agent_performance(agent_name: str):
    """Get performance metrics for an agent"""
    perf = await db.agent_performance.find_one(
        {"agent_name": agent_name},
        {"_id": 0}
    )
    return perf or {"agent_name": agent_name, "total_tasks": 0}


@router.post("/agent/performance/update")
async def update_agent_performance(
    agent_name: str,
    agent_role: str,
    task_successful: bool,
    quality_score: int,
    time_seconds: int
):
    """Update agent performance after a task"""
    existing = await db.agent_performance.find_one({"agent_name": agent_name})
    
    if existing:
        # Update rolling averages
        total = existing.get("total_tasks", 0) + 1
        successful = existing.get("successful_tasks", 0) + (1 if task_successful else 0)
        
        old_avg_score = existing.get("average_quality_score", 0)
        new_avg_score = ((old_avg_score * (total - 1)) + quality_score) / total
        
        old_avg_time = existing.get("average_time_seconds", 0)
        new_avg_time = ((old_avg_time * (total - 1)) + time_seconds) / total
        
        await db.agent_performance.update_one(
            {"agent_name": agent_name},
            {"$set": {
                "total_tasks": total,
                "successful_tasks": successful,
                "average_quality_score": round(new_avg_score, 2),
                "average_time_seconds": round(new_avg_time, 2),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    else:
        perf = AgentPerformance(
            agent_name=agent_name,
            agent_role=agent_role,
            total_tasks=1,
            successful_tasks=1 if task_successful else 0,
            average_quality_score=float(quality_score),
            average_time_seconds=float(time_seconds)
        )
        await db.agent_performance.insert_one(perf.model_dump())
    
    return {"success": True}


@router.get("/insights")
async def get_learning_insights(category: Optional[str] = None, limit: int = 20):
    """Get learning insights"""
    query = {}
    if category:
        query["category"] = category
    
    insights = await db.learning_insights.find(
        query,
        {"_id": 0}
    ).sort("confidence", -1).limit(limit).to_list(limit)
    
    return insights


@router.get("/recommendations/{project_type}")
async def get_build_recommendations(project_type: str):
    """Get recommendations based on past successful builds"""
    
    # Get successful architectures for this type
    successful_builds = await db.build_memories.find(
        {"project_type": project_type, "successful": True, "final_score": {"$gte": 80}},
        {"_id": 0}
    ).sort("final_score", -1).limit(5).to_list(5)
    
    # Get relevant insights
    insights = await db.learning_insights.find(
        {"confidence": {"$gte": 0.7}},
        {"_id": 0}
    ).limit(10).to_list(10)
    
    # Get agent performance
    agent_perf = await db.agent_performance.find(
        {},
        {"_id": 0}
    ).sort("average_quality_score", -1).to_list(10)
    
    recommendations = {
        "recommended_architecture": successful_builds[0]["architecture_used"] if successful_builds else None,
        "recommended_tech_stack": successful_builds[0]["tech_stack"] if successful_builds else {},
        "patterns_that_work": [],
        "patterns_to_avoid": [],
        "best_performing_agents": [a["agent_name"] for a in agent_perf[:3]],
        "insights": [i["insight"] for i in insights]
    }
    
    # Aggregate patterns
    for build in successful_builds:
        recommendations["patterns_that_work"].extend(build.get("patterns_that_worked", []))
        recommendations["patterns_to_avoid"].extend(build.get("patterns_to_avoid", []))
    
    # Deduplicate
    recommendations["patterns_that_work"] = list(set(recommendations["patterns_that_work"]))[:10]
    recommendations["patterns_to_avoid"] = list(set(recommendations["patterns_to_avoid"]))[:10]
    
    return recommendations


@router.get("/stats")
async def get_memory_stats():
    """Get overall memory system statistics"""
    total_builds = await db.build_memories.count_documents({})
    successful_builds = await db.build_memories.count_documents({"successful": True})
    total_insights = await db.learning_insights.count_documents({})
    
    # Average scores by project type
    pipeline = [
        {"$group": {
            "_id": "$project_type",
            "avg_score": {"$avg": "$final_score"},
            "count": {"$sum": 1}
        }}
    ]
    type_stats = await db.build_memories.aggregate(pipeline).to_list(100)
    
    return {
        "total_builds": total_builds,
        "successful_builds": successful_builds,
        "success_rate": round((successful_builds / total_builds * 100) if total_builds > 0 else 0, 1),
        "total_insights": total_insights,
        "by_project_type": {s["_id"]: {"avg_score": round(s["avg_score"], 1), "count": s["count"]} for s in type_stats}
    }


# ============ INTERNAL FUNCTIONS ============

async def update_learning_insights(memory: BuildMemory):
    """Extract and store insights from a build"""
    
    # If build was successful with high score, learn from it
    if memory.successful and memory.final_score >= 75:
        
        # Learn architecture patterns
        if memory.architecture_used:
            await add_or_update_insight(
                category="architecture",
                insight=f"Architecture pattern works well for {memory.project_type}: {memory.architecture_used[:100]}",
                confidence_boost=0.1
            )
        
        # Learn from patterns that worked
        for pattern in memory.patterns_that_worked:
            await add_or_update_insight(
                category="patterns",
                insight=pattern,
                confidence_boost=0.15
            )
    
    # Learn from failures
    if not memory.successful or memory.final_score < 60:
        for pattern in memory.patterns_to_avoid:
            await add_or_update_insight(
                category="anti_patterns",
                insight=f"AVOID: {pattern}",
                confidence_boost=0.1
            )


async def add_or_update_insight(category: str, insight: str, confidence_boost: float):
    """Add a new insight or increase confidence in existing one"""
    
    existing = await db.learning_insights.find_one({"insight": insight})
    
    if existing:
        new_confidence = min(1.0, existing.get("confidence", 0.5) + confidence_boost)
        await db.learning_insights.update_one(
            {"insight": insight},
            {"$set": {
                "confidence": new_confidence,
                "evidence_count": existing.get("evidence_count", 1) + 1
            }}
        )
    else:
        new_insight = LearningInsight(
            category=category,
            insight=insight,
            confidence=min(1.0, 0.3 + confidence_boost),
            evidence_count=1
        )
        await db.learning_insights.insert_one(new_insight.model_dump())
