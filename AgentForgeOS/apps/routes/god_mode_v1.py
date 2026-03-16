"""
God Mode V1 - Original Autonomous Build System
===============================================
Single-shot 5-phase build with streaming and resume capability.

This is the original God Mode implementation. God Mode V2 in god_mode_v2.py
provides a more advanced multi-agent, recursive approach.

Phases (for games): Player Controller, Combat, Inventory, AI, Save System
Phases (for web): Core App, Hero, Features, Pricing

Features:
- Streaming SSE responses with heartbeats
- Resume from any phase (start_phase parameter)
- Real-time file extraction and saving
- Progress tracking via god_mode_phase in projects
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime, timezone
from engine.core.database import db
import uuid
import json
import zipfile
import io
import logging

router = APIRouter(prefix="/god-mode", tags=["god-mode"])
logger = logging.getLogger(__name__)


def get_llm_client():
    """Get LLM client from server.py"""
    from server import llm_client
    return llm_client


def extract_code_blocks(content: str):
    """Extract code blocks - import from server.py"""
    from server import extract_code_blocks
    return extract_code_blocks(content)


async def get_or_create_agents():
    """Get agents from server.py"""
    from server import get_or_create_agents
    return await get_or_create_agents()


# ============ MODELS ============

class GodModeRequest(BaseModel):
    project_id: str
    start_phase: int = 0  # For resume functionality - skip to this phase


class GodModeResumeRequest(BaseModel):
    project_id: str
    start_phase: int = 0


# ============ ROUTES ============

@router.post("/activate")
async def activate_god_mode(request: GodModeRequest):
    """Activate God Mode - AI builds the entire project autonomously"""
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await db.projects.update_one(
        {"id": request.project_id},
        {"$set": {"god_mode": True, "phase": "building", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"status": "activated", "message": "God Mode activated. AI will build your project."}


@router.post("/build/stream")
async def god_mode_build_stream(request: GodModeRequest):
    """Stream God Mode build - AI builds everything autonomously in phases"""
    llm_client = get_llm_client()
    
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    agents = await get_or_create_agents()
    forge_agent = next((a for a in agents if a['name'] == 'FORGE'), agents[0])
    
    project_name = project.get('name', 'Project')
    project_type = project.get('type', 'web_app')
    engine = project.get('engine_version', 'Unreal Engine 5')
    
    # Get start phase from request (for resume functionality)
    start_phase = request.start_phase
    
    # Define build phases based on project type
    if project_type in ['game', 'unreal', 'unity']:
        phases = get_game_phases(project_name, engine)
    else:
        phases = get_web_phases(project_name)
    
    async def generate():
        yield f"data: {json.dumps({'type': 'god_mode_start', 'project': project_name, 'total_phases': len(phases)})}\n\n"
        
        all_saved_files = []
        heartbeat_counter = 0
        
        for phase_idx, phase in enumerate(phases):
            # Skip phases if resuming
            if phase_idx < start_phase:
                yield f"data: {json.dumps({'type': 'phase_skipped', 'phase': phase['name'], 'phase_num': phase_idx + 1})}\n\n"
                continue
            
            yield f"data: {json.dumps({'type': 'phase_start', 'phase': phase['name'], 'phase_num': phase_idx + 1, 'total': len(phases)})}\n\n"
            
            full_content = ""
            chunk_buffer = ""
            
            try:
                stream = llm_client.chat.completions.create(
                    model="google/gemini-2.5-flash",
                    messages=[
                        {"role": "system", "content": forge_agent['system_prompt'] + "\n\n🔥 GOD MODE - Build AAA quality only. No placeholders."},
                        {"role": "user", "content": phase['prompt']}
                    ],
                    max_tokens=12000,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_content += content
                        chunk_buffer += content
                        
                        # Send content in batches to reduce message overhead
                        if len(chunk_buffer) > 100:
                            yield f"data: {json.dumps({'type': 'content', 'content': chunk_buffer})}\n\n"
                            chunk_buffer = ""
                        
                        # Send heartbeat every ~50 chunks to keep connection alive
                        heartbeat_counter += 1
                        if heartbeat_counter % 50 == 0:
                            yield f"data: {json.dumps({'type': 'heartbeat', 'phase': phase['name']})}\n\n"
                        
                        # Real-time file extraction
                        if "```" in full_content:
                            code_blocks = extract_code_blocks(full_content)
                            for block in code_blocks:
                                filepath = block.get('filepath')
                                if filepath and filepath not in all_saved_files:
                                    try:
                                        existing = await db.files.find_one({
                                            "project_id": request.project_id,
                                            "filepath": filepath
                                        })
                                        
                                        file_doc = {
                                            "id": str(uuid.uuid4()),
                                            "project_id": request.project_id,
                                            "filepath": filepath,
                                            "filename": block.get('filename', filepath.split('/')[-1]),
                                            "language": block.get('language', 'cpp'),
                                            "content": block['content'],
                                            "version": (existing.get('version', 0) + 1) if existing else 1,
                                            "created_at": datetime.now(timezone.utc).isoformat(),
                                            "updated_at": datetime.now(timezone.utc).isoformat()
                                        }
                                        
                                        if existing:
                                            await db.files.update_one(
                                                {"project_id": request.project_id, "filepath": filepath},
                                                {"$set": file_doc}
                                            )
                                        else:
                                            await db.files.insert_one(file_doc)
                                        
                                        all_saved_files.append(filepath)
                                        yield f"data: {json.dumps({'type': 'file_saved', 'filepath': filepath})}\n\n"
                                    except Exception as e:
                                        logger.error(f"Error saving file {filepath}: {e}")
                
                # Send remaining buffer
                if chunk_buffer:
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk_buffer})}\n\n"
                
                # Final file extraction for this phase
                code_blocks = extract_code_blocks(full_content)
                phase_files = []
                
                for block in code_blocks:
                    filepath = block.get('filepath')
                    if filepath and filepath not in all_saved_files:
                        try:
                            existing = await db.files.find_one({
                                "project_id": request.project_id,
                                "filepath": filepath
                            })
                            
                            file_doc = {
                                "id": str(uuid.uuid4()),
                                "project_id": request.project_id,
                                "filepath": filepath,
                                "filename": block.get('filename', filepath.split('/')[-1]),
                                "language": block.get('language', 'cpp'),
                                "content": block['content'],
                                "version": (existing.get('version', 0) + 1) if existing else 1,
                                "created_at": datetime.now(timezone.utc).isoformat(),
                                "updated_at": datetime.now(timezone.utc).isoformat()
                            }
                            
                            if existing:
                                await db.files.update_one(
                                    {"project_id": request.project_id, "filepath": filepath},
                                    {"$set": file_doc}
                                )
                            else:
                                await db.files.insert_one(file_doc)
                            
                            all_saved_files.append(filepath)
                            phase_files.append(filepath)
                            yield f"data: {json.dumps({'type': 'file_saved', 'filepath': filepath})}\n\n"
                        except Exception as e:
                            logger.error(f"Error saving file {filepath}: {e}")
                
                # Save phase progress for resume capability
                await db.projects.update_one(
                    {"id": request.project_id},
                    {"$set": {
                        "god_mode_phase": phase_idx + 1,
                        "god_mode_files": all_saved_files,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                yield f"data: {json.dumps({'type': 'phase_complete', 'phase': phase['name'], 'files': len(phase_files), 'total_files': len(all_saved_files)})}\n\n"
                
            except Exception as e:
                logger.error(f"Phase {phase['name']} error: {e}")
                yield f"data: {json.dumps({'type': 'phase_error', 'phase': phase['name'], 'error': str(e), 'phase_num': phase_idx})}\n\n"
        
        # Final cleanup
        await db.projects.update_one(
            {"id": request.project_id},
            {"$set": {"phase": "review", "god_mode_complete": True, "god_mode_phase": len(phases), "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        yield f"data: {json.dumps({'type': 'god_mode_complete', 'files_created': len(all_saved_files), 'saved_files': all_saved_files})}\n\n"
    
    return StreamingResponse(
        generate(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/status/{project_id}")
async def get_god_mode_status(project_id: str):
    """Get God Mode build status for resume functionality"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(200)
    
    return {
        "project_id": project_id,
        "god_mode_complete": project.get("god_mode_complete", False),
        "god_mode_phase": project.get("god_mode_phase", 0),
        "files_saved": len(files),
        "file_paths": [f["filepath"] for f in files]
    }


