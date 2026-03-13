"""
Autonomous Discovery - Background Experiments
==============================================
AgentForge runs exploration builds in the background,
discovering new software patterns and keeping the best results.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.database import db
from core.clients import llm_client
from core.utils import serialize_doc
import uuid
import json
import asyncio
import random

router = APIRouter(prefix="/discovery", tags=["autonomous-discovery"])


# ========== EXPERIMENT TYPES ==========

EXPERIMENT_TYPES = {
    "architecture": {
        "name": "Architecture Experiment",
        "description": "Test new software architecture patterns",
        "duration_minutes": 30,
        "examples": ["microservices", "event-driven", "serverless", "modular-monolith"]
    },
    "ui_component": {
        "name": "UI Component Discovery",
        "description": "Generate and test new UI component patterns",
        "duration_minutes": 15,
        "examples": ["dashboard-widget", "data-table", "form-builder", "navigation"]
    },
    "algorithm": {
        "name": "Algorithm Optimization",
        "description": "Discover optimized algorithms for common tasks",
        "duration_minutes": 20,
        "examples": ["search", "sorting", "caching", "compression"]
    },
    "integration": {
        "name": "Integration Pattern",
        "description": "Test new API and service integration patterns",
        "duration_minutes": 25,
        "examples": ["webhook", "event-bus", "saga", "circuit-breaker"]
    },
    "game_system": {
        "name": "Game System Discovery",
        "description": "Experiment with game mechanics and systems",
        "duration_minutes": 45,
        "examples": ["inventory", "combat", "dialogue", "procedural-generation"]
    }
}


@router.get("/types")
async def get_experiment_types():
    """Get available experiment types"""
    return EXPERIMENT_TYPES


@router.get("/experiments")
async def list_experiments(status: str = None, limit: int = 50):
    """List all experiments"""
    query = {}
    if status:
        query["status"] = status
    
    return await db.experiments.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)


@router.post("/start")
async def start_experiment(
    experiment_type: str,
    hypothesis: str,
    target_area: str = None,
    auto_iterate: bool = True
):
    """Start a new autonomous experiment"""
    if experiment_type not in EXPERIMENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid experiment type: {experiment_type}")
    
    exp_config = EXPERIMENT_TYPES[experiment_type]
    
    experiment = {
        "id": str(uuid.uuid4()),
        "type": experiment_type,
        "type_name": exp_config["name"],
        "hypothesis": hypothesis,
        "target_area": target_area,
        "auto_iterate": auto_iterate,
        "status": "running",
        "iterations": [],
        "current_iteration": 0,
        "max_iterations": 5,
        "best_result": None,
        "best_score": 0,
        "discoveries": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "estimated_duration_minutes": exp_config["duration_minutes"]
    }
    
    # Run first iteration
    iteration_result = await _run_experiment_iteration(experiment)
    experiment["iterations"].append(iteration_result)
    experiment["current_iteration"] = 1
    
    if iteration_result.get("score", 0) > experiment["best_score"]:
        experiment["best_score"] = iteration_result["score"]
        experiment["best_result"] = iteration_result
    
    await db.experiments.insert_one(experiment)
    
    return serialize_doc(experiment)


async def _run_experiment_iteration(experiment: dict) -> dict:
    """Run a single experiment iteration"""
    iteration = {
        "iteration_num": experiment.get("current_iteration", 0) + 1,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "running"
    }
    
    try:
        # Use LLM to generate experiment
        response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": f"""You are an autonomous software discovery system.
You're running an experiment of type: {experiment['type']}
Hypothesis: {experiment['hypothesis']}

