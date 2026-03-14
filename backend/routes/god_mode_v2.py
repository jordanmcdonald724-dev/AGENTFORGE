"""
God Mode V2 - Full AI Development Pipeline
==========================================
Architecture-first, multi-agent, self-improving builds.

Pipeline:
1. DIRECTOR - Creates project brief
2. ATLAS - Designs architecture
3. Specialist Agents - Build each system
4. SENTINEL - Reviews code
5. Iterate and improve
6. Deploy
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from core.database import db
from routes.pipeline import SPECIALIST_AGENTS
import uuid
import json
import asyncio
import re

router = APIRouter(prefix="/god-mode-v2", tags=["god-mode-v2"])


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


class GodModeV2Request(BaseModel):
    project_id: str
    iterations: int = 3  # Number of improvement iterations
    auto_review: bool = True
    quality_target: int = 85  # Minimum quality score


# ============ PHASE PROMPTS ============

def get_director_prompt(project_name: str, project_type: str, description: str) -> str:
    return f"""You are DIRECTOR, the Project Director AI.

Analyze this project request and create a comprehensive build plan:

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

@router.post("/build/stream")
async def god_mode_v2_build_stream(request: GodModeV2Request):
    """Full pipeline God Mode build with streaming"""
    
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_name = project.get('name', 'Project').replace(' ', '')
    project_type = project.get('type', 'game')
    project_desc = project.get('description', '')
    engine = project.get('engine_version', 'Unreal Engine 5')
    
    llm_client = get_llm_client()
    
    async def generate():
        yield f"data: {json.dumps({'type': 'pipeline_start', 'project': project_name, 'iterations': request.iterations})}\n\n"
        
        all_files = []
        architecture = ""
        
        # ========== PHASE 1: DIRECTOR ==========
        yield f"data: {json.dumps({'type': 'phase_start', 'phase': 'Director', 'agent': 'DIRECTOR', 'description': 'Creating build plan'})}\n\n"
        
        try:
            director_response = llm_client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": SPECIALIST_AGENTS["director"]["prompt"]},
                    {"role": "user", "content": get_director_prompt(project_name, project_type, project_desc)}
                ],
                max_tokens=2000
            )
            
            build_plan = director_response.choices[0].message.content
            yield f"data: {json.dumps({'type': 'director_plan', 'content': build_plan})}\n\n"
            yield f"data: {json.dumps({'type': 'phase_complete', 'phase': 'Director'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'phase_error', 'phase': 'Director', 'error': str(e)})}\n\n"
        
        # ========== PHASE 2: ARCHITECT ==========
        yield f"data: {json.dumps({'type': 'phase_start', 'phase': 'Architecture', 'agent': 'ATLAS', 'description': 'Designing system architecture'})}\n\n"
        
        try:
            arch_response = llm_client.chat.completions.create(
                model="google/gemini-2.5-flash",
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
        except Exception as e:
            yield f"data: {json.dumps({'type': 'phase_error', 'phase': 'Architecture', 'error': str(e)})}\n\n"
        
        # ========== PHASE 3-N: SPECIALIST BUILDS ==========
        build_modules = [
            ("Player Controller", "player_controller"),
            ("Combat System", "combat_system"),
            ("Inventory System", "inventory_system"),
            ("AI System", "ai_system"),
            ("Save System", "save_system")
        ]
        
        for iteration in range(1, request.iterations + 1):
            yield f"data: {json.dumps({'type': 'iteration_start', 'iteration': iteration, 'total': request.iterations})}\n\n"
            
            for module_name, module_key in build_modules:
                yield f"data: {json.dumps({'type': 'phase_start', 'phase': module_name, 'agent': 'TITAN', 'iteration': iteration})}\n\n"
                
                try:
                    prompt = get_specialist_prompt(
                        "game_engine",
                        module_key,
                        project_name,
                        engine,
                        architecture,
                        iteration
                    )
                    
                    full_content = ""
                    stream = llm_client.chat.completions.create(
                        model="google/gemini-2.5-flash",
                        messages=[
                            {"role": "system", "content": SPECIALIST_AGENTS["game_engine"]["prompt"]},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=12000,
                        stream=True
                    )
                    
                    for chunk in stream:
                        if chunk.choices and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            full_content += content
                            
                            # Stream content
                            if len(full_content) % 200 == 0:
                                yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                    
                    # Extract and save files
                    code_blocks = extract_code_blocks(full_content)
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
                            yield f"data: {json.dumps({'type': 'file_saved', 'filepath': filepath, 'module': module_name})}\n\n"
                    
                    yield f"data: {json.dumps({'type': 'phase_complete', 'phase': module_name, 'files': len(code_blocks)})}\n\n"
                    
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'phase_error', 'phase': module_name, 'error': str(e)})}\n\n"
            
            # ========== REVIEW PHASE ==========
            if request.auto_review and iteration < request.iterations:
                yield f"data: {json.dumps({'type': 'phase_start', 'phase': 'Code Review', 'agent': 'SENTINEL', 'iteration': iteration})}\n\n"
                
                try:
                    # Get sample of generated code for review
                    recent_files = await db.files.find(
                        {"project_id": request.project_id, "iteration": iteration},
                        {"_id": 0}
                    ).limit(5).to_list(5)
                    
                    code_sample = "\n\n".join([f"// {f['filepath']}\n{f['content'][:1000]}" for f in recent_files])
                    
                    review_response = llm_client.chat.completions.create(
                        model="google/gemini-2.5-flash",
                        messages=[
                            {"role": "system", "content": SPECIALIST_AGENTS["reviewer"]["prompt"]},
                            {"role": "user", "content": get_review_prompt(code_sample, iteration)}
                        ],
                        max_tokens=2000
                    )
                    
                    review_content = review_response.choices[0].message.content
                    yield f"data: {json.dumps({'type': 'review', 'content': review_content, 'iteration': iteration})}\n\n"
                    yield f"data: {json.dumps({'type': 'phase_complete', 'phase': 'Code Review'})}\n\n"
                    
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'phase_error', 'phase': 'Code Review', 'error': str(e)})}\n\n"
            
            yield f"data: {json.dumps({'type': 'iteration_complete', 'iteration': iteration})}\n\n"
        
        # ========== FINAL ==========
        await db.projects.update_one(
            {"id": request.project_id},
            {"$set": {
                "phase": "complete",
                "god_mode_v2_complete": True,
                "iterations_completed": request.iterations,
                "total_files": len(all_files),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        yield f"data: {json.dumps({'type': 'pipeline_complete', 'total_files': len(all_files), 'iterations': request.iterations})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
