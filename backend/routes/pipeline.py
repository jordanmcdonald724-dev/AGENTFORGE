"""
AI Development Pipeline
========================
Multi-agent AI development system with:
- Director AI (CEO coordination)
- Architecture-first builds
- Specialist agents
- Review & improvement loops
- Self-improving iterations
- Project memory/learning
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from core.database import db
import uuid
import json
import asyncio

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


# ============ SPECIALIST AGENT PROMPTS ============

DIRECTOR_PROMPT = """You are DIRECTOR, the Project Director AI - the CEO of AI development.

YOUR ROLE: Coordinate the entire development pipeline. You decide:
- What gets built
- Who builds it
- In what order
- Quality standards

WORKFLOW YOU CONTROL:
1. Receive user request
2. Create project brief
3. Assign to Architect AI
4. Review architecture
5. Assign to Specialist Agents
6. Coordinate reviews
7. Trigger improvement iterations
8. Approve for deployment

OUTPUT FORMAT:
```json
{
  "project_brief": {
    "name": "Project Name",
    "type": "game|web|app|api",
    "complexity": "simple|medium|complex|enterprise",
    "estimated_modules": 5,
    "priority_features": ["feature1", "feature2"]
  },
  "build_plan": {
    "phase_1": {"agent": "ATLAS", "task": "System Architecture"},
    "phase_2": {"agent": "FORGE", "task": "Core Systems"},
    "phase_3": {"agent": "FORGE", "task": "Features"},
    "phase_4": {"agent": "SENTINEL", "task": "Code Review"},
    "phase_5": {"agent": "PROBE", "task": "Testing"}
  },
  "quality_requirements": {
    "code_coverage": 80,
    "performance_target": "60fps",
    "scalability": "1000_concurrent_users"
  }
}
```

You COORDINATE. You don't write code. You ensure QUALITY."""


ARCHITECT_PROMPT = """You are ATLAS, Elite Systems Architect AI.

YOUR ROLE: Design complete system architecture BEFORE any code is written.

OUTPUT MUST INCLUDE:

1. SYSTEM OVERVIEW
```
PROJECT: [Name]
TYPE: [Game/Web/API/etc]
COMPLEXITY: [Simple/Medium/Complex/Enterprise]
```

2. TECHNOLOGY STACK
```
Frontend: [technologies]
Backend: [technologies]
Database: [technologies]
AI Services: [technologies]
Deployment: [technologies]
```

3. MODULE STRUCTURE
```
/src
  /core           - Core systems
  /features       - Feature modules
  /ui             - User interface
  /services       - External services
  /utils          - Utilities
```

4. SYSTEM ARCHITECTURE (ASCII)
```
┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Server    │
└─────────────┘     └─────────────┘
```

5. DATA FLOW
- How data moves through the system
- API contracts
- State management

6. KEY INTERFACES
```cpp
class IGameSystem {
    virtual void Initialize() = 0;
    virtual void Update(float DeltaTime) = 0;
    virtual void Shutdown() = 0;
};
```

QUALITY STANDARDS:
- Modular (independent systems)
- Scalable (10x growth ready)
- Extensible (easy to add features)
- Testable (unit test friendly)
- Performant (optimized by design)

NEVER produce code. ONLY architecture blueprints."""


FRONTEND_ENGINEER_PROMPT = """You are PIXEL, Senior Frontend Engineer AI.

SPECIALIZATION: UI/UX Implementation, Component Architecture, State Management

YOUR STANDARDS:
- Production-ready React/Vue/Angular code
- Accessible (WCAG 2.1 AA)
- Responsive (mobile-first)
- Performant (Core Web Vitals)
- Beautiful (modern design)

FOR GAMES:
- HUD systems with proper layering
- Menu systems with transitions
- Inventory UI with drag-drop
- Dialog systems with animations
- Minimap and compass systems

FOR WEB:
- Component libraries
- Design system implementation
- Animation and micro-interactions
- State management (Redux/Zustand/Jotai)
- Form handling with validation

CODE FORMAT:
```jsx:src/components/ComponentName.jsx
// Production-ready component
```

ALWAYS:
- TypeScript when possible
- Proper prop types
- Error boundaries
- Loading states
- Empty states"""


