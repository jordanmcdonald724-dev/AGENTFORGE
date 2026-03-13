"""
Celery Task Queue Routes
========================
Routes for managing distributed build jobs via Celery.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from core.database import db
from core.utils import serialize_doc

router = APIRouter(prefix="/celery", tags=["celery"])


# Track in-memory jobs when Celery/Redis unavailable
_memory_jobs: Dict[str, Dict[str, Any]] = {}
_job_counter = 0


def _celery_available() -> bool:
    """Check if Celery is available"""
    try:
        from core.celery_tasks import celery_app
        return celery_app.control.ping(timeout=1.0) is not None
    except:
        return False


@router.post("/jobs/submit")
async def submit_celery_job(project_id: str, job_type: str = "build", priority: int = 5, config: dict = None):
    """Submit a job to the Celery queue"""
    global _job_counter
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    _job_counter += 1
    job_id = f"job-{_job_counter}-{project_id[:8]}"
    
    job = {
        "id": job_id,
        "project_id": project_id,
        "job_type": job_type,
        "priority": priority,
        "config": config or {},
        "status": "queued",
        "progress": 0,
        "result": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "started_at": None,
        "completed_at": None
    }
    
    if _celery_available():
        try:
            from core.celery_tasks import run_build_task
            task = run_build_task.apply_async(
                args=[project_id, job_type, config or {}],
                task_id=job_id,
                priority=priority
            )
            job["celery_task_id"] = task.id
        except Exception as e:
            job["error"] = str(e)
    
    _memory_jobs[job_id] = job
    await db.celery_jobs.insert_one(job)
    
    return serialize_doc(job)


@router.get("/jobs/{job_id}")
async def get_celery_job(job_id: str):
    """Get status of a Celery job"""
    job = await db.celery_jobs.find_one({"id": job_id}, {"_id": 0})
    if not job:
        job = _memory_jobs.get(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.post("/jobs/{job_id}/cancel")
async def cancel_celery_job(job_id: str):
    """Cancel a Celery job"""
    job = await db.celery_jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if _celery_available() and job.get("celery_task_id"):
        try:
            from core.celery_tasks import celery_app
            celery_app.control.revoke(job["celery_task_id"], terminate=True)
        except:
            pass
    
    await db.celery_jobs.update_one(
        {"id": job_id},
        {"$set": {"status": "cancelled", "completed_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if job_id in _memory_jobs:
        _memory_jobs[job_id]["status"] = "cancelled"
    
    return {"success": True}


@router.get("/stats")
async def get_celery_stats():
    """Get Celery queue statistics"""
    jobs = await db.celery_jobs.find({}, {"_id": 0}).to_list(1000)
    
    stats = {
        "celery_available": _celery_available(),
        "total_jobs": len(jobs),
        "queued": len([j for j in jobs if j.get("status") == "queued"]),
        "running": len([j for j in jobs if j.get("status") == "running"]),
        "completed": len([j for j in jobs if j.get("status") == "completed"]),
        "failed": len([j for j in jobs if j.get("status") == "failed"]),
        "cancelled": len([j for j in jobs if j.get("status") == "cancelled"])
    }
    
    if _celery_available():
        try:
            from core.celery_tasks import celery_app
            inspect = celery_app.control.inspect()
            active = inspect.active() or {}
            reserved = inspect.reserved() or {}
            stats["active_tasks"] = sum(len(tasks) for tasks in active.values())
            stats["reserved_tasks"] = sum(len(tasks) for tasks in reserved.values())
        except:
            pass
    
    return stats


@router.get("/workers")
async def get_celery_workers():
    """Get list of Celery workers"""
    workers = []
    
    if _celery_available():
        try:
            from core.celery_tasks import celery_app
            inspect = celery_app.control.inspect()
            stats = inspect.stats() or {}
            active = inspect.active() or {}
            
            for worker_name, worker_stats in stats.items():
                workers.append({
                    "name": worker_name,
                    "status": "online",
                    "pool": worker_stats.get("pool", {}),
                    "active_tasks": len(active.get(worker_name, [])),
                    "total_tasks": worker_stats.get("total", {})
                })
        except:
            pass
    
    return workers
