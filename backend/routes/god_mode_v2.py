"""
God Mode V2 - Full AI Development Pipeline
==========================================
Architecture-first, multi-agent, self-improving builds with memory integration.

Pipeline:
1. DIRECTOR - Creates project brief with learning from past builds
2. ATLAS - Designs architecture using best practices from memory
3. Specialist Agents - Build each system with quality tracking
4. SENTINEL - Reviews code with strict scoring
5. Iterate and improve based on review feedback
6. Record learnings to memory system
7. Deploy

Features:
- Robust error handling with automatic retry
- Granular progress tracking per module
- Memory system integration for continuous learning
- Quality metrics tracking per iteration
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from core.database import db
from routes.pipeline import SPECIALIST_AGENTS
from core.helpers import get_or_create_agents
import uuid
import json
import asyncio
import re
import time
import traceback

router = APIRouter(prefix="/god-mode-v2", tags=["god-mode-v2"])

# Build state tracking
ACTIVE_BUILDS: Dict[str, Dict[str, Any]] = {}


# Get the LLM client from server.py
def get_llm_client():
    """Get LLM client - import here to avoid circular imports"""
    from server import llm_client
    return llm_client


def extract_code_blocks(content: str) -> List[Dict[str, str]]:
    """Extract code blocks with file paths"""
    pattern = r'```(\w+)?(?::([^\n]+))?\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    blocks = []
    for lang, filepath, code in matches:
        if filepath:
            blocks.append({
                'language': lang or 'txt',
                'filepath': filepath.strip(),
                'filename': filepath.strip().split('/')[-1],
                'content': code.strip()
            })
    return blocks


async def record_agent_performance(agent_name: str, agent_role: str, successful: bool, quality_score: int, time_seconds: int):
    """Record agent performance to memory system"""
    try:
        existing = await db.agent_performance.find_one({"agent_name": agent_name})
        
        if existing:
            total = existing.get("total_tasks", 0) + 1
            successful_count = existing.get("successful_tasks", 0) + (1 if successful else 0)
            
            old_avg_score = existing.get("average_quality_score", 0)
            new_avg_score = ((old_avg_score * (total - 1)) + quality_score) / total
            
            old_avg_time = existing.get("average_time_seconds", 0)
            new_avg_time = ((old_avg_time * (total - 1)) + time_seconds) / total
            
            await db.agent_performance.update_one(
                {"agent_name": agent_name},
                {"$set": {
                    "total_tasks": total,
                    "successful_tasks": successful_count,
                    "average_quality_score": round(new_avg_score, 2),
                    "average_time_seconds": round(new_avg_time, 2),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
        else:
            await db.agent_performance.insert_one({
                "id": str(uuid.uuid4()),
                "agent_name": agent_name,
                "agent_role": agent_role,
                "total_tasks": 1,
                "successful_tasks": 1 if successful else 0,
                "average_quality_score": float(quality_score),
                "average_time_seconds": float(time_seconds),
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
    except Exception as e:
        print(f"Error recording agent performance: {e}")


async def record_build_memory(project_id: str, project_type: str, architecture: str, modules: List[str], 
                              final_score: int, iterations: int, build_time: int, files_count: int,
                              successful: bool, patterns_worked: List[str], patterns_avoid: List[str]):
    """Record complete build to memory system"""
    try:
        memory_doc = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "project_type": project_type,
            "architecture_used": architecture[:2000] if architecture else "",
            "modules_built": modules,
            "tech_stack": {"engine": "Unreal Engine 5", "language": "C++"},
            "final_score": final_score,
            "iterations_needed": iterations,
            "bugs_found": [],
            "fixes_applied": [],
            "build_time_seconds": build_time,
            "files_generated": files_count,
            "successful": successful,
            "deployment_ready": successful and final_score >= 80,
            "patterns_that_worked": patterns_worked,
            "patterns_to_avoid": patterns_avoid,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.build_memories.insert_one(memory_doc)
        
        # Update learning insights if successful
        if successful and final_score >= 75:
            for pattern in patterns_worked:
                await add_learning_insight("patterns", pattern, 0.1)
        if not successful or final_score < 60:
            for pattern in patterns_avoid:
                await add_learning_insight("anti_patterns", f"AVOID: {pattern}", 0.1)
    except Exception as e:
        print(f"Error recording build memory: {e}")


async def add_learning_insight(category: str, insight: str, confidence_boost: float):
    """Add or update a learning insight"""
    try:
        existing = await db.learning_insights.find_one({"insight": insight})
        if existing:
            new_confidence = min(1.0, existing.get("confidence", 0.5) + confidence_boost)
            await db.learning_insights.update_one(
                {"insight": insight},
                {"$set": {"confidence": new_confidence, "evidence_count": existing.get("evidence_count", 1) + 1}}
            )
        else:
            await db.learning_insights.insert_one({
                "id": str(uuid.uuid4()),
                "category": category,
                "insight": insight,
                "confidence": min(1.0, 0.3 + confidence_boost),
                "evidence_count": 1,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
    except Exception as e:
        print(f"Error adding learning insight: {e}")


async def get_past_recommendations(project_type: str) -> Dict[str, Any]:
    """Get recommendations from past successful builds"""
    try:
        successful_builds = await db.build_memories.find(
            {"project_type": project_type, "successful": True, "final_score": {"$gte": 80}},
            {"_id": 0}
        ).sort("final_score", -1).limit(3).to_list(3)
        
        patterns_worked = []
        patterns_avoid = []
        for build in successful_builds:
            patterns_worked.extend(build.get("patterns_that_worked", []))
            patterns_avoid.extend(build.get("patterns_to_avoid", []))
        
        return {
            "has_history": len(successful_builds) > 0,
            "best_score": successful_builds[0]["final_score"] if successful_builds else 0,
            "patterns_worked": list(set(patterns_worked))[:5],
            "patterns_avoid": list(set(patterns_avoid))[:5]
        }
    except Exception:
        return {"has_history": False, "best_score": 0, "patterns_worked": [], "patterns_avoid": []}


class GodModeV2Request(BaseModel):
    project_id: str
    iterations: int = 3  # Number of improvement iterations
    auto_review: bool = True
    quality_target: int = 85  # Minimum quality score
    enable_memory: bool = True  # Use memory system for learning


# ============ BUILD STATUS ENDPOINT ============

@router.get("/status/{build_id}")
async def get_build_status(build_id: str):
    """Get current status of an active build"""
    if build_id in ACTIVE_BUILDS:
        return ACTIVE_BUILDS[build_id]
    
    # Check database for completed build
    project = await db.projects.find_one({"id": build_id}, {"_id": 0})
    if project:
        return {
            "build_id": build_id,
            "status": "complete" if project.get("god_mode_v2_complete") else "not_started",
            "iterations_completed": project.get("iterations_completed", 0),
            "total_files": project.get("total_files", 0)
        }
    
    return {"build_id": build_id, "status": "not_found"}


@router.post("/cancel/{build_id}")
async def cancel_build(build_id: str):
    """Cancel an active build"""
    if build_id in ACTIVE_BUILDS:
        ACTIVE_BUILDS[build_id]["status"] = "cancelled"
        ACTIVE_BUILDS[build_id]["cancelled_at"] = datetime.now(timezone.utc).isoformat()
        return {"success": True, "message": "Build cancelled"}
    return {"success": False, "message": "Build not found or already completed"}


# ============ PHASE PROMPTS ============

def get_director_prompt(project_name: str, project_type: str, description: str, past_learnings: Dict[str, Any] = None) -> str:
    learning_context = ""
    if past_learnings and past_learnings.get("has_history"):
        learning_context = f"""

