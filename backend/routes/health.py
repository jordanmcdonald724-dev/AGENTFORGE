from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()


@router.get("/")
async def root():
    return {
        "message": "AgentForge Development Studio API",
        "version": "4.5.0",
        "features": [
            "streaming", "delegation", "image_generation", "github_push",
            "agent_chains", "quick_actions", "live_preview", "agent_memory",
            "custom_actions", "project_duplicate", "multi_file_refactor",
            "simulation_mode", "war_room", "autonomous_builds", "open_world_systems",
            "build_scheduling", "playable_demos", "blueprint_scripting",
            "build_queue", "realtime_collaboration", "notifications",
            "audio_generation", "one_click_deploy", "build_sandbox",
            "asset_pipeline", "project_autopsy", "self_debugging_loop",
            "time_machine", "idea_engine", "system_visualization", "build_farm",
            "one_click_saas", "self_expanding_agents", "goal_loop",
            "knowledge_graph", "multi_future_build", "autonomous_refactor",
            "mission_control", "deployment_pipeline", "system_modules",
            "reality_pipeline"
        ]
    }


@router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