Generate an innovative solution or pattern. Output JSON:
{{
    "approach": "Description of the approach",
    "code_sample": "// Key code demonstrating the pattern",
    "innovations": ["innovation1", "innovation2"],
    "potential_applications": ["app1", "app2"],
    "complexity_score": 0.0-1.0,
    "novelty_score": 0.0-1.0
}}"""},
                {"role": "user", "content": f"Run iteration {iteration['iteration_num']} of experiment: {experiment['hypothesis']}"}
            ],
            max_tokens=3000
        )
        
        result_text = response.choices[0].message.content
        
        # Try to parse JSON
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {"approach": result_text, "innovations": []}
        except:
            result = {"approach": result_text, "innovations": []}
        
        iteration["result"] = result
        iteration["score"] = (result.get("novelty_score", 0.5) + result.get("complexity_score", 0.5)) / 2
        iteration["status"] = "completed"
        
    except Exception as e:
        iteration["status"] = "failed"
        iteration["error"] = str(e)
        iteration["score"] = 0
    
    iteration["completed_at"] = datetime.now(timezone.utc).isoformat()
    return iteration


@router.post("/{experiment_id}/iterate")
async def run_next_iteration(experiment_id: str):
    """Run the next iteration of an experiment"""
    experiment = await db.experiments.find_one({"id": experiment_id})
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    if experiment["current_iteration"] >= experiment["max_iterations"]:
        return {"message": "Max iterations reached", "status": "completed"}
    
    iteration_result = await _run_experiment_iteration(experiment)
    
    update = {
        "$push": {"iterations": iteration_result},
        "$inc": {"current_iteration": 1}
    }
    
    if iteration_result.get("score", 0) > experiment.get("best_score", 0):
        update["$set"] = {
            "best_score": iteration_result["score"],
            "best_result": iteration_result
        }
    
    await db.experiments.update_one({"id": experiment_id}, update)
    
    return iteration_result


@router.post("/{experiment_id}/stop")
async def stop_experiment(experiment_id: str):
    """Stop an experiment"""
    await db.experiments.update_one(
        {"id": experiment_id},
        {"$set": {"status": "stopped", "stopped_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"success": True}


@router.get("/{experiment_id}")
async def get_experiment(experiment_id: str):
    """Get experiment details"""
    experiment = await db.experiments.find_one({"id": experiment_id}, {"_id": 0})
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@router.post("/{experiment_id}/promote")
async def promote_discovery(experiment_id: str, iteration_num: int = None):
    """Promote a discovery to the gene library"""
    experiment = await db.experiments.find_one({"id": experiment_id}, {"_id": 0})
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Get best iteration or specified one
    if iteration_num:
        iteration = next((i for i in experiment["iterations"] if i["iteration_num"] == iteration_num), None)
    else:
        iteration = experiment.get("best_result")
    
    if not iteration:
        raise HTTPException(status_code=404, detail="No iteration found to promote")
    
    # Create gene from discovery
    result = iteration.get("result", {})
    
    gene = {
        "id": str(uuid.uuid4()),
        "name": f"Discovery: {experiment['hypothesis'][:50]}",
        "category": experiment["type"],
        "gene_type": f"discovered-{experiment['type']}",
        "code_snippet": result.get("code_sample", ""),
        "source_experiment": experiment_id,
        "innovations": result.get("innovations", []),
        "score": iteration.get("score", 0),
        "usage_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.genes.insert_one(gene)
    
    # Record discovery
    discovery = {
        "id": str(uuid.uuid4()),
        "experiment_id": experiment_id,
        "gene_id": gene["id"],
        "hypothesis": experiment["hypothesis"],
        "approach": result.get("approach", ""),
        "score": iteration.get("score", 0),
        "promoted_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.discoveries.insert_one(discovery)
    await db.experiments.update_one(
        {"id": experiment_id},
        {"$push": {"discoveries": discovery["id"]}, "$set": {"status": "promoted"}}
    )
    
    return {
        "gene_id": gene["id"],
        "discovery_id": discovery["id"],
        "message": "Discovery promoted to gene library"
    }


@router.get("/discoveries/all")
async def list_discoveries(limit: int = 50):
    """List all promoted discoveries"""
    return await db.discoveries.find({}, {"_id": 0}).sort("promoted_at", -1).to_list(limit)


@router.get("/stats")
async def get_discovery_stats():
    """Get autonomous discovery statistics"""
    experiments = await db.experiments.find({}, {"_id": 0}).to_list(500)
    discoveries = await db.discoveries.find({}, {"_id": 0}).to_list(500)
    
    type_stats = {}
    for exp in experiments:
        exp_type = exp.get("type", "unknown")
        type_stats[exp_type] = type_stats.get(exp_type, 0) + 1
    
    return {
        "total_experiments": len(experiments),
        "running": len([e for e in experiments if e.get("status") == "running"]),
        "completed": len([e for e in experiments if e.get("status") == "completed"]),
        "promoted": len([e for e in experiments if e.get("status") == "promoted"]),
        "total_discoveries": len(discoveries),
        "by_type": type_stats,
        "average_score": sum(e.get("best_score", 0) for e in experiments) / max(len(experiments), 1)
    }


# ========== AUTO-DISCOVERY QUEUE ==========

@router.post("/auto-discover")
async def start_auto_discovery(focus_areas: List[str] = None):
    """Start autonomous discovery across multiple areas"""
    focus_areas = focus_areas or list(EXPERIMENT_TYPES.keys())
    
    started_experiments = []
    
    for area in focus_areas[:3]:  # Limit to 3 concurrent
        if area in EXPERIMENT_TYPES:
            exp_config = EXPERIMENT_TYPES[area]
            hypothesis = random.choice(exp_config["examples"])
            
            experiment = {
                "id": str(uuid.uuid4()),
                "type": area,
                "type_name": exp_config["name"],
                "hypothesis": f"Explore new {hypothesis} patterns",
                "auto_iterate": True,
                "status": "queued",
                "iterations": [],
                "current_iteration": 0,
                "max_iterations": 3,
                "best_result": None,
                "best_score": 0,
                "discoveries": [],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.experiments.insert_one(experiment)
            started_experiments.append({"id": experiment["id"], "type": area, "hypothesis": experiment["hypothesis"]})
    
    return {
        "message": "Auto-discovery started",
        "experiments_queued": len(started_experiments),
        "experiments": started_experiments
    }