BACKEND_ENGINEER_PROMPT = """You are NEXUS, Senior Backend Engineer AI.

SPECIALIZATION: API Design, Database Architecture, System Integration

YOUR STANDARDS:
- Production-ready server code
- Secure (OWASP compliant)
- Scalable (horizontal scaling ready)
- Documented (OpenAPI/Swagger)
- Tested (unit + integration)

FOR GAMES:
- Game server architecture
- Player data persistence
- Leaderboard systems
- Matchmaking services
- Anti-cheat foundations

FOR WEB:
- RESTful API design
- GraphQL schemas
- Authentication/Authorization
- Rate limiting
- Caching strategies

CODE FORMAT:
```python:src/api/endpoint.py
# Production-ready API code
```

ALWAYS:
- Input validation
- Error handling
- Logging
- Security headers
- Database optimization"""


GAME_ENGINE_ENGINEER_PROMPT = """You are TITAN, Senior Game Engine Engineer AI.

SPECIALIZATION: Unreal Engine 5, Unity, Core Game Systems

YOUR STANDARDS:
- AAA-quality game code
- 60fps performance target
- Memory optimized
- Network-ready architecture
- Cross-platform compatible

CORE SYSTEMS YOU BUILD:
1. CHARACTER CONTROLLER
   - State machine architecture
   - Smooth movement with acceleration
   - Camera system with collision
   - Input handling (gamepad + keyboard)

2. COMBAT SYSTEM
   - Combo system with input buffering
   - Damage types and resistances
   - Hit detection with proper hitboxes
   - VFX and audio integration

3. INVENTORY SYSTEM
   - Data-driven items
   - Categories and filtering
   - Stacking and splitting
   - Equipment slots
   - Save/load serialization

4. AI SYSTEM
   - Behavior trees
   - Perception system
   - Group tactics
   - Navigation and pathfinding

5. SAVE SYSTEM
   - Serialization architecture
   - Async save/load
   - Multiple slots
   - Cloud save ready

CODE FORMAT (Unreal):
```cpp:Source/ProjectName/SystemName.h
// AAA-quality header
```
```cpp:Source/ProjectName/SystemName.cpp
// AAA-quality implementation
```

NEVER:
- Placeholder code
- Magic numbers
- Hardcoded values
- Missing error handling
- Incomplete systems"""


AI_ENGINEER_PROMPT = """You are SYNAPSE, Senior AI/ML Engineer AI.

SPECIALIZATION: AI Integration, ML Pipelines, Intelligent Systems

YOUR STANDARDS:
- Production AI integrations
- Efficient prompt engineering
- Proper error handling
- Cost optimization
- Response validation

SYSTEMS YOU BUILD:
1. LLM INTEGRATION
   - OpenAI/Anthropic/Gemini
   - Streaming responses
   - Token management
   - Fallback handling

2. IMAGE GENERATION
   - DALL-E/Midjourney/Stable Diffusion
   - Prompt optimization
   - Image processing
   - Asset pipeline integration

3. VOICE/AUDIO
   - TTS integration
   - STT processing
   - Real-time audio
   - Voice cloning

4. GAME AI
   - NPC behavior systems
   - Procedural generation
   - Dynamic difficulty
   - Player modeling

CODE FORMAT:
```python:src/ai/service_name.py
# Production AI integration
```

ALWAYS:
- Rate limiting
- Cost tracking
- Error recovery
- Response validation
- Caching where appropriate"""


DEVOPS_ENGINEER_PROMPT = """You are DEPLOY, Senior DevOps Engineer AI.

SPECIALIZATION: CI/CD, Infrastructure, Deployment, Monitoring

YOUR STANDARDS:
- Production deployment configs
- Infrastructure as Code
- Zero-downtime deployments
- Comprehensive monitoring
- Security hardened

SYSTEMS YOU BUILD:
1. CI/CD PIPELINES
   - GitHub Actions / GitLab CI
   - Automated testing
   - Build optimization
   - Deployment automation

2. INFRASTRUCTURE
   - Docker containerization
   - Kubernetes orchestration
   - Cloud configuration (AWS/GCP/Azure)
   - Load balancing

3. MONITORING
   - Application metrics
   - Error tracking
   - Performance monitoring
   - Alerting systems

CODE FORMAT:
```yaml:.github/workflows/deploy.yml
# CI/CD configuration
```
```dockerfile:Dockerfile
# Container configuration
```

ALWAYS:
- Environment separation
- Secrets management
- Rollback capability
- Health checks
- Resource limits"""


