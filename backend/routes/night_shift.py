"""
Night Shift Mode - Autonomous overnight processing
Schedules and runs background tasks during off-hours
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from core.database import db
import uuid

router = APIRouter(prefix="/night-shift", tags=["night-shift"])


class NightShiftConfig(BaseModel):
    project_id: str
    enabled: bool = True
    start_hour: int = 22  # 10 PM
    end_hour: int = 6     # 6 AM
    tasks: List[str] = ["evolution_scan", "test_suite", "dependency_update", "backup"]
    auto_deploy: bool = False
    notification_email: Optional[str] = None


class NightShiftJob(BaseModel):
    project_id: str
    task_type: str
    priority: int = 1


NIGHT_SHIFT_TASKS = {
    "evolution_scan": {
        "name": "Evolution Scan",
        "description": "Full project optimization scan",
        "duration_estimate": "15-30 min",
        "icon": "🔍"
    },
    "test_suite": {
        "name": "Full Test Suite",
        "description": "Run complete test coverage",
        "duration_estimate": "20-45 min",
        "icon": "🧪"
    },
    "dependency_update": {
        "name": "Dependency Updates",
        "description": "Check and update dependencies",
        "duration_estimate": "10-20 min",
        "icon": "📦"
    },
    "backup": {
        "name": "Project Backup",
        "description": "Create full project snapshot",
        "duration_estimate": "5-10 min",
        "icon": "💾"
    },
    "performance_audit": {
        "name": "Performance Audit",
        "description": "Deep performance analysis",
        "duration_estimate": "30-60 min",
        "icon": "⚡"
    },
    "security_scan": {
        "name": "Security Scan",
        "description": "Vulnerability assessment",
        "duration_estimate": "20-40 min",
        "icon": "🛡️"
    },
    "code_cleanup": {
        "name": "Code Cleanup",
        "description": "Remove dead code, optimize imports",
        "duration_estimate": "15-30 min",
        "icon": "🧹"
    },
    "documentation_gen": {
        "name": "Documentation Generation",
        "description": "Auto-generate API docs",
        "duration_estimate": "10-15 min",
        "icon": "📚"
    }
}


@router.post("/configure")
async def configure_night_shift(config: NightShiftConfig):
    """Configure night shift for a project"""
    
    # Verify project exists
    project = await db.projects.find_one({"id": config.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Calculate next run time
    now = datetime.now(timezone.utc)
    next_run = now.replace(hour=config.start_hour, minute=0, second=0, microsecond=0)
    if next_run <= now:
        next_run += timedelta(days=1)
    
    # Save configuration
    night_shift_config = {
        "id": str(uuid.uuid4()),
        "project_id": config.project_id,
        "enabled": config.enabled,
        "start_hour": config.start_hour,
        "end_hour": config.end_hour,
        "tasks": config.tasks,
        "auto_deploy": config.auto_deploy,
        "notification_email": config.notification_email,
        "next_run": next_run.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_run": None,
        "total_runs": 0
    }
    
    # Upsert configuration
    await db.night_shift_configs.update_one(
        {"project_id": config.project_id},
        {"$set": night_shift_config},
        upsert=True
    )
    
    return {
        "status": "configured",
        "project_id": config.project_id,
        "enabled": config.enabled,
        "next_run": next_run.isoformat(),
        "tasks_scheduled": config.tasks
    }


@router.get("/config/{project_id}")
async def get_night_shift_config(project_id: str):
    """Get night shift configuration for a project"""
    config = await db.night_shift_configs.find_one(
        {"project_id": project_id},
        {"_id": 0}
    )
    
    if not config:
        return {
            "project_id": project_id,
            "enabled": False,
            "message": "Night shift not configured"
        }
    
    return config


@router.get("/tasks")
async def list_available_tasks():
    """List all available night shift tasks"""
    return NIGHT_SHIFT_TASKS


@router.post("/trigger/{project_id}")
async def trigger_night_shift(project_id: str, background_tasks: BackgroundTasks):
    """Manually trigger night shift for a project"""
    
    config = await db.night_shift_configs.find_one(
        {"project_id": project_id},
        {"_id": 0}
    )
    
    if not config:
        raise HTTPException(status_code=404, detail="Night shift not configured for this project")
    
    # Create night shift run
    run_id = str(uuid.uuid4())
    run = {
        "id": run_id,
        "project_id": project_id,
        "status": "running",
        "triggered_by": "manual",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "tasks": [],
        "completed_tasks": [],
        "failed_tasks": []
    }
    
    # Schedule tasks
    for task_name in config.get("tasks", []):
        task_info = NIGHT_SHIFT_TASKS.get(task_name, {})
        run["tasks"].append({
            "id": str(uuid.uuid4()),
            "name": task_name,
            "display_name": task_info.get("name", task_name),
            "status": "pending",
            "started_at": None,
            "completed_at": None
        })
    
    await db.night_shift_runs.insert_one(run)
    
    # Run in background
    background_tasks.add_task(execute_night_shift, run_id, project_id, config.get("tasks", []))
    
    return {
        "run_id": run_id,
        "status": "started",
        "tasks": len(config.get("tasks", [])),
        "message": "Night shift triggered manually"
    }


async def execute_night_shift(run_id: str, project_id: str, tasks: List[str]):
    """Execute night shift tasks"""
    import asyncio
    
    completed = []
    failed = []
    
    for task_name in tasks:
        task_id = str(uuid.uuid4())
        
        # Update task status to running
        await db.night_shift_runs.update_one(
            {"id": run_id, "tasks.name": task_name},
            {
                "$set": {
                    "tasks.$.status": "running",
                    "tasks.$.started_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        try:
            # Simulate task execution
            await asyncio.sleep(2)  # Simulated work
            
            result = {
                "task": task_name,
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "result": f"{task_name} completed successfully"
            }
            completed.append(result)
            
            # Update task status
            await db.night_shift_runs.update_one(
                {"id": run_id, "tasks.name": task_name},
                {
                    "$set": {
                        "tasks.$.status": "completed",
                        "tasks.$.completed_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
        except Exception as e:
            result = {
                "task": task_name,
                "status": "failed",
                "error": str(e)
            }
            failed.append(result)
            
            await db.night_shift_runs.update_one(
                {"id": run_id, "tasks.name": task_name},
                {
                    "$set": {
                        "tasks.$.status": "failed",
                        "tasks.$.error": str(e)
                    }
                }
            )
    
    # Update run completion
    await db.night_shift_runs.update_one(
        {"id": run_id},
        {
            "$set": {
                "status": "completed" if not failed else "completed_with_errors",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "completed_tasks": completed,
                "failed_tasks": failed,
                "summary": {
                    "total": len(tasks),
                    "completed": len(completed),
                    "failed": len(failed)
                }
            }
        }
    )
    
    # Update config with last run
    await db.night_shift_configs.update_one(
        {"project_id": project_id},
        {
            "$set": {"last_run": datetime.now(timezone.utc).isoformat()},
            "$inc": {"total_runs": 1}
        }
    )


@router.get("/runs/{project_id}")
async def get_night_shift_runs(project_id: str):
    """Get night shift run history for a project"""
    runs = await db.night_shift_runs.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("started_at", -1).to_list(20)
    
    return runs


@router.get("/run/{run_id}")
async def get_night_shift_run(run_id: str):
    """Get details of a specific night shift run"""
    run = await db.night_shift_runs.find_one({"id": run_id}, {"_id": 0})
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.delete("/config/{project_id}")
async def disable_night_shift(project_id: str):
    """Disable night shift for a project"""
    result = await db.night_shift_configs.update_one(
        {"project_id": project_id},
        {"$set": {"enabled": False}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Night shift config not found")
    
    return {"status": "disabled", "project_id": project_id}
