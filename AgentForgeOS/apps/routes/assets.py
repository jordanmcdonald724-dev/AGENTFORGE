"""
Asset Pipeline Routes
=====================
Routes for managing project assets (images, audio, textures, etc.).
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Optional
from engine.core.database import db
from services.utils import serialize_doc
import uuid

router = APIRouter(prefix="/assets", tags=["assets"])


ASSET_TYPES = {
    "image": {"formats": ["png", "jpg", "jpeg", "webp", "gif", "svg"], "icon": "image", "color": "blue"},
    "audio": {"formats": ["mp3", "wav", "ogg", "flac", "aac"], "icon": "volume-2", "color": "purple"},
    "texture": {"formats": ["png", "jpg", "tga", "dds", "exr"], "icon": "grid", "color": "amber"},
    "sprite": {"formats": ["png", "gif", "webp"], "icon": "layers", "color": "cyan"},
    "model_3d": {"formats": ["fbx", "obj", "gltf", "glb", "blend"], "icon": "box", "color": "emerald"},
    "material": {"formats": ["mat", "json", "uasset"], "icon": "palette", "color": "pink"},
    "animation": {"formats": ["fbx", "anim", "json"], "icon": "play", "color": "orange"},
    "font": {"formats": ["ttf", "otf", "woff", "woff2"], "icon": "type", "color": "zinc"},
    "video": {"formats": ["mp4", "webm", "mov", "avi"], "icon": "film", "color": "red"},
    "script": {"formats": ["js", "ts", "py", "cs", "cpp", "lua", "gd"], "icon": "code", "color": "green"}
}

ASSET_CATEGORIES = [
    {"id": "ui", "name": "UI/HUD", "description": "User interface elements"},
    {"id": "character", "name": "Characters", "description": "Player, NPCs, enemies"},
    {"id": "environment", "name": "Environment", "description": "World, props, terrain"},
    {"id": "vfx", "name": "VFX/Particles", "description": "Visual effects"},
    {"id": "audio", "name": "Audio", "description": "Sound effects and music"},
    {"id": "animation", "name": "Animations", "description": "Character and object animations"},
    {"id": "misc", "name": "Miscellaneous", "description": "Other assets"}
]


@router.get("/types")
async def get_asset_types():
    """Get supported asset types"""
    return ASSET_TYPES


@router.get("/categories")
async def get_asset_categories():
    """Get asset categories"""
    return ASSET_CATEGORIES


@router.get("/{project_id}")
async def get_project_assets(project_id: str, asset_type: str = None, category: str = None):
    """Get all assets for a project"""
    query = {"project_id": project_id}
    if asset_type:
        query["asset_type"] = asset_type
    if category:
        query["category"] = category
    
    return await db.assets.find(query, {"_id": 0}).to_list(500)


@router.get("/{project_id}/summary")
async def get_asset_summary(project_id: str):
    """Get asset summary for a project"""
    assets = await db.assets.find({"project_id": project_id}, {"_id": 0}).to_list(1000)
    
    summary = {
        "total": len(assets),
        "by_type": {},
        "by_category": {},
        "total_size_mb": 0
    }
    
    for asset in assets:
        atype = asset.get("asset_type", "unknown")
        category = asset.get("category", "misc")
        size = asset.get("file_size_bytes", 0)
        
        summary["by_type"][atype] = summary["by_type"].get(atype, 0) + 1
        summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
        summary["total_size_mb"] += size / (1024 * 1024)
    
    summary["total_size_mb"] = round(summary["total_size_mb"], 2)
    return summary


@router.post("/import")
async def import_asset(
    project_id: str,
    name: str,
    asset_type: str,
    category: str = "misc",
    url: str = None,
    tags: List[str] = None
):
    """Import an asset into a project"""
    if asset_type not in ASSET_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid asset type: {asset_type}")
    
    asset = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "name": name,
        "asset_type": asset_type,
        "category": category,
        "url": url,
        "tags": tags or [],
        "source": "imported",
        "status": "ready",
        "version": 1,
        "created_by": "user",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.assets.insert_one(asset)
    return serialize_doc(asset)


@router.post("/{project_id}/from-generation")
async def link_generated_asset(
    project_id: str,
    source_id: str,
    source_type: str,
    name: str,
    category: str = "misc"
):
    """Link a generated asset (image/audio) to the asset pipeline"""
    if source_type == "image":
        source = await db.images.find_one({"id": source_id}, {"_id": 0})
        asset_type = "image"
    elif source_type == "audio":
        source = await db.audio_assets.find_one({"id": source_id}, {"_id": 0})
        asset_type = "audio"
    else:
        raise HTTPException(status_code=400, detail=f"Invalid source type: {source_type}")
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    asset = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "name": name,
        "asset_type": asset_type,
        "category": category,
        "url": source.get("url"),
        "source": "generated",
        "source_id": source_id,
        "metadata": {"prompt": source.get("prompt")},
        "status": "ready",
        "version": 1,
        "created_by": "system",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.assets.insert_one(asset)
    return serialize_doc(asset)


@router.patch("/{asset_id}")
async def update_asset(asset_id: str, updates: dict):
    """Update an asset"""
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.assets.update_one({"id": asset_id}, {"$set": updates})
    return {"success": True}


@router.delete("/{asset_id}")
async def delete_asset(asset_id: str):
    """Delete an asset"""
    await db.assets.delete_one({"id": asset_id})
    return {"success": True}


@router.post("/{asset_id}/add-dependency")
async def add_dependency(asset_id: str, depends_on: str):
    """Add a dependency between assets"""
    await db.assets.update_one(
        {"id": asset_id},
        {"$addToSet": {"dependencies": depends_on}}
    )
    await db.assets.update_one(
        {"id": depends_on},
        {"$addToSet": {"dependents": asset_id}}
    )
    return {"success": True}


@router.post("/{asset_id}/remove-dependency")
async def remove_dependency(asset_id: str, depends_on: str):
    """Remove a dependency between assets"""
    await db.assets.update_one(
        {"id": asset_id},
        {"$pull": {"dependencies": depends_on}}
    )
    await db.assets.update_one(
        {"id": depends_on},
        {"$pull": {"dependents": asset_id}}
    )
    return {"success": True}


@router.get("/{project_id}/dependency-graph")
async def get_dependency_graph(project_id: str):
    """Get the dependency graph for project assets"""
    assets = await db.assets.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    nodes = [{"id": a["id"], "name": a["name"], "type": a.get("asset_type")} for a in assets]
    edges = []
    
    for asset in assets:
        for dep in asset.get("dependencies", []):
            edges.append({"source": asset["id"], "target": dep})
    
    return {"nodes": nodes, "edges": edges}


@router.post("/{project_id}/sync-from-files")
async def sync_assets_from_files(project_id: str):
    """Sync assets from project files"""
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    synced = []
    
    for f in files:
        ext = f.get("filepath", "").split(".")[-1].lower() if "." in f.get("filepath", "") else ""
        
        asset_type = None
        for atype, config in ASSET_TYPES.items():
            if ext in config["formats"]:
                asset_type = atype
                break
        
        if asset_type:
            existing = await db.assets.find_one({
                "project_id": project_id,
                "file_path": f.get("filepath")
            })
            
            if not existing:
                asset = {
                    "id": str(uuid.uuid4()),
                    "project_id": project_id,
                    "name": f.get("filename", f.get("filepath", "").split("/")[-1]),
                    "asset_type": asset_type,
                    "category": "misc",
                    "file_path": f.get("filepath"),
                    "source": "synced",
                    "status": "ready",
                    "version": 1,
                    "created_by": "system",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                await db.assets.insert_one(asset)
                synced.append(asset["name"])
    
    return {"synced": synced, "count": len(synced)}