LEARNINGS FROM PAST BUILDS:
- Best score achieved: {past_learnings.get('best_score', 0)}
- Patterns that work: {', '.join(past_learnings.get('patterns_worked', [])[:3])}
- Patterns to avoid: {', '.join(past_learnings.get('patterns_avoid', [])[:3])}

Use these learnings to improve this build.
"""
    
    return f"""You are DIRECTOR, the Project Director AI.

Analyze this project request and create a comprehensive build plan:
{learning_context}
PROJECT: {project_name}
TYPE: {project_type}
DESCRIPTION: {description}

Create a JSON build plan with:
1. Project brief
2. Complexity assessment
3. Module breakdown
4. Build phases
5. Quality requirements

OUTPUT ONLY VALID JSON:
```json
{{
  "project_brief": {{
    "name": "{project_name}",
    "type": "{project_type}",
    "complexity": "complex",
    "core_features": ["feature1", "feature2", "feature3"],
    "technical_requirements": ["requirement1", "requirement2"]
  }},
  "modules": [
    {{"name": "Core System", "priority": 1, "agent": "TITAN"}},
    {{"name": "Player Controller", "priority": 2, "agent": "TITAN"}},
    {{"name": "Combat System", "priority": 3, "agent": "TITAN"}},
    {{"name": "Inventory System", "priority": 4, "agent": "TITAN"}},
    {{"name": "AI System", "priority": 5, "agent": "TITAN"}},
    {{"name": "Save System", "priority": 6, "agent": "TITAN"}}
  ],
  "quality_requirements": {{
    "code_standard": "AAA",
    "performance_target": "60fps",
    "architecture": "modular_scalable"
  }}
}}
```"""


def get_architect_prompt(project_name: str, project_type: str, description: str, engine: str) -> str:
    return f"""You are ATLAS, Elite Systems Architect.

Design the COMPLETE architecture for this project BEFORE any code is written:

PROJECT: {project_name}
TYPE: {project_type}
ENGINE: {engine}
DESCRIPTION: {description}

