"""
Audio Generation Routes
=======================
Routes for generating and managing audio assets.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List
from core.database import db
from core.utils import serialize_doc
import os
import uuid

router = APIRouter(prefix="/audio", tags=["audio"])


AUDIO_CATEGORIES = {
    "sfx": {
        "explosion": "Powerful explosion sound effect, rumbling bass with debris",
        "footstep_grass": "Footstep on grass, soft rustling sound",
        "footstep_stone": "Footstep on stone, hard clicking impact",
        "sword_swing": "Sword swing whoosh, metal cutting through air",
        "sword_hit": "Sword hitting metal armor, clang and ring",
        "pickup_item": "Item pickup sound, magical sparkle chime",
        "ui_click": "UI button click, soft satisfying pop",
        "ui_hover": "UI hover sound, subtle whoosh",
        "door_open": "Wooden door opening, creaking hinges",
        "chest_open": "Treasure chest opening, wood and metal",
        "level_up": "Level up fanfare, triumphant ascending notes",
        "damage_hit": "Taking damage, impact thud with grunt",
        "heal": "Healing sound, gentle magical restoration",
        "jump": "Character jump, effort grunt with air movement",
        "land": "Landing on ground, impact thud"
    },
    "music": {
        "menu_ambient": "Calm ambient menu music, gentle synth pads",
        "battle_epic": "Epic battle music, orchestral with drums",
        "exploration": "Exploration music, wonder and discovery theme",
        "boss_fight": "Intense boss fight music, dramatic and urgent",
        "victory": "Victory fanfare, triumphant celebration",
        "defeat": "Defeat music, somber and reflective",
        "shop": "Shop music, cheerful and welcoming",
        "dungeon": "Dungeon ambience, dark and mysterious",
        "village": "Village theme, peaceful and friendly",
        "night": "Nighttime ambient, calm with cricket sounds"
    },
    "voice": {
        "narrator_intro": "Epic narrator voice for game intro",
        "npc_greeting": "Friendly NPC greeting the player",
        "npc_merchant": "Merchant voice offering wares",
        "enemy_taunt": "Enemy taunting the player",
        "tutorial_guide": "Helpful tutorial guide voice",
        "quest_giver": "Quest giver explaining a mission"
    }
}


@router.get("/categories")
async def get_audio_categories():
    """Get available audio categories and presets"""
    return AUDIO_CATEGORIES


@router.post("/generate")
async def generate_audio(
    project_id: str,
    name: str,
    audio_type: str,
    prompt: str,
    provider: str = "openai"
):
    """Generate an audio asset using TTS"""
    from core.clients import tts_client
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    audio_asset = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "name": name,
        "audio_type": audio_type,
        "prompt": prompt,
        "provider": provider,
        "status": "generating",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        if provider == "openai" and tts_client:
            result = await tts_client.generate_speech(
                text=prompt,
                voice="alloy",
                model="tts-1"
            )
            audio_asset["url"] = result.get("url", "")
            audio_asset["duration_seconds"] = result.get("duration", 0)
            audio_asset["status"] = "ready"
        else:
            audio_asset["url"] = f"https://audio-placeholder.example.com/{audio_asset['id']}.mp3"
            audio_asset["duration_seconds"] = 5.0
            audio_asset["status"] = "mocked"
    except Exception as e:
        audio_asset["status"] = "failed"
        audio_asset["error"] = str(e)
    
    await db.audio_assets.insert_one(audio_asset)
    return serialize_doc(audio_asset)


@router.get("/{project_id}")
async def get_project_audio(project_id: str):
    """Get all audio assets for a project"""
    return await db.audio_assets.find({"project_id": project_id}, {"_id": 0}).to_list(200)


@router.get("/asset/{audio_id}")
async def get_audio_asset(audio_id: str):
    """Get a specific audio asset"""
    asset = await db.audio_assets.find_one({"id": audio_id}, {"_id": 0})
    if not asset:
        raise HTTPException(status_code=404, detail="Audio asset not found")
    return asset


@router.delete("/{audio_id}")
async def delete_audio_asset(audio_id: str):
    """Delete an audio asset"""
    await db.audio_assets.delete_one({"id": audio_id})
    return {"success": True}


@router.post("/generate-pack")
async def generate_audio_pack(
    project_id: str,
    pack_type: str = "sfx",
    items: List[str] = None
):
    """Generate a pack of audio assets"""
    if pack_type not in AUDIO_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid pack type: {pack_type}")
    
    presets = AUDIO_CATEGORIES[pack_type]
    items_to_generate = items or list(presets.keys())[:5]
    
    generated = []
    for item in items_to_generate:
        if item in presets:
            asset = {
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "name": item.replace("_", " ").title(),
                "audio_type": pack_type,
                "prompt": presets[item],
                "provider": "openai",
                "url": f"https://audio-placeholder.example.com/{item}.mp3",
                "duration_seconds": 3.0,
                "status": "mocked",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.audio_assets.insert_one(asset)
            generated.append(serialize_doc(asset))
    
    return {"generated": generated, "count": len(generated)}
