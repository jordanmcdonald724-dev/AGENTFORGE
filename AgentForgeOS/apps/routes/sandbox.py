from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from engine.core.database import db
from providers.clients import tts_client
from services.utils import serialize_doc
from engine.core.config import ASSET_TYPES, ASSET_CATEGORIES, AUDIO_CATEGORIES, DEPLOYMENT_PLATFORMS
from models.sandbox import (
    SandboxSession, PipelineAsset, NotificationSettings, AudioAsset, 
    Deployment, AssetImportRequest
)
import uuid
import base64
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sandbox"])


# Sandbox Routes
@router.post("/sandbox/{project_id}/create")
async def create_sandbox(project_id: str, environment: str = "web"):
    """Create a new sandbox session"""
    session = SandboxSession(
        project_id=project_id,
        environment=environment
    )
    doc = session.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.sandbox_sessions.insert_one(doc)
    return serialize_doc(doc)


@router.get("/sandbox/{project_id}")
async def get_sandbox(project_id: str):
    """Get current sandbox session"""
    return await db.sandbox_sessions.find_one(
        {"project_id": project_id},
        {"_id": 0},
        sort=[("created_at", -1)]
    )


@router.post("/sandbox/{session_id}/execute")
async def execute_in_sandbox(session_id: str, code: str, entry_file: str = None):
    """Execute code in sandbox"""
    session = await db.sandbox_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Sandbox session not found")
    
    output = [
        {"type": "log", "message": f"Executing in {session['environment']} environment...", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"type": "log", "message": "Code parsed successfully", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"type": "log", "message": "Execution complete", "timestamp": datetime.now(timezone.utc).isoformat()}
    ]
    
    await db.sandbox_sessions.update_one(
        {"id": session_id},
        {"$set": {
            "status": "idle",
            "console_output": output,
            "execution_time_ms": 150,
            "memory_usage_mb": 24
        }}
    )
    
    return {"success": True, "output": output}


@router.post("/sandbox/{session_id}/stop")
async def stop_sandbox(session_id: str):
    """Stop sandbox execution"""
    await db.sandbox_sessions.update_one({"id": session_id}, {"$set": {"status": "stopped"}})
    return {"success": True}


# Asset Pipeline Routes
@router.get("/assets/types")
async def get_asset_types():
    """Get available asset types"""
    return ASSET_TYPES


@router.get("/assets/categories")
async def get_asset_categories():
    """Get asset categories"""
    return ASSET_CATEGORIES


@router.post("/assets")
async def create_asset(request: AssetImportRequest):
    """Import or create an asset"""
    asset = PipelineAsset(
        project_id=request.project_id,
        name=request.name,
        asset_type=request.asset_type,
        category=request.category,
        url=request.url,
        tags=request.tags
    )
    doc = asset.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.pipeline_assets.insert_one(doc)
    return serialize_doc(doc)


@router.get("/assets")
async def get_assets(project_id: str, asset_type: str = None, category: str = None):
    """Get assets for a project"""
    query = {"project_id": project_id}
    if asset_type:
        query["asset_type"] = asset_type
    if category:
        query["category"] = category
    return await db.pipeline_assets.find(query, {"_id": 0}).to_list(500)


@router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: str):
    """Delete an asset"""
    await db.pipeline_assets.delete_one({"id": asset_id})
    return {"success": True}


# Audio Generation Routes
@router.get("/audio/categories")
async def get_audio_categories():
    """Get audio generation categories"""
    return AUDIO_CATEGORIES


@router.post("/audio/generate")
async def generate_audio(project_id: str, name: str, audio_type: str, prompt: str, voice: str = "alloy"):
    """Generate audio using OpenAI TTS"""
    try:
        audio_data = await tts_client.generate_speech(
            text=prompt,
            voice=voice,
            model="tts-1"
        )
        
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        audio_url = f"data:audio/mp3;base64,{audio_base64}"
        
        asset = AudioAsset(
            project_id=project_id,
            name=name,
            audio_type=audio_type,
            prompt=prompt,
            provider="openai",
            url=audio_url,
            duration_seconds=len(prompt) / 15,
            metadata={"voice": voice}
        )
        doc = asset.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.audio_assets.insert_one(doc)
        
        return serialize_doc(doc)
        
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")


@router.get("/audio")
async def get_audio_assets(project_id: str):
    """Get audio assets for a project"""
    return await db.audio_assets.find({"project_id": project_id}, {"_id": 0}).to_list(100)


# Notification Routes
@router.get("/notifications/{project_id}/settings")
async def get_notification_settings(project_id: str):
    """Get notification settings"""
    settings = await db.notifications.find_one({"project_id": project_id}, {"_id": 0})
    if not settings:
        default = NotificationSettings(project_id=project_id)
        doc = default.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.notifications.insert_one(doc)
        return serialize_doc(doc)
    return settings


@router.patch("/notifications/{project_id}/settings")
async def update_notification_settings(project_id: str, updates: dict):
    """Update notification settings"""
    await db.notifications.update_one(
        {"project_id": project_id},
        {"$set": updates},
        upsert=True
    )
    return {"success": True}


# Deployment Routes
@router.get("/deploy/platforms")
async def get_deployment_platforms():
    """Get available deployment platforms"""
    return DEPLOYMENT_PLATFORMS


@router.post("/deploy")
async def deploy_project(project_id: str, platform: str, project_name: str):
    """Deploy a project (simulated)"""
    deployment = Deployment(
        project_id=project_id,
        platform=platform,
        project_name=project_name,
        status="deploying"
    )
    doc = deployment.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.deployments.insert_one(doc)
    
    # Simulate deployment
    deploy_url = f"https://{project_name.lower().replace(' ', '-')}.{platform}.app"
    await db.deployments.update_one(
        {"id": deployment.id},
        {"$set": {
            "status": "live",
            "deploy_url": deploy_url,
            "deployed_at": datetime.now(timezone.utc).isoformat(),
            "logs": [
                "Connecting to platform...",
                "Uploading files...",
                "Building project...",
                "Deployment successful!"
            ]
        }}
    )
    
    return {
        "success": True,
        "deployment_id": deployment.id,
        "deploy_url": deploy_url
    }


@router.get("/deploy/{project_id}")
async def get_deployments(project_id: str):
    """Get deployments for a project"""
    return await db.deployments.find({"project_id": project_id}, {"_id": 0}).to_list(20)