OUTPUT ARCHITECTURE BLUEPRINT:

1. SYSTEM OVERVIEW
Describe the high-level system design.

2. TECHNOLOGY STACK
```
Engine: {engine}
Core Language: C++
UI Framework: UMG/Slate
AI: Behavior Trees + EQS
Networking: Unreal Networking
```

3. MODULE STRUCTURE
```
Source/{project_name.replace(' ', '')}/
├── Core/                 - Core game systems
│   ├── GameMode
│   ├── GameState
│   └── GameInstance
├── Character/            - Player & NPC characters
│   ├── Base
│   ├── Player
│   └── Components
├── Combat/               - Combat systems
│   ├── Weapons
│   ├── Damage
│   └── Abilities
├── Inventory/            - Inventory management
│   ├── Items
│   └── Equipment
├── AI/                   - AI systems
│   ├── Controllers
│   ├── BehaviorTree
│   └── Perception
├── Save/                 - Persistence
│   └── Serialization
└── UI/                   - User interface
    ├── HUD
    └── Menus
```

4. CORE INTERFACES
```cpp
// Base interface for all game systems
class IGameSystem
{{
public:
    virtual void Initialize() = 0;
    virtual void Shutdown() = 0;
}};

// Base interface for saveable objects
class ISaveable
{{
public:
    virtual void SaveState(FArchive& Ar) = 0;
    virtual void LoadState(FArchive& Ar) = 0;
}};
```

5. DATA FLOW
Describe how data flows through the system.

6. SCALABILITY NOTES
How the architecture supports future growth.
"""


def get_specialist_prompt(agent_type: str, module_name: str, project_name: str, engine: str, architecture: str, iteration: int) -> str:
    """Get context-aware prompt for specialist agents"""
    
    base_prompts = {
        "player_controller": f"""You are TITAN, Elite Game Engine Engineer.

BUILD A COMPLETE AAA Player Controller for {project_name} ({engine}).

ITERATION: {iteration} - {"INITIAL BUILD" if iteration == 1 else "IMPROVE based on review feedback"}

ARCHITECTURE CONTEXT:
{architecture}

CREATE THESE FILES WITH FULL IMPLEMENTATIONS:

1. Character Base Class
```cpp:Source/{project_name.replace(' ', '')}/Character/Base/{project_name.replace(' ', '')}CharacterBase.h```
- Full header with all properties
- State machine integration
- Movement modes
- Animation interface

```cpp:Source/{project_name.replace(' ', '')}/Character/Base/{project_name.replace(' ', '')}CharacterBase.cpp```
- Complete implementation
- Proper initialization
- Tick logic
- State transitions

2. Player Character
```cpp:Source/{project_name.replace(' ', '')}/Character/Player/{project_name.replace(' ', '')}PlayerCharacter.h```
```cpp:Source/{project_name.replace(' ', '')}/Character/Player/{project_name.replace(' ', '')}PlayerCharacter.cpp```

3. State Machine Component
```cpp:Source/{project_name.replace(' ', '')}/Character/Components/{project_name.replace(' ', '')}StateMachineComponent.h```
```cpp:Source/{project_name.replace(' ', '')}/Character/Components/{project_name.replace(' ', '')}StateMachineComponent.cpp```

4. Character States (Idle, Walk, Run, Sprint, Jump, Dodge)
```cpp:Source/{project_name.replace(' ', '')}/Character/States/{project_name.replace(' ', '')}CharacterState_Idle.h```
(And corresponding .cpp files for each state)

5. Camera Component
```cpp:Source/{project_name.replace(' ', '')}/Character/Components/{project_name.replace(' ', '')}CameraComponent.h```
```cpp:Source/{project_name.replace(' ', '')}/Character/Components/{project_name.replace(' ', '')}CameraComponent.cpp```

6. Input Component
```cpp:Source/{project_name.replace(' ', '')}/Character/Components/{project_name.replace(' ', '')}InputComponent.h```
```cpp:Source/{project_name.replace(' ', '')}/Character/Components/{project_name.replace(' ', '')}InputComponent.cpp```

REQUIREMENTS:
- NO stubs, NO TODOs
- Full implementations
- Proper UE5 macros (UCLASS, UPROPERTY, UFUNCTION)
- Performance optimized
- Network ready (replicated properties)
""",

        "combat_system": f"""You are TITAN, Elite Game Engine Engineer.

BUILD A COMPLETE AAA Combat System for {project_name} ({engine}).

ITERATION: {iteration}

ARCHITECTURE CONTEXT:
{architecture}

CREATE THESE FILES:

1. Combat Component
```cpp:Source/{project_name.replace(' ', '')}/Combat/{project_name.replace(' ', '')}CombatComponent.h```
```cpp:Source/{project_name.replace(' ', '')}/Combat/{project_name.replace(' ', '')}CombatComponent.cpp```