@router.post("/resume")
async def resume_god_mode_build(request: GodModeResumeRequest):
    """Resume a God Mode build from a specific phase"""
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    god_request = GodModeRequest(project_id=request.project_id, start_phase=request.start_phase)
    return await god_mode_build_stream(god_request)


@router.get("/download/{project_id}")
async def download_project_files(project_id: str):
    """Download all generated files as a ZIP"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    if not files:
        raise HTTPException(status_code=404, detail="No files found for this project")
    
    project_name = project.get('name', 'Project').replace(' ', '_')
    
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            filepath = file.get('filepath', file.get('filename', 'unknown.txt'))
            content = file.get('content', '')
            zf.writestr(filepath, content)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{project_name}_Files.zip"'
        }
    )


# ============ PHASE DEFINITIONS ============

def get_game_phases(project_name: str, engine: str):
    """Get build phases for game projects"""
    clean_name = project_name.replace(' ', '')
    return [
        {
            "name": "Player Controller",
            "prompt": f"""Build a COMPLETE AAA Player Controller for {project_name} ({engine}).

Create these files with FULL implementations:
1. Character base class with movement
2. State machine component
3. States: Idle, Walk, Run, Sprint, Jump, Dodge
4. Camera component with collision
5. Input component for gamepad + keyboard

