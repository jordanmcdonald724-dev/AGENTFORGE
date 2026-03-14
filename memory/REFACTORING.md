# AgentForge Server Refactoring Plan

## Current State (Updated March 2026)
- **File**: `/app/backend/server.py`
- **Size**: 5,932 lines (was 8,574)
- **Route handlers**: 220 using `@api_router`
- **All 61 Pydantic models extracted to `/app/backend/models/`**

## Refactoring Strategy

### Completed Extractions
| Section | Lines Removed | Target File | Status |
|---------|---------------|-------------|--------|
| Settings & Local Bridge | ~91 | `routes/settings.py` | ✅ DONE |
| God Mode V1 | ~394 | `routes/god_mode_v1.py` | ✅ DONE |
| Quick Actions | ~58 | `routes/quick_actions.py` | ✅ DONE |
| Live Preview | ~72 | `routes/quick_actions.py` | ✅ DONE |
| Custom Actions | ~83 | `routes/quick_actions.py` | ✅ DONE |
| Agent Memory | ~95 | `routes/agent_memory.py` | ✅ DONE |
| Project Duplication | ~64 | `routes/agent_memory.py` | ✅ DONE |
| Multi-File Refactoring | ~156 | `routes/build_operations.py` | ✅ DONE |
| War Room | ~44 | `routes/build_operations.py` | ✅ DONE |
| Simulation Mode | ~70 | `routes/build_operations.py` | ✅ DONE |
| Playable Demos | ~28 | `routes/build_operations.py` | ✅ DONE |
| Blueprints | ~36 | `routes/build_operations.py` | ✅ DONE |
| Autonomous Builds | ~485 | `routes/autonomous_builds.py` | ✅ DONE |
| **Pydantic Models** | **~965** | `models/` directory | ✅ DONE |

### Server.py Progress
- **Original Size**: 8,578 lines
- **Previous Size**: 6,897 lines
- **Current Size**: 5,932 lines
- **Total Lines Removed**: ~2,646 lines (30.8% reduction)
- **Routes Modularized**: 15 route files now in /routes/
- **Models Extracted**: 61 models now in /models/

### Phase 1: Extract Standalone Features (Low Risk)
These sections have minimal dependencies and can be extracted first:

| Section | Lines | Target File | Priority |
|---------|-------|-------------|----------|
| Settings & Local Bridge | 8463-8557 | `routes/settings.py` | P1 ✅ |
| Quick Actions | 2613-2672 | `routes/quick_actions.py` | P2 |
| Custom Quick Actions | 3245-3325 | `routes/custom_actions.py` | P2 |
| Project Duplication | 3326-3389 | `routes/duplicate.py` | P2 |

### Phase 2: Extract Coupled Features (Medium Risk)
These sections share helpers and models:

| Section | Lines | Target File | Priority |
|---------|-------|-------------|----------|
| God Mode v1 | 2673-3032 | `routes/god_mode_v1.py` | P2 |
| Autonomous Builds | 3766-4251 | `routes/autonomous.py` | P2 |
| Playable Demo Generation | 4252-4580 | `routes/demo.py` | P3 |

### Phase 3: Extract Core Features (Higher Risk) - REMAINING
These need careful planning:

| Section | Lines | Target File | Priority |
|---------|-------|-------------|----------|
| Agent Configuration | - | `core/agents.py` | P3 |
| Open World Game Systems | - | `core/game_systems.py` | P3 |
| API Routes | - | Already in routes/ | - |

### Phase 4: Model Extraction ✅ COMPLETED (March 2026)
All 61 Pydantic models have been extracted to `/app/backend/models/`:

