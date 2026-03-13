"""
AI Dev Economy - Module Marketplace
====================================
Agents publish and consume reusable modules.
A living ecosystem of software components.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.database import db
from core.utils import serialize_doc
import uuid

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


# ========== MODULE CATEGORIES ==========

MODULE_CATEGORIES = {
    "frontend": {
        "name": "Frontend",
        "icon": "layout",
        "subcategories": ["components", "pages", "hooks", "styles", "animations"]
    },
    "backend": {
        "name": "Backend",
        "icon": "server",
        "subcategories": ["api", "auth", "database", "middleware", "utils"]
    },
    "game": {
        "name": "Game Dev",
        "icon": "gamepad",
        "subcategories": ["mechanics", "ai", "physics", "ui", "networking"]
    },
    "ai": {
        "name": "AI/ML",
        "icon": "brain",
        "subcategories": ["llm", "vision", "audio", "agents", "embeddings"]
    },
    "infrastructure": {
        "name": "Infrastructure",
        "icon": "cloud",
        "subcategories": ["docker", "ci-cd", "monitoring", "deployment", "security"]
    }
}


@router.get("/categories")
async def get_marketplace_categories():
    """Get marketplace categories"""
    return MODULE_CATEGORIES


@router.get("/modules")
async def list_modules(
    category: str = None,
    subcategory: str = None,
    search: str = None,
    sort_by: str = "downloads",
    limit: int = 50
):
    """List marketplace modules"""
    query = {"status": "published"}
    
    if category:
        query["category"] = category
    if subcategory:
        query["subcategory"] = subcategory
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [search.lower()]}}
        ]
    
    sort_field = "downloads" if sort_by == "downloads" else "rating" if sort_by == "rating" else "created_at"
    sort_order = -1
    
    return await db.marketplace_modules.find(query, {"_id": 0}).sort(sort_field, sort_order).to_list(limit)


@router.get("/modules/{module_id}")
async def get_module(module_id: str):
    """Get module details"""
    module = await db.marketplace_modules.find_one({"id": module_id}, {"_id": 0})
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module


@router.post("/modules/publish")
async def publish_module(
    name: str,
    description: str,
    category: str,
    subcategory: str,
    version: str = "1.0.0",
    tags: List[str] = None,
    source_gene_id: str = None,
    source_project_id: str = None,
    code_files: List[dict] = None,
    documentation: str = None,
    publisher_agent: str = "FORGE"
):
    """Publish a module to the marketplace"""
    if category not in MODULE_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    if subcategory not in MODULE_CATEGORIES[category]["subcategories"]:
        raise HTTPException(status_code=400, detail=f"Invalid subcategory: {subcategory}")
    
    module = {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "category": category,
        "subcategory": subcategory,
        "version": version,
        "tags": tags or [],
        "source_gene_id": source_gene_id,
        "source_project_id": source_project_id,
        "code_files": code_files or [],
        "documentation": documentation,
        "publisher_agent": publisher_agent,
        "status": "published",
        "downloads": 0,
        "rating": 0,
        "ratings_count": 0,
        "reviews": [],
        "dependencies": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.marketplace_modules.insert_one(module)
    return serialize_doc(module)


@router.post("/modules/{module_id}/download")
async def download_module(module_id: str, project_id: str = None):
    """Download/use a module"""
    module = await db.marketplace_modules.find_one({"id": module_id})
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Increment download count
    await db.marketplace_modules.update_one(
        {"id": module_id},
        {"$inc": {"downloads": 1}}
    )
    
    # Record usage
    usage = {
        "id": str(uuid.uuid4()),
        "module_id": module_id,
        "project_id": project_id,
        "downloaded_at": datetime.now(timezone.utc).isoformat()
    }
    await db.module_usage.insert_one(usage)
    
    return {
        "module": {
            "id": module["id"],
            "name": module["name"],
            "version": module["version"],
            "code_files": module.get("code_files", [])
        },
        "message": "Module downloaded successfully"
    }


@router.post("/modules/{module_id}/rate")
async def rate_module(module_id: str, rating: int, review: str = None):
    """Rate a module"""
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    
    module = await db.marketplace_modules.find_one({"id": module_id})
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Calculate new average
    current_total = module.get("rating", 0) * module.get("ratings_count", 0)
    new_count = module.get("ratings_count", 0) + 1
    new_rating = (current_total + rating) / new_count
    
    update = {
        "$set": {"rating": round(new_rating, 2), "ratings_count": new_count}
    }
    
    if review:
        review_obj = {
            "id": str(uuid.uuid4()),
            "rating": rating,
            "review": review,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        update["$push"] = {"reviews": review_obj}
    
    await db.marketplace_modules.update_one({"id": module_id}, update)
    
    return {"success": True, "new_rating": round(new_rating, 2)}


@router.delete("/modules/{module_id}")
async def unpublish_module(module_id: str):
    """Unpublish a module"""
    await db.marketplace_modules.update_one(
        {"id": module_id},
        {"$set": {"status": "unpublished"}}
    )
    return {"success": True}


# ========== AGENT PUBLISHING ==========

@router.post("/auto-publish")
async def auto_publish_from_genes():
    """Auto-publish high-quality genes as modules"""
    # Find genes with high usage/quality
    genes = await db.genes.find(
        {"usage_count": {"$gte": 3}, "quality_score": {"$gte": 0.7}},
        {"_id": 0}
    ).to_list(20)
    
    published = []
    
    for gene in genes:
        # Check if already published
        existing = await db.marketplace_modules.find_one({"source_gene_id": gene["id"]})
        if existing:
            continue
        
        # Map gene category to marketplace category
        category_map = {
            "auth": ("backend", "auth"),
            "ui": ("frontend", "components"),
            "data": ("backend", "database"),
            "game": ("game", "mechanics"),
            "infra": ("infrastructure", "deployment"),
            "ai": ("ai", "llm")
        }
        
        gene_cat = gene.get("category", "misc")
        cat, subcat = category_map.get(gene_cat, ("backend", "utils"))
        
        module = {
            "id": str(uuid.uuid4()),
            "name": gene["name"],
            "description": f"Auto-published from gene library. Quality score: {gene.get('quality_score', 0)}",
            "category": cat,
            "subcategory": subcat,
            "version": "1.0.0",
            "tags": [gene_cat, "auto-published", "verified"],
            "source_gene_id": gene["id"],
            "code_files": [{"filename": "main", "content": gene.get("code_snippet", "")}],
            "publisher_agent": "AUTO-PUBLISHER",
            "status": "published",
            "downloads": 0,
            "rating": gene.get("quality_score", 0) * 5,
            "ratings_count": 1,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.marketplace_modules.insert_one(module)
        published.append({"id": module["id"], "name": module["name"]})
    
    return {
        "message": "Auto-publish complete",
        "published_count": len(published),
        "modules": published
    }


@router.get("/stats")
async def get_marketplace_stats():
    """Get marketplace statistics"""
    modules = await db.marketplace_modules.find({"status": "published"}, {"_id": 0}).to_list(1000)
    
    category_stats = {}
    for m in modules:
        cat = m.get("category", "unknown")
        category_stats[cat] = category_stats.get(cat, 0) + 1
    
    total_downloads = sum(m.get("downloads", 0) for m in modules)
    avg_rating = sum(m.get("rating", 0) for m in modules) / max(len(modules), 1)
    
    return {
        "total_modules": len(modules),
        "total_downloads": total_downloads,
        "average_rating": round(avg_rating, 2),
        "by_category": category_stats,
        "top_downloaded": sorted(
            [{"name": m["name"], "downloads": m.get("downloads", 0)} for m in modules],
            key=lambda x: -x["downloads"]
        )[:10],
        "top_rated": sorted(
            [{"name": m["name"], "rating": m.get("rating", 0)} for m in modules if m.get("ratings_count", 0) > 0],
            key=lambda x: -x["rating"]
        )[:10]
    }


@router.get("/recommended")
async def get_recommended_modules(project_type: str = None, limit: int = 10):
    """Get recommended modules based on project type"""
    query = {"status": "published"}
    
    # Recommend based on project type
    if project_type:
        type_recommendations = {
            "web_app": ["frontend", "backend"],
            "game": ["game", "ai"],
            "saas": ["backend", "frontend", "infrastructure"],
            "ai_tool": ["ai", "backend"]
        }
        categories = type_recommendations.get(project_type, ["backend", "frontend"])
        query["category"] = {"$in": categories}
    
    return await db.marketplace_modules.find(
        query,
        {"_id": 0}
    ).sort("downloads", -1).to_list(limit)
