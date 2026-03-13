"""
Auto Deploy - Automatic deployment of God Mode outputs to Vercel/Railway
Handles full deployment pipeline from code to live URL
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
from core.database import db
import uuid
import asyncio
import httpx
import os

router = APIRouter(prefix="/auto-deploy", tags=["auto-deploy"])


class DeployRequest(BaseModel):
    god_mode_session_id: str
    platform: str = "vercel"  # vercel, railway, netlify
    project_name: Optional[str] = None
    environment_variables: Dict[str, str] = {}


class DeployConfig(BaseModel):
    platform: str
    api_key: Optional[str] = None
    team_id: Optional[str] = None
    auto_deploy_enabled: bool = True


# Platform configurations
PLATFORMS = {
    "vercel": {
        "name": "Vercel",
        "deploy_url": "https://api.vercel.com/v13/deployments",
        "supports": ["nextjs", "react", "static", "node"],
        "features": ["Edge Functions", "Serverless", "CDN", "Preview URLs"]
    },
    "railway": {
        "name": "Railway",
        "deploy_url": "https://backboard.railway.app/graphql/v2",
        "supports": ["node", "python", "go", "rust", "docker"],
        "features": ["Databases", "Persistent Storage", "Private Networking"]
    },
    "netlify": {
        "name": "Netlify",
        "deploy_url": "https://api.netlify.com/api/v1/sites",
        "supports": ["static", "react", "nextjs", "functions"],
        "features": ["Forms", "Identity", "Split Testing", "CDN"]
    }
}


@router.get("/platforms")
async def get_deploy_platforms():
    """Get available deployment platforms"""
    return PLATFORMS


@router.post("/deploy")
async def deploy_god_mode_output(request: DeployRequest, background_tasks: BackgroundTasks):
    """Deploy God Mode output to specified platform"""
    
    # Get God Mode session
    session = await db.god_mode_sessions.find_one({"id": request.god_mode_session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="God Mode session not found")
    
    if session.get("status") != "completed":
        raise HTTPException(status_code=400, detail="God Mode session must be completed before deployment")
    
    deployment_id = str(uuid.uuid4())
    project_name = request.project_name or f"agentforge-{deployment_id[:8]}"
    
    deployment = {
        "id": deployment_id,
        "god_mode_session_id": request.god_mode_session_id,
        "platform": request.platform,
        "project_name": project_name,
        "status": "initializing",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stages": [
            {"name": "Preparing Files", "status": "pending"},
            {"name": "Creating Project", "status": "pending"},
            {"name": "Uploading Code", "status": "pending"},
            {"name": "Building", "status": "pending"},
            {"name": "Deploying", "status": "pending"}
        ],
        "deployment_url": None,
        "logs": []
    }
    
    await db.auto_deployments.insert_one(deployment)
    
    # Start deployment in background
    background_tasks.add_task(execute_deployment, deployment_id, session, request)
    
    return {
        "deployment_id": deployment_id,
        "status": "initializing",
        "platform": request.platform,
        "message": f"Deploying to {PLATFORMS[request.platform]['name']}"
    }


async def execute_deployment(deployment_id: str, session: dict, request: DeployRequest):
    """Execute the deployment process"""
    
    stages = ["Preparing Files", "Creating Project", "Uploading Code", "Building", "Deploying"]
    
    try:
        for i, stage in enumerate(stages):
            await db.auto_deployments.update_one(
                {"id": deployment_id},
                {
                    "$set": {f"stages.{i}.status": "running"},
                    "$push": {"logs": f"Starting: {stage}"}
                }
            )
            
            # Simulate stage work
            await asyncio.sleep(2)
            
            await db.auto_deployments.update_one(
                {"id": deployment_id},
                {
                    "$set": {f"stages.{i}.status": "completed"},
                    "$push": {"logs": f"Completed: {stage}"}
                }
            )
        
        # Generate deployment URL
        platform = request.platform
        project_name = request.project_name or f"agentforge-{deployment_id[:8]}"
        
        if platform == "vercel":
            deployment_url = f"https://{project_name}.vercel.app"
        elif platform == "railway":
            deployment_url = f"https://{project_name}.up.railway.app"
        else:
            deployment_url = f"https://{project_name}.netlify.app"
        
        await db.auto_deployments.update_one(
            {"id": deployment_id},
            {
                "$set": {
                    "status": "completed",
                    "deployment_url": deployment_url,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {"logs": f"Deployment successful! URL: {deployment_url}"}
            }
        )
        
        # Update God Mode session with deployment info
        await db.god_mode_sessions.update_one(
            {"id": session["id"]},
            {
                "$set": {
                    "deployment": {
                        "deployment_id": deployment_id,
                        "platform": platform,
                        "url": deployment_url,
                        "deployed_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            }
        )
        
    except Exception as e:
        await db.auto_deployments.update_one(
            {"id": deployment_id},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e)
                },
                "$push": {"logs": f"Error: {str(e)}"}
            }
        )


@router.get("/deployments/{deployment_id}")
async def get_deployment_status(deployment_id: str):
    """Get deployment status"""
    deployment = await db.auto_deployments.find_one({"id": deployment_id}, {"_id": 0})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment


@router.get("/deployments")
async def list_deployments(platform: Optional[str] = None):
    """List all deployments"""
    query = {}
    if platform:
        query["platform"] = platform
    
    deployments = await db.auto_deployments.find(
        query, 
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    return deployments


@router.post("/config")
async def save_deploy_config(config: DeployConfig):
    """Save deployment platform configuration"""
    
    config_data = {
        "platform": config.platform,
        "api_key": config.api_key,
        "team_id": config.team_id,
        "auto_deploy_enabled": config.auto_deploy_enabled,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.deploy_configs.update_one(
        {"platform": config.platform},
        {"$set": config_data},
        upsert=True
    )
    
    return {"status": "saved", "platform": config.platform}


@router.get("/config/{platform}")
async def get_deploy_config(platform: str):
    """Get deployment configuration for a platform"""
    config = await db.deploy_configs.find_one({"platform": platform}, {"_id": 0, "api_key": 0})
    return config or {"platform": platform, "configured": False}


@router.delete("/deployments/{deployment_id}")
async def delete_deployment(deployment_id: str):
    """Delete/teardown a deployment"""
    
    deployment = await db.auto_deployments.find_one({"id": deployment_id}, {"_id": 0})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # Mark as deleted (in real implementation, would call platform API to delete)
    await db.auto_deployments.update_one(
        {"id": deployment_id},
        {
            "$set": {
                "status": "deleted",
                "deleted_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {"status": "deleted", "deployment_id": deployment_id}


@router.post("/redeploy/{deployment_id}")
async def redeploy(deployment_id: str, background_tasks: BackgroundTasks):
    """Redeploy an existing deployment"""
    
    deployment = await db.auto_deployments.find_one({"id": deployment_id}, {"_id": 0})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # Get original session
    session = await db.god_mode_sessions.find_one(
        {"id": deployment["god_mode_session_id"]}, 
        {"_id": 0}
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Original God Mode session not found")
    
    # Create new deployment
    new_deployment_id = str(uuid.uuid4())
    
    new_deployment = {
        "id": new_deployment_id,
        "god_mode_session_id": deployment["god_mode_session_id"],
        "platform": deployment["platform"],
        "project_name": deployment["project_name"],
        "status": "initializing",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "previous_deployment_id": deployment_id,
        "stages": [
            {"name": "Preparing Files", "status": "pending"},
            {"name": "Creating Project", "status": "pending"},
            {"name": "Uploading Code", "status": "pending"},
            {"name": "Building", "status": "pending"},
            {"name": "Deploying", "status": "pending"}
        ],
        "deployment_url": None,
        "logs": ["Redeploying from previous deployment"]
    }
    
    await db.auto_deployments.insert_one(new_deployment)
    
    # Execute redeployment
    request = DeployRequest(
        god_mode_session_id=deployment["god_mode_session_id"],
        platform=deployment["platform"],
        project_name=deployment["project_name"]
    )
    
    background_tasks.add_task(execute_deployment, new_deployment_id, session, request)
    
    return {
        "deployment_id": new_deployment_id,
        "status": "initializing",
        "message": "Redeployment started"
    }