Format: ```cpp:Source/{clean_name}/FileName.h```

NO stubs. NO TODOs. COMPLETE production code."""
        },
        {
            "name": "Combat System", 
            "prompt": f"""Build a COMPLETE AAA Combat System for {project_name} ({engine}).

Create these files with FULL implementations:
1. Combat component
2. Melee attack system with combos
3. Damage types and calculations
4. Hit reactions
5. Lock-on targeting

Format: ```cpp:Source/{clean_name}/Combat/FileName.h```

NO stubs. COMPLETE production code."""
        },
        {
            "name": "Inventory System",
            "prompt": f"""Build a COMPLETE AAA Inventory System for {project_name} ({engine}).

Create these files with FULL implementations:
1. Inventory component
2. Item base class
3. Weapon, Armor, Consumable subclasses
4. Equipment slots
5. Stack management

Format: ```cpp:Source/{clean_name}/Inventory/FileName.h```

NO stubs. COMPLETE production code."""
        },
        {
            "name": "AI System",
            "prompt": f"""Build a COMPLETE AAA AI System for {project_name} ({engine}).

Create these files with FULL implementations:
1. AI Controller base
2. Behavior tree tasks
3. Perception component
4. AI States: Patrol, Alert, Chase, Attack
5. Group tactics manager

Format: ```cpp:Source/{clean_name}/AI/FileName.h```

NO stubs. COMPLETE production code."""
        },
        {
            "name": "Save System",
            "prompt": f"""Build a COMPLETE Save/Load System for {project_name} ({engine}).

Create these files with FULL implementations:
1. Save game object
2. Save manager subsystem
3. Serialization helpers
4. Auto-save component
5. Save slot UI data

Format: ```cpp:Source/{clean_name}/Save/FileName.h```

NO stubs. COMPLETE production code."""
        }
    ]


def get_web_phases(project_name: str):
    """Get build phases for web projects"""
    return [
        {
            "name": "Core App",
            "prompt": f"""Build the CORE app structure for {project_name}.

Create with FULL implementations:
1. src/App.js - Routing, providers
2. src/index.css - Tailwind + animations
3. src/components/Layout/Header.jsx
4. src/components/Layout/Footer.jsx

React 18 + Tailwind. Dark theme. Format: ```javascript:path/file.jsx```"""
        },
        {
            "name": "Hero Section",
            "prompt": f"""Build a STUNNING Hero section for {project_name}.

Create with FULL implementations:
1. src/components/Hero/Hero.jsx - Animated background
2. src/components/Hero/HeroStats.jsx - Counters
3. src/components/Hero/HeroCTA.jsx

Framer Motion animations. Format: ```javascript:path/file.jsx```"""
        },
        {
            "name": "Features Section",
            "prompt": f"""Build a PREMIUM Features section for {project_name}.

Create with FULL implementations:
1. src/components/Features/Features.jsx - Bento grid
2. src/components/Features/FeatureCard.jsx - 3D hover
3. 6 feature icons and descriptions

Format: ```javascript:path/file.jsx```"""
        },
        {
            "name": "Pricing & CTA",
            "prompt": f"""Build Pricing and CTA sections for {project_name}.

Create with FULL implementations:
1. src/components/Pricing/Pricing.jsx - Toggle monthly/yearly
2. src/components/Pricing/PricingCard.jsx
3. src/components/CTA/CTA.jsx

Format: ```javascript:path/file.jsx```"""
        }
    ]
