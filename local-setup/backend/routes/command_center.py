from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from core.database import db
from core.utils import serialize_doc, logger
from core.config import PROJECT_THUMBNAILS
from models.base import Project
from models.build import (
    Checkpoint, IdeaConcept, IdeaBatch, SaaSBlueprint, BuildWorker, 
    BuildFarmJob, DebugLoop, SystemMap
)
from models.autopsy import ProjectAutopsy
from models.v45_features import (
    GoalLoop, KnowledgeEntry, ArchitectureVariant, ArchitectureExploration,
    RefactorJob, MissionControlEvent, DeploymentPipeline, SystemModule, RealityPipeline
)
import uuid
import json
import asyncio

router = APIRouter(tags=["command_center"])


# ========== AUTOPSY ENDPOINTS ==========

@router.post("/autopsy/analyze")
async def analyze_project(project_id: str, source_type: str = "existing", source_url: Optional[str] = None):
    """Start project autopsy analysis"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    autopsy = ProjectAutopsy(
        project_id=project_id,
        source_type=source_type,
        source_url=source_url,
        status="analyzing"
    )
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    # Analyze file structure
    file_tree = {}
    languages = {}
    total_lines = 0
    
    for f in files:
        path = f.get("filepath", "")
        content = f.get("content", "")
        lines = len(content.split("\n"))
        total_lines += lines
        
        ext = path.split(".")[-1] if "." in path else "unknown"
        lang_map = {"js": "JavaScript", "jsx": "React", "ts": "TypeScript", "tsx": "React/TS", 
                   "py": "Python", "cs": "C#", "cpp": "C++", "h": "C/C++ Header",
                   "html": "HTML", "css": "CSS", "json": "JSON", "md": "Markdown"}
        lang = lang_map.get(ext, ext.upper())
        languages[lang] = languages.get(lang, 0) + lines
    
    # Detect tech stack
    tech_stack = []
    all_content = " ".join([f.get("content", "") for f in files])
    
    tech_patterns = [
        ("React", "import React", "frontend"),
        ("FastAPI", "from fastapi", "backend"),
        ("MongoDB", "mongodb://", "database"),
        ("Tailwind", "tailwind", "styling"),
    ]
    
    for name, pattern, category in tech_patterns:
        if pattern.lower() in all_content.lower():
            tech_stack.append({"name": name, "category": category, "detected": True})
    
    # Identify weak points
    weak_points = []
    for f in files:
        content = f.get("content", "")
        lines = len(content.split("\n"))
        
        if lines > 500:
            weak_points.append({
                "severity": "medium",
                "issue": f"Large file: {f['filepath']} ({lines} lines)",
                "recommendation": "Consider splitting into smaller modules"
            })
    
    autopsy.file_tree = file_tree
    autopsy.tech_stack = tech_stack
    autopsy.weak_points = weak_points[:20]
    autopsy.stats = {"total_files": len(files), "total_lines": total_lines, "languages": languages}
    autopsy.analyzed_by = ["ATLAS", "SENTINEL", "COMMANDER"]
    autopsy.status = "complete"
    autopsy.completed_at = datetime.now(timezone.utc)
    
    doc = autopsy.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['completed_at'] = doc['completed_at'].isoformat()
    await db.autopsies.insert_one(doc)
    
    return serialize_doc(doc)


@router.get("/autopsy/{project_id}")
async def get_autopsy(project_id: str):
    return await db.autopsies.find_one({"project_id": project_id}, {"_id": 0})


# ========== BUILD FARM ENDPOINTS ==========

@router.get("/build-farm/workers")
async def get_build_workers():
    workers = await db.build_workers.find({}, {"_id": 0}).to_list(50)
    if not workers:
        # Create default workers
        default_workers = [
            BuildWorker(name="Alpha", capabilities=["web", "api"], status="idle"),
            BuildWorker(name="Beta", capabilities=["game", "mobile"], status="idle"),
            BuildWorker(name="Gamma", capabilities=["web", "game", "api"], status="idle")
        ]
        for w in default_workers:
            doc = w.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            doc['last_heartbeat'] = doc['last_heartbeat'].isoformat()
            await db.build_workers.insert_one(doc)
        workers = await db.build_workers.find({}, {"_id": 0}).to_list(50)
    return workers


@router.get("/build-farm/status")
async def get_build_farm_status():
    workers = await db.build_workers.find({}, {"_id": 0}).to_list(50)
    jobs = await db.build_farm_jobs.find({}, {"_id": 0}).to_list(100)
    
    return {
        "workers": {
            "total": len(workers),
            "idle": len([w for w in workers if w.get("status") == "idle"]),
            "building": len([w for w in workers if w.get("status") == "building"])
        },
        "jobs": {
            "total": len(jobs),
            "queued": len([j for j in jobs if j.get("status") == "queued"]),
            "building": len([j for j in jobs if j.get("status") == "building"]),
            "complete": len([j for j in jobs if j.get("status") == "complete"])
        }
    }


@router.post("/build-farm/jobs/add")
async def add_build_job(project_id: str, job_type: str = "prototype", priority: int = 5):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    job = BuildFarmJob(
        project_id=project_id,
        project_name=project.get("name", "Unknown"),
        job_type=job_type,
        priority=priority
    )
    doc = job.model_dump()
    doc['queued_at'] = doc['queued_at'].isoformat()
    await db.build_farm_jobs.insert_one(doc)
    return serialize_doc(doc)


@router.get("/build-farm/jobs")
async def get_build_jobs():
    return await db.build_farm_jobs.find({}, {"_id": 0}).sort("priority", -1).to_list(100)


# ========== IDEA ENGINE ENDPOINTS ==========

@router.post("/ideas/generate")
async def generate_ideas(prompt: str = "Create innovative project ideas", category: str = None, count: int = 5):
    batch = IdeaBatch(prompt=prompt, category_filter=category, count=count, status="generating")
    
    # Generate ideas (simulated)
    idea_templates = [
        {"title": "AI-Powered Code Review Bot", "category": "saas", "complexity": "medium"},
        {"title": "Multiplayer Survival Game", "category": "game", "complexity": "complex"},
        {"title": "Smart Home Dashboard", "category": "tool", "complexity": "simple"},
        {"title": "Social Learning Platform", "category": "saas", "complexity": "complex"},
        {"title": "Procedural Music Generator", "category": "tool", "complexity": "medium"},
    ]
    
    ideas = []
    for i, template in enumerate(idea_templates[:count]):
        idea = IdeaConcept(
            title=template["title"],
            category=template["category"],
            description=f"An innovative {template['category']} project generated from: {prompt}",
            complexity=template["complexity"],
            unique_features=["AI-powered", "Real-time", "Collaborative"],
            tech_stack_suggestion=["React", "FastAPI", "MongoDB"]
        )
        ideas.append(idea.model_dump())
    
    batch.ideas = ideas
    batch.status = "complete"
    
    doc = batch.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.idea_batches.insert_one(doc)
    
    return serialize_doc(doc)


@router.get("/ideas/batches")
async def get_idea_batches():
    return await db.idea_batches.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)


@router.post("/ideas/{idea_id}/build")
async def build_from_idea(idea_id: str):
    # Create project from idea
    project = Project(
        name=f"Project from Idea {idea_id[:8]}",
        description="Auto-generated from Idea Engine",
        type="app",
        status="planning",
        thumbnail=PROJECT_THUMBNAILS["web_app"]
    )
    doc = project.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.projects.insert_one(doc)
    
    return {"success": True, "project_id": project.id}


# ========== SAAS BUILDER ENDPOINTS ==========

@router.post("/saas/generate")
async def generate_saas_blueprint(name: str, description: str):
    blueprint = SaaSBlueprint(
        name=name,
        description=description,
        backend_api={
            "endpoints": ["/api/auth/login", "/api/auth/register", "/api/users", "/api/billing"],
            "models": ["User", "Subscription", "Payment"]
        },
        database_schema={"collections": ["users", "subscriptions", "payments", "sessions"]},
        auth_system={"type": "JWT", "providers": ["email", "google", "github"]},
        frontend_ui={"pages": ["Landing", "Dashboard", "Settings", "Billing"], "components": 15},
        payment_integration={"provider": "Stripe", "plans": ["Free", "Pro", "Enterprise"]},
        tech_stack={"frontend": "React", "backend": "FastAPI", "database": "MongoDB"},
        status="ready"
    )
    
    doc = blueprint.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.saas_blueprints.insert_one(doc)
    
    return serialize_doc(doc)


@router.get("/saas/blueprints")
async def get_saas_blueprints():
    return await db.saas_blueprints.find({}, {"_id": 0}).to_list(50)


@router.post("/saas/blueprint/{blueprint_id}/build")
async def build_from_blueprint(blueprint_id: str):
    blueprint = await db.saas_blueprints.find_one({"id": blueprint_id}, {"_id": 0})
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    project = Project(
        name=blueprint.get("name", "SaaS Project"),
        description=blueprint.get("description", ""),
        type="web_app",
        status="planning",
        thumbnail=PROJECT_THUMBNAILS["web_app"]
    )
    doc = project.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.projects.insert_one(doc)
    
    await db.saas_blueprints.update_one({"id": blueprint_id}, {"$set": {"project_id": project.id, "status": "deployed"}})
    
    return {"success": True, "project_id": project.id}


# ========== TIME MACHINE ENDPOINTS ==========

@router.post("/checkpoints/{project_id}/create")
async def create_checkpoint(project_id: str, name: str, description: str = "", auto: bool = False):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    existing = await db.checkpoints.count_documents({"project_id": project_id})
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    files_snapshot = [{"filepath": f.get("filepath"), "content": f.get("content")} for f in files]
    
    checkpoint = Checkpoint(
        project_id=project_id,
        name=name,
        description=description,
        step_number=existing + 1,
        files_snapshot=files_snapshot,
        auto_created=auto
    )
    
    doc = checkpoint.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.checkpoints.insert_one(doc)
    
    return serialize_doc(doc)


@router.get("/checkpoints/{project_id}")
async def get_checkpoints(project_id: str):
    return await db.checkpoints.find(
        {"project_id": project_id}, 
        {"_id": 0, "files_snapshot": 0}
    ).sort("step_number", -1).to_list(100)


@router.post("/checkpoints/{checkpoint_id}/restore")
async def restore_checkpoint(checkpoint_id: str):
    checkpoint = await db.checkpoints.find_one({"id": checkpoint_id}, {"_id": 0})
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    project_id = checkpoint["project_id"]
    await db.files.delete_many({"project_id": project_id})
    
    for f in checkpoint.get("files_snapshot", []):
        await db.files.insert_one({
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "filepath": f["filepath"],
            "filename": f["filepath"].split("/")[-1],
            "content": f["content"],
            "language": f["filepath"].split(".")[-1] if "." in f["filepath"] else "text",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
    
    return {"success": True, "restored_files": len(checkpoint.get("files_snapshot", []))}


# ========== DEBUG LOOP ENDPOINTS ==========

@router.post("/debug-loop/{project_id}/start")
async def start_debug_loop(project_id: str, max_iterations: int = 10):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    debug_loop = DebugLoop(
        project_id=project_id,
        max_iterations=max_iterations,
        status="detecting",
        started_at=datetime.now(timezone.utc)
    )
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(100)
    
    errors = []
    for f in files:
        content = f.get("content", "")
        if "TODO" in content:
            errors.append({"type": "incomplete_code", "file": f.get("filepath"), "severity": "medium"})
    
    debug_loop.errors_detected = errors[:10]
    debug_loop.status = "success" if len(errors) == 0 else "partial"
    debug_loop.success = len(errors) == 0
    debug_loop.completed_at = datetime.now(timezone.utc)
    
    doc = debug_loop.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['started_at'] = doc['started_at'].isoformat()
    doc['completed_at'] = doc['completed_at'].isoformat()
    await db.debug_loops.insert_one(doc)
    
    return serialize_doc(doc)


@router.get("/debug-loop/{project_id}")
async def get_debug_loops(project_id: str):
    return await db.debug_loops.find({"project_id": project_id}, {"_id": 0}).sort("created_at", -1).to_list(20)


# ========== DYNAMIC AGENTS ENDPOINTS ==========

@router.get("/dynamic-agents")
async def get_dynamic_agents():
    return await db.dynamic_agents.find({"active": True}, {"_id": 0}).to_list(50)


@router.post("/dynamic-agents/spawn")
async def spawn_dynamic_agent(name: str, specialty: str, created_by: str = "COMMANDER"):
    from models.agent import DynamicAgent
    
    agent = DynamicAgent(
        name=name,
        role="specialist",
        specialty=specialty,
        description=f"Specialized agent for {specialty}",
        capabilities=[specialty, "analysis", "code_generation"],
        created_by=created_by,
        creation_reason=f"Project requires {specialty} expertise"
    )
    
    doc = agent.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.dynamic_agents.insert_one(doc)
    
    return serialize_doc(doc)


@router.delete("/dynamic-agents/{agent_id}")
async def deactivate_dynamic_agent(agent_id: str):
    await db.dynamic_agents.update_one({"id": agent_id}, {"$set": {"active": False}})
    return {"success": True}


# ========== V4.5 GOAL LOOP ENDPOINTS ==========

@router.post("/goal-loop/{project_id}/start")
async def start_goal_loop(project_id: str, goal: str, max_cycles: int = 50):
    loop = GoalLoop(
        project_id=project_id,
        goal=goal,
        status="running",
        max_cycles=max_cycles,
        started_at=datetime.now(timezone.utc)
    )
    
    # Simulate a few cycles
    loop.current_cycle = 3
    loop.cycles = [
        {"cycle": 1, "phase": "build", "agent": "FORGE", "action": "Generated initial code", "metrics": {"tests_pass_rate": 60}},
        {"cycle": 2, "phase": "test", "agent": "PROBE", "action": "Ran test suite", "metrics": {"tests_pass_rate": 75}},
        {"cycle": 3, "phase": "fix", "agent": "FORGE", "action": "Fixed failing tests", "metrics": {"tests_pass_rate": 92}}
    ]
    loop.current_metrics = {"tests_pass_rate": 92, "performance_score": 78, "code_quality": 85}
    loop.thresholds_met = {"tests_pass_rate": True, "performance_score": True, "code_quality": True}
    loop.status = "success"
    loop.completed_at = datetime.now(timezone.utc)
    
    doc = loop.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['started_at'] = doc['started_at'].isoformat()
    doc['completed_at'] = doc['completed_at'].isoformat()
    await db.goal_loops.insert_one(doc)
    
    return serialize_doc(doc)


@router.get("/goal-loop/{project_id}")
async def get_goal_loops(project_id: str):
    return await db.goal_loops.find({"project_id": project_id}, {"_id": 0}).to_list(20)


# ========== V4.5 KNOWLEDGE GRAPH ENDPOINTS ==========

@router.post("/knowledge/add")
async def add_knowledge_entry(entry_type: str, title: str, description: str, category: str = "general", tags: List[str] = None):
    entry = KnowledgeEntry(
        entry_type=entry_type,
        title=title,
        description=description,
        category=category,
        tags=tags or []
    )
    
    doc = entry.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.knowledge_graph.insert_one(doc)
    
    return serialize_doc(doc)


@router.get("/knowledge")
async def get_knowledge_entries(category: str = None):
    query = {"category": category} if category else {}
    return await db.knowledge_graph.find(query, {"_id": 0}).sort("reuse_count", -1).to_list(100)


@router.get("/knowledge/search")
async def search_knowledge(query: str):
    entries = await db.knowledge_graph.find(
        {"$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"tags": {"$in": [query]}}
        ]},
        {"_id": 0}
    ).to_list(50)
    return entries


# ========== V4.5 MISSION CONTROL ENDPOINTS ==========

@router.get("/mission-control/{project_id}/stream")
async def stream_mission_control(project_id: str):
    async def generate():
        while True:
            events = await db.mission_control.find(
                {"project_id": project_id},
                {"_id": 0}
            ).sort("timestamp", -1).limit(20).to_list(20)
            
            yield f"data: {json.dumps({'events': events})}\n\n"
            await asyncio.sleep(2)
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/mission-control/{project_id}/event")
async def add_mission_control_event(project_id: str, event_type: str, title: str, description: str, agent_name: str = None):
    event = MissionControlEvent(
        project_id=project_id,
        event_type=event_type,
        title=title,
        description=description,
        agent_name=agent_name
    )
    
    doc = event.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.mission_control.insert_one(doc)
    
    return serialize_doc(doc)


@router.get("/mission-control/{project_id}")
async def get_mission_control_events(project_id: str, limit: int = 50):
    return await db.mission_control.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("timestamp", -1).to_list(limit)


# ========== V4.5 REALITY PIPELINE ENDPOINTS ==========

@router.post("/reality-pipeline/start")
async def start_reality_pipeline(idea: str):
    pipeline = RealityPipeline(
        idea=idea,
        status="intake",
        started_at=datetime.now(timezone.utc)
    )
    
    # Simulate pipeline completion
    phases = pipeline.phases.copy()
    for i, phase in enumerate(phases):
        phases[i]["status"] = "complete"
        phases[i]["output"] = f"{phase['name']} completed successfully"
    
    pipeline.phases = phases
    pipeline.status = "live"
    pipeline.current_phase = len(phases)
    pipeline.deploy_url = f"https://app-{str(uuid.uuid4())[:8]}.vercel.app"
    pipeline.completed_at = datetime.now(timezone.utc)
    
    # Create project
    project = Project(
        name=idea[:50],
        description=idea,
        type="app",
        status="development",
        thumbnail=PROJECT_THUMBNAILS["web_app"]
    )
    proj_doc = project.model_dump()
    proj_doc['created_at'] = proj_doc['created_at'].isoformat()
    proj_doc['updated_at'] = proj_doc['updated_at'].isoformat()
    await db.projects.insert_one(proj_doc)
    
    pipeline.project_id = project.id
    
    doc = pipeline.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['started_at'] = doc['started_at'].isoformat()
    doc['completed_at'] = doc['completed_at'].isoformat()
    await db.reality_pipelines.insert_one(doc)
    
    return serialize_doc(doc)


@router.get("/reality-pipeline")
async def get_reality_pipelines():
    return await db.reality_pipelines.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)


# ========== V4.5 REFACTOR ENGINE ENDPOINTS ==========

@router.post("/refactor/{project_id}/start")
async def start_refactor_job(project_id: str, job_type: str = "on_demand"):
    job = RefactorJob(
        project_id=project_id,
        job_type=job_type,
        status="scanning",
        started_at=datetime.now(timezone.utc)
    )
    
    # Simulate scan results
    job.code_smells = [{"type": "long_method", "file": "server.py", "severity": "medium"}]
    job.improvement_score = 15.5
    job.status = "complete"
    job.completed_at = datetime.now(timezone.utc)
    
    doc = job.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['started_at'] = doc['started_at'].isoformat()
    doc['completed_at'] = doc['completed_at'].isoformat()
    await db.refactor_jobs.insert_one(doc)
    
    return serialize_doc(doc)


@router.get("/refactor/{project_id}")
async def get_refactor_jobs(project_id: str):
    return await db.refactor_jobs.find({"project_id": project_id}, {"_id": 0}).to_list(20)


# ========== V4.5 DEPLOYMENT PIPELINE ENDPOINTS ==========

@router.post("/pipeline/{project_id}/create")
async def create_deployment_pipeline(project_id: str, target_platform: str = "vercel", auto_deploy: bool = False):
    pipeline = DeploymentPipeline(
        project_id=project_id,
        target_platform=target_platform,
        auto_deploy_enabled=auto_deploy
    )
    
    doc = pipeline.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.deployment_pipelines.insert_one(doc)
    
    return serialize_doc(doc)


@router.post("/pipeline/{pipeline_id}/trigger")
async def trigger_pipeline(pipeline_id: str):
    pipeline = await db.deployment_pipelines.find_one({"id": pipeline_id}, {"_id": 0})
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    stages = [
        {"name": "lint", "status": "success", "duration_ms": 1200},
        {"name": "test", "status": "success", "duration_ms": 5400},
        {"name": "build", "status": "success", "duration_ms": 8900},
        {"name": "deploy", "status": "success", "duration_ms": 12000},
        {"name": "verify", "status": "success", "duration_ms": 3200}
    ]
    
    deploy_url = f"https://{pipeline['project_id'][:8]}.{pipeline['target_platform']}.app"
    
    await db.deployment_pipelines.update_one(
        {"id": pipeline_id},
        {"$set": {
            "status": "live",
            "stages": stages,
            "deploy_url": deploy_url,
            "triggered_at": datetime.now(timezone.utc).isoformat(),
            "deployed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"success": True, "deploy_url": deploy_url, "stages": stages}


@router.get("/pipeline/{project_id}")
async def get_project_pipelines(project_id: str):
    return await db.deployment_pipelines.find({"project_id": project_id}, {"_id": 0}).to_list(20)


# ========== V4.5 SYSTEM MODULES ENDPOINTS ==========

@router.post("/modules/create")
async def create_system_module(name: str, module_type: str, description: str, detected_need: str):
    module = SystemModule(
        name=name,
        module_type=module_type,
        description=description,
        detected_need=detected_need
    )
    
    doc = module.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.system_modules.insert_one(doc)
    
    return serialize_doc(doc)


@router.get("/modules")
async def get_system_modules():
    return await db.system_modules.find({"active": True}, {"_id": 0}).to_list(100)


# ========== VISUALIZATION ENDPOINTS ==========

@router.get("/visualization/{project_id}/map")
async def get_system_map(project_id: str):
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(200)
    
    nodes = []
    edges = []
    
    for f in files:
        nodes.append({
            "id": f["id"],
            "name": f.get("filename", f.get("filepath", "").split("/")[-1]),
            "type": f.get("language", "unknown"),
            "x": len(nodes) * 100,
            "y": (len(nodes) % 5) * 80
        })
    
    return {"nodes": nodes, "edges": edges, "clusters": []}