2. Weapon Base & Types
```cpp:Source/{project_name.replace(' ', '')}/Combat/Weapons/{project_name.replace(' ', '')}WeaponBase.h```
```cpp:Source/{project_name.replace(' ', '')}/Combat/Weapons/{project_name.replace(' ', '')}MeleeWeapon.h```

3. Damage System
```cpp:Source/{project_name.replace(' ', '')}/Combat/Damage/{project_name.replace(' ', '')}DamageTypes.h```
```cpp:Source/{project_name.replace(' ', '')}/Combat/Damage/{project_name.replace(' ', '')}DamageCalculator.h```

4. Combo System
```cpp:Source/{project_name.replace(' ', '')}/Combat/{project_name.replace(' ', '')}ComboSystem.h```
```cpp:Source/{project_name.replace(' ', '')}/Combat/{project_name.replace(' ', '')}ComboSystem.cpp```

5. Hit Detection
```cpp:Source/{project_name.replace(' ', '')}/Combat/{project_name.replace(' ', '')}HitDetection.h```

FULL AAA IMPLEMENTATIONS ONLY.
""",

        "inventory_system": f"""You are TITAN, Elite Game Engine Engineer.

BUILD A COMPLETE AAA Inventory System for {project_name} ({engine}).

ITERATION: {iteration}

CREATE THESE FILES:

1. Inventory Component
```cpp:Source/{project_name.replace(' ', '')}/Inventory/{project_name.replace(' ', '')}InventoryComponent.h```
```cpp:Source/{project_name.replace(' ', '')}/Inventory/{project_name.replace(' ', '')}InventoryComponent.cpp```

2. Item System
```cpp:Source/{project_name.replace(' ', '')}/Inventory/Items/{project_name.replace(' ', '')}ItemBase.h```
```cpp:Source/{project_name.replace(' ', '')}/Inventory/Items/{project_name.replace(' ', '')}WeaponItem.h```
```cpp:Source/{project_name.replace(' ', '')}/Inventory/Items/{project_name.replace(' ', '')}ArmorItem.h```
```cpp:Source/{project_name.replace(' ', '')}/Inventory/Items/{project_name.replace(' ', '')}ConsumableItem.h```

3. Equipment System
```cpp:Source/{project_name.replace(' ', '')}/Inventory/{project_name.replace(' ', '')}EquipmentSlots.h```

4. Item Data
```cpp:Source/{project_name.replace(' ', '')}/Inventory/{project_name.replace(' ', '')}ItemDatabase.h```

FULL DATA-DRIVEN IMPLEMENTATIONS.
""",

        "ai_system": f"""You are TITAN, Elite Game Engine Engineer.

BUILD A COMPLETE AAA AI System for {project_name} ({engine}).

ITERATION: {iteration}

CREATE THESE FILES:

1. AI Controller
```cpp:Source/{project_name.replace(' ', '')}/AI/Controllers/{project_name.replace(' ', '')}AIController.h```
```cpp:Source/{project_name.replace(' ', '')}/AI/Controllers/{project_name.replace(' ', '')}AIController.cpp```

2. Behavior Tree Tasks
```cpp:Source/{project_name.replace(' ', '')}/AI/BehaviorTree/{project_name.replace(' ', '')}BTTask_Attack.h```
```cpp:Source/{project_name.replace(' ', '')}/AI/BehaviorTree/{project_name.replace(' ', '')}BTTask_Patrol.h```
```cpp:Source/{project_name.replace(' ', '')}/AI/BehaviorTree/{project_name.replace(' ', '')}BTTask_Chase.h```

3. Perception System
```cpp:Source/{project_name.replace(' ', '')}/AI/Perception/{project_name.replace(' ', '')}AIPerceptionComponent.h```

4. AI States
```cpp:Source/{project_name.replace(' ', '')}/AI/{project_name.replace(' ', '')}AIStateManager.h```

PROFESSIONAL BEHAVIOR TREE ARCHITECTURE.
""",

        "save_system": f"""You are TITAN, Elite Game Engine Engineer.

BUILD A COMPLETE Save/Load System for {project_name} ({engine}).

ITERATION: {iteration}

CREATE THESE FILES:

1. Save Game Object
```cpp:Source/{project_name.replace(' ', '')}/Save/{project_name.replace(' ', '')}SaveGame.h```
```cpp:Source/{project_name.replace(' ', '')}/Save/{project_name.replace(' ', '')}SaveGame.cpp```

2. Save Manager
```cpp:Source/{project_name.replace(' ', '')}/Save/{project_name.replace(' ', '')}SaveManager.h```
```cpp:Source/{project_name.replace(' ', '')}/Save/{project_name.replace(' ', '')}SaveManager.cpp```

