"""
AgentForge - AI Development Studio
Main server entry point - thin wrapper that imports modular routes
"""
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os
import logging

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AgentForge API",
    description="AI Development Studio - Operating System for Inventing Software",
    version="4.5.0"
)

# Import core database for shutdown handler
from core.database import client as mongo_client

# Import all route modules
try:
    # Core routes
    from routes.health import router as health_router
    from routes.projects import router as projects_router
    from routes.agents import router as agents_router
    from routes.tasks import router as tasks_router
    from routes.files import router as files_router
    from routes.images import router as images_router
    from routes.plans import router as plans_router
    from routes.chat import router as chat_router
    from routes.github import router as github_router
    
    # Feature routes
    from routes.builds import router as builds_router
    from routes.memory import router as memory_router
    from routes.chains import router as chains_router
    from routes.preview import router as preview_router
    from routes.refactor import router as refactor_router
    from routes.collaboration import router as collaboration_router
    from routes.sandbox import router as sandbox_router
    from routes.command_center import router as command_center_router
    
    # Infrastructure routes
    from routes.celery_routes import router as celery_router
    from routes.k8s import router as k8s_router
    from routes.notifications import router as notifications_router
    from routes.audio import router as audio_router
    from routes.deploy import router as deploy_router
    from routes.assets import router as assets_router
    from routes.blueprints import router as blueprints_router
    from routes.exploration import router as exploration_router
    
    # Labs experimental routes
    from routes.world_model import router as world_model_router
    from routes.software_dna import router as software_dna_router
    from routes.god_mode import router as god_mode_router
    from routes.discovery import router as discovery_router
    from routes.marketplace import router as marketplace_router
    
    # OS Phase 1-5 routes
    from routes.github_universe import router as github_universe_router
    from routes.cloud_deploy import router as cloud_deploy_router
    from routes.dev_env import router as dev_env_router
    from routes.asset_factory import router as asset_factory_router
    from routes.saas_factory import router as saas_factory_router
    from routes.game_engine import router as game_engine_router
    from routes.game_studio import router as game_studio_router
    from routes.knowledge_engine import router as knowledge_engine_router
    from routes.live_monitoring import router as live_monitoring_router
    from routes.self_improve import router as self_improve_router
    from routes.hardware import router as hardware_router
    from routes.agent_network import router as agent_network_router
    from routes.global_intelligence import router as global_intelligence_router
    from routes.voice import router as voice_router
    from routes.god_mode_v2 import router as god_mode_v2_router
    from routes.intelligence.core import router as intelligence_router
    
    # New Mission Control features
    from routes.websocket import router as websocket_router
    from routes.evolution import router as evolution_router
    from routes.night_shift import router as night_shift_router
    from routes.time_travel import router as time_travel_router
    
    # New P3 features
    from routes.unreal_engine import router as unreal_router
    from routes.research import router as research_router
    from routes.auto_deploy import router as auto_deploy_router
    from routes.ai_review import router as ai_review_router
    
    # Game Builder (Real UE5 + Unity builds)
    from routes.game_builder import router as game_builder_router
    
    # New feature routes
    from routes.mobile_builder import router as mobile_builder_router
    from routes.cloud_builder import router as cloud_builder_router
    
    # Register all routers with /api prefix
    # Core routes
    app.include_router(health_router, prefix="/api", tags=["health"])
    app.include_router(projects_router, prefix="/api", tags=["projects"])
    app.include_router(agents_router, prefix="/api", tags=["agents"])
    app.include_router(tasks_router, prefix="/api", tags=["tasks"])
    app.include_router(files_router, prefix="/api", tags=["files"])
    app.include_router(images_router, prefix="/api", tags=["images"])
    app.include_router(plans_router, prefix="/api", tags=["plans"])
    app.include_router(chat_router, prefix="/api", tags=["chat"])
    app.include_router(github_router, prefix="/api", tags=["github"])
    
    # Feature routes
    app.include_router(builds_router, prefix="/api", tags=["builds"])
    app.include_router(memory_router, prefix="/api", tags=["memory"])
    app.include_router(chains_router, prefix="/api", tags=["chains"])
    app.include_router(preview_router, prefix="/api", tags=["preview"])
    app.include_router(refactor_router, prefix="/api", tags=["refactor"])
    app.include_router(collaboration_router, prefix="/api", tags=["collaboration"])
    app.include_router(sandbox_router, prefix="/api", tags=["sandbox"])
    app.include_router(command_center_router, prefix="/api", tags=["command-center"])
    
    # Infrastructure routes
    app.include_router(celery_router, prefix="/api", tags=["celery"])
    app.include_router(k8s_router, prefix="/api", tags=["kubernetes"])
    app.include_router(notifications_router, prefix="/api", tags=["notifications"])
    app.include_router(audio_router, prefix="/api", tags=["audio"])
    app.include_router(deploy_router, prefix="/api", tags=["deploy"])
    app.include_router(assets_router, prefix="/api", tags=["assets"])
    app.include_router(blueprints_router, prefix="/api", tags=["blueprints"])
    app.include_router(exploration_router, prefix="/api", tags=["exploration"])
    
    # Labs experimental routes
    app.include_router(world_model_router, prefix="/api", tags=["world-model"])
    app.include_router(software_dna_router, prefix="/api", tags=["software-dna"])
    app.include_router(god_mode_router, prefix="/api", tags=["god-mode"])
    app.include_router(discovery_router, prefix="/api", tags=["discovery"])
    app.include_router(marketplace_router, prefix="/api", tags=["marketplace"])
    
    # OS Phase 1-5 routes
    app.include_router(github_universe_router, prefix="/api", tags=["github-universe"])
    app.include_router(cloud_deploy_router, prefix="/api", tags=["cloud-deploy"])
    app.include_router(dev_env_router, prefix="/api", tags=["dev-environment"])
    app.include_router(asset_factory_router, prefix="/api", tags=["asset-factory"])
    app.include_router(saas_factory_router, prefix="/api", tags=["saas-factory"])
    app.include_router(game_engine_router, prefix="/api", tags=["game-engine"])
    app.include_router(game_studio_router, prefix="/api", tags=["game-studio"])
    app.include_router(knowledge_engine_router, prefix="/api", tags=["knowledge-engine"])
    app.include_router(live_monitoring_router, prefix="/api", tags=["live-monitoring"])
    app.include_router(self_improve_router, prefix="/api", tags=["self-improve"])
    app.include_router(hardware_router, prefix="/api", tags=["hardware"])
    app.include_router(agent_network_router, prefix="/api", tags=["agent-network"])
    app.include_router(global_intelligence_router, prefix="/api", tags=["global-intelligence"])
    app.include_router(voice_router, prefix="/api", tags=["voice"])
    app.include_router(god_mode_v2_router, prefix="/api", tags=["god-mode-v2"])
    app.include_router(intelligence_router, prefix="/api", tags=["intelligence"])
    
    # New Mission Control features
    app.include_router(websocket_router, prefix="/api", tags=["websocket"])
    app.include_router(evolution_router, prefix="/api", tags=["evolution"])
    app.include_router(night_shift_router, prefix="/api", tags=["night-shift"])
    app.include_router(time_travel_router, prefix="/api", tags=["time-travel"])
    
    # New P3 features
    app.include_router(unreal_router, prefix="/api", tags=["unreal-engine"])
    app.include_router(research_router, prefix="/api", tags=["research"])
    app.include_router(auto_deploy_router, prefix="/api", tags=["auto-deploy"])
    app.include_router(ai_review_router, prefix="/api", tags=["ai-review"])
    
    # Game Builder (Real UE5 + Unity builds)
    app.include_router(game_builder_router, prefix="/api", tags=["game-builder"])
    
    # New feature routes
    app.include_router(mobile_builder_router, prefix="/api", tags=["mobile-builder"])
    app.include_router(cloud_builder_router, prefix="/api", tags=["cloud-builder"])
    
    logger.info("Successfully loaded all modular routers")
    
except Exception as e:
    logger.error(f"Failed to load routers: {e}")
    import traceback
    traceback.print_exc()
    raise

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    mongo_client.close()
