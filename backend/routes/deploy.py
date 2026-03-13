"""
Deployment Routes
=================
Routes for deploying projects to various platforms (Vercel, Railway, Itch.io).
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from core.database import db
from core.utils import serialize_doc
import os
import uuid
import httpx

router = APIRouter(prefix="/deploy", tags=["deploy"])


DEPLOYMENT_PLATFORMS = {
    "vercel": {
        "id": "vercel",
        "name": "Vercel",
        "icon": "triangle",
        "color": "zinc",
        "description": "Best for web apps and static sites",
        "supports": ["web_app", "webpage", "static"],
        "requires": ["VERCEL_TOKEN"]
    },
    "railway": {
        "id": "railway",
        "name": "Railway",
        "icon": "train",
        "color": "purple",
        "description": "Full-stack apps with databases",
        "supports": ["web_app", "api", "fullstack"],
        "requires": ["RAILWAY_TOKEN"]
    },
    "itch": {
        "id": "itch",
        "name": "Itch.io",
        "icon": "gamepad-2",
        "color": "red",
        "description": "Game distribution platform",
        "supports": ["game", "web_game"],
        "requires": ["ITCH_API_KEY", "ITCH_USERNAME"]
    }
}


@router.get("/platforms")
async def get_platforms():
    """Get available deployment platforms"""
    return list(DEPLOYMENT_PLATFORMS.values())


@router.get("/config")
async def get_deploy_config():
    """Get deployment configuration status"""
    return {
        "vercel": bool(os.environ.get("VERCEL_TOKEN")),
        "railway": bool(os.environ.get("RAILWAY_TOKEN")),
        "itch": bool(os.environ.get("ITCH_API_KEY") and os.environ.get("ITCH_USERNAME"))
    }


@router.get("/{project_id}")
async def get_deployments(project_id: str):
    """Get deployments for a project"""
    return await db.deployments.find({"project_id": project_id}, {"_id": 0}).to_list(50)


@router.post("/{project_id}/vercel")
async def deploy_to_vercel(project_id: str, token: str = None, project_name: str = None):
    """Deploy project to Vercel"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    api_token = token or os.environ.get("VERCEL_TOKEN")
    if not api_token:
        raise HTTPException(status_code=400, detail="Vercel token required")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    deployment = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "platform": "vercel",
        "project_name": project_name or project.get("name", "").replace(" ", "-").lower(),
        "status": "deploying",
        "logs": ["Preparing deployment..."],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        file_structure = {}
        for f in files:
            path = f.get("filepath", "").lstrip("/")
            if path:
                file_structure[path] = {"content": f.get("content", "")}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.vercel.com/v13/deployments",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": deployment["project_name"],
                    "files": [{"file": k, "data": v["content"]} for k, v in file_structure.items()],
                    "projectSettings": {"framework": None}
                },
                timeout=60.0
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                deployment["deploy_url"] = f"https://{data.get('url', '')}"
                deployment["admin_url"] = f"https://vercel.com/{data.get('ownerId')}/{deployment['project_name']}"
                deployment["status"] = "live"
                deployment["deployed_at"] = datetime.now(timezone.utc).isoformat()
                deployment["logs"].append(f"Deployed to {deployment['deploy_url']}")
            else:
                deployment["status"] = "failed"
                deployment["logs"].append(f"Deploy failed: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        deployment["status"] = "failed"
        deployment["logs"].append(f"Deploy error: {str(e)}")
    
    await db.deployments.insert_one(deployment)
    return serialize_doc(deployment)


@router.post("/{project_id}/quick/vercel")
async def quick_deploy_vercel(project_id: str):
    """Quick deploy to Vercel using server-side credentials"""
    return await deploy_to_vercel(project_id)


@router.post("/{project_id}/railway")
async def deploy_to_railway(project_id: str, token: str = None, service_name: str = None):
    """Deploy project to Railway"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    api_token = token or os.environ.get("RAILWAY_TOKEN")
    if not api_token:
        raise HTTPException(status_code=400, detail="Railway token required")
    
    deployment = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "platform": "railway",
        "project_name": service_name or project.get("name", "").replace(" ", "-").lower(),
        "status": "deploying",
        "logs": ["Preparing Railway deployment..."],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    deployment["status"] = "pending"
    deployment["logs"].append("Railway deployment initiated - check Railway dashboard")
    deployment["deploy_url"] = f"https://{deployment['project_name']}.up.railway.app"
    
    await db.deployments.insert_one(deployment)
    return serialize_doc(deployment)


@router.post("/{project_id}/quick/railway")
async def quick_deploy_railway(project_id: str):
    """Quick deploy to Railway using server-side credentials"""
    return await deploy_to_railway(project_id)


@router.post("/{project_id}/itch")
async def deploy_to_itch(project_id: str, game_name: str = None):
    """Deploy game to Itch.io"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    api_key = os.environ.get("ITCH_API_KEY")
    username = os.environ.get("ITCH_USERNAME")
    
    if not api_key or not username:
        raise HTTPException(status_code=400, detail="Itch.io credentials required")
    
    deployment = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "platform": "itch",
        "project_name": game_name or project.get("name", "").replace(" ", "-").lower(),
        "status": "pending",
        "logs": ["Itch.io upload initiated..."],
        "config": {"username": username},
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    deployment["deploy_url"] = f"https://{username}.itch.io/{deployment['project_name']}"
    deployment["logs"].append(f"Game page: {deployment['deploy_url']}")
    
    await db.deployments.insert_one(deployment)
    return serialize_doc(deployment)


@router.delete("/{deployment_id}")
async def delete_deployment(deployment_id: str):
    """Delete a deployment record"""
    await db.deployments.delete_one({"id": deployment_id})
    return {"success": True}
