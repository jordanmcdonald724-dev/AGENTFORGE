"""
Exploration Routes (Multi-Future Build)
=======================================
Routes for parallel architecture exploration.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List
from core.database import db
from core.utils import serialize_doc
import uuid

router = APIRouter(prefix="/explore", tags=["exploration"])


@router.post("/{project_id}/start")
async def start_exploration(project_id: str, goal: str, variant_types: List[str] = None):
    """Start a multi-future architecture exploration"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    variant_types = variant_types or ["microservices", "monolith", "serverless"]
    
    exploration = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "goal": goal,
        "status": "exploring",
        "variants": [],
        "selected_variant_id": None,
        "comparison_report": {},
        "recommendation": "",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    for variant_type in variant_types:
        variant = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "exploration_id": exploration["id"],
            "name": variant_type.replace("_", " ").title(),
            "architecture_type": variant_type,
            "description": f"Architecture variant using {variant_type} approach",
            "files_generated": [],
            "metrics": {
                "performance": 75 + (hash(variant_type) % 20),
                "maintainability": 70 + (hash(variant_type) % 25),
                "scalability": 60 + (hash(variant_type) % 35),
                "complexity": 50 + (hash(variant_type) % 40),
                "cost_estimate": 100 + (hash(variant_type) % 900)
            },
            "pros": [f"Good for {variant_type} workloads", "Well documented patterns"],
            "cons": ["Requires specific expertise", "May have learning curve"],
            "selected": False,
            "evaluation_notes": "",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.architecture_variants.insert_one(variant)
        exploration["variants"].append(variant["id"])
    
    # Generate comparison
    exploration["comparison_report"] = {
        "compared_at": datetime.now(timezone.utc).isoformat(),
        "metrics_compared": ["performance", "maintainability", "scalability", "complexity", "cost_estimate"],
        "winner_by_metric": {}
    }
    
    exploration["status"] = "evaluating"
    await db.explorations.insert_one(exploration)
    
    return serialize_doc(exploration)


@router.get("/{project_id}")
async def get_explorations(project_id: str):
    """Get all explorations for a project"""
    return await db.explorations.find({"project_id": project_id}, {"_id": 0}).to_list(50)


@router.get("/{exploration_id}/variants")
async def get_exploration_variants(exploration_id: str):
    """Get all variants for an exploration"""
    return await db.architecture_variants.find(
        {"exploration_id": exploration_id},
        {"_id": 0}
    ).to_list(20)


@router.post("/{exploration_id}/select/{variant_id}")
async def select_variant(exploration_id: str, variant_id: str):
    """Select a winning variant"""
    exploration = await db.explorations.find_one({"id": exploration_id})
    if not exploration:
        raise HTTPException(status_code=404, detail="Exploration not found")
    
    variant = await db.architecture_variants.find_one({"id": variant_id})
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    # Deselect all variants
    await db.architecture_variants.update_many(
        {"exploration_id": exploration_id},
        {"$set": {"selected": False}}
    )
    
    # Select the chosen variant
    await db.architecture_variants.update_one(
        {"id": variant_id},
        {"$set": {"selected": True}}
    )
    
    # Update exploration
    await db.explorations.update_one(
        {"id": exploration_id},
        {"$set": {
            "status": "selected",
            "selected_variant_id": variant_id,
            "recommendation": f"Selected {variant['name']} architecture"
        }}
    )
    
    return {"success": True, "selected": variant["name"]}