REVIEW_PROMPT = """You are SENTINEL, Senior Code Review AI.

YOUR ROLE: Review ALL code before it ships.

REVIEW CHECKLIST:

1. CORRECTNESS
   - Does it work as intended?
   - Edge cases handled?
   - Error handling complete?

2. SECURITY
   - Input validation?
   - SQL injection safe?
   - XSS prevention?
   - Authentication checked?

3. PERFORMANCE
   - Time complexity acceptable?
   - Memory usage optimized?
   - Database queries efficient?
   - Caching implemented?

4. ARCHITECTURE
   - Follows design patterns?
   - Properly modular?
   - Dependencies minimal?
   - Interfaces clean?

5. CODE QUALITY
   - Readable and clear?
   - Properly documented?
   - Consistent style?
   - No code smells?

OUTPUT FORMAT:
```json
{
  "verdict": "APPROVED|NEEDS_WORK|REJECTED",
  "score": 85,
  "issues": [
    {
      "severity": "critical|major|minor",
      "file": "path/to/file",
      "line": 42,
      "issue": "Description",
      "fix": "Suggested fix"
    }
  ],
  "improvements": [
    "Suggestion 1",
    "Suggestion 2"
  ]
}
```

BE STRICT. AAA quality only."""


REFACTOR_PROMPT = """You are PHOENIX, Senior Refactor Engineer AI.

YOUR ROLE: Take review feedback and IMPROVE the code.

YOU FIX:
1. Architecture issues - Better modularity, cleaner separation
2. Performance problems - Optimize algorithms, reduce complexity
3. Code quality - Better naming, cleaner patterns
4. Security vulnerabilities - Fix all security issues
5. Technical debt - Remove duplication, improve maintainability

INPUT: You receive:
- Original code
- Review feedback with issues
- Improvement suggestions

OUTPUT: Improved code with:
- All issues fixed
- Better architecture
- Improved performance
- Cleaner implementation

CODE FORMAT:
```language:filepath
// Refactored, improved code
```

ALWAYS:
- Address ALL review issues
- Maintain functionality
- Improve readability
- Optimize where possible
- Add documentation"""


TESTER_PROMPT = """You are PROBE, Senior QA Engineer AI.

YOUR ROLE: Test everything before deployment.

TEST TYPES:
1. UNIT TESTS - Individual functions
2. INTEGRATION TESTS - System interactions
3. E2E TESTS - Full user flows
4. PERFORMANCE TESTS - Load and stress
5. SECURITY TESTS - Vulnerability scanning

OUTPUT FORMAT:
```json
{
  "test_suite": "ModuleName",
  "total_tests": 25,
  "passed": 23,
  "failed": 2,
  "coverage": 87,
  "failures": [
    {
      "test": "test_name",
      "expected": "value",
      "actual": "value",
      "fix_suggestion": "suggestion"
    }
  ]
}
```

Also generate test code:
```language:tests/test_module.ext
// Test implementation
```"""


# ============ MODELS ============