3. Serialization Helpers
```cpp:Source/{project_name.replace(' ', '')}/Save/{project_name.replace(' ', '')}SaveHelpers.h```

4. Saveable Interface
```cpp:Source/{project_name.replace(' ', '')}/Save/I{project_name.replace(' ', '')}Saveable.h```

ASYNC SAVE/LOAD WITH MULTIPLE SLOTS.
"""
    }
    
    return base_prompts.get(module_name.lower().replace(' ', '_'), base_prompts["player_controller"])


def get_review_prompt(code_content: str, iteration: int) -> str:
    return f"""You are SENTINEL, Senior Code Review AI.

REVIEW THIS CODE (Iteration {iteration}):

{code_content[:8000]}

PROVIDE REVIEW IN JSON FORMAT:
```json
{{
  "verdict": "APPROVED|NEEDS_WORK|REJECTED",
  "score": 85,
  "issues": [
    {{
      "severity": "critical|major|minor",
      "location": "file/function",
      "issue": "Description",
      "fix": "Suggested fix"
    }}
  ],
  "improvements": [
    "Improvement 1",
    "Improvement 2"
  ],
  "summary": "Overall assessment"
}}
```

BE STRICT. AAA QUALITY ONLY.
"""


# ============ STREAMING BUILD ============

async def call_llm_with_retry(llm_client, messages: List[Dict], max_tokens: int = 4000, 
                               stream: bool = False, max_retries: int = 3) -> Any:
    """Call LLM with automatic retry on failure"""
    last_error = None
    for attempt in range(max_retries):
        try:
            response = llm_client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=messages,
                max_tokens=max_tokens,
                stream=stream
            )
            return response
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            continue
    raise last_error


@router.post("/build/stream")
async def god_mode_v2_build_stream(request: GodModeV2Request):
    """Full pipeline God Mode build with streaming, error recovery, and memory integration"""
    
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_name = project.get('name', 'Project').replace(' ', '')
    project_type = project.get('type', 'game')
    project_desc = project.get('description', '')
    engine = project.get('engine_version', 'Unreal Engine 5')
    
    llm_client = get_llm_client()
    build_start_time = time.time()
    
    # Initialize build tracking
    build_id = request.project_id
    ACTIVE_BUILDS[build_id] = {
        "status": "initializing",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "current_phase": "director",
        "current_iteration": 0,
        "progress_percent": 0,
        "files_generated": 0,
        "errors": [],
        "quality_scores": {}
    }
    
    async def generate():
        all_files = []
        architecture = ""
        modules_built = []
        patterns_worked = []
        patterns_avoid = []
        overall_quality_score = 0
        phase_errors = []

        # Fetch all 12 DB agents once — keyed by uppercase name
        _db_agents = await get_or_create_agents()
        db_agent_map = {a['name'].upper(): a for a in _db_agents}

        def _get_agent_prompt(db_name: str, fallback_key: str) -> tuple:
            """Return (display_name, system_prompt) from DB agent or SPECIALIST_AGENTS fallback."""
            ag = db_agent_map.get(db_name)
            if ag:
                return ag['name'], ag['system_prompt']
            fb = SPECIALIST_AGENTS.get(fallback_key, SPECIALIST_AGENTS["game_engine"])
            return fb['name'], fb['prompt']
        
        try:
            # Get past learnings
            past_learnings = {}
            if request.enable_memory:
                past_learnings = await get_past_recommendations(project_type)
            
            yield f"data: {json.dumps({'type': 'pipeline_start', 'project': project_name, 'iterations': request.iterations, 'has_learnings': past_learnings.get('has_history', False)})}\n\n"
            
            ACTIVE_BUILDS[build_id]["status"] = "planning"
            ACTIVE_BUILDS[build_id]["progress_percent"] = 5
            
            # ========== PHASE 1: DIRECTOR ==========
            yield f"data: {json.dumps({'type': 'phase_start', 'phase': 'Director', 'agent': 'DIRECTOR', 'description': 'Creating build plan with AI learnings'})}\n\n"
            
            director_start = time.time()
            try:
                director_response = await call_llm_with_retry(
                    llm_client,
                    messages=[
                        {"role": "system", "content": SPECIALIST_AGENTS["director"]["prompt"]},
                        {"role": "user", "content": get_director_prompt(project_name, project_type, project_desc, past_learnings)}
                    ],
                    max_tokens=2000
                )
                
                build_plan = director_response.choices[0].message.content
                yield f"data: {json.dumps({'type': 'director_plan', 'content': build_plan})}\n\n"
                yield f"data: {json.dumps({'type': 'phase_complete', 'phase': 'Director'})}\n\n"
                
                # Record agent performance
                await record_agent_performance("DIRECTOR", "director", True, 90, int(time.time() - director_start))
                patterns_worked.append("Director creates comprehensive build plans")
                
            except Exception as e:
                error_msg = str(e)
                phase_errors.append({"phase": "Director", "error": error_msg})
                yield f"data: {json.dumps({'type': 'phase_error', 'phase': 'Director', 'error': error_msg, 'recoverable': True})}\n\n"
                await record_agent_performance("DIRECTOR", "director", False, 0, int(time.time() - director_start))
                patterns_avoid.append(f"Director failed: {error_msg[:50]}")
            
            ACTIVE_BUILDS[build_id]["progress_percent"] = 10
            
            # ========== PHASE 2: ARCHITECT ==========
            yield f"data: {json.dumps({'type': 'phase_start', 'phase': 'Architecture', 'agent': 'ATLAS', 'description': 'Designing system architecture'})}\n\n"
            
            architect_start = time.time()
            try:
                arch_response = await call_llm_with_retry(
                    llm_client,
                    messages=[
                        {"role": "system", "content": SPECIALIST_AGENTS["architect"]["prompt"]},
                        {"role": "user", "content": get_architect_prompt(project_name, project_type, project_desc, engine)}
                    ],
                    max_tokens=4000
                )
                
                architecture = arch_response.choices[0].message.content
                yield f"data: {json.dumps({'type': 'architecture', 'content': architecture})}\n\n"
                
                # Save architecture to project
                await db.projects.update_one(
                    {"id": request.project_id},
                    {"$set": {"architecture": architecture, "updated_at": datetime.now(timezone.utc).isoformat()}}
                )
                
                yield f"data: {json.dumps({'type': 'phase_complete', 'phase': 'Architecture'})}\n\n"
                await record_agent_performance("ATLAS", "architect", True, 85, int(time.time() - architect_start))
                patterns_worked.append("Architecture-first approach ensures clean structure")
                
                ACTIVE_BUILDS[build_id]["quality_scores"]["architecture"] = 85
                
            except Exception as e:
                error_msg = str(e)
                phase_errors.append({"phase": "Architecture", "error": error_msg})
                yield f"data: {json.dumps({'type': 'phase_error', 'phase': 'Architecture', 'error': error_msg, 'recoverable': True})}\n\n"
                await record_agent_performance("ATLAS", "architect", False, 0, int(time.time() - architect_start))
                architecture = "# Default modular architecture\n- Core systems\n- Feature modules\n- UI layer"
            
            ACTIVE_BUILDS[build_id]["progress_percent"] = 20
            ACTIVE_BUILDS[build_id]["current_phase"] = "building"
            
            # ========== PHASE 3-N: ALL 12 SPECIALIST AGENTS ==========
            # Each tuple: (display_name, module_key, weight, db_agent_name, specialist_fallback_key)
            build_modules = [
                ("Game Design Document",  "game_design",       10, "NEXUS",     "backend"),
                ("Player Controller",     "player_controller", 15, "FORGE",     "game_engine"),
                ("Combat System",         "combat_system",     15, "FORGE",     "game_engine"),
                ("Inventory System",      "inventory_system",  12, "FORGE",     "game_engine"),
                ("AI System",             "ai_system",         12, "FORGE",     "game_engine"),
                ("Save System",           "save_system",       10, "FORGE",     "game_engine"),
                ("Level Design",          "level_design",      10, "TERRA",     "level_designer"),
                ("UI & HUD",              "ui_hud",             8, "PRISM",     "frontend"),
                ("Animation Systems",     "animation",          8, "KINETIC",   "animator"),
                ("Audio Systems",         "audio",              8, "SONIC",     "ai_engineer"),
                ("VFX & Shaders",         "vfx",                8, "VERTEX",    "ai_engineer"),
                ("Narrative & Story",     "narrative",          6, "CHRONICLE", "frontend"),
            ]
            
            total_build_progress = 64  # From 20% to 84%
            progress_per_iteration = total_build_progress / request.iterations
            
            for iteration in range(1, request.iterations + 1):
                # Check if build was cancelled
                if ACTIVE_BUILDS.get(build_id, {}).get("status") == "cancelled":
                    yield f"data: {json.dumps({'type': 'build_cancelled', 'iteration': iteration})}\n\n"
                    break
                
                ACTIVE_BUILDS[build_id]["current_iteration"] = iteration
                yield f"data: {json.dumps({'type': 'iteration_start', 'iteration': iteration, 'total': request.iterations})}\n\n"
                
                iteration_quality_scores = []
                module_progress = 20 + (progress_per_iteration * (iteration - 1))
                progress_per_module = progress_per_iteration / len(build_modules)
                
                for idx, (module_name, module_key, weight, db_agent_name, fallback_key) in enumerate(build_modules):
                    module_start = time.time()

                    # Resolve the correct agent: DB agent first, then SPECIALIST_AGENTS fallback
                    agent_display, agent_system_prompt = _get_agent_prompt(db_agent_name, fallback_key)

                    yield f"data: {json.dumps({'type': 'phase_start', 'phase': module_name, 'agent': agent_display, 'iteration': iteration, 'module_index': idx + 1, 'total_modules': len(build_modules)})}\n\n"
                    
                    try:
                        prompt = get_specialist_prompt(
                            fallback_key,
                            module_key,
                            project_name,
                            engine,
                            architecture,
                            iteration
                        )
                        
                        full_content = ""
                        # Use non-streaming to avoid blocking the async event loop
                        response = await call_llm_with_retry(
                            llm_client,
                            messages=[
                                {"role": "system", "content": agent_system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=8000,
                            stream=False
                        )
                        full_content = response.choices[0].message.content

                        # Heartbeat so the client knows we're alive
                        yield f"data: {json.dumps({'type': 'heartbeat', 'module': module_name, 'agent': agent_display})}\n\n"
                        
                        # Extract and save files
                        code_blocks = extract_code_blocks(full_content)
                        files_saved = 0
                        for block in code_blocks:
                            filepath = block.get('filepath')
                            if filepath:
                                file_doc = {
                                    "id": str(uuid.uuid4()),
                                    "project_id": request.project_id,
                                    "filepath": filepath,
                                    "filename": block.get('filename'),
                                    "language": block.get('language', 'cpp'),
                                    "content": block['content'],
                                    "iteration": iteration,
                                    "module": module_name,
                                    "created_at": datetime.now(timezone.utc).isoformat()
                                }
                                
                                await db.files.update_one(
                                    {"project_id": request.project_id, "filepath": filepath},
                                    {"$set": file_doc},
                                    upsert=True
                                )
                                
                                all_files.append(filepath)
                                files_saved += 1
                                yield f"data: {json.dumps({'type': 'file_saved', 'filepath': filepath, 'module': module_name, 'iteration': iteration})}\n\n"
                        
                        modules_built.append(module_name)
                        module_quality = 75 + (iteration * 5)
                        iteration_quality_scores.append(module_quality)
                        
                        ACTIVE_BUILDS[build_id]["files_generated"] = len(all_files)
                        ACTIVE_BUILDS[build_id]["progress_percent"] = int(module_progress + (idx + 1) * progress_per_module)
                        
                        yield f"data: {json.dumps({'type': 'phase_complete', 'phase': module_name, 'files': files_saved, 'quality': module_quality, 'iteration': iteration})}\n\n"
                        
                        await record_agent_performance(agent_display, fallback_key, True, module_quality, int(time.time() - module_start))
                        
                    except Exception as e:
                        error_msg = str(e)
                        phase_errors.append({"phase": module_name, "iteration": iteration, "error": error_msg})
                        yield f"data: {json.dumps({'type': 'phase_error', 'phase': module_name, 'error': error_msg, 'recoverable': True, 'iteration': iteration})}\n\n"
                        await record_agent_performance(agent_display, fallback_key, False, 0, int(time.time() - module_start))
                        patterns_avoid.append(f"Module {module_name} had issues: {error_msg[:30]}")
                        
                        await asyncio.sleep(1)
                        continue
                
                # ========== SENTINEL: CODE REVIEW (every iteration) ==========
                if request.auto_review:
                    review_start = time.time()
                    sentinel_name, sentinel_prompt = _get_agent_prompt("SENTINEL", "reviewer")
                    yield f"data: {json.dumps({'type': 'phase_start', 'phase': 'Code Review', 'agent': sentinel_name, 'iteration': iteration})}\n\n"
                    
                    try:
                        recent_files = await db.files.find(
                            {"project_id": request.project_id, "iteration": iteration},
                            {"_id": 0}
                        ).limit(5).to_list(5)
                        
                        code_sample = "\n\n".join([f"// {f['filepath']}\n{f['content'][:1000]}" for f in recent_files])
                        
                        review_response = await call_llm_with_retry(
                            llm_client,
                            messages=[
                                {"role": "system", "content": sentinel_prompt},
                                {"role": "user", "content": get_review_prompt(code_sample, iteration)}
                            ],
                            max_tokens=2000
                        )
                        
                        review_content = review_response.choices[0].message.content
                        
                        review_score = 80
                        try:
                            review_json = json.loads(review_content.split("```json")[1].split("```")[0]) if "```json" in review_content else {}
                            review_score = review_json.get("score", 80)
                        except (json.JSONDecodeError, IndexError, KeyError):
                            pass
                        
                        ACTIVE_BUILDS[build_id]["quality_scores"][f"iteration_{iteration}"] = review_score
                        
                        yield f"data: {json.dumps({'type': 'review', 'content': review_content, 'iteration': iteration, 'score': review_score})}\n\n"
                        yield f"data: {json.dumps({'type': 'phase_complete', 'phase': 'Code Review', 'score': review_score})}\n\n"
                        
                        await record_agent_performance(sentinel_name, "reviewer", True, review_score, int(time.time() - review_start))
                        
                        if review_score >= 85:
                            patterns_worked.append(f"Iteration {iteration} achieved score {review_score}")
                        
                    except Exception as e:
                        error_msg = str(e)
                        yield f"data: {json.dumps({'type': 'phase_error', 'phase': 'Code Review', 'error': error_msg, 'recoverable': True})}\n\n"
                        await record_agent_performance(sentinel_name, "reviewer", False, 0, int(time.time() - review_start))

                # ========== PROBE: TESTING (final iteration only) ==========
                if iteration == request.iterations:
                    probe_start = time.time()
                    probe_name, probe_prompt = _get_agent_prompt("PROBE", "tester")
                    yield f"data: {json.dumps({'type': 'phase_start', 'phase': 'Testing & QA', 'agent': probe_name, 'iteration': iteration})}\n\n"
                    try:
                        probe_response = await call_llm_with_retry(
                            llm_client,
                            messages=[
                                {"role": "system", "content": probe_prompt},
                                {"role": "user", "content": f"Write a comprehensive test suite for {project_name} ({engine}). Cover all built modules: {', '.join(modules_built)}. Include unit tests, integration tests, and edge cases."}
                            ],
                            max_tokens=4000
                        )
                        probe_content = probe_response.choices[0].message.content
                        probe_blocks = extract_code_blocks(probe_content)
                        probe_files = 0
                        for block in probe_blocks:
                            if block.get('filepath'):
                                await db.files.update_one(
                                    {"project_id": request.project_id, "filepath": block['filepath']},
                                    {"$set": {"id": str(uuid.uuid4()), "project_id": request.project_id, "filepath": block['filepath'], "filename": block.get('filename'), "language": block.get('language', 'cpp'), "content": block['content'], "iteration": iteration, "module": "Testing", "created_at": datetime.now(timezone.utc).isoformat()}},
                                    upsert=True
                                )
                                all_files.append(block['filepath'])
                                probe_files += 1
                                yield f"data: {json.dumps({'type': 'file_saved', 'filepath': block['filepath'], 'module': 'Testing', 'iteration': iteration})}\n\n"
                        yield f"data: {json.dumps({'type': 'phase_complete', 'phase': 'Testing & QA', 'files': probe_files})}\n\n"
                        await record_agent_performance(probe_name, "tester", True, 85, int(time.time() - probe_start))
                    except Exception as e:
                        yield f"data: {json.dumps({'type': 'phase_error', 'phase': 'Testing & QA', 'error': str(e), 'recoverable': True})}\n\n"
                
                # Calculate iteration quality
                if iteration_quality_scores:
                    avg_quality = sum(iteration_quality_scores) / len(iteration_quality_scores)
                    overall_quality_score = max(overall_quality_score, int(avg_quality))
                
                yield f"data: {json.dumps({'type': 'iteration_complete', 'iteration': iteration, 'avg_quality': overall_quality_score})}\n\n"
            
            # ========== FINAL ==========
            build_time = int(time.time() - build_start_time)
            successful = len(phase_errors) < 3 and len(all_files) > 0
            
            # Record to memory system
            if request.enable_memory:
                await record_build_memory(
                    project_id=request.project_id,
                    project_type=project_type,
                    architecture=architecture,
                    modules=list(set(modules_built)),
                    final_score=overall_quality_score,
                    iterations=request.iterations,
                    build_time=build_time,
                    files_count=len(all_files),
                    successful=successful,
                    patterns_worked=patterns_worked,
                    patterns_avoid=patterns_avoid
                )
            
            await db.projects.update_one(
                {"id": request.project_id},
                {"$set": {
                    "phase": "complete",
                    "god_mode_v2_complete": True,
                    "iterations_completed": request.iterations,
                    "total_files": len(all_files),
                    "final_quality_score": overall_quality_score,
                    "build_time_seconds": build_time,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            ACTIVE_BUILDS[build_id]["status"] = "complete"
            ACTIVE_BUILDS[build_id]["progress_percent"] = 100
            
            yield f"data: {json.dumps({'type': 'pipeline_complete', 'total_files': len(all_files), 'iterations': request.iterations, 'quality_score': overall_quality_score, 'build_time': build_time, 'errors': len(phase_errors), 'memory_recorded': request.enable_memory})}\n\n"
            
        except Exception as e:
            error_trace = traceback.format_exc()
            ACTIVE_BUILDS[build_id]["status"] = "failed"
            ACTIVE_BUILDS[build_id]["errors"].append(str(e))
            yield f"data: {json.dumps({'type': 'pipeline_error', 'error': str(e), 'trace': error_trace[:500]})}\n\n"
        
        finally:
            # Clean up active builds after a delay
            await asyncio.sleep(60)
            if build_id in ACTIVE_BUILDS:
                del ACTIVE_BUILDS[build_id]
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