| Model File | Models | Status |
|------------|--------|--------|
| `models/base.py` | Agent, Project, Task, Message, ProjectFile, GeneratedImage, ProjectPlan, AgentMemory, CustomQuickAction | ✅ |
| `models/project.py` | ProjectCreate, ChatRequest, ImageGenRequest, FileCreate, FileUpdate, TaskCreate, PlanApproval, GitHubPushRequest, AgentChainRequest, RefactorRequest, ProjectDuplicateRequest, CustomActionCreate, MemoryCreate, QuickActionRequest | ✅ |
| `models/build.py` | SimulationRequest, SimulationResult, AutonomousBuild, WarRoomMessage, StartBuildRequest, PlayableDemo, BuildWorker, BuildFarmJob, BuildQueueItem, DebugLoop, Checkpoint, IdeaConcept, IdeaBatch, SaaSBlueprint, SystemMap | ✅ |
| `models/collaboration.py` | BlueprintNode, Blueprint, Collaborator, FileLock, CollaborationMessage | ✅ |
| `models/sandbox.py` | NotificationSettings, AudioAsset, Deployment, SandboxSession, SandboxConfig, PipelineAsset, AssetImportRequest | ✅ |
| `models/autopsy.py` | ProjectAutopsy | ✅ |
| `models/agent.py` | DynamicAgent | ✅ |
| `models/v45_features.py` | GoalLoop, KnowledgeEntry, ArchitectureVariant, ArchitectureExploration, RefactorJob, MissionControlEvent, DeploymentPipeline, SystemModule, RealityPipeline | ✅ |

**Import in server.py:**
```python
from models import (
    Agent, Project, Task, Message, ProjectFile, ...  # All 61 models
)
```

## Extraction Template

When extracting a section:

1. **Create new route file** in `/app/backend/routes/`
2. **Import shared dependencies**:
   ```python
   from fastapi import APIRouter, HTTPException
   from core.database import db
   from pydantic import BaseModel
   ```
3. **Create router**:
   ```python
   router = APIRouter(prefix="/feature", tags=["feature"])
   ```
4. **Move endpoint definitions** with `@router` decorator
5. **Register in server.py**:
   ```python
   from routes.feature import router as feature_router
   app.include_router(feature_router, prefix="/api", tags=["feature"])
   ```
6. **Test endpoints** before removing from server.py
7. **Remove old code** from server.py

## Shared Dependencies

These are used across multiple sections and should stay in server.py or move to core/:

- `llm_client` - LLM client for AI calls
- `db` - MongoDB database connection
- `extract_code_blocks()` - Code extraction helper
- `get_or_create_agents()` - Agent management
- Common Pydantic models

## Already Modularized

These routes are already in separate files:
- `routes/pipeline.py` - AI Pipeline
- `routes/god_mode_v2.py` - God Mode V2
- `routes/build_memory.py` - Memory System
- `routes/hardware.py` - Hardware Integration
- `routes/research.py` - Research Mode
- `routes/game_engine.py` - Game Engine
- And 20+ more in `/app/backend/routes/`

## Next Steps

1. ✅ Document refactoring plan (this file)
2. ✅ Extract Settings/Local Bridge section (proof of concept)
3. ✅ Extract God Mode v1
4. ✅ Extract Quick Actions, Custom Actions, Live Preview
5. ✅ Extract Agent Memory, Project Duplication
6. ✅ Extract Build Operations (Refactoring, War Room, Simulation, Demos, Blueprints)
7. ✅ Extract Autonomous Builds
8. ✅ Move models to `/app/backend/models/` (61 models, ~965 lines)
9. ⏳ Extract remaining helper functions and constants
10. ⏳ Final cleanup and testing

## Risk Mitigation

- **Always test** after each extraction
- **Keep backups** of server.py before major changes
- **Extract one section at a time**
- **Run full test suite** after each extraction
- **Document any shared dependencies** that need to be exposed

## Progress Summary

| Phase | Status | Lines Removed |
|-------|--------|---------------|
| Phase 1: Standalone Features | ✅ Complete | ~300 |
| Phase 2: Coupled Features | ✅ Complete | ~900 |
| Phase 3: Core Features | ⏳ Pending | ~800 |
| Phase 4: Model Extraction | ✅ Complete | ~965 |
| **Total** | **70% Done** | **~2,646** |

**Current server.py size: 5,932 lines (31% reduction from 8,578)**

Target: ~4,000-4,500 lines remaining
