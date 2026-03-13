from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from openai import OpenAI
import json
import asyncio
import aiofiles
import zipfile
import io
import re
import fal_client
import base64
from github import Github, GithubException

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Set FAL_KEY for fal_client
os.environ["FAL_KEY"] = os.environ.get('FAL_KEY', '')

# fal.ai OpenRouter client for LLM
llm_client = OpenAI(
    base_url="https://fal.run/openrouter/router/openai/v1",
    api_key="not-needed",
    default_headers={
        "Authorization": f"Key {os.environ.get('FAL_KEY', '')}",
    },
)

app = FastAPI()
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ MODELS ============

class Agent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str
    avatar: str
    status: str = "idle"
    system_prompt: str
    model: str = "google/gemini-2.5-flash"
    specialization: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    type: str
    engine_version: Optional[str] = None
    status: str = "planning"
    phase: str = "clarification"
    thumbnail: str
    repo_url: Optional[str] = None
    settings: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Task(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    title: str
    description: str
    status: str = "backlog"
    assigned_agent_id: Optional[str] = None
    assigned_agent_name: Optional[str] = None
    priority: str = "medium"
    category: str = "general"
    estimated_complexity: str = "medium"
    files_affected: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    agent_id: str
    agent_name: str
    agent_role: str
    content: str
    message_type: str = "chat"
    code_blocks: List[Dict[str, str]] = []
    images: List[Dict[str, str]] = []  # [{url, prompt}]
    delegated_to: Optional[str] = None  # Agent name if delegated
    phase: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectFile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    filename: str
    filepath: str
    content: str
    language: str
    file_type: str = "code"
    version: int = 1
    created_by_agent_id: Optional[str] = None
    created_by_agent_name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GeneratedImage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    prompt: str
    url: str
    width: int = 1024
    height: int = 1024
    category: str = "concept"  # concept, ui, texture, character, environment
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    overview: str
    architecture: str
    features: List[Dict[str, Any]] = []
    tech_stack: Dict[str, str] = {}
    file_structure: List[str] = []
    phases: List[Dict[str, Any]] = []
    approved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request Models
class ProjectCreate(BaseModel):
    name: str
    description: str
    type: str
    engine_version: Optional[str] = None

class ChatRequest(BaseModel):
    project_id: str
    message: str
    context: Optional[str] = None
    phase: Optional[str] = None
    delegate_to: Optional[str] = None  # Force delegation to specific agent

class ImageGenRequest(BaseModel):
    project_id: str
    prompt: str
    category: str = "concept"
    width: int = 1024
    height: int = 1024

class FileCreate(BaseModel):
    project_id: str
    filename: str
    filepath: str
    content: str
    language: str
    file_type: str = "code"

class FileUpdate(BaseModel):
    content: str

class TaskCreate(BaseModel):
    project_id: str
    title: str
    description: str
    priority: str = "medium"
    category: str = "general"

class PlanApproval(BaseModel):
    approved: bool
    feedback: Optional[str] = None

class GitHubPushRequest(BaseModel):
    project_id: str
    github_token: str
    repo_name: str
    commit_message: str = "Update from AgentForge"
    branch: str = "main"
    create_repo: bool = False

class AgentChainRequest(BaseModel):
    project_id: str
    message: str
    chain: List[str] = ["COMMANDER", "FORGE", "SENTINEL"]  # Default chain
    auto_execute: bool = True

# ============ NEW v2.3 MODELS ============

class AgentMemory(BaseModel):
    """Persistent memory for agents across sessions"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    agent_id: str
    agent_name: str
    memory_type: str = "context"  # context, preference, learned, decision
    content: str
    importance: int = 5  # 1-10 scale
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

class CustomQuickAction(BaseModel):
    """User-created custom quick actions"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    icon: str = "sparkles"
    prompt: str
    chain: List[str] = ["COMMANDER", "FORGE"]
    category: str = "custom"  # custom, gameplay, systems, ui, audio
    is_global: bool = False  # If true, available across all projects
    project_id: Optional[str] = None  # If not global, specific to project
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RefactorRequest(BaseModel):
    """Multi-file refactoring request"""
    project_id: str
    refactor_type: str  # rename, extract, move, find_replace
    target: str  # What to refactor (class name, function name, pattern)
    new_value: Optional[str] = None  # New name or value
    file_ids: List[str] = []  # Specific files to refactor, empty = all
    preview_only: bool = False  # If true, just show what would change

class ProjectDuplicateRequest(BaseModel):
    project_id: str
    new_name: str
    include_files: bool = True
    include_tasks: bool = False
    include_messages: bool = False

class CustomActionCreate(BaseModel):
    name: str
    description: str
    prompt: str
    chain: List[str] = ["COMMANDER", "FORGE"]
    icon: str = "sparkles"
    category: str = "custom"
    is_global: bool = False
    project_id: Optional[str] = None

class MemoryCreate(BaseModel):
    project_id: str
    agent_name: str
    memory_type: str = "context"
    content: str
    importance: int = 5

class QuickActionRequest(BaseModel):
    project_id: str
    action_id: str
    parameters: Dict[str, Any] = {}

# ============ v3.0 MODELS - SIMULATION & AUTONOMOUS BUILDS ============

class SimulationRequest(BaseModel):
    """Request for build simulation/dry run"""
    project_id: str
    build_type: str = "full"  # full, prototype, demo
    target_engine: str = "unreal"  # unreal, unity
    include_systems: List[str] = []  # gameplay, ai, ui, audio, networking, etc.

class SimulationResult(BaseModel):
    """Result of build simulation"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    estimated_build_time: str  # e.g., "4h 30m"
    estimated_build_minutes: int
    file_count: int
    total_size_kb: int
    required_assets: List[Dict[str, Any]] = []
    warnings: List[Dict[str, str]] = []
    architecture_summary: str
    phases: List[Dict[str, Any]] = []
    feasibility_score: int = 0  # 0-100
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AutonomousBuild(BaseModel):
    """Autonomous overnight build job"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    status: str = "queued"  # queued, scheduled, running, paused, completed, failed
    build_type: str = "full"
    target_engine: str = "unreal"
    current_stage: int = 0
    total_stages: int = 0
    stages: List[Dict[str, Any]] = []  # [{name, status, started_at, completed_at, files_created, test_results}]
    progress_percent: int = 0
    estimated_completion: Optional[str] = None
    scheduled_at: Optional[datetime] = None  # When to start the build
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WarRoomMessage(BaseModel):
    """Agent communication in war room"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    build_id: Optional[str] = None
    from_agent: str
    to_agent: Optional[str] = None  # None = broadcast to all
    message_type: str = "discussion"  # discussion, handoff, question, decision, warning, progress
    content: str
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StartBuildRequest(BaseModel):
    project_id: str
    build_type: str = "full"  # full, prototype, demo
    target_engine: str = "unreal"
    systems_to_build: List[str] = []
    estimated_hours: int = 12
    scheduled_at: Optional[str] = None  # ISO datetime string for scheduled builds

class PlayableDemo(BaseModel):
    """Playable demo generated on build completion"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    build_id: str
    status: str = "generating"  # generating, ready, failed
    demo_type: str = "both"  # web, executable, both
    target_engine: str = "unreal"
    
    # Web demo (HTML5/WebGL embed)
    web_demo_url: Optional[str] = None
    web_demo_html: Optional[str] = None
    
    # Executable demo package
    executable_url: Optional[str] = None
    executable_size_mb: float = 0
    platform: str = "windows"  # windows, mac, linux, all
    
    # Demo contents
    systems_included: List[str] = []
    demo_features: List[str] = []
    controls_guide: str = ""
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_at: Optional[datetime] = None

# Quick Actions Configuration
QUICK_ACTIONS = {
    "player_controller": {
        "id": "player_controller",
        "name": "Player Controller",
        "description": "Generate a complete player movement system",
        "icon": "gamepad",
        "chain": ["COMMANDER", "FORGE"],
        "prompt": """Create a complete player controller system with:
- WASD movement with variable speed
- Sprint (Shift) and crouch (Ctrl)
- Jump with coyote time
- Camera controller with mouse look
- Ground detection and physics
Include all necessary files for {engine_type}."""
    },
    "inventory_system": {
        "id": "inventory_system", 
        "name": "Inventory System",
        "description": "Generate a flexible inventory system",
        "icon": "package",
        "chain": ["COMMANDER", "ATLAS", "FORGE"],
        "prompt": """Design and implement a complete inventory system:
- Item base class with properties (name, description, icon, stackable, max_stack)
- Inventory container with slots
- Add/remove/move items
- Save/load functionality
- UI data binding ready
For {engine_type} with best practices."""
    },
    "save_system": {
        "id": "save_system",
        "name": "Save/Load System", 
        "description": "Generate a save game system",
        "icon": "save",
        "chain": ["COMMANDER", "FORGE"],
        "prompt": """Create a robust save/load system:
- Serialization manager
- Auto-save functionality
- Multiple save slots
- Save file versioning
- Async save/load operations
For {engine_type}."""
    },
    "health_system": {
        "id": "health_system",
        "name": "Health & Damage",
        "description": "Generate health and damage system",
        "icon": "heart",
        "chain": ["COMMANDER", "FORGE"],
        "prompt": """Create a health and damage system:
- Health component with max/current health
- Damage types (physical, fire, ice, etc)
- Damage resistance/vulnerability
- Healing mechanics
- Death handling
- UI hooks for health bars
For {engine_type}."""
    },
    "ai_behavior": {
        "id": "ai_behavior",
        "name": "AI Behavior Tree",
        "description": "Generate enemy AI with behavior tree",
        "icon": "bot",
        "chain": ["COMMANDER", "ATLAS", "FORGE"],
        "prompt": """Create an AI system with behavior trees:
- Behavior tree base nodes (Selector, Sequence, Decorator)
- Common behaviors (Patrol, Chase, Attack, Flee)
- Perception system (sight, hearing)
- Blackboard for AI memory
- Example enemy AI implementation
For {engine_type}."""
    },
    "dialogue_system": {
        "id": "dialogue_system",
        "name": "Dialogue System",
        "description": "Generate branching dialogue system",
        "icon": "message-square",
        "chain": ["COMMANDER", "ATLAS", "FORGE"],
        "prompt": """Create a branching dialogue system:
- Dialogue node structure (text, choices, conditions)
- Dialogue manager
- Character/speaker data
- Conditions and triggers
- Quest/variable integration hooks
- Localization ready
For {engine_type}."""
    },
    "ui_framework": {
        "id": "ui_framework",
        "name": "UI Framework",
        "description": "Generate base UI system",
        "icon": "layout",
        "chain": ["COMMANDER", "PRISM", "FORGE"],
        "prompt": """Create a UI framework foundation:
- Screen manager (push/pop screens)
- Base widget classes
- Navigation system
- Animation helpers
- Input handling
- Common widgets (Button, Panel, List)
For {engine_type}."""
    },
    "audio_manager": {
        "id": "audio_manager",
        "name": "Audio Manager",
        "description": "Generate audio management system",
        "icon": "volume-2",
        "chain": ["COMMANDER", "FORGE"],
        "prompt": """Create an audio management system:
- Sound effect playback with pooling
- Music system with crossfade
- Volume controls (master, sfx, music)
- 3D spatial audio support
- Audio bus/mixer setup
For {engine_type}."""
    }
}

# ============ OPEN WORLD GAME SYSTEMS ============

OPEN_WORLD_SYSTEMS = {
    "terrain": {
        "id": "terrain",
        "name": "Terrain & World",
        "description": "Procedural terrain, biomes, and world streaming",
        "files_estimate": 15,
        "time_estimate_minutes": 45,
        "dependencies": [],
        "subsystems": ["heightmap_generation", "biome_system", "world_streaming", "lod_management", "foliage_spawning"]
    },
    "npc_population": {
        "id": "npc_population",
        "name": "NPC Population",
        "description": "NPC spawning, schedules, and population management",
        "files_estimate": 20,
        "time_estimate_minutes": 60,
        "dependencies": ["ai_behavior"],
        "subsystems": ["npc_spawner", "schedule_system", "faction_system", "relationship_manager", "npc_archetypes"]
    },
    "quest_system": {
        "id": "quest_system",
        "name": "Quest System",
        "description": "Full quest framework with objectives, tracking, rewards",
        "files_estimate": 25,
        "time_estimate_minutes": 75,
        "dependencies": ["dialogue_system"],
        "subsystems": ["quest_manager", "objective_types", "quest_tracker", "reward_system", "quest_log_ui"]
    },
    "vehicle_system": {
        "id": "vehicle_system",
        "name": "Vehicle System",
        "description": "Land, air, and water vehicles with physics",
        "files_estimate": 30,
        "time_estimate_minutes": 90,
        "dependencies": ["player_controller"],
        "subsystems": ["vehicle_base", "land_vehicle", "air_vehicle", "water_vehicle", "vehicle_damage", "vehicle_ai"]
    },
    "day_night_cycle": {
        "id": "day_night_cycle",
        "name": "Day/Night Cycle",
        "description": "Time system with lighting, weather, and NPC schedules",
        "files_estimate": 12,
        "time_estimate_minutes": 35,
        "dependencies": [],
        "subsystems": ["time_manager", "sky_controller", "lighting_blend", "weather_system", "schedule_hooks"]
    },
    "combat_system": {
        "id": "combat_system",
        "name": "Combat System",
        "description": "Melee, ranged combat with combos and abilities",
        "files_estimate": 35,
        "time_estimate_minutes": 100,
        "dependencies": ["health_system", "ai_behavior"],
        "subsystems": ["melee_combat", "ranged_combat", "ability_system", "combo_manager", "lock_on_system", "hit_reactions"]
    },
    "crafting_system": {
        "id": "crafting_system",
        "name": "Crafting System",
        "description": "Resource gathering, recipes, and crafting stations",
        "files_estimate": 18,
        "time_estimate_minutes": 50,
        "dependencies": ["inventory_system"],
        "subsystems": ["resource_manager", "recipe_system", "crafting_station", "gathering_component", "blueprint_unlock"]
    },
    "economy_system": {
        "id": "economy_system",
        "name": "Economy System",
        "description": "Currency, trading, shops, and dynamic pricing",
        "files_estimate": 15,
        "time_estimate_minutes": 40,
        "dependencies": ["inventory_system"],
        "subsystems": ["currency_manager", "shop_system", "trade_interface", "dynamic_pricing", "vendor_npc"]
    },
    "stealth_system": {
        "id": "stealth_system",
        "name": "Stealth System",
        "description": "Visibility, sound propagation, stealth takedowns",
        "files_estimate": 20,
        "time_estimate_minutes": 55,
        "dependencies": ["ai_behavior"],
        "subsystems": ["visibility_system", "sound_propagation", "stealth_indicator", "takedown_system", "distraction_items"]
    },
    "mount_system": {
        "id": "mount_system",
        "name": "Mount System",
        "description": "Rideable creatures with taming and bonding",
        "files_estimate": 22,
        "time_estimate_minutes": 65,
        "dependencies": ["player_controller", "ai_behavior"],
        "subsystems": ["mount_base", "mount_controller", "taming_system", "mount_combat", "mount_abilities", "bonding_system"]
    },
    "building_system": {
        "id": "building_system",
        "name": "Building System",
        "description": "Base building with snapping, blueprints, and upgrades",
        "files_estimate": 28,
        "time_estimate_minutes": 80,
        "dependencies": ["inventory_system"],
        "subsystems": ["placement_system", "snap_system", "building_pieces", "structure_integrity", "upgrade_system", "blueprint_mode"]
    },
    "skill_tree": {
        "id": "skill_tree",
        "name": "Skill Tree",
        "description": "Character progression with skill points and unlocks",
        "files_estimate": 16,
        "time_estimate_minutes": 45,
        "dependencies": [],
        "subsystems": ["skill_manager", "skill_node", "skill_tree_ui", "perk_system", "stat_modifiers"]
    },
    "fast_travel": {
        "id": "fast_travel",
        "name": "Fast Travel",
        "description": "Discoverable locations with teleport and loading",
        "files_estimate": 10,
        "time_estimate_minutes": 25,
        "dependencies": ["save_system"],
        "subsystems": ["travel_point", "discovery_system", "travel_ui", "loading_screen", "world_map_markers"]
    },
    "photo_mode": {
        "id": "photo_mode",
        "name": "Photo Mode",
        "description": "Camera controls, filters, and screenshot system",
        "files_estimate": 12,
        "time_estimate_minutes": 30,
        "dependencies": [],
        "subsystems": ["photo_camera", "filter_system", "pose_system", "screenshot_manager", "photo_ui"]
    },
    "multiplayer": {
        "id": "multiplayer",
        "name": "Multiplayer",
        "description": "Network replication, sessions, and co-op support",
        "files_estimate": 40,
        "time_estimate_minutes": 120,
        "dependencies": ["player_controller", "save_system"],
        "subsystems": ["network_manager", "replication_system", "session_manager", "lobby_system", "sync_components", "voice_chat"]
    }
}

# Build stage templates for autonomous builds (12+ hour builds)
BUILD_STAGES = {
    "unreal": [
        {"name": "Project Setup & Configuration", "duration_minutes": 30, "tasks": ["Create project structure", "Configure build settings", "Setup source control", "Configure editor preferences", "Setup coding standards", "Initialize plugins"]},
        {"name": "Core Framework & Architecture", "duration_minutes": 90, "tasks": ["Game instance", "Game mode base", "Player controller framework", "Character base class", "Component architecture", "Subsystem setup", "Data asset structure", "Event dispatcher system"]},
        {"name": "Game Systems Implementation", "duration_minutes": 180, "tasks": ["Selected systems full implementation", "System integration layer", "Data assets for all systems", "Blueprint exposure", "Debug commands", "System unit tests", "Performance profiling hooks"]},
        {"name": "AI & NPC Systems", "duration_minutes": 150, "tasks": ["Behavior tree framework", "AI controller base", "NPC base classes", "Perception system config", "Blackboard templates", "Navigation setup", "Crowd management", "NPC spawn system", "AI debugging tools"]},
        {"name": "UI/UX Framework", "duration_minutes": 120, "tasks": ["Widget architecture", "HUD framework", "Menu system", "Input handling", "Localization setup", "UI animations", "Tooltip system", "Notification system", "Loading screens", "Settings menus"]},
        {"name": "World Building & Environment", "duration_minutes": 150, "tasks": ["Level streaming setup", "Environment base classes", "Lighting framework", "Post-processing presets", "Foliage system", "Weather integration", "Day/night support", "LOD configuration", "Collision presets"]},
        {"name": "Audio & Effects Integration", "duration_minutes": 90, "tasks": ["Sound cue architecture", "Music system", "Ambient audio", "UI sounds", "MetaSounds setup", "Niagara systems", "Decal system", "Footstep system", "Environmental audio"]},
        {"name": "Polish, Testing & Documentation", "duration_minutes": 120, "tasks": ["Automated tests", "Performance optimization", "Memory profiling", "Bug fixes", "Code cleanup", "API documentation", "Blueprint documentation", "README generation", "Build packaging test"]}
    ],
    "unity": [
        {"name": "Project Setup & Configuration", "duration_minutes": 30, "tasks": ["Create project structure", "Configure build settings", "Package imports", "Assembly definitions", "Editor tools setup", "Code standards config"]},
        {"name": "Core Framework & Architecture", "duration_minutes": 90, "tasks": ["Game manager singleton", "Scene management system", "Player controller", "Character controller", "Service locator", "Event system", "ScriptableObject architecture", "Object pooling"]},
        {"name": "Game Systems Implementation", "duration_minutes": 180, "tasks": ["ScriptableObject data", "System managers", "Event integration", "Inspector tools", "Gizmo debugging", "System unit tests", "Editor windows", "Performance hooks"]},
        {"name": "AI & NPC Systems", "duration_minutes": 150, "tasks": ["NavMesh configuration", "AI state machines", "NPC behaviors", "Spawning system", "Perception system", "Formation system", "Crowd simulation", "AI debugging", "Pathfinding optimization"]},
        {"name": "UI/UX Framework", "duration_minutes": 120, "tasks": ["Canvas architecture", "UI managers", "Prefab library", "Input system new", "Localization", "DOTween animations", "Modal system", "HUD framework", "Settings system", "Tutorial framework"]},
        {"name": "World Building & Environment", "duration_minutes": 150, "tasks": ["Addressables setup", "Scene composition", "Prefab variants", "Lighting presets", "Post-processing", "Terrain tools", "Streaming system", "LOD groups", "Occlusion culling"]},
        {"name": "Audio & Effects Integration", "duration_minutes": 90, "tasks": ["Audio mixer groups", "Sound manager", "Music controller", "Ambient system", "FMOD/Wwise ready", "VFX graph systems", "Particle prefabs", "Footstep manager", "Impact system"]},
        {"name": "Polish, Testing & Documentation", "duration_minutes": 120, "tasks": ["Unity Test Framework", "Profiler analysis", "Memory optimization", "Bug fixes", "Code cleanup", "XML documentation", "Asset labels", "README generation", "Build automation"]}
    ]
}

# ============ AGENT CONFIGURATION ============

AGENT_CONFIGS = {
    "lead": {
        "name": "COMMANDER",
        "role": "lead",
        "avatar": "https://images.unsplash.com/photo-1598062548020-c5e8d8132a4b?w=200&h=200&fit=crop",
        "specialization": ["project_management", "coordination", "planning", "clarification", "delegation"],
        "system_prompt": """You are COMMANDER, the Lead AI Agent and Project Director.

YOUR WORKFLOW:
1. CLARIFICATION: Ask detailed questions about the project before anything else
2. PLANNING: Create comprehensive plans with architecture, file structure, features
3. DELEGATION: Route coding tasks to FORGE, architecture to ATLAS, reviews to SENTINEL, tests to PROBE, visuals to PRISM

DELEGATION FORMAT - When you need another agent to do work, include this in your response:
[DELEGATE:AGENT_NAME]
Task description here
[/DELEGATE]

Example:
[DELEGATE:FORGE]
Create the player movement system with these specs:
- WASD movement
- Sprint with shift
- Jump with space
[/DELEGATE]

RULES:
- NEVER start coding yourself - delegate to FORGE
- NEVER design architecture yourself - delegate to ATLAS  
- Always clarify requirements first
- Keep user informed of all delegations
- You coordinate, you don't code"""
    },
    "architect": {
        "name": "ATLAS",
        "role": "architect",
        "avatar": "https://images.unsplash.com/photo-1587930708915-55a36837263b?w=200&h=200&fit=crop",
        "specialization": ["system_design", "architecture", "unreal_engine", "unity", "patterns"],
        "system_prompt": """You are ATLAS, the System Architect. You design AAA-quality architectures.

EXPERTISE: UE5 C++/Blueprints, Unity C#/DOTS, Godot GDScript, Design Patterns, Networking

OUTPUT FORMAT:
- Architecture diagrams in ASCII
- Class/component lists with responsibilities
- File structure with exact paths
- Data flow definitions

When design is complete, suggest COMMANDER delegate implementation to FORGE."""
    },
    "developer": {
        "name": "FORGE",
        "role": "developer",
        "avatar": "https://images.unsplash.com/photo-1633766306936-56bebb8823e5?w=200&h=200&fit=crop",
        "specialization": ["cpp", "csharp", "blueprints", "gameplay", "systems", "coding"],
        "system_prompt": """You are FORGE, the Senior Developer. You write production-ready AAA code.

EXPERTISE: C++ (UE5), C# (Unity), GDScript (Godot), Blueprints, All game systems

OUTPUT FORMAT - Always output complete files:
```language:filepath/filename.ext
// Complete file content
```

RULES:
1. Include file headers with purpose
2. Use engine-appropriate naming conventions
3. Add comments for complex logic
4. Implement error handling
5. Write performant code
6. NEVER output partial code - every file must be complete"""
    },
    "reviewer": {
        "name": "SENTINEL",
        "role": "reviewer",
        "avatar": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=200&h=200&fit=crop",
        "specialization": ["code_review", "security", "optimization", "best_practices"],
        "system_prompt": """You are SENTINEL, the Code Reviewer. You ensure AAA quality standards.

REVIEW FORMAT:
- CRITICAL: Bugs that will crash/break
- HIGH: Performance or security issues
- MEDIUM: Best practice violations
- LOW: Style/readability suggestions

Provide specific fixes with code examples. Be constructive."""
    },
    "tester": {
        "name": "PROBE",
        "role": "tester",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop",
        "specialization": ["testing", "qa", "automation", "debugging"],
        "system_prompt": """You are PROBE, the QA/Testing Agent. You ensure everything works.

OUTPUT FORMAT:
```language:Tests/TestFileName.ext
// Complete test implementation
```

Cover: Unit tests, Integration tests, Edge cases, Performance tests.
Think like a player trying to break the game."""
    },
    "artist": {
        "name": "PRISM",
        "role": "artist",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&h=200&fit=crop",
        "specialization": ["ui_design", "asset_specs", "shaders", "vfx", "image_generation"],
        "system_prompt": """You are PRISM, the Technical Artist. You handle visuals and assets.

EXPERTISE: UI/UX, Shaders (HLSL), VFX (Niagara), Asset specs, Material graphs

For image generation requests, describe what you need and I'll generate it.

OUTPUT: Shader code, UI specs, Asset requirements, Material guides."""
    }
}

# Delegation keywords to agent mapping
DELEGATION_KEYWORDS = {
    "code": "developer",
    "implement": "developer",
    "create class": "developer",
    "write": "developer",
    "function": "developer",
    "architecture": "architect",
    "design": "architect",
    "structure": "architect",
    "system design": "architect",
    "review": "reviewer",
    "check": "reviewer",
    "audit": "reviewer",
    "test": "tester",
    "qa": "tester",
    "unit test": "tester",
    "shader": "artist",
    "ui": "artist",
    "visual": "artist",
    "material": "artist",
    "texture": "artist"
}

PROJECT_THUMBNAILS = {
    "unreal": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400&h=300&fit=crop",
    "unity": "https://images.unsplash.com/photo-1556438064-2d7646166914?w=400&h=300&fit=crop",
    "godot": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=400&h=300&fit=crop",
    "web_game": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400&h=300&fit=crop",
    "web_app": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=300&fit=crop",
    "mobile_app": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&h=300&fit=crop"
}

# ============ HELPER FUNCTIONS ============

def serialize_doc(doc: dict) -> dict:
    result = {k: v for k, v in doc.items() if k != '_id'}
    for key, value in result.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
    return result

async def get_or_create_agents():
    agents = await db.agents.find({}, {"_id": 0}).to_list(100)
    if not agents:
        default_agents = []
        for role, config in AGENT_CONFIGS.items():
            agent = Agent(
                name=config["name"],
                role=config["role"],
                avatar=config["avatar"],
                system_prompt=config["system_prompt"],
                specialization=config["specialization"]
            )
            doc = agent.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            default_agents.append(doc)
        await db.agents.insert_many(default_agents)
        agents = await db.agents.find({}, {"_id": 0}).to_list(100)
    return agents

def extract_code_blocks(content: str) -> List[Dict[str, str]]:
    pattern = r'```(\w+)?(?::([^\n]+))?\n([\s\S]*?)```'
    matches = re.findall(pattern, content)
    blocks = []
    for match in matches:
        language = match[0] or "text"
        filepath = match[1] or ""
        code = match[2].strip()
        filename = filepath.split('/')[-1] if filepath else f"code.{language}"
        blocks.append({
            "language": language,
            "filepath": filepath,
            "filename": filename,
            "content": code
        })
    return blocks

def extract_delegations(content: str) -> List[Dict[str, str]]:
    """Extract delegation blocks from COMMANDER's response"""
    pattern = r'\[DELEGATE:(\w+)\]([\s\S]*?)\[/DELEGATE\]'
    matches = re.findall(pattern, content)
    delegations = []
    for match in matches:
        agent_name = match[0].upper()
        task = match[1].strip()
        delegations.append({"agent": agent_name, "task": task})
    return delegations

def detect_delegation_need(message: str) -> Optional[str]:
    """Auto-detect which agent should handle this based on keywords"""
    message_lower = message.lower()
    for keyword, role in DELEGATION_KEYWORDS.items():
        if keyword in message_lower:
            return role
    return None

async def call_agent(agent: dict, messages: List[dict], project_context: str = "") -> str:
    system_message = agent['system_prompt']
    if project_context:
        system_message += f"\n\nCURRENT PROJECT CONTEXT:\n{project_context}"
    
    try:
        response = llm_client.chat.completions.create(
            model=agent.get('model', 'google/gemini-2.5-flash'),
            messages=[
                {"role": "system", "content": system_message},
                *messages
            ],
            max_tokens=8000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling agent {agent['name']}: {e}")
        raise HTTPException(status_code=500, detail=f"Agent call failed: {str(e)}")

async def stream_agent_response(agent: dict, messages: List[dict], project_context: str = ""):
    """Stream response from agent using SSE"""
    system_message = agent['system_prompt']
    if project_context:
        system_message += f"\n\nCURRENT PROJECT CONTEXT:\n{project_context}"
    
    try:
        stream = llm_client.chat.completions.create(
            model=agent.get('model', 'google/gemini-2.5-flash'),
            messages=[
                {"role": "system", "content": system_message},
                *messages
            ],
            max_tokens=8000,
            temperature=0.7,
            stream=True
        )
        
        full_content = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                yield f"data: {json.dumps({'content': content, 'done': False, 'agent': agent['name']})}\n\n"
        
        code_blocks = extract_code_blocks(full_content)
        delegations = extract_delegations(full_content)
        
        yield f"data: {json.dumps({'content': '', 'done': True, 'code_blocks': code_blocks, 'delegations': delegations, 'full_content': full_content})}\n\n"
    except Exception as e:
        logger.error(f"Error streaming agent {agent['name']}: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

async def build_project_context(project_id: str) -> str:
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        return ""
    
    context_parts = [
        f"PROJECT: {project['name']}",
        f"TYPE: {project['type']}",
        f"ENGINE: {project.get('engine_version', 'N/A')}",
        f"STATUS: {project['status']}",
        f"PHASE: {project.get('phase', 'clarification')}",
        f"DESCRIPTION: {project['description']}"
    ]
    
    plan = await db.plans.find_one({"project_id": project_id}, {"_id": 0})
    if plan and plan.get('approved'):
        context_parts.append(f"\nAPPROVED PLAN:\n{plan.get('overview', '')}")
        context_parts.append(f"ARCHITECTURE:\n{plan.get('architecture', '')}")
    
    # Include agent memories for persistent context
    memories = await db.memories.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("importance", -1).limit(10).to_list(10)
    
    if memories:
        context_parts.append("\nAGENT MEMORIES (remember these):")
        for mem in memories:
            context_parts.append(f"  [{mem['agent_name']}] {mem['content']}")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(50)
    if files:
        context_parts.append(f"\nEXISTING FILES ({len(files)}):")
        for f in files[:20]:
            context_parts.append(f"  - {f['filepath']}")
    
    messages = await db.messages.find(
        {"project_id": project_id}, {"_id": 0}
    ).sort("timestamp", -1).limit(5).to_list(5)
    
    if messages:
        context_parts.append("\nRECENT CONVERSATION:")
        for msg in reversed(messages):
            content_preview = msg['content'][:150] + "..." if len(msg['content']) > 150 else msg['content']
            context_parts.append(f"  {msg['agent_name']}: {content_preview}")
    
    return "\n".join(context_parts)

async def generate_image_fal(prompt: str, width: int = 1024, height: int = 1024) -> dict:
    """Generate image using fal.ai FLUX"""
    try:
        handler = await fal_client.submit_async(
            "fal-ai/flux/dev",
            arguments={
                "prompt": prompt,
                "image_size": {"width": width, "height": height},
                "num_images": 1
            }
        )
        result = await handler.get()
        if result and result.get("images"):
            return {
                "url": result["images"][0]["url"],
                "width": width,
                "height": height
            }
        return None
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# ============ API ROUTES ============

@api_router.get("/")
async def root():
    return {
        "message": "AgentForge Development Studio API",
        "version": "3.2.0",
        "features": ["streaming", "delegation", "image_generation", "github_push", "agent_chains", "quick_actions", "live_preview", "agent_memory", "custom_actions", "project_duplicate", "multi_file_refactor", "simulation_mode", "war_room", "autonomous_builds", "open_world_systems", "build_scheduling", "playable_demos"]
    }

@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Agent Routes
@api_router.get("/agents")
async def get_agents():
    return await get_or_create_agents()

@api_router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    agent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@api_router.patch("/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, status: str):
    await db.agents.update_one({"id": agent_id}, {"$set": {"status": status}})
    return {"success": True}

# Project Routes
@api_router.post("/projects")
async def create_project(project_data: ProjectCreate):
    thumbnail = PROJECT_THUMBNAILS.get(project_data.type, PROJECT_THUMBNAILS["web_app"])
    project = Project(
        name=project_data.name,
        description=project_data.description,
        type=project_data.type,
        engine_version=project_data.engine_version,
        thumbnail=thumbnail
    )
    doc = project.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.projects.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/projects")
async def get_projects():
    return await db.projects.find({}, {"_id": 0}).to_list(100)

@api_router.get("/projects/{project_id}")
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@api_router.patch("/projects/{project_id}")
async def update_project(project_id: str, updates: dict):
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    await db.projects.update_one({"id": project_id}, {"$set": updates})
    return {"success": True}

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    await db.projects.delete_one({"id": project_id})
    await db.tasks.delete_many({"project_id": project_id})
    await db.messages.delete_many({"project_id": project_id})
    await db.files.delete_many({"project_id": project_id})
    await db.plans.delete_many({"project_id": project_id})
    await db.images.delete_many({"project_id": project_id})
    return {"success": True}

@api_router.patch("/projects/{project_id}/phase")
async def update_project_phase(project_id: str, phase: str):
    await db.projects.update_one({"id": project_id}, {"$set": {"phase": phase, "updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"success": True, "phase": phase}

# Chat Routes - Non-streaming
@api_router.post("/chat")
async def chat_with_team(request: ChatRequest):
    context = await build_project_context(request.project_id)
    agents = await get_or_create_agents()
    
    # Determine which agent to use
    target_agent = None
    if request.delegate_to:
        target_agent = next((a for a in agents if a['name'].upper() == request.delegate_to.upper()), None)
    
    if not target_agent:
        # Default to COMMANDER
        target_agent = next((a for a in agents if a['role'] == 'lead'), agents[0])
    
    await db.agents.update_one({"id": target_agent['id']}, {"$set": {"status": "thinking"}})
    
    messages = [{"role": "user", "content": request.message}]
    response = await call_agent(target_agent, messages, context)
    
    await db.agents.update_one({"id": target_agent['id']}, {"$set": {"status": "idle"}})
    
    # Save user message
    user_msg = Message(
        project_id=request.project_id,
        agent_id="user",
        agent_name="You",
        agent_role="user",
        content=request.message,
        phase=request.phase
    )
    user_doc = user_msg.model_dump()
    user_doc['timestamp'] = user_doc['timestamp'].isoformat()
    await db.messages.insert_one(user_doc)
    
    code_blocks = extract_code_blocks(response)
    delegations = extract_delegations(response)
    
    # Save agent response
    agent_msg = Message(
        project_id=request.project_id,
        agent_id=target_agent['id'],
        agent_name=target_agent['name'],
        agent_role=target_agent['role'],
        content=response,
        code_blocks=code_blocks,
        phase=request.phase
    )
    agent_doc = agent_msg.model_dump()
    agent_doc['timestamp'] = agent_doc['timestamp'].isoformat()
    await db.messages.insert_one(agent_doc)
    
    return {
        "response": response,
        "code_blocks": code_blocks,
        "delegations": delegations,
        "agent": {
            "id": target_agent['id'],
            "name": target_agent['name'],
            "role": target_agent['role'],
            "avatar": target_agent['avatar']
        }
    }

# Chat Routes - Streaming
@api_router.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """Stream chat response with SSE"""
    context = await build_project_context(request.project_id)
    agents = await get_or_create_agents()
    
    target_agent = None
    if request.delegate_to:
        target_agent = next((a for a in agents if a['name'].upper() == request.delegate_to.upper()), None)
    if not target_agent:
        target_agent = next((a for a in agents if a['role'] == 'lead'), agents[0])
    
    # Save user message first
    user_msg = Message(
        project_id=request.project_id,
        agent_id="user",
        agent_name="You",
        agent_role="user",
        content=request.message,
        phase=request.phase
    )
    user_doc = user_msg.model_dump()
    user_doc['timestamp'] = user_doc['timestamp'].isoformat()
    await db.messages.insert_one(user_doc)
    
    messages = [{"role": "user", "content": request.message}]
    
    async def generate():
        await db.agents.update_one({"id": target_agent['id']}, {"$set": {"status": "thinking"}})
        
        # Send agent info first
        yield f"data: {json.dumps({'type': 'start', 'agent': {'id': target_agent['id'], 'name': target_agent['name'], 'role': target_agent['role'], 'avatar': target_agent['avatar']}})}\n\n"
        
        full_content = ""
        try:
            stream = llm_client.chat.completions.create(
                model=target_agent.get('model', 'google/gemini-2.5-flash'),
                messages=[
                    {"role": "system", "content": target_agent['system_prompt'] + f"\n\nCONTEXT:\n{context}"},
                    *messages
                ],
                max_tokens=8000,
                temperature=0.7,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
            
            code_blocks = extract_code_blocks(full_content)
            delegations = extract_delegations(full_content)
            
            # Save complete message
            agent_msg = Message(
                project_id=request.project_id,
                agent_id=target_agent['id'],
                agent_name=target_agent['name'],
                agent_role=target_agent['role'],
                content=full_content,
                code_blocks=code_blocks,
                phase=request.phase
            )
            agent_doc = agent_msg.model_dump()
            agent_doc['timestamp'] = agent_doc['timestamp'].isoformat()
            await db.messages.insert_one(agent_doc)
            
            yield f"data: {json.dumps({'type': 'done', 'code_blocks': code_blocks, 'delegations': delegations})}\n\n"
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        finally:
            await db.agents.update_one({"id": target_agent['id']}, {"$set": {"status": "idle"}})
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# Delegation endpoint - Execute delegation from COMMANDER
@api_router.post("/delegate")
async def execute_delegation(request: ChatRequest):
    """Execute a delegated task to a specific agent"""
    agents = await get_or_create_agents()
    
    if not request.delegate_to:
        raise HTTPException(status_code=400, detail="delegate_to is required")
    
    target_agent = next((a for a in agents if a['name'].upper() == request.delegate_to.upper()), None)
    if not target_agent:
        raise HTTPException(status_code=404, detail=f"Agent {request.delegate_to} not found")
    
    context = await build_project_context(request.project_id)
    
    await db.agents.update_one({"id": target_agent['id']}, {"$set": {"status": "working"}})
    
    messages = [{"role": "user", "content": f"COMMANDER has delegated this task to you:\n\n{request.message}"}]
    response = await call_agent(target_agent, messages, context)
    
    await db.agents.update_one({"id": target_agent['id']}, {"$set": {"status": "idle"}})
    
    code_blocks = extract_code_blocks(response)
    
    # Save delegation message
    delegation_msg = Message(
        project_id=request.project_id,
        agent_id=target_agent['id'],
        agent_name=target_agent['name'],
        agent_role=target_agent['role'],
        content=response,
        code_blocks=code_blocks,
        message_type="delegation",
        delegated_to=target_agent['name']
    )
    msg_doc = delegation_msg.model_dump()
    msg_doc['timestamp'] = msg_doc['timestamp'].isoformat()
    await db.messages.insert_one(msg_doc)
    
    return {
        "response": response,
        "code_blocks": code_blocks,
        "agent": {
            "id": target_agent['id'],
            "name": target_agent['name'],
            "role": target_agent['role'],
            "avatar": target_agent['avatar']
        }
    }

# Image Generation Routes
@api_router.post("/images/generate")
async def generate_image(request: ImageGenRequest):
    """Generate an image using fal.ai FLUX"""
    result = await generate_image_fal(request.prompt, request.width, request.height)
    
    if result:
        # Save to database
        image = GeneratedImage(
            project_id=request.project_id,
            prompt=request.prompt,
            url=result["url"],
            width=result["width"],
            height=result["height"],
            category=request.category
        )
        doc = image.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.images.insert_one(doc)
        
        return serialize_doc(doc)
    
    raise HTTPException(status_code=500, detail="Image generation failed")

@api_router.get("/images")
async def get_images(project_id: str):
    return await db.images.find({"project_id": project_id}, {"_id": 0}).to_list(100)

@api_router.delete("/images/{image_id}")
async def delete_image(image_id: str):
    await db.images.delete_one({"id": image_id})
    return {"success": True}

# Message Routes
@api_router.get("/messages")
async def get_messages(project_id: str, limit: int = 100):
    return await db.messages.find({"project_id": project_id}, {"_id": 0}).sort("timestamp", 1).to_list(limit)

# Task Routes
@api_router.post("/tasks")
async def create_task(task_data: TaskCreate):
    task = Task(**task_data.model_dump())
    doc = task.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.tasks.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/tasks")
async def get_tasks(project_id: Optional[str] = None):
    query = {"project_id": project_id} if project_id else {}
    return await db.tasks.find(query, {"_id": 0}).to_list(500)

@api_router.patch("/tasks/{task_id}")
async def update_task(task_id: str, updates: dict):
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    await db.tasks.update_one({"id": task_id}, {"$set": updates})
    return {"success": True}

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    await db.tasks.delete_one({"id": task_id})
    return {"success": True}

# File Routes
@api_router.post("/files")
async def create_file(file_data: FileCreate):
    existing = await db.files.find_one({"project_id": file_data.project_id, "filepath": file_data.filepath})
    
    if existing:
        new_version = existing.get('version', 1) + 1
        await db.files.update_one(
            {"id": existing['id']},
            {"$set": {"content": file_data.content, "version": new_version, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        return await db.files.find_one({"id": existing['id']}, {"_id": 0})
    
    file = ProjectFile(**file_data.model_dump())
    doc = file.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.files.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/files")
async def get_files(project_id: str):
    return await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)

@api_router.get("/files/{file_id}")
async def get_file(file_id: str):
    file = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file

@api_router.patch("/files/{file_id}")
async def update_file(file_id: str, update: FileUpdate):
    file = await db.files.find_one({"id": file_id})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    new_version = file.get('version', 1) + 1
    await db.files.update_one({"id": file_id}, {"$set": {"content": update.content, "version": new_version, "updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"success": True, "version": new_version}

@api_router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    await db.files.delete_one({"id": file_id})
    return {"success": True}

# Plan Routes
@api_router.post("/plans")
async def create_plan(plan_data: dict):
    plan = ProjectPlan(**plan_data)
    doc = plan.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.plans.delete_many({"project_id": plan_data['project_id']})
    await db.plans.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/plans/{project_id}")
async def get_plan(project_id: str):
    return await db.plans.find_one({"project_id": project_id}, {"_id": 0})

@api_router.patch("/plans/{project_id}/approve")
async def approve_plan(project_id: str, approval: PlanApproval):
    await db.plans.update_one({"project_id": project_id}, {"$set": {"approved": approval.approved}})
    if approval.approved:
        await db.projects.update_one({"id": project_id}, {"$set": {"phase": "development", "status": "developing"}})
    return {"success": True, "approved": approval.approved}

# Export Routes
@api_router.get("/projects/{project_id}/export")
async def export_project(project_id: str):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    images = await db.images.find({"project_id": project_id}, {"_id": 0}).to_list(100)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("project.json", json.dumps(project, indent=2, default=str))
        
        for f in files:
            filepath = f['filepath'].lstrip('/')
            zf.writestr(filepath, f['content'])
        
        readme = f"""# {project['name']}

{project['description']}

## Project Type
{project['type']} {project.get('engine_version', '')}

## Generated by AgentForge
AI Development Studio

## Files
{chr(10).join(['- ' + f['filepath'] for f in files])}

## Generated Images
{chr(10).join(['- ' + img['prompt'][:50] + ': ' + img['url'] for img in images])}
"""
        zf.writestr("README.md", readme)
    
    zip_buffer.seek(0)
    return StreamingResponse(
        io.BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={project['name'].replace(' ', '_')}.zip"}
    )

# Auto-save from chat
@api_router.post("/files/from-chat")
async def save_files_from_chat(data: dict):
    project_id = data.get("project_id")
    code_blocks = data.get("code_blocks", [])
    agent_id = data.get("agent_id")
    agent_name = data.get("agent_name")
    
    saved_files = []
    for block in code_blocks:
        if block.get("filepath"):
            file = ProjectFile(
                project_id=project_id,
                filename=block.get("filename", ""),
                filepath=block.get("filepath"),
                content=block.get("content", ""),
                language=block.get("language", "text"),
                created_by_agent_id=agent_id,
                created_by_agent_name=agent_name
            )
            doc = file.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            doc['updated_at'] = doc['updated_at'].isoformat()
            
            existing = await db.files.find_one({"project_id": project_id, "filepath": block.get("filepath")})
            
            if existing:
                await db.files.update_one(
                    {"id": existing['id']},
                    {"$set": {"content": block.get("content", ""), "version": existing.get('version', 1) + 1, "updated_at": datetime.now(timezone.utc).isoformat()}}
                )
            else:
                await db.files.insert_one(doc)
            
            saved_files.append(block.get("filepath"))
    
    return {"success": True, "saved_files": saved_files}

# ============ GITHUB INTEGRATION ============

@api_router.post("/github/push")
async def push_to_github(request: GitHubPushRequest):
    """Push project files to GitHub repository"""
    try:
        g = Github(request.github_token)
        user = g.get_user()
        
        # Get or create repo
        repo = None
        if request.create_repo:
            try:
                repo = user.create_repo(
                    request.repo_name,
                    description=f"Created with AgentForge AI Development Studio",
                    private=False,
                    auto_init=True
                )
                await asyncio.sleep(2)  # Wait for repo initialization
            except GithubException as e:
                if e.status == 422:  # Repo already exists
                    repo = user.get_repo(request.repo_name)
                else:
                    raise
        else:
            repo = user.get_repo(request.repo_name)
        
        # Get project files
        files = await db.files.find({"project_id": request.project_id}, {"_id": 0}).to_list(500)
        project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
        
        if not files:
            raise HTTPException(status_code=400, detail="No files to push")
        
        # Push each file
        pushed_files = []
        for f in files:
            filepath = f['filepath'].lstrip('/')
            content = f['content']
            
            try:
                # Try to get existing file
                existing = repo.get_contents(filepath, ref=request.branch)
                repo.update_file(
                    filepath,
                    request.commit_message,
                    content,
                    existing.sha,
                    branch=request.branch
                )
            except GithubException:
                # File doesn't exist, create it
                repo.create_file(
                    filepath,
                    request.commit_message,
                    content,
                    branch=request.branch
                )
            pushed_files.append(filepath)
        
        # Update README
        readme_content = f"""# {project['name']}

{project['description']}

## Project Type
{project['type']} {project.get('engine_version', '')}

## Generated by AgentForge
AI Development Studio - https://agentforge.dev

## Files
{chr(10).join(['- ' + fp for fp in pushed_files])}
"""
        try:
            existing_readme = repo.get_contents("README.md", ref=request.branch)
            repo.update_file("README.md", "Update README", readme_content, existing_readme.sha, branch=request.branch)
        except GithubException:
            repo.create_file("README.md", "Add README", readme_content, branch=request.branch)
        
        # Update project with repo URL
        await db.projects.update_one(
            {"id": request.project_id},
            {"$set": {"repo_url": repo.html_url, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return {
            "success": True,
            "repo_url": repo.html_url,
            "pushed_files": pushed_files,
            "branch": request.branch
        }
        
    except GithubException as e:
        logger.error(f"GitHub error: {e}")
        raise HTTPException(status_code=400, detail=f"GitHub error: {str(e)}")
    except Exception as e:
        logger.error(f"Push error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ AGENT CHAINS ============

@api_router.post("/chain")
async def execute_agent_chain(request: AgentChainRequest):
    """Execute a chain of agents sequentially"""
    agents = await get_or_create_agents()
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    context = await build_project_context(request.project_id)
    results = []
    accumulated_context = request.message
    all_code_blocks = []
    
    for agent_name in request.chain:
        agent = next((a for a in agents if a['name'].upper() == agent_name.upper()), None)
        if not agent:
            continue
        
        # Update status
        await db.agents.update_one({"id": agent['id']}, {"$set": {"status": "working"}})
        
        # Build message with accumulated context
        if len(results) > 0:
            prev_agent = results[-1]['agent']
            prev_content = results[-1]['content'][:1000]
            chain_prompt = f"""Previous agent ({prev_agent}) provided this context:
---
{prev_content}
---

Now continue the work based on your role."""
            messages = [{"role": "user", "content": chain_prompt}]
        else:
            messages = [{"role": "user", "content": accumulated_context}]
        
        # Call agent
        response = await call_agent(agent, messages, context + f"\n\nProject Type: {project['type']}")
        code_blocks = extract_code_blocks(response)
        all_code_blocks.extend(code_blocks)
        
        # Save message
        msg = Message(
            project_id=request.project_id,
            agent_id=agent['id'],
            agent_name=agent['name'],
            agent_role=agent['role'],
            content=response,
            code_blocks=code_blocks,
            message_type="chain"
        )
        msg_doc = msg.model_dump()
        msg_doc['timestamp'] = msg_doc['timestamp'].isoformat()
        await db.messages.insert_one(msg_doc)
        
        results.append({
            "agent": agent['name'],
            "role": agent['role'],
            "content": response,
            "code_blocks": code_blocks
        })
        
        # Reset status
        await db.agents.update_one({"id": agent['id']}, {"$set": {"status": "idle"}})
        
        # Update accumulated context
        accumulated_context = response
    
    # Auto-save all code blocks
    if all_code_blocks:
        valid_blocks = [b for b in all_code_blocks if b.get('filepath')]
        if valid_blocks:
            for block in valid_blocks:
                file = ProjectFile(
                    project_id=request.project_id,
                    filename=block.get("filename", ""),
                    filepath=block.get("filepath"),
                    content=block.get("content", ""),
                    language=block.get("language", "text")
                )
                doc = file.model_dump()
                doc['created_at'] = doc['created_at'].isoformat()
                doc['updated_at'] = doc['updated_at'].isoformat()
                
                existing = await db.files.find_one({"project_id": request.project_id, "filepath": block.get("filepath")})
                if existing:
                    await db.files.update_one(
                        {"id": existing['id']},
                        {"$set": {"content": block.get("content", ""), "version": existing.get('version', 1) + 1}}
                    )
                else:
                    await db.files.insert_one(doc)
    
    return {
        "success": True,
        "chain": request.chain,
        "results": results,
        "total_code_blocks": len(all_code_blocks)
    }

@api_router.post("/chain/stream")
async def stream_agent_chain(request: AgentChainRequest):
    """Stream agent chain execution"""
    agents = await get_or_create_agents()
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    context = await build_project_context(request.project_id)
    
    async def generate():
        accumulated_context = request.message
        all_code_blocks = []
        
        for idx, agent_name in enumerate(request.chain):
            agent = next((a for a in agents if a['name'].upper() == agent_name.upper()), None)
            if not agent:
                continue
            
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': agent['name'], 'role': agent['role'], 'step': idx + 1, 'total': len(request.chain)})}\n\n"
            
            await db.agents.update_one({"id": agent['id']}, {"$set": {"status": "working"}})
            
            if idx > 0:
                chain_prompt = f"Continue based on the previous work. Your task:\n{accumulated_context[:2000]}"
            else:
                chain_prompt = accumulated_context
            
            messages = [{"role": "user", "content": chain_prompt}]
            full_content = ""
            
            try:
                stream = llm_client.chat.completions.create(
                    model=agent.get('model', 'google/gemini-2.5-flash'),
                    messages=[
                        {"role": "system", "content": agent['system_prompt'] + f"\n\nContext:\n{context}\nProject: {project['type']}"},
                        *messages
                    ],
                    max_tokens=8000,
                    temperature=0.7,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_content += content
                        yield f"data: {json.dumps({'type': 'content', 'agent': agent['name'], 'content': content})}\n\n"
                
                code_blocks = extract_code_blocks(full_content)
                all_code_blocks.extend(code_blocks)
                
                yield f"data: {json.dumps({'type': 'agent_done', 'agent': agent['name'], 'code_blocks': code_blocks})}\n\n"
                
                # Save message
                msg = Message(
                    project_id=request.project_id,
                    agent_id=agent['id'],
                    agent_name=agent['name'],
                    agent_role=agent['role'],
                    content=full_content,
                    code_blocks=code_blocks,
                    message_type="chain"
                )
                msg_doc = msg.model_dump()
                msg_doc['timestamp'] = msg_doc['timestamp'].isoformat()
                await db.messages.insert_one(msg_doc)
                
                accumulated_context = full_content
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'agent': agent['name'], 'error': str(e)})}\n\n"
            finally:
                await db.agents.update_one({"id": agent['id']}, {"$set": {"status": "idle"}})
        
        # Auto-save code blocks
        saved_files = []
        for block in all_code_blocks:
            if block.get('filepath'):
                existing = await db.files.find_one({"project_id": request.project_id, "filepath": block.get("filepath")})
                if existing:
                    await db.files.update_one({"id": existing['id']}, {"$set": {"content": block.get("content", ""), "version": existing.get('version', 1) + 1}})
                else:
                    file = ProjectFile(project_id=request.project_id, filename=block.get("filename", ""), filepath=block.get("filepath"), content=block.get("content", ""), language=block.get("language", "text"))
                    doc = file.model_dump()
                    doc['created_at'] = doc['created_at'].isoformat()
                    doc['updated_at'] = doc['updated_at'].isoformat()
                    await db.files.insert_one(doc)
                saved_files.append(block.get("filepath"))
        
        yield f"data: {json.dumps({'type': 'chain_complete', 'saved_files': saved_files, 'total_code_blocks': len(all_code_blocks)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# ============ QUICK ACTIONS ============

@api_router.get("/quick-actions")
async def get_quick_actions():
    """Get available quick actions"""
    return list(QUICK_ACTIONS.values())

@api_router.post("/quick-actions/execute")
async def execute_quick_action(request: QuickActionRequest):
    """Execute a quick action"""
    action = QUICK_ACTIONS.get(request.action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Quick action not found")
    
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Fill in template variables
    prompt = action['prompt'].format(
        engine_type=project.get('type', 'game'),
        engine_version=project.get('engine_version', ''),
        **request.parameters
    )
    
    # Execute as agent chain
    chain_request = AgentChainRequest(
        project_id=request.project_id,
        message=prompt,
        chain=action['chain']
    )
    
    return await execute_agent_chain(chain_request)

@api_router.post("/quick-actions/execute/stream")
async def stream_quick_action(request: QuickActionRequest):
    """Stream execute a quick action"""
    action = QUICK_ACTIONS.get(request.action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Quick action not found")
    
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    prompt = action['prompt'].format(
        engine_type=project.get('type', 'game'),
        engine_version=project.get('engine_version', ''),
        **request.parameters
    )
    
    chain_request = AgentChainRequest(
        project_id=request.project_id,
        message=prompt,
        chain=action['chain']
    )
    
    return await stream_agent_chain(chain_request)

# ============ LIVE PREVIEW ============

@api_router.get("/projects/{project_id}/preview")
async def get_project_preview(project_id: str):
    """Get live preview HTML for web projects"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project['type'] not in ['web_app', 'web_game']:
        raise HTTPException(status_code=400, detail="Preview only available for web projects")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    # Find HTML file
    html_file = next((f for f in files if f['filepath'].endswith('.html') or f['filename'] == 'index.html'), None)
    css_files = [f for f in files if f['filepath'].endswith('.css')]
    js_files = [f for f in files if f['filepath'].endswith('.js')]
    
    if not html_file:
        # Generate basic preview HTML
        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview</title>
    <style>{css}</style>
</head>
<body>
    <div id="app">
        <h1>Project Preview</h1>
        <p>No index.html found. Create an HTML file to see your preview.</p>
    </div>
    <script>{js}</script>
</body>
</html>"""
        css_content = "\n".join([f['content'] for f in css_files])
        js_content = "\n".join([f['content'] for f in js_files])
        html_content = html_content.format(css=css_content, js=js_content)
    else:
        html_content = html_file['content']
        
        # Inject CSS and JS if not already included
        if css_files and '<style>' not in html_content:
            css_content = "\n".join([f['content'] for f in css_files])
            html_content = html_content.replace('</head>', f'<style>{css_content}</style></head>')
        
        if js_files and '</body>' in html_content:
            js_content = "\n".join([f['content'] for f in js_files])
            html_content = html_content.replace('</body>', f'<script>{js_content}</script></body>')
    
    return HTMLResponse(content=html_content)

@api_router.get("/projects/{project_id}/preview-data")
async def get_preview_data(project_id: str):
    """Get preview data including HTML, CSS, JS separately"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    html_files = [f for f in files if f['filepath'].endswith('.html')]
    css_files = [f for f in files if f['filepath'].endswith('.css')]
    js_files = [f for f in files if f['filepath'].endswith('.js')]
    
    return {
        "html": [{"path": f['filepath'], "content": f['content']} for f in html_files],
        "css": [{"path": f['filepath'], "content": f['content']} for f in css_files],
        "js": [{"path": f['filepath'], "content": f['content']} for f in js_files],
        "project_type": project['type']
    }

# ============ AGENT MEMORY PERSISTENCE ============

@api_router.post("/memory")
async def create_memory(memory_data: MemoryCreate):
    """Store agent memory for persistence across sessions"""
    agents = await get_or_create_agents()
    agent = next((a for a in agents if a['name'].upper() == memory_data.agent_name.upper()), None)
    
    memory = AgentMemory(
        project_id=memory_data.project_id,
        agent_id=agent['id'] if agent else "",
        agent_name=memory_data.agent_name,
        memory_type=memory_data.memory_type,
        content=memory_data.content,
        importance=memory_data.importance
    )
    doc = memory.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('expires_at'):
        doc['expires_at'] = doc['expires_at'].isoformat()
    await db.memories.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/memory")
async def get_memories(project_id: str, agent_name: Optional[str] = None, limit: int = 50):
    """Get agent memories for a project"""
    query = {"project_id": project_id}
    if agent_name:
        query["agent_name"] = agent_name.upper()
    memories = await db.memories.find(query, {"_id": 0}).sort("importance", -1).limit(limit).to_list(limit)
    return memories

@api_router.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str):
    await db.memories.delete_one({"id": memory_id})
    return {"success": True}

@api_router.post("/memory/auto-extract")
async def auto_extract_memories(project_id: str):
    """Auto-extract important memories from recent messages"""
    messages = await db.messages.find(
        {"project_id": project_id, "agent_role": {"$ne": "user"}},
        {"_id": 0}
    ).sort("timestamp", -1).limit(20).to_list(20)
    
    if not messages:
        return {"extracted": 0, "memories": []}
    
    # Use COMMANDER to extract key learnings
    agents = await get_or_create_agents()
    lead = next((a for a in agents if a['role'] == 'lead'), agents[0])
    
    conversation = "\n".join([f"{m['agent_name']}: {m['content'][:500]}" for m in messages])
    
    extract_prompt = f"""Review this conversation and extract 3-5 key facts, decisions, or learnings that should be remembered for future sessions.

Conversation:
{conversation}

Output as JSON array:
[{{"agent": "AGENT_NAME", "type": "decision|context|preference|learned", "content": "What to remember", "importance": 1-10}}]"""

    try:
        response = llm_client.chat.completions.create(
            model=lead.get('model', 'google/gemini-2.5-flash'),
            messages=[{"role": "user", "content": extract_prompt}],
            max_tokens=2000
        )
        
        # Parse JSON from response
        content = response.choices[0].message.content
        json_match = re.search(r'\[[\s\S]*\]', content)
        if json_match:
            extracted = json.loads(json_match.group())
            saved_memories = []
            
            for mem in extracted:
                memory = AgentMemory(
                    project_id=project_id,
                    agent_id="",
                    agent_name=mem.get('agent', 'COMMANDER'),
                    memory_type=mem.get('type', 'context'),
                    content=mem.get('content', ''),
                    importance=mem.get('importance', 5)
                )
                doc = memory.model_dump()
                doc['created_at'] = doc['created_at'].isoformat()
                await db.memories.insert_one(doc)
                saved_memories.append(serialize_doc(doc))
            
            return {"extracted": len(saved_memories), "memories": saved_memories}
    except Exception as e:
        logger.error(f"Memory extraction failed: {e}")
    
    return {"extracted": 0, "memories": []}

# ============ CUSTOM QUICK ACTIONS ============

@api_router.post("/custom-actions")
async def create_custom_action(action_data: CustomActionCreate):
    """Create a custom quick action"""
    action = CustomQuickAction(
        name=action_data.name,
        description=action_data.description,
        prompt=action_data.prompt,
        chain=action_data.chain,
        icon=action_data.icon,
        category=action_data.category,
        is_global=action_data.is_global,
        project_id=action_data.project_id
    )
    doc = action.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.custom_actions.insert_one(doc)
    return serialize_doc(doc)

@api_router.get("/custom-actions")
async def get_custom_actions(project_id: Optional[str] = None):
    """Get custom quick actions (global + project-specific)"""
    query = {"$or": [{"is_global": True}]}
    if project_id:
        query["$or"].append({"project_id": project_id})
    
    actions = await db.custom_actions.find(query, {"_id": 0}).to_list(100)
    return actions

@api_router.delete("/custom-actions/{action_id}")
async def delete_custom_action(action_id: str):
    await db.custom_actions.delete_one({"id": action_id})
    return {"success": True}

@api_router.post("/custom-actions/{action_id}/execute")
async def execute_custom_action(action_id: str, project_id: str):
    """Execute a custom quick action"""
    action = await db.custom_actions.find_one({"id": action_id}, {"_id": 0})
    if not action:
        raise HTTPException(status_code=404, detail="Custom action not found")
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Fill template variables
    prompt = action['prompt'].replace('{engine_type}', project.get('type', 'game'))
    prompt = prompt.replace('{engine_version}', project.get('engine_version', ''))
    prompt = prompt.replace('{project_name}', project.get('name', ''))
    
    chain_request = AgentChainRequest(
        project_id=project_id,
        message=prompt,
        chain=action['chain']
    )
    
    return await execute_agent_chain(chain_request)

@api_router.post("/custom-actions/{action_id}/execute/stream")
async def stream_custom_action(action_id: str, project_id: str):
    """Stream execute a custom quick action"""
    action = await db.custom_actions.find_one({"id": action_id}, {"_id": 0})
    if not action:
        raise HTTPException(status_code=404, detail="Custom action not found")
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    prompt = action['prompt'].replace('{engine_type}', project.get('type', 'game'))
    prompt = prompt.replace('{engine_version}', project.get('engine_version', ''))
    
    chain_request = AgentChainRequest(
        project_id=project_id,
        message=prompt,
        chain=action['chain']
    )
    
    return await stream_agent_chain(chain_request)

# ============ PROJECT DUPLICATION ============

@api_router.post("/projects/{project_id}/duplicate")
async def duplicate_project(project_id: str, request: ProjectDuplicateRequest):
    """Duplicate a project with all its files"""
    original = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not original:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create new project
    new_project = Project(
        name=request.new_name,
        description=original['description'] + " (Copy)",
        type=original['type'],
        engine_version=original.get('engine_version'),
        thumbnail=original['thumbnail'],
        phase="clarification",
        status="planning"
    )
    new_doc = new_project.model_dump()
    new_doc['created_at'] = new_doc['created_at'].isoformat()
    new_doc['updated_at'] = new_doc['updated_at'].isoformat()
    await db.projects.insert_one(new_doc)
    
    duplicated = {"project": serialize_doc(new_doc), "files": 0, "tasks": 0, "messages": 0}
    
    # Duplicate files
    if request.include_files:
        files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
        for f in files:
            new_file = ProjectFile(
                project_id=new_project.id,
                filename=f['filename'],
                filepath=f['filepath'],
                content=f['content'],
                language=f['language'],
                file_type=f.get('file_type', 'code')
            )
            file_doc = new_file.model_dump()
            file_doc['created_at'] = file_doc['created_at'].isoformat()
            file_doc['updated_at'] = file_doc['updated_at'].isoformat()
            await db.files.insert_one(file_doc)
        duplicated["files"] = len(files)
    
    # Duplicate tasks
    if request.include_tasks:
        tasks = await db.tasks.find({"project_id": project_id}, {"_id": 0}).to_list(500)
        for t in tasks:
            new_task = Task(
                project_id=new_project.id,
                title=t['title'],
                description=t['description'],
                status="backlog",
                priority=t['priority'],
                category=t.get('category', 'general')
            )
            task_doc = new_task.model_dump()
            task_doc['created_at'] = task_doc['created_at'].isoformat()
            task_doc['updated_at'] = task_doc['updated_at'].isoformat()
            await db.tasks.insert_one(task_doc)
        duplicated["tasks"] = len(tasks)
    
    return duplicated

# ============ MULTI-FILE REFACTORING ============

@api_router.post("/refactor/preview")
async def preview_refactor(request: RefactorRequest):
    """Preview what a refactor would change without applying"""
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get files to refactor
    if request.file_ids:
        files = await db.files.find({"id": {"$in": request.file_ids}}, {"_id": 0}).to_list(500)
    else:
        files = await db.files.find({"project_id": request.project_id}, {"_id": 0}).to_list(500)
    
    changes = []
    
    for f in files:
        original_content = f['content']
        new_content = original_content
        
        if request.refactor_type == "find_replace":
            if request.target in original_content:
                new_content = original_content.replace(request.target, request.new_value or "")
                
        elif request.refactor_type == "rename":
            # Rename class, function, or variable
            patterns = [
                (rf'\bclass\s+{re.escape(request.target)}\b', f'class {request.new_value}'),
                (rf'\bdef\s+{re.escape(request.target)}\b', f'def {request.new_value}'),
                (rf'\bfunction\s+{re.escape(request.target)}\b', f'function {request.new_value}'),
                (rf'\bvoid\s+{re.escape(request.target)}\s*\(', f'void {request.new_value}('),
                (rf'\b{re.escape(request.target)}\s*\(', f'{request.new_value}('),
                (rf'\b{re.escape(request.target)}\b', request.new_value),
            ]
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, new_content)
        
        if new_content != original_content:
            # Count changes
            old_lines = original_content.split('\n')
            new_lines = new_content.split('\n')
            
            changes.append({
                "file_id": f['id'],
                "filepath": f['filepath'],
                "occurrences": original_content.count(request.target),
                "preview": {
                    "before": original_content[:500] + ("..." if len(original_content) > 500 else ""),
                    "after": new_content[:500] + ("..." if len(new_content) > 500 else "")
                }
            })
    
    return {
        "refactor_type": request.refactor_type,
        "target": request.target,
        "new_value": request.new_value,
        "files_affected": len(changes),
        "total_files_scanned": len(files),
        "changes": changes
    }

@api_router.post("/refactor/apply")
async def apply_refactor(request: RefactorRequest):
    """Apply a refactor across multiple files"""
    # First get preview
    preview = await preview_refactor(request)
    
    if preview["files_affected"] == 0:
        return {"success": True, "files_updated": 0, "message": "No changes needed"}
    
    # Apply changes
    updated_files = []
    for change in preview["changes"]:
        file = await db.files.find_one({"id": change["file_id"]})
        if not file:
            continue
        
        original_content = file['content']
        new_content = original_content
        
        if request.refactor_type == "find_replace":
            new_content = original_content.replace(request.target, request.new_value or "")
        elif request.refactor_type == "rename":
            patterns = [
                (rf'\bclass\s+{re.escape(request.target)}\b', f'class {request.new_value}'),
                (rf'\bdef\s+{re.escape(request.target)}\b', f'def {request.new_value}'),
                (rf'\bfunction\s+{re.escape(request.target)}\b', f'function {request.new_value}'),
                (rf'\b{re.escape(request.target)}\b', request.new_value),
            ]
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, new_content)
        
        # Update file
        new_version = file.get('version', 1) + 1
        await db.files.update_one(
            {"id": change["file_id"]},
            {"$set": {
                "content": new_content,
                "version": new_version,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        updated_files.append(change["filepath"])
    
    return {
        "success": True,
        "files_updated": len(updated_files),
        "updated_files": updated_files,
        "refactor_type": request.refactor_type
    }

@api_router.post("/refactor/ai-suggest")
async def ai_suggest_refactor(project_id: str, description: str):
    """Use AI to suggest and perform a refactor based on natural language"""
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(50)
    if not files:
        raise HTTPException(status_code=400, detail="No files to refactor")
    
    agents = await get_or_create_agents()
    lead = next((a for a in agents if a['role'] == 'lead'), agents[0])
    
    file_list = "\n".join([f"- {f['filepath']}: {f['language']}" for f in files])
    
    prompt = f"""Analyze this refactoring request and suggest specific changes:

Request: {description}

Project files:
{file_list}

Respond with a JSON object:
{{
    "refactor_type": "rename|find_replace|extract|reorganize",
    "target": "what to change",
    "new_value": "what to change it to",
    "explanation": "why this change",
    "affected_files": ["list of filepaths"]
}}"""

    try:
        response = llm_client.chat.completions.create(
            model=lead.get('model', 'google/gemini-2.5-flash'),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            suggestion = json.loads(json_match.group())
            return {"success": True, "suggestion": suggestion}
    except Exception as e:
        logger.error(f"AI refactor suggestion failed: {e}")
    
    return {"success": False, "error": "Could not generate suggestion"}

# ============ SIMULATION MODE (DRY RUN) ============

@api_router.get("/systems/open-world")
async def get_open_world_systems():
    """Get available open world game systems"""
    return list(OPEN_WORLD_SYSTEMS.values())

@api_router.get("/build-stages/{engine}")
async def get_build_stages(engine: str):
    """Get build stages for an engine"""
    stages = BUILD_STAGES.get(engine, BUILD_STAGES["unreal"])
    return stages

@api_router.post("/simulate")
async def simulate_build(request: SimulationRequest):
    """Run a simulation/dry run of the build to predict problems"""
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    agents = await get_or_create_agents()
    atlas = next((a for a in agents if a['name'] == 'ATLAS'), agents[0])
    
    # Calculate estimates based on selected systems
    selected_systems = request.include_systems if request.include_systems else list(OPEN_WORLD_SYSTEMS.keys())[:5]
    
    total_files = 0
    total_time_minutes = 0
    required_assets = []
    warnings = []
    phases = []
    
    # Base stages from engine
    base_stages = BUILD_STAGES.get(request.target_engine, BUILD_STAGES["unreal"])
    for stage in base_stages:
        total_time_minutes += stage["duration_minutes"]
        phases.append({
            "name": stage["name"],
            "duration_minutes": stage["duration_minutes"],
            "tasks": stage["tasks"],
            "status": "pending"
        })
    
    # Add system-specific estimates
    system_phase = {"name": "Game Systems", "systems": [], "duration_minutes": 0, "files": 0}
    for sys_id in selected_systems:
        system = OPEN_WORLD_SYSTEMS.get(sys_id)
        if system:
            total_files += system["files_estimate"]
            additional_time = system["time_estimate_minutes"]
            system_phase["systems"].append(system["name"])
            system_phase["duration_minutes"] += additional_time
            system_phase["files"] += system["files_estimate"]
            
            # Check dependencies
            for dep in system.get("dependencies", []):
                if dep not in selected_systems:
                    warnings.append({
                        "type": "missing_dependency",
                        "severity": "high",
                        "message": f"⚠ {system['name']} requires {dep} which is not selected",
                        "suggestion": f"Add {dep} to your build or implement it separately"
                    })
            
            # Add required assets
            required_assets.append({
                "system": system["name"],
                "assets": system.get("subsystems", []),
                "type": "code"
            })
    
    total_time_minutes += system_phase["duration_minutes"]
    
    # Engine-specific warnings
    if request.target_engine == "unreal":
        if "multiplayer" in selected_systems:
            warnings.append({
                "type": "complexity",
                "severity": "medium",
                "message": "⚠ Unreal multiplayer requires careful replication setup",
                "suggestion": "Ensure all replicated actors use proper UPROPERTY specifiers"
            })
        if total_files > 100:
            warnings.append({
                "type": "performance",
                "severity": "low",
                "message": "⚠ Large file count may increase compilation times",
                "suggestion": "Consider using precompiled headers and unity builds"
            })
    elif request.target_engine == "unity":
        if "terrain" in selected_systems:
            warnings.append({
                "type": "memory",
                "severity": "medium",
                "message": "⚠ Unity terrain can be memory-intensive",
                "suggestion": "Use terrain LOD and streaming for large worlds"
            })
    
    # Check for common issues
    if len(selected_systems) > 10:
        warnings.append({
            "type": "scope",
            "severity": "high",
            "message": "⚠ Project scope is very large (10+ systems)",
            "suggestion": "Consider building in phases to reduce risk"
        })
    
    if "vehicle_system" in selected_systems and "terrain" not in selected_systems:
        warnings.append({
            "type": "missing_dependency",
            "severity": "medium",
            "message": "⚠ Vehicle system selected without terrain system",
            "suggestion": "Vehicles need a world to drive in - add terrain or level design"
        })
    
    # Calculate feasibility score
    feasibility = 100
    for w in warnings:
        if w["severity"] == "high":
            feasibility -= 15
        elif w["severity"] == "medium":
            feasibility -= 8
        else:
            feasibility -= 3
    feasibility = max(0, feasibility)
    
    # Build time formatting
    hours = total_time_minutes // 60
    minutes = total_time_minutes % 60
    time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
    
    # Estimate total size (rough: ~5KB per file average)
    total_size_kb = total_files * 5
    
    # Use AI to generate architecture summary
    arch_prompt = f"""Briefly describe the architecture for a {request.target_engine} game with these systems: {', '.join(selected_systems)}.
Keep it to 2-3 sentences focusing on core patterns and data flow."""
    
    try:
        arch_response = llm_client.chat.completions.create(
            model=atlas.get('model', 'google/gemini-2.5-flash'),
            messages=[{"role": "user", "content": arch_prompt}],
            max_tokens=200
        )
        architecture_summary = arch_response.choices[0].message.content
    except:
        architecture_summary = f"Modular {request.target_engine} architecture with component-based systems and event-driven communication."
    
    result = {
        "id": str(uuid.uuid4()),
        "project_id": request.project_id,
        "build_type": request.build_type,
        "target_engine": request.target_engine,
        "estimated_build_time": time_str,
        "estimated_build_minutes": total_time_minutes,
        "file_count": total_files,
        "total_size_kb": total_size_kb,
        "required_assets": required_assets,
        "warnings": warnings,
        "warning_count": len(warnings),
        "high_severity_warnings": len([w for w in warnings if w["severity"] == "high"]),
        "architecture_summary": architecture_summary,
        "phases": phases,
        "systems_selected": selected_systems,
        "feasibility_score": feasibility,
        "ready_to_build": feasibility >= 60 and len([w for w in warnings if w["severity"] == "high"]) == 0
    }
    
    # Save simulation result
    await db.simulations.insert_one({**result, "created_at": datetime.now(timezone.utc).isoformat()})
    
    return result

# ============ WAR ROOM (AGENT COMMUNICATION) ============

@api_router.get("/war-room/{project_id}")
async def get_war_room_messages(project_id: str, limit: int = 100):
    """Get war room messages for a project"""
    messages = await db.war_room.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    return list(reversed(messages))

@api_router.post("/war-room/message")
async def post_war_room_message(project_id: str, from_agent: str, content: str, message_type: str = "discussion", to_agent: Optional[str] = None):
    """Post a message to the war room"""
    message = WarRoomMessage(
        project_id=project_id,
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=message_type,
        content=content
    )
    doc = message.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.war_room.insert_one(doc)
    return serialize_doc(doc)

@api_router.delete("/war-room/{project_id}")
async def clear_war_room(project_id: str):
    """Clear war room messages for a project"""
    await db.war_room.delete_many({"project_id": project_id})
    return {"success": True}

async def broadcast_to_war_room(project_id: str, from_agent: str, content: str, message_type: str = "progress", build_id: str = None):
    """Helper to broadcast a message to war room"""
    message = WarRoomMessage(
        project_id=project_id,
        build_id=build_id,
        from_agent=from_agent,
        message_type=message_type,
        content=content
    )
    doc = message.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.war_room.insert_one(doc)
    return doc

# ============ AUTONOMOUS BUILDS ============

@api_router.post("/builds/start")
async def start_autonomous_build(request: StartBuildRequest):
    """Start or schedule an autonomous overnight build"""
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check for existing running build
    existing = await db.builds.find_one({"project_id": request.project_id, "status": {"$in": ["running", "scheduled"]}})
    if existing:
        raise HTTPException(status_code=400, detail="A build is already running or scheduled for this project")
    
    # Get build stages
    base_stages = BUILD_STAGES.get(request.target_engine, BUILD_STAGES["unreal"])
    stages = []
    for i, stage in enumerate(base_stages):
        stages.append({
            "index": i,
            "name": stage["name"],
            "duration_minutes": stage["duration_minutes"],
            "tasks": stage["tasks"],
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "files_created": [],
            "test_results": None,
            "agent_notes": []
        })
    
    total_minutes = sum(s["duration_minutes"] for s in stages)
    hours = total_minutes // 60
    mins = total_minutes % 60
    
    # Parse scheduled time
    scheduled_time = None
    status = "queued"
    if request.scheduled_at:
        try:
            scheduled_time = datetime.fromisoformat(request.scheduled_at.replace('Z', '+00:00'))
            status = "scheduled"
        except:
            pass
    
    build = AutonomousBuild(
        project_id=request.project_id,
        build_type=request.build_type,
        target_engine=request.target_engine,
        status=status,
        total_stages=len(stages),
        stages=stages,
        estimated_completion=f"{hours}h {mins}m",
        scheduled_at=scheduled_time
    )
    
    doc = build.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('scheduled_at'):
        doc['scheduled_at'] = doc['scheduled_at'].isoformat()
    await db.builds.insert_one(doc)
    
    # Post to war room
    if scheduled_time:
        scheduled_str = scheduled_time.strftime("%I:%M %p on %b %d")
        await broadcast_to_war_room(
            request.project_id,
            "COMMANDER",
            f"⏰ Build SCHEDULED for {scheduled_str}! Target: {request.target_engine.upper()}. Estimated time: {build.estimated_completion}. Get some rest, I'll handle this.",
            "progress",
            build.id
        )
    else:
        await broadcast_to_war_room(
            request.project_id,
            "COMMANDER",
            f"🚀 Autonomous build initiated! Target: {request.target_engine.upper()}. Estimated time: {build.estimated_completion}. {len(stages)} stages queued.",
            "progress",
            build.id
        )
    
    # Update project status
    await db.projects.update_one(
        {"id": request.project_id},
        {"$set": {"status": "scheduled" if scheduled_time else "building", "build_id": build.id}}
    )
    
    return serialize_doc(doc)

@api_router.get("/builds/{project_id}")
async def get_project_builds(project_id: str):
    """Get all builds for a project"""
    builds = await db.builds.find({"project_id": project_id}, {"_id": 0}).sort("created_at", -1).to_list(20)
    return builds

@api_router.get("/builds/{project_id}/current")
async def get_current_build(project_id: str):
    """Get the current/latest build for a project"""
    build = await db.builds.find_one(
        {"project_id": project_id, "status": {"$in": ["queued", "running"]}},
        {"_id": 0}
    )
    if not build:
        build = await db.builds.find_one(
            {"project_id": project_id},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
    return build

@api_router.post("/builds/{build_id}/advance")
async def advance_build_stage(build_id: str):
    """Advance to the next build stage (called by build runner or manually)"""
    build = await db.builds.find_one({"id": build_id})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    
    current_stage = build["current_stage"]
    stages = build["stages"]
    
    if current_stage >= len(stages):
        return {"message": "Build already complete"}
    
    # Mark current stage as complete
    if build["status"] == "running":
        stages[current_stage]["status"] = "completed"
        stages[current_stage]["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    # Move to next stage
    next_stage = current_stage + 1
    progress = int((next_stage / len(stages)) * 100)
    
    if next_stage >= len(stages):
        # Build complete
        await db.builds.update_one(
            {"id": build_id},
            {"$set": {
                "status": "completed",
                "stages": stages,
                "current_stage": next_stage,
                "progress_percent": 100,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        await broadcast_to_war_room(
            build["project_id"],
            "COMMANDER",
            "✅ BUILD COMPLETE! All stages finished successfully. Review the generated files and run tests.",
            "progress",
            build_id
        )
    else:
        # Start next stage
        stages[next_stage]["status"] = "in_progress"
        stages[next_stage]["started_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.builds.update_one(
            {"id": build_id},
            {"$set": {
                "status": "running",
                "stages": stages,
                "current_stage": next_stage,
                "progress_percent": progress,
                "started_at": build.get("started_at") or datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # War room update
        stage_name = stages[next_stage]["name"]
        await broadcast_to_war_room(
            build["project_id"],
            "COMMANDER",
            f"📍 Stage {next_stage + 1}/{len(stages)}: {stage_name} starting... ({progress}% complete)",
            "progress",
            build_id
        )
    
    return await db.builds.find_one({"id": build_id}, {"_id": 0})

@api_router.post("/builds/{build_id}/pause")
async def pause_build(build_id: str):
    """Pause a running build"""
    await db.builds.update_one({"id": build_id}, {"$set": {"status": "paused"}})
    build = await db.builds.find_one({"id": build_id}, {"_id": 0})
    await broadcast_to_war_room(build["project_id"], "COMMANDER", "⏸️ Build paused by user.", "progress", build_id)
    return {"success": True}

@api_router.post("/builds/{build_id}/resume")
async def resume_build(build_id: str):
    """Resume a paused build"""
    await db.builds.update_one({"id": build_id}, {"$set": {"status": "running"}})
    build = await db.builds.find_one({"id": build_id}, {"_id": 0})
    await broadcast_to_war_room(build["project_id"], "COMMANDER", "▶️ Build resumed!", "progress", build_id)
    return {"success": True}

@api_router.post("/builds/{build_id}/cancel")
async def cancel_build(build_id: str):
    """Cancel a build"""
    await db.builds.update_one({"id": build_id}, {"$set": {"status": "cancelled"}})
    build = await db.builds.find_one({"id": build_id}, {"_id": 0})
    await broadcast_to_war_room(build["project_id"], "COMMANDER", "❌ Build cancelled.", "progress", build_id)
    await db.projects.update_one({"id": build["project_id"]}, {"$set": {"status": "planning"}})
    return {"success": True}

@api_router.get("/builds/scheduled")
async def get_scheduled_builds():
    """Get all scheduled builds that should start now"""
    now = datetime.now(timezone.utc)
    builds = await db.builds.find({
        "status": "scheduled",
        "scheduled_at": {"$lte": now.isoformat()}
    }, {"_id": 0}).to_list(100)
    return builds

@api_router.post("/builds/{build_id}/start-scheduled")
async def start_scheduled_build(build_id: str, background_tasks: BackgroundTasks):
    """Start a scheduled build that is ready"""
    build = await db.builds.find_one({"id": build_id})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    
    if build["status"] != "scheduled":
        raise HTTPException(status_code=400, detail="Build is not in scheduled status")
    
    # Update status to running
    await db.builds.update_one(
        {"id": build_id},
        {"$set": {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await broadcast_to_war_room(
        build["project_id"],
        "COMMANDER",
        "⏰ Scheduled build starting NOW! All agents, prepare for overnight shift. ☕",
        "progress",
        build_id
    )
    
    # Start background execution
    async def execute_all_stages():
        for i in range(len(build["stages"])):
            current_build = await db.builds.find_one({"id": build_id})
            if current_build["status"] in ["cancelled", "paused"]:
                break
            
            try:
                await execute_build_stage(build_id, i)
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Build stage {i} failed: {e}")
                break
        
        final_build = await db.builds.find_one({"id": build_id})
        if final_build["status"] == "running":
            all_complete = all(s["status"] == "completed" for s in final_build["stages"])
            await db.builds.update_one(
                {"id": build_id},
                {"$set": {
                    "status": "completed" if all_complete else "partial",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "progress_percent": 100 if all_complete else final_build.get("progress_percent", 0)
                }}
            )
            
            # Final war room message
            if all_complete:
                await broadcast_to_war_room(
                    final_build["project_id"],
                    "COMMANDER",
                    "🎉 OVERNIGHT BUILD COMPLETE! All stages finished. Your project is ready! Time to review the generated files.",
                    "progress",
                    build_id
                )
    
    background_tasks.add_task(execute_all_stages)
    
    return {"success": True, "message": "Scheduled build started"}

@api_router.post("/builds/{build_id}/stage/{stage_index}/execute")
async def execute_build_stage(build_id: str, stage_index: int):
    """Execute a specific build stage using the agent team"""
    build = await db.builds.find_one({"id": build_id})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    
    if stage_index >= len(build["stages"]):
        raise HTTPException(status_code=400, detail="Invalid stage index")
    
    stage = build["stages"][stage_index]
    project = await db.projects.find_one({"id": build["project_id"]}, {"_id": 0})
    agents = await get_or_create_agents()
    
    # Determine which agent handles this stage
    stage_agent_map = {
        "Project Setup": "COMMANDER",
        "Core Framework": "ATLAS",
        "Game Systems": "FORGE",
        "AI & NPCs": "FORGE",
        "UI/UX": "PRISM",
        "World Building": "PRISM",
        "Audio Integration": "FORGE",
        "Polish & Testing": "PROBE"
    }
    
    agent_name = stage_agent_map.get(stage["name"], "FORGE")
    agent = next((a for a in agents if a['name'] == agent_name), agents[0])
    
    # Broadcast stage start
    await broadcast_to_war_room(
        build["project_id"],
        agent_name,
        f"🔧 Taking over {stage['name']}. Tasks: {', '.join(stage['tasks'])}",
        "handoff",
        build_id
    )
    
    # Build the prompt for this stage
    tasks_str = "\n".join([f"- {t}" for t in stage["tasks"]])
    prompt = f"""You are working on an autonomous build for a {build['target_engine']} {build['build_type']} game.

PROJECT: {project['name']}
DESCRIPTION: {project['description']}
ENGINE: {build['target_engine'].upper()}

CURRENT STAGE: {stage['name']} ({stage_index + 1}/{len(build['stages'])})

YOUR TASKS FOR THIS STAGE:
{tasks_str}

IMPORTANT RULES:
1. Generate COMPLETE, PRODUCTION-READY files - no placeholders or "TODO" comments
2. Split large systems into logical modules (max 500 lines per file)
3. Use proper {build['target_engine']} conventions and best practices
4. Include all necessary includes/imports
5. Add documentation comments
6. Output each file with the format: ```language:filepath/filename.ext

Generate all the necessary files for this stage now."""

    context = await build_project_context(build["project_id"])
    
    # Execute with agent
    try:
        response = await call_agent(agent, [{"role": "user", "content": prompt}], context)
        code_blocks = extract_code_blocks(response)
        
        # Save generated files
        files_created = []
        for block in code_blocks:
            if block.get("filepath"):
                file = ProjectFile(
                    project_id=build["project_id"],
                    filename=block.get("filename", ""),
                    filepath=block.get("filepath"),
                    content=block.get("content", ""),
                    language=block.get("language", "text"),
                    created_by_agent_name=agent_name
                )
                doc = file.model_dump()
                doc['created_at'] = doc['created_at'].isoformat()
                doc['updated_at'] = doc['updated_at'].isoformat()
                
                existing = await db.files.find_one({"project_id": build["project_id"], "filepath": block.get("filepath")})
                if existing:
                    await db.files.update_one(
                        {"id": existing['id']},
                        {"$set": {"content": block.get("content", ""), "version": existing.get('version', 1) + 1}}
                    )
                else:
                    await db.files.insert_one(doc)
                
                files_created.append(block.get("filepath"))
        
        # Update stage with results
        build["stages"][stage_index]["status"] = "completed"
        build["stages"][stage_index]["completed_at"] = datetime.now(timezone.utc).isoformat()
        build["stages"][stage_index]["files_created"] = files_created
        build["stages"][stage_index]["agent_notes"].append({
            "agent": agent_name,
            "note": f"Generated {len(files_created)} files",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        await db.builds.update_one({"id": build_id}, {"$set": {"stages": build["stages"]}})
        
        # War room completion message
        await broadcast_to_war_room(
            build["project_id"],
            agent_name,
            f"✅ {stage['name']} complete! Generated {len(files_created)} files: {', '.join(files_created[:5])}{'...' if len(files_created) > 5 else ''}",
            "progress",
            build_id
        )
        
        return {
            "success": True,
            "stage": stage["name"],
            "files_created": files_created,
            "agent": agent_name
        }
        
    except Exception as e:
        logger.error(f"Stage execution failed: {e}")
        build["stages"][stage_index]["status"] = "failed"
        build["stages"][stage_index]["agent_notes"].append({
            "agent": agent_name,
            "note": f"Error: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        await db.builds.update_one({"id": build_id}, {"$set": {"stages": build["stages"], "status": "failed"}})
        
        await broadcast_to_war_room(
            build["project_id"],
            agent_name,
            f"❌ {stage['name']} failed: {str(e)}",
            "warning",
            build_id
        )
        
        raise HTTPException(status_code=500, detail=f"Stage execution failed: {str(e)}")

@api_router.post("/builds/{build_id}/run-full")
async def run_full_build(build_id: str, background_tasks: BackgroundTasks):
    """Run all build stages sequentially (async background task)"""
    build = await db.builds.find_one({"id": build_id})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    
    # Start the build
    await db.builds.update_one(
        {"id": build_id},
        {"$set": {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Queue background execution
    async def execute_all_stages():
        for i in range(len(build["stages"])):
            current_build = await db.builds.find_one({"id": build_id})
            if current_build["status"] in ["cancelled", "paused"]:
                break
            
            try:
                await execute_build_stage(build_id, i)
                await asyncio.sleep(2)  # Brief pause between stages
            except Exception as e:
                logger.error(f"Build stage {i} failed: {e}")
                break
        
        # Mark complete
        final_build = await db.builds.find_one({"id": build_id})
        if final_build["status"] == "running":
            all_complete = all(s["status"] == "completed" for s in final_build["stages"])
            await db.builds.update_one(
                {"id": build_id},
                {"$set": {
                    "status": "completed" if all_complete else "partial",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "progress_percent": 100 if all_complete else final_build.get("progress_percent", 0)
                }}
            )
            
            # AUTO-GENERATE PLAYABLE DEMO ON COMPLETION
            if all_complete:
                await broadcast_to_war_room(
                    final_build["project_id"],
                    "COMMANDER",
                    "🎮 BUILD COMPLETE! Now generating playable demo with all systems...",
                    "progress",
                    build_id
                )
                try:
                    await generate_playable_demo(build_id)
                except Exception as e:
                    logger.error(f"Demo generation failed: {e}")
                    await broadcast_to_war_room(
                        final_build["project_id"],
                        "PRISM",
                        f"⚠️ Demo generation encountered an issue: {str(e)[:100]}",
                        "warning",
                        build_id
                    )
    
    background_tasks.add_task(execute_all_stages)
    
    return {"success": True, "message": "Build started in background", "build_id": build_id}

# ============ PLAYABLE DEMO GENERATION ============

async def generate_playable_demo(build_id: str):
    """Generate playable demo on build completion"""
    build = await db.builds.find_one({"id": build_id})
    if not build:
        return None
    
    project = await db.projects.find_one({"id": build["project_id"]}, {"_id": 0})
    files = await db.files.find({"project_id": build["project_id"]}, {"_id": 0}).to_list(500)
    agents = await get_or_create_agents()
    
    # Create demo record
    demo = PlayableDemo(
        project_id=build["project_id"],
        build_id=build_id,
        status="generating",
        target_engine=build["target_engine"],
        demo_type="both"
    )
    
    doc = demo.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.demos.insert_one(doc)
    
    # Determine which systems were built
    systems_built = []
    for stage in build.get("stages", []):
        if stage.get("status") == "completed":
            systems_built.append(stage.get("name", ""))
    
    # Get PRISM (artist) to generate demo
    prism = next((a for a in agents if a['name'] == 'PRISM'), agents[0])
    
    await broadcast_to_war_room(
        build["project_id"],
        "PRISM",
        f"🎨 Taking over demo generation. Creating playable showcase for {build['target_engine'].upper()}...",
        "handoff",
        build_id
    )
    
    # Generate Web Demo (HTML5 embed)
    web_demo_prompt = f"""Create a playable HTML5 demo for this {build['target_engine']} game project.

PROJECT: {project['name']}
DESCRIPTION: {project['description']}
ENGINE: {build['target_engine'].upper()}
SYSTEMS BUILT: {', '.join(systems_built)}

Create a COMPLETE, FULLY PLAYABLE HTML5 demo that showcases ALL the game systems.
Include:
1. Full HTML document with embedded CSS and JavaScript
2. Canvas-based rendering or DOM-based game view
3. Working player controls (WASD/Arrow keys for movement, mouse for camera/actions)
4. Visual representation of all implemented systems
5. On-screen controls guide
6. Demo should be immediately playable in browser

The demo should demonstrate:
- Player movement and controls
- Any combat/interaction systems
- UI elements (health bars, inventory preview, etc.)
- Visual effects and feedback
- A small test environment to explore

Output a single complete HTML file that works standalone:
```html:demo/web_demo.html
<!DOCTYPE html>
<html>
...complete playable demo...
</html>
```"""

    try:
        web_response = await call_agent(prism, [{"role": "user", "content": web_demo_prompt}], "")
        web_blocks = extract_code_blocks(web_response)
        
        web_demo_html = None
        for block in web_blocks:
            if block.get("language") == "html" or "html" in block.get("filepath", ""):
                web_demo_html = block.get("content", "")
                break
        
        if not web_demo_html:
            # Fallback: extract any HTML content
            html_match = re.search(r'<!DOCTYPE html>[\s\S]*?</html>', web_response, re.IGNORECASE)
            if html_match:
                web_demo_html = html_match.group(0)
        
        # Save web demo file
        if web_demo_html:
            web_file = ProjectFile(
                project_id=build["project_id"],
                filename="web_demo.html",
                filepath="demo/web_demo.html",
                content=web_demo_html,
                language="html",
                created_by_agent_name="PRISM"
            )
            web_doc = web_file.model_dump()
            web_doc['created_at'] = web_doc['created_at'].isoformat()
            web_doc['updated_at'] = web_doc['updated_at'].isoformat()
            await db.files.insert_one(web_doc)
            
            await broadcast_to_war_room(
                build["project_id"],
                "PRISM",
                "✅ Web demo (HTML5) generated! Playable in browser.",
                "progress",
                build_id
            )
    except Exception as e:
        logger.error(f"Web demo generation failed: {e}")
        web_demo_html = None
    
    # Generate Executable Demo Package Instructions
    exe_demo_prompt = f"""Create executable demo build configuration and main demo scene for {build['target_engine']}.

PROJECT: {project['name']}
ENGINE: {build['target_engine'].upper()}
SYSTEMS: {', '.join(systems_built)}

Generate:
1. Demo scene/level that showcases ALL systems
2. Build configuration for Windows/Mac/Linux
3. Demo launcher/main menu
4. Controls configuration
5. README with play instructions

For {build['target_engine'].upper()}, create:
"""

    if build['target_engine'] == 'unreal':
        exe_demo_prompt += """
- Demo map (.cpp level setup)
- Demo game mode with all systems active
- DefaultGame.ini build settings
- Demo-specific player controller
- Package configuration for shipping build

Output files:
```cpp:Source/Demo/DemoGameMode.cpp
```cpp:Source/Demo/DemoPlayerController.cpp
```cpp:Source/Demo/DemoLevel.cpp
```ini:Config/DefaultGame_Demo.ini
```markdown:Demo/README.md
"""
    else:
        exe_demo_prompt += """
- Demo scene script
- Build settings profile
- Demo manager with all systems
- Player demo controller
- Package manifest

Output files:
```csharp:Assets/Demo/DemoManager.cs
```csharp:Assets/Demo/DemoSceneSetup.cs
```json:ProjectSettings/DemoBuildSettings.json
```markdown:Demo/README.md
"""

    try:
        exe_response = await call_agent(prism, [{"role": "user", "content": exe_demo_prompt}], "")
        exe_blocks = extract_code_blocks(exe_response)
        
        demo_files = []
        controls_guide = ""
        
        for block in exe_blocks:
            if block.get("filepath"):
                file = ProjectFile(
                    project_id=build["project_id"],
                    filename=block.get("filename", ""),
                    filepath=block.get("filepath"),
                    content=block.get("content", ""),
                    language=block.get("language", "text"),
                    created_by_agent_name="PRISM"
                )
                file_doc = file.model_dump()
                file_doc['created_at'] = file_doc['created_at'].isoformat()
                file_doc['updated_at'] = file_doc['updated_at'].isoformat()
                await db.files.insert_one(file_doc)
                demo_files.append(block.get("filepath"))
                
                if "README" in block.get("filepath", ""):
                    controls_guide = block.get("content", "")
        
        await broadcast_to_war_room(
            build["project_id"],
            "PRISM",
            f"✅ Executable demo package created! {len(demo_files)} files generated.",
            "progress",
            build_id
        )
    except Exception as e:
        logger.error(f"Executable demo generation failed: {e}")
        demo_files = []
        controls_guide = ""
    
    # Generate controls guide if not from README
    if not controls_guide:
        controls_guide = f"""# {project['name']} - Demo Controls

## Movement
- W/A/S/D or Arrow Keys: Move
- Mouse: Look around
- Space: Jump
- Shift: Sprint
- Ctrl: Crouch

## Interaction
- E: Interact
- Left Click: Primary action
- Right Click: Secondary action
- Tab: Open inventory
- Esc: Pause menu

## Systems Included
{chr(10).join([f'- {s}' for s in systems_built])}

## How to Play
1. Web Demo: Open demo/web_demo.html in browser
2. Executable: Build using the provided configuration files
"""
    
    # Determine demo features
    demo_features = []
    for system in systems_built:
        if "player" in system.lower() or "controller" in system.lower():
            demo_features.append("Player movement and controls")
        if "combat" in system.lower():
            demo_features.append("Combat system showcase")
        if "inventory" in system.lower() or "item" in system.lower():
            demo_features.append("Inventory management")
        if "ai" in system.lower() or "npc" in system.lower():
            demo_features.append("AI/NPC interactions")
        if "ui" in system.lower():
            demo_features.append("UI framework demo")
        if "world" in system.lower() or "terrain" in system.lower():
            demo_features.append("World exploration")
        if "quest" in system.lower():
            demo_features.append("Quest system")
        if "dialogue" in system.lower():
            demo_features.append("Dialogue interactions")
    
    if not demo_features:
        demo_features = ["Core gameplay loop", "Basic controls", "System showcase"]
    
    # Update demo record
    await db.demos.update_one(
        {"id": demo.id},
        {"$set": {
            "status": "ready",
            "web_demo_html": web_demo_html,
            "systems_included": systems_built,
            "demo_features": list(set(demo_features)),
            "controls_guide": controls_guide,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Update build with demo info
    await db.builds.update_one(
        {"id": build_id},
        {"$set": {"demo_id": demo.id, "demo_status": "ready"}}
    )
    
    # Final war room message
    await broadcast_to_war_room(
        build["project_id"],
        "COMMANDER",
        f"🎉 PROJECT COMPLETE! Playable demo ready!\n\n🌐 Web Demo: Open demo/web_demo.html\n📦 Executable: Use demo build configs\n\nFeatures: {', '.join(demo_features[:5])}\n\nYour project is ready to play!",
        "progress",
        build_id
    )
    
    return demo

@api_router.get("/demos/{project_id}")
async def get_project_demos(project_id: str):
    """Get all demos for a project"""
    demos = await db.demos.find({"project_id": project_id}, {"_id": 0}).sort("created_at", -1).to_list(10)
    return demos

@api_router.get("/demos/{project_id}/latest")
async def get_latest_demo(project_id: str):
    """Get the latest demo for a project"""
    demo = await db.demos.find_one(
        {"project_id": project_id, "status": "ready"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    return demo

@api_router.get("/demos/{project_id}/web")
async def get_web_demo(project_id: str):
    """Get the web demo HTML for embedding"""
    demo = await db.demos.find_one(
        {"project_id": project_id, "status": "ready"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    if not demo or not demo.get("web_demo_html"):
        raise HTTPException(status_code=404, detail="No web demo available")
    
    return HTMLResponse(content=demo["web_demo_html"])

@api_router.post("/demos/{project_id}/regenerate")
async def regenerate_demo(project_id: str, background_tasks: BackgroundTasks):
    """Regenerate demo for a completed build"""
    # Find the latest completed build
    build = await db.builds.find_one(
        {"project_id": project_id, "status": "completed"},
        {"_id": 0},
        sort=[("completed_at", -1)]
    )
    if not build:
        raise HTTPException(status_code=404, detail="No completed build found")
    
    # Delete existing demos for this build
    await db.demos.delete_many({"build_id": build["id"]})
    
    # Regenerate
    background_tasks.add_task(generate_playable_demo, build["id"])
    
    return {"success": True, "message": "Demo regeneration started", "build_id": build["id"]}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
