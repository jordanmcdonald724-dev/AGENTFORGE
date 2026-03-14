"""
Settings & Local Bridge Routes
==============================
User settings and local IDE integration endpoints.
Extracted from server.py as part of refactoring.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any
from datetime import datetime, timezone
from pathlib import Path
from core.database import db
import uuid
import tempfile
import zipfile

router = APIRouter()  # No prefix here, will be added when included


# ============ MODELS ============

class UserSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    default_engine: str = "unreal"
    theme: str = "dark"
    auto_save_files: bool = True
    streaming_mode: str = "sse"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============ SETTINGS ROUTES ============

@router.get("")
async def get_settings():
    """Get user settings"""
    settings = await db.settings.find_one({}, {"_id": 0})
    if not settings:
        return {
            "default_engine": "unreal",
            "theme": "dark",
            "auto_save_files": True,
            "streaming_mode": "sse"
        }
    return settings


@router.post("")
async def save_settings(settings: Dict[str, Any]):
    """Save user settings"""
    existing = await db.settings.find_one({})
    
    settings_doc = {
        **settings,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if existing:
        await db.settings.update_one({}, {"$set": settings_doc})
    else:
        settings_doc["id"] = str(uuid.uuid4())
        settings_doc["created_at"] = datetime.now(timezone.utc).isoformat()
        await db.settings.insert_one(settings_doc)
    
    return {"success": True}


# ============ LOCAL BRIDGE ROUTES ============

# Create a separate router for local-bridge with different prefix
local_bridge_router = APIRouter(prefix="/local-bridge", tags=["local-bridge"])


@local_bridge_router.get("/download")
async def download_local_bridge():
    """Download the local bridge installation package"""
    ROOT_DIR = Path(__file__).parent.parent.parent
    bridge_dir = ROOT_DIR / "local-bridge"
    
    if not bridge_dir.exists():
        raise HTTPException(status_code=404, detail="Bridge files not found")
    
    # Check if pre-built ZIP exists
    prebuilt_zip = bridge_dir / "AgentForge-LocalBridge.zip"
    if prebuilt_zip.exists():
        return FileResponse(
            prebuilt_zip,
            media_type="application/zip",
            filename="AgentForge-LocalBridge.zip"
        )
    
    # Create temp zip file if no pre-built exists
    temp_dir = tempfile.mkdtemp()
    zip_path = Path(temp_dir) / "AgentForge-LocalBridge.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in bridge_dir.iterdir():
            if file.is_file() and not file.name.endswith('.zip'):
                zipf.write(file, file.name)
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="AgentForge-LocalBridge.zip"
    )


@local_bridge_router.get("/extension")
async def download_extension():
    """Download the browser extension"""
    ROOT_DIR = Path(__file__).parent.parent.parent
    ext_dir = ROOT_DIR / "browser-extension"
    
    if not ext_dir.exists():
        raise HTTPException(status_code=404, detail="Extension files not found")
    
    # Check if pre-built ZIP exists
    prebuilt_zip = ext_dir / "AgentForge-Extension.zip"
    if prebuilt_zip.exists():
        return FileResponse(
            prebuilt_zip,
            media_type="application/zip",
            filename="AgentForge-Extension.zip"
        )
    
    # Create temp zip file
    temp_dir = tempfile.mkdtemp()
    zip_path = Path(temp_dir) / "AgentForge-Extension.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in ext_dir.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(ext_dir)
                zipf.write(file, arcname)
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="AgentForge-Extension.zip"
    )