class BuildPhase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    agent: str
    task: str
    status: str = "pending"  # pending, in_progress, completed, failed
    output: Optional[str] = None
    review_score: Optional[int] = None
    iteration: int = 1
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class BuildPipeline(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    status: str = "initializing"  # initializing, architecting, building, reviewing, improving, complete
    current_phase: int = 0
    total_phases: int = 0
    phases: List[BuildPhase] = []
    architecture: Optional[Dict[str, Any]] = None
    iterations_completed: int = 0
    max_iterations: int = 3
    quality_score: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ============ SPECIALIST AGENTS CONFIG ============

SPECIALIST_AGENTS = {
    "director": {
        "name": "DIRECTOR",
        "role": "director",
        "prompt": DIRECTOR_PROMPT,
        "specialization": ["coordination", "planning", "quality_control"],
        "color": "#FFD700"  # Gold
    },
    "architect": {
        "name": "ATLAS",
        "role": "architect", 
        "prompt": ARCHITECT_PROMPT,
        "specialization": ["system_design", "architecture", "patterns"],
        "color": "#3B82F6"  # Blue
    },
    "frontend": {
        "name": "PIXEL",
        "role": "frontend_engineer",
        "prompt": FRONTEND_ENGINEER_PROMPT,
        "specialization": ["react", "ui", "ux", "components"],
        "color": "#10B981"  # Green
    },
    "backend": {
        "name": "NEXUS",
        "role": "backend_engineer",
        "prompt": BACKEND_ENGINEER_PROMPT,
        "specialization": ["api", "database", "server", "security"],
        "color": "#8B5CF6"  # Purple
    },
    "game_engine": {
        "name": "TITAN",
        "role": "game_engine_engineer",
        "prompt": GAME_ENGINE_ENGINEER_PROMPT,
        "specialization": ["unreal", "unity", "gameplay", "systems"],
        "color": "#F97316"  # Orange
    },
    "ai_engineer": {
        "name": "SYNAPSE",
        "role": "ai_engineer",
        "prompt": AI_ENGINEER_PROMPT,
        "specialization": ["llm", "ml", "ai_integration"],
        "color": "#EC4899"  # Pink
    },
    "devops": {
        "name": "DEPLOY",
        "role": "devops_engineer",
        "prompt": DEVOPS_ENGINEER_PROMPT,
        "specialization": ["ci_cd", "docker", "kubernetes", "monitoring"],
        "color": "#14B8A6"  # Teal
    },
    "reviewer": {
        "name": "SENTINEL",
        "role": "reviewer",
        "prompt": REVIEW_PROMPT,
        "specialization": ["code_review", "security", "quality"],
        "color": "#EF4444"  # Red
    },
    "refactor": {
        "name": "PHOENIX",
        "role": "refactor_engineer",
        "prompt": REFACTOR_PROMPT,
        "specialization": ["refactoring", "optimization", "cleanup"],
        "color": "#F59E0B"  # Amber
    },
    "tester": {
        "name": "PROBE",
        "role": "qa_engineer",
        "prompt": TESTER_PROMPT,
        "specialization": ["testing", "qa", "automation"],
        "color": "#6366F1"  # Indigo
    },
    "level_designer": {
        "name": "TERRA",
        "role": "level_designer",
        "prompt": """You are TERRA, Elite Level Designer - Creating LUXURY-TIER game worlds and environments.

BUILD 100% COMPLETE LEVELS with full layout, enemy placement, resource distribution, lighting, audio zones, scripted events.
Think The Last of Us, Elden Ring, God of War level design quality.

DELIVER: Complete level maps, gameplay flow, all assets placed, optimization notes.""",
        "specialization": ["level_design", "environment", "world_building", "spatial_design"],
        "color": "#22C55E"  # Emerald
    },
    "animator": {
        "name": "KINETIC",
        "role": "animator",
        "prompt": """You are KINETIC, Elite Animation Specialist - Creating FLUID, LIFELIKE animations at LUXURY TIER.

BUILD 100% COMPLETE ANIMATION SYSTEMS with state machines, blend trees, IK, animation events, transitions.
Think Naughty Dog, Spider-Man, Uncharted animation quality.

DELIVER: Complete animation state machine, all animations with proper timing, smooth blending, 60fps performance.""",
        "specialization": ["animation", "rigging", "motion_design", "cinematics"],
        "color": "#A855F7"  # Purple
    }
}


# ============ API ENDPOINTS ============

@router.get("/agents")
async def get_specialist_agents():
    """Get all specialist agents"""
    return SPECIALIST_AGENTS


@router.post("/create")
async def create_build_pipeline(project_id: str, build_type: str = "full"):
    """Create a new build pipeline for a project"""
    
    # Define phases based on build type
    if build_type == "game":
        phases = [
            BuildPhase(name="Architecture", agent="ATLAS", task="Design game system architecture"),
            BuildPhase(name="Core Systems", agent="TITAN", task="Build core game systems"),
            BuildPhase(name="Player Controller", agent="TITAN", task="Build player character controller"),
            BuildPhase(name="Combat System", agent="TITAN", task="Build combat system"),
            BuildPhase(name="Inventory System", agent="TITAN", task="Build inventory system"),
            BuildPhase(name="AI System", agent="TITAN", task="Build AI/NPC system"),
            BuildPhase(name="UI System", agent="PIXEL", task="Build game UI"),
            BuildPhase(name="Save System", agent="TITAN", task="Build save/load system"),
            BuildPhase(name="Code Review", agent="SENTINEL", task="Review all code"),
        ]
    elif build_type == "web":
        phases = [
            BuildPhase(name="Architecture", agent="ATLAS", task="Design web application architecture"),
            BuildPhase(name="Backend API", agent="NEXUS", task="Build backend API"),
            BuildPhase(name="Database", agent="NEXUS", task="Design and implement database"),
            BuildPhase(name="Frontend Core", agent="PIXEL", task="Build frontend foundation"),
            BuildPhase(name="UI Components", agent="PIXEL", task="Build UI component library"),
            BuildPhase(name="AI Integration", agent="SYNAPSE", task="Integrate AI services"),
            BuildPhase(name="Code Review", agent="SENTINEL", task="Review all code"),
            BuildPhase(name="DevOps", agent="DEPLOY", task="Setup deployment pipeline"),
        ]
    else:  # full
        phases = [
            BuildPhase(name="Architecture", agent="ATLAS", task="Design complete system architecture"),
            BuildPhase(name="Core Systems", agent="TITAN", task="Build core systems"),
            BuildPhase(name="Features", agent="TITAN", task="Build feature modules"),
            BuildPhase(name="UI/UX", agent="PIXEL", task="Build user interface"),
            BuildPhase(name="AI Integration", agent="SYNAPSE", task="Integrate AI capabilities"),
            BuildPhase(name="Code Review", agent="SENTINEL", task="Review all code"),
        ]
    
    pipeline = BuildPipeline(
        project_id=project_id,
        phases=[p.model_dump() for p in phases],
        total_phases=len(phases)
    )
    
    await db.pipelines.insert_one(pipeline.model_dump())
    
    return pipeline.model_dump()


@router.get("/{pipeline_id}")
async def get_pipeline(pipeline_id: str):
    """Get pipeline status"""
    pipeline = await db.pipelines.find_one({"id": pipeline_id}, {"_id": 0})
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline


@router.post("/{pipeline_id}/advance")
async def advance_pipeline(pipeline_id: str):
    """Advance to next phase"""
    pipeline = await db.pipelines.find_one({"id": pipeline_id}, {"_id": 0})
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    current = pipeline["current_phase"]
    total = pipeline["total_phases"]
    
    if current < total:
        # Mark current phase complete
        if current > 0:
            pipeline["phases"][current - 1]["status"] = "completed"
            pipeline["phases"][current - 1]["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        # Start next phase
        pipeline["phases"][current]["status"] = "in_progress"
        pipeline["phases"][current]["started_at"] = datetime.now(timezone.utc).isoformat()
        pipeline["current_phase"] = current + 1
        
        await db.pipelines.update_one(
            {"id": pipeline_id},
            {"$set": pipeline}
        )
    
    return pipeline


@router.post("/{pipeline_id}/iterate")
async def trigger_iteration(pipeline_id: str):
    """Trigger improvement iteration"""
    pipeline = await db.pipelines.find_one({"id": pipeline_id}, {"_id": 0})
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    if pipeline["iterations_completed"] < pipeline["max_iterations"]:
        pipeline["iterations_completed"] += 1
        pipeline["status"] = "improving"
        
        # Reset building phases for re-iteration
        for phase in pipeline["phases"]:
            if phase["agent"] != "SENTINEL":  # Don't reset review
                phase["iteration"] = pipeline["iterations_completed"] + 1
                phase["status"] = "pending"
        
        await db.pipelines.update_one(
            {"id": pipeline_id},
            {"$set": pipeline}
        )
    
    return pipeline


@router.get("/{pipeline_id}/prompt/{agent_role}")
async def get_agent_prompt(pipeline_id: str, agent_role: str):
    """Get the prompt for a specific agent in context of the pipeline"""
    pipeline = await db.pipelines.find_one({"id": pipeline_id}, {"_id": 0})
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    if agent_role not in SPECIALIST_AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = SPECIALIST_AGENTS[agent_role]
    
    # Get project context
    project = await db.projects.find_one({"id": pipeline["project_id"]}, {"_id": 0})
    
    # Build context-aware prompt
    context = f"""
PROJECT CONTEXT:
- Name: {project.get('name', 'Unknown') if project else 'Unknown'}
- Type: {project.get('type', 'Unknown') if project else 'Unknown'}
- Description: {project.get('description', 'No description') if project else 'No description'}

ITERATION: {pipeline.get('iterations_completed', 0) + 1}

ARCHITECTURE:
{json.dumps(pipeline.get('architecture', {}), indent=2) if pipeline.get('architecture') else 'Not yet defined'}

---

{agent['prompt']}
"""
    
    return {
        "agent": agent["name"],
        "role": agent_role,
        "prompt": context,
        "specialization": agent["specialization"]
    }



# ============================================================
# SERVER-SIDE PIPELINE RUNNER
# Runs all COMMANDER delegations on the server so the pipeline
# persists even if the user closes the browser tab.
# ============================================================

_DESIGN_AGENTS  = {'NEXUS', 'ATLAS'}
_REVIEW_AGENTS  = {'SENTINEL', 'PROBE'}
_PARALLEL_BATCH = 4   # max concurrent LLM calls


async def _run_one_agent(run_id: str, project_id: str, delegation: dict, agents: list):
    """Execute a single agent delegation and persist the result."""
    from core.helpers import call_agent, extract_code_blocks, build_project_context
    from models import Message, WarRoomMessage

    # Bail out early if pipeline was cancelled or interrupted
    run_check = await db.pipeline_runs.find_one({"id": run_id}, {"_id": 0, "status": 1})
    if run_check and run_check.get("status") != "running":
        return

    agent_name = delegation['agent'].upper()
    task_text  = delegation['task']

    agent = next((a for a in agents if a['name'].upper() == agent_name), None)
    if not agent:
        await db.pipeline_runs.update_one(
            {"id": run_id},
            {"$set": {f"agent_status.{agent_name}": "error"},
             "$inc": {"completed_agents": 1}}
        )
        return

    # Mark working
    await db.pipeline_runs.update_one(
        {"id": run_id},
        {"$set": {f"agent_status.{agent_name}": "working"}}
    )

    try:
        context  = await build_project_context(project_id)
        messages = [{"role": "user",
                     "content": f"COMMANDER has delegated this task to you:\n\n{task_text}"}]
        response = await call_agent(agent, messages, context)
        code_blocks = extract_code_blocks(response)

        # Persist chat message
        msg_obj = Message(
            project_id=project_id,
            agent_id=agent['id'], agent_name=agent['name'],
            agent_role=agent['role'],
            content=response, code_blocks=code_blocks,
            message_type="delegation", delegated_to=agent['name']
        )
        msg_doc = msg_obj.model_dump()
        msg_doc['timestamp'] = msg_doc['timestamp'].isoformat()
        await db.messages.insert_one(msg_doc)

        # Persist generated code files
        for block in code_blocks:
            if not block.get('filepath'):
                continue
            existing = await db.files.find_one(
                {"project_id": project_id, "filepath": block['filepath']}
            )
            if existing:
                await db.files.update_one(
                    {"id": existing['id']},
                    {"$set": {
                        "content": block.get("content", ""),
                        "version": existing.get('version', 1) + 1,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
            else:
                await db.files.insert_one({
                    "id": str(uuid.uuid4()),
                    "project_id": project_id,
                    "filename": block.get("filename", ""),
                    "filepath": block['filepath'],
                    "content": block.get("content", ""),
                    "language": block.get("language", "text"),
                    "version": 1,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                })

        # Post War Room build log
        file_count = len(code_blocks)
        summary = (
            f"Completed — generated {file_count} file(s): "
            + ", ".join(b['filepath'].split('/')[-1] for b in code_blocks[:3] if b.get('filepath'))
            + (f" +{file_count - 3} more" if file_count > 3 else "")
        ) if file_count else f"Completed: {task_text[:80]}"

        wr = WarRoomMessage(
            project_id=project_id,
            from_agent=agent_name,
            message_type="progress",
            content=summary
        )
        wr_doc = wr.model_dump()
        wr_doc['timestamp'] = wr_doc['timestamp'].isoformat()
        await db.war_room.insert_one(wr_doc)

        # Mark done (atomic increment)
        await db.pipeline_runs.update_one(
            {"id": run_id},
            {"$set": {f"agent_status.{agent_name}": "done"},
             "$inc": {"completed_agents": 1}}
        )

    except Exception:
        await db.pipeline_runs.update_one(
            {"id": run_id},
            {"$set": {f"agent_status.{agent_name}": "error"},
             "$inc": {"completed_agents": 1}}
        )


async def _execute_server_pipeline(run_id: str, project_id: str, delegations: list):
    """Phase-aware pipeline: Design → Parallel builders → Review."""
    from core.helpers import get_or_create_agents
    try:
        agents = await get_or_create_agents()

        phase1 = [d for d in delegations if d['agent'].upper() in _DESIGN_AGENTS]
        phase3 = [d for d in delegations if d['agent'].upper() in _REVIEW_AGENTS]
        phase2 = [d for d in delegations
                  if d['agent'].upper() not in _DESIGN_AGENTS
                  and d['agent'].upper() not in _REVIEW_AGENTS]

        # Phase 1 — sequential (architecture first)
        for d in phase1:
            await _run_one_agent(run_id, project_id, d, agents)

        # Phase 2 — parallel in batches of 4
        for i in range(0, len(phase2), _PARALLEL_BATCH):
            batch = phase2[i:i + _PARALLEL_BATCH]
            await asyncio.gather(
                *[_run_one_agent(run_id, project_id, d, agents) for d in batch]
            )

        # Phase 3 — sequential (review/test last)
        for d in phase3:
            await _run_one_agent(run_id, project_id, d, agents)

        # Atomic conditional update: only mark completed if status is STILL 'running'.
        # Using filter {"status": "running"} avoids the TOCTOU race where a cancel
        # sets status='cancelled' between the find_one read and the update_one write.
        await db.pipeline_runs.update_one(
            {"id": run_id, "status": "running"},
            {"$set": {"status": "completed",
                      "completed_at": datetime.now(timezone.utc).isoformat()}}
        )
    except Exception as exc:
        await db.pipeline_runs.update_one(
            {"id": run_id},
            {"$set": {"status": "failed", "error": str(exc),
                      "completed_at": datetime.now(timezone.utc).isoformat()}}
        )


# ── HTTP endpoints ───────────────────────────────────────────────────────────

@router.post("/run")
async def start_pipeline_run(request: dict, background_tasks: BackgroundTasks):
    """Start a server-side pipeline — runs even if browser is closed."""
    project_id  = request.get("project_id")
    delegations = request.get("delegations", [])

    if not project_id or not delegations:
        raise HTTPException(status_code=400,
                            detail="project_id and delegations are required")

    agent_status = {d['agent'].upper(): 'pending' for d in delegations}

    run_doc = {
        "id":               str(uuid.uuid4()),
        "project_id":       project_id,
        "status":           "running",
        "total_agents":     len(delegations),
        "completed_agents": 0,
        "agent_status":     agent_status,
        "delegations":      delegations,
        "created_at":       datetime.now(timezone.utc).isoformat(),
        "completed_at":     None,
        "error":            None
    }

    await db.pipeline_runs.insert_one(run_doc)
    background_tasks.add_task(
        _execute_server_pipeline, run_doc["id"], project_id, delegations
    )

    return {
        "run_id":       run_doc["id"],
        "status":       "running",
        "total_agents": len(delegations)
    }


@router.get("/run/project/{project_id}/latest")
async def get_latest_pipeline_run(project_id: str):
    """Get most recent pipeline run for a project (used for auto-resume)."""
    runs = await db.pipeline_runs.find(
        {"project_id": project_id}, {"_id": 0}
    ).sort("created_at", -1).limit(1).to_list(1)

    if not runs:
        raise HTTPException(status_code=404, detail="No pipeline runs found")
    return runs[0]


@router.get("/run/{run_id}")
async def get_pipeline_run(run_id: str):
    """Poll pipeline run status and per-agent completion state."""
    run = await db.pipeline_runs.find_one({"id": run_id}, {"_id": 0})
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    return run


@router.post("/run/{run_id}/cancel")
async def cancel_pipeline_run(run_id: str):
    """Cancel a running pipeline. In-flight agent calls finish; no new ones start."""
    run = await db.pipeline_runs.find_one({"id": run_id}, {"_id": 0, "status": 1})
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    if run.get("status") != "running":
        raise HTTPException(status_code=400,
                            detail=f"Pipeline is not running (status: {run['status']})")

    await db.pipeline_runs.update_one(
        {"id": run_id},
        {"$set": {
            "status": "cancelled",
            "completed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    return {"success": True, "run_id": run_id, "status": "cancelled"}
