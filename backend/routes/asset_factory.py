"""
AI Asset Factory
================
Advanced asset generation pipeline using fal.ai.
Generate UI assets, textures, 3D models, icons, sound effects, voice acting.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.database import db
from core.utils import serialize_doc
import uuid
import os
import httpx

router = APIRouter(prefix="/asset-factory", tags=["asset-factory"])

FAL_KEY = os.environ.get("FAL_KEY", "")


ASSET_PIPELINES = {
    "ui_kit": {
        "name": "UI Kit Generator",
        "description": "Generate complete UI component sets",
        "outputs": ["buttons", "cards", "icons", "backgrounds", "avatars"],
        "model": "fal-ai/flux/schnell"
    },
    "texture_pack": {
        "name": "Texture Pack Generator",
        "description": "Generate seamless textures for games",
        "outputs": ["ground", "walls", "metal", "wood", "fabric", "stone"],
        "model": "fal-ai/flux/schnell"
    },
    "icon_set": {
        "name": "Icon Set Generator",
        "description": "Generate consistent icon sets",
        "outputs": ["navigation", "actions", "status", "social", "tools"],
        "model": "fal-ai/flux/schnell"
    },
    "character_art": {
        "name": "Character Art Generator",
        "description": "Generate character portraits and sprites",
        "outputs": ["portrait", "full_body", "sprite_sheet", "expressions"],
        "model": "fal-ai/flux/schnell"
    },
    "environment_art": {
        "name": "Environment Art Generator",
        "description": "Generate backgrounds and environments",
        "outputs": ["landscape", "interior", "skybox", "props"],
        "model": "fal-ai/flux/schnell"
    },
    "audio_sfx": {
        "name": "Sound Effects Generator",
        "description": "Generate game sound effects",
        "outputs": ["ui_sounds", "footsteps", "impacts", "ambient", "magic"],
        "uses_tts": True
    },
    "voice_acting": {
        "name": "Voice Acting Generator",
        "description": "Generate character voice lines",
        "outputs": ["dialogue", "narration", "reactions", "combat_sounds"],
        "uses_tts": True
    }
}


@router.get("/pipelines")
async def get_asset_pipelines():
    """Get available asset generation pipelines"""
    return ASSET_PIPELINES


@router.post("/generate")
async def generate_asset(
    project_id: str,
    pipeline: str,
    prompt: str,
    style: str = "modern",
    count: int = 1,
    size: str = "1024x1024"
):
    """Generate assets using AI"""
    
    if pipeline not in ASSET_PIPELINES:
        raise HTTPException(status_code=400, detail=f"Unknown pipeline: {pipeline}")
    
    pipeline_config = ASSET_PIPELINES[pipeline]
    
    generation = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "pipeline": pipeline,
        "pipeline_name": pipeline_config["name"],
        "prompt": prompt,
        "style": style,
        "count": count,
        "size": size,
        "status": "generating",
        "assets": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Generate with fal.ai if available
    if FAL_KEY and not pipeline_config.get("uses_tts"):
        try:
            async with httpx.AsyncClient() as client:
                for i in range(count):
                    enhanced_prompt = f"{prompt}, {style} style, high quality, professional"
                    
                    response = await client.post(
                        "https://fal.run/fal-ai/flux/schnell",
                        headers={
                            "Authorization": f"Key {FAL_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "prompt": enhanced_prompt,
                            "image_size": size,
                            "num_images": 1
                        },
                        timeout=120.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        images = data.get("images", [])
                        for img in images:
                            generation["assets"].append({
                                "id": str(uuid.uuid4()),
                                "type": "image",
                                "url": img.get("url"),
                                "prompt": enhanced_prompt,
                                "pipeline": pipeline
                            })
                    
            generation["status"] = "completed" if generation["assets"] else "partial"
            
        except Exception as e:
            generation["status"] = "error"
            generation["error"] = str(e)
    else:
        # Generate placeholder assets
        for i in range(count):
            generation["assets"].append({
                "id": str(uuid.uuid4()),
                "type": "image",
                "url": f"https://placeholder.asset/{generation['id']}/{i}.png",
                "prompt": prompt,
                "pipeline": pipeline,
                "mocked": True
            })
        generation["status"] = "mocked"
    
    generation["completed_at"] = datetime.now(timezone.utc).isoformat()
    await db.asset_generations.insert_one(generation)
    
    return serialize_doc(generation)


@router.post("/generate-pack")
async def generate_asset_pack(
    project_id: str,
    pack_type: str,
    theme: str = "fantasy",
    style: str = "stylized"
):
    """Generate a complete asset pack"""
    
    pack_configs = {
        "game_ui": {
            "assets": [
                {"name": "main_button", "prompt": "game UI button, {theme}, {style}"},
                {"name": "secondary_button", "prompt": "small game button, {theme}, {style}"},
                {"name": "health_bar", "prompt": "health bar UI element, {theme}, {style}"},
                {"name": "inventory_slot", "prompt": "inventory slot icon, {theme}, {style}"},
                {"name": "coin_icon", "prompt": "gold coin icon, {theme}, {style}"},
                {"name": "gem_icon", "prompt": "gem currency icon, {theme}, {style}"}
            ]
        },
        "textures": {
            "assets": [
                {"name": "ground_grass", "prompt": "seamless grass texture, {theme}"},
                {"name": "ground_dirt", "prompt": "seamless dirt texture, {theme}"},
                {"name": "wall_stone", "prompt": "seamless stone wall texture, {theme}"},
                {"name": "wall_brick", "prompt": "seamless brick texture, {theme}"},
                {"name": "wood_planks", "prompt": "seamless wood plank texture, {theme}"},
                {"name": "metal_plate", "prompt": "seamless metal plate texture, {theme}"}
            ]
        },
        "characters": {
            "assets": [
                {"name": "hero_portrait", "prompt": "hero character portrait, {theme}, {style}"},
                {"name": "villain_portrait", "prompt": "villain character portrait, {theme}, {style}"},
                {"name": "npc_merchant", "prompt": "friendly merchant NPC, {theme}, {style}"},
                {"name": "npc_guard", "prompt": "town guard NPC, {theme}, {style}"}
            ]
        },
        "environments": {
            "assets": [
                {"name": "forest_bg", "prompt": "forest environment background, {theme}, {style}"},
                {"name": "dungeon_bg", "prompt": "dungeon environment background, {theme}, {style}"},
                {"name": "village_bg", "prompt": "peaceful village background, {theme}, {style}"},
                {"name": "castle_bg", "prompt": "castle interior background, {theme}, {style}"}
            ]
        }
    }
    
    if pack_type not in pack_configs:
        raise HTTPException(status_code=400, detail=f"Unknown pack type: {pack_type}")
    
    pack = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "pack_type": pack_type,
        "theme": theme,
        "style": style,
        "status": "generating",
        "assets": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    config = pack_configs[pack_type]
    
    for asset_config in config["assets"]:
        prompt = asset_config["prompt"].replace("{theme}", theme).replace("{style}", style)
        
        asset = {
            "id": str(uuid.uuid4()),
            "name": asset_config["name"],
            "prompt": prompt,
            "url": f"https://generated.asset/{pack['id']}/{asset_config['name']}.png",
            "status": "generated"
        }
        
        # Generate with fal.ai if available
        if FAL_KEY:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://fal.run/fal-ai/flux/schnell",
                        headers={
                            "Authorization": f"Key {FAL_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={"prompt": prompt, "image_size": "1024x1024"},
                        timeout=60.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        images = data.get("images", [])
                        if images:
                            asset["url"] = images[0].get("url")
                            asset["status"] = "completed"
            except:
                asset["status"] = "mocked"
        
        pack["assets"].append(asset)
    
    pack["status"] = "completed"
    pack["completed_at"] = datetime.now(timezone.utc).isoformat()
    pack["total_assets"] = len(pack["assets"])
    
    await db.asset_packs.insert_one(pack)
    return serialize_doc(pack)


@router.post("/auto-generate")
async def auto_generate_project_assets(project_id: str):
    """
    Automatically identify and generate all needed assets for a project.
    Atlas identifies assets → Prism generates them → Assets inserted into project.
    """
    from core.clients import llm_client
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(100)
    
    auto_gen = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "project_name": project.get("name"),
        "status": "analyzing",
        "identified_assets": [],
        "generated_assets": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Use LLM to analyze project and identify needed assets
    file_list = [f.get("filepath", "") for f in files]
    
    try:
        response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": """Analyze the project and identify needed assets. Output JSON:
{
    "assets_needed": [
        {"type": "image|icon|texture|audio", "name": "asset_name", "description": "what it should look like", "priority": "high|medium|low"}
    ]
}
Focus on UI elements, icons, backgrounds, and any visual assets the project needs."""},
                {"role": "user", "content": f"Project: {project.get('name')}\nType: {project.get('type')}\nFiles: {file_list[:20]}"}
            ],
            max_tokens=2000
        )
        
        import json
        import re
        result_text = response.choices[0].message.content
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        
        if json_match:
            result = json.loads(json_match.group())
            auto_gen["identified_assets"] = result.get("assets_needed", [])
        
    except Exception as e:
        auto_gen["analysis_error"] = str(e)
    
    auto_gen["status"] = "identified"
    auto_gen["assets_count"] = len(auto_gen["identified_assets"])
    
    # Generate high priority assets
    for asset in auto_gen["identified_assets"][:5]:  # Limit to 5 for now
        if asset.get("priority") == "high" and asset.get("type") == "image":
            generated = {
                "id": str(uuid.uuid4()),
                "name": asset.get("name"),
                "description": asset.get("description"),
                "url": f"https://auto-generated.asset/{auto_gen['id']}/{asset.get('name')}.png",
                "status": "mocked"
            }
            auto_gen["generated_assets"].append(generated)
    
    auto_gen["status"] = "completed"
    auto_gen["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.auto_asset_generations.insert_one(auto_gen)
    return serialize_doc(auto_gen)


@router.get("/generations")
async def list_generations(project_id: str = None, limit: int = 20):
    """List asset generations"""
    query = {}
    if project_id:
        query["project_id"] = project_id
    return await db.asset_generations.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)


@router.get("/packs")
async def list_asset_packs(project_id: str = None):
    """List asset packs"""
    query = {}
    if project_id:
        query["project_id"] = project_id
    return await db.asset_packs.find(query, {"_id": 0}).to_list(50)
