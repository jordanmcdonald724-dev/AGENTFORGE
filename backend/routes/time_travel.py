"""
Time Travel Debugging - Project state history and rollback
Track project changes and enable reverting to any previous state
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
from core.database import db
import uuid
import json

router = APIRouter(prefix="/time-travel", tags=["time-travel"])


class Snapshot(BaseModel):
    project_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    auto: bool = False


class RollbackRequest(BaseModel):
    project_id: str
    snapshot_id: str
    confirm: bool = False


@router.post("/snapshot")
async def create_snapshot(snapshot: Snapshot):
    """Create a snapshot of the current project state"""
    
    # Get project
    project = await db.projects.find_one({"id": snapshot.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all project files
    files = await db.files.find(
        {"project_id": snapshot.project_id},
        {"_id": 0}
    ).to_list(1000)
    
    # Get project tasks
    tasks = await db.tasks.find(
        {"project_id": snapshot.project_id},
        {"_id": 0}
    ).to_list(500)
    
    # Get project images
    images = await db.images.find(
        {"project_id": snapshot.project_id},
        {"_id": 0}
    ).to_list(100)
    
    # Calculate snapshot size
    total_size = sum(len(f.get("content", "")) for f in files)
    
    # Create snapshot
    snapshot_id = str(uuid.uuid4())
    snapshot_record = {
        "id": snapshot_id,
        "project_id": snapshot.project_id,
        "name": snapshot.name or f"Snapshot {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
        "description": snapshot.description,
        "auto": snapshot.auto,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project_state": project,
        "files": files,
        "tasks": tasks,
        "images": [{"id": img.get("id"), "filename": img.get("filename")} for img in images],
        "stats": {
            "file_count": len(files),
            "task_count": len(tasks),
            "image_count": len(images),
            "total_size_bytes": total_size
        }
    }
    
    await db.snapshots.insert_one(snapshot_record)
    
    # Update snapshot count on project
    await db.projects.update_one(
        {"id": snapshot.project_id},
        {"$inc": {"snapshot_count": 1}}
    )
    
    return {
        "snapshot_id": snapshot_id,
        "name": snapshot_record["name"],
        "created_at": snapshot_record["created_at"],
        "stats": snapshot_record["stats"]
    }


@router.get("/snapshots/{project_id}")
async def list_snapshots(project_id: str):
    """List all snapshots for a project"""
    snapshots = await db.snapshots.find(
        {"project_id": project_id},
        {
            "_id": 0,
            "id": 1,
            "name": 1,
            "description": 1,
            "auto": 1,
            "created_at": 1,
            "stats": 1
        }
    ).sort("created_at", -1).to_list(100)
    
    return snapshots


@router.get("/snapshot/{snapshot_id}")
async def get_snapshot(snapshot_id: str):
    """Get detailed snapshot information"""
    snapshot = await db.snapshots.find_one({"id": snapshot_id}, {"_id": 0})
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snapshot


@router.post("/compare")
async def compare_snapshots(snapshot_id_1: str, snapshot_id_2: str):
    """Compare two snapshots to see differences"""
    
    snap1 = await db.snapshots.find_one({"id": snapshot_id_1}, {"_id": 0})
    snap2 = await db.snapshots.find_one({"id": snapshot_id_2}, {"_id": 0})
    
    if not snap1 or not snap2:
        raise HTTPException(status_code=404, detail="One or both snapshots not found")
    
    # Compare files
    files1 = {f["filepath"]: f for f in snap1.get("files", [])}
    files2 = {f["filepath"]: f for f in snap2.get("files", [])}
    
    added = [f for f in files2.keys() if f not in files1]
    removed = [f for f in files1.keys() if f not in files2]
    modified = [
        f for f in files1.keys() 
        if f in files2 and files1[f].get("content") != files2[f].get("content")
    ]
    
    return {
        "snapshot_1": {
            "id": snapshot_id_1,
            "name": snap1.get("name"),
            "created_at": snap1.get("created_at")
        },
        "snapshot_2": {
            "id": snapshot_id_2,
            "name": snap2.get("name"),
            "created_at": snap2.get("created_at")
        },
        "diff": {
            "files_added": added,
            "files_removed": removed,
            "files_modified": modified,
            "total_changes": len(added) + len(removed) + len(modified)
        }
    }


@router.post("/rollback")
async def rollback_to_snapshot(request: RollbackRequest, background_tasks: BackgroundTasks):
    """Rollback project to a previous snapshot"""
    
    if not request.confirm:
        raise HTTPException(
            status_code=400, 
            detail="Rollback requires confirmation. Set confirm=true to proceed."
        )
    
    # Get snapshot
    snapshot = await db.snapshots.find_one({"id": request.snapshot_id}, {"_id": 0})
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    if snapshot["project_id"] != request.project_id:
        raise HTTPException(status_code=400, detail="Snapshot does not belong to this project")
    
    # Create a pre-rollback snapshot first
    pre_rollback_snapshot = Snapshot(
        project_id=request.project_id,
        name=f"Pre-rollback backup {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
        description=f"Automatic backup before rollback to {snapshot.get('name')}",
        auto=True
    )
    await create_snapshot(pre_rollback_snapshot)
    
    # Create rollback job
    rollback_id = str(uuid.uuid4())
    rollback_job = {
        "id": rollback_id,
        "project_id": request.project_id,
        "snapshot_id": request.snapshot_id,
        "snapshot_name": snapshot.get("name"),
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "changes": []
    }
    
    await db.rollback_jobs.insert_one(rollback_job)
    
    # Execute rollback in background
    background_tasks.add_task(execute_rollback, rollback_id, request.project_id, snapshot)
    
    return {
        "rollback_id": rollback_id,
        "status": "running",
        "message": f"Rolling back to '{snapshot.get('name')}'",
        "pre_rollback_snapshot_created": True
    }


async def execute_rollback(rollback_id: str, project_id: str, snapshot: dict):
    """Execute the rollback operation"""
    
    changes = []
    
    try:
        # Delete current files
        delete_result = await db.files.delete_many({"project_id": project_id})
        changes.append(f"Removed {delete_result.deleted_count} current files")
        
        # Restore files from snapshot
        snapshot_files = snapshot.get("files", [])
        if snapshot_files:
            # Update file IDs to avoid conflicts
            for f in snapshot_files:
                f["id"] = str(uuid.uuid4())
                f["restored_from_snapshot"] = snapshot["id"]
                f["restored_at"] = datetime.now(timezone.utc).isoformat()
            
            await db.files.insert_many(snapshot_files)
            changes.append(f"Restored {len(snapshot_files)} files from snapshot")
        
        # Restore tasks
        await db.tasks.delete_many({"project_id": project_id})
        snapshot_tasks = snapshot.get("tasks", [])
        if snapshot_tasks:
            for t in snapshot_tasks:
                t["id"] = str(uuid.uuid4())
            await db.tasks.insert_many(snapshot_tasks)
            changes.append(f"Restored {len(snapshot_tasks)} tasks")
        
        # Update rollback job status
        await db.rollback_jobs.update_one(
            {"id": rollback_id},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "changes": changes
                }
            }
        )
        
        # Update project with rollback info
        await db.projects.update_one(
            {"id": project_id},
            {
                "$set": {
                    "last_rollback": {
                        "rollback_id": rollback_id,
                        "snapshot_id": snapshot["id"],
                        "snapshot_name": snapshot.get("name"),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }
            }
        )
        
    except Exception as e:
        await db.rollback_jobs.update_one(
            {"id": rollback_id},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e),
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "changes": changes
                }
            }
        )


@router.get("/rollback/{rollback_id}")
async def get_rollback_status(rollback_id: str):
    """Get status of a rollback operation"""
    job = await db.rollback_jobs.find_one({"id": rollback_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Rollback job not found")
    return job


@router.get("/history/{project_id}")
async def get_project_timeline(project_id: str):
    """Get complete project timeline including snapshots and rollbacks"""
    
    # Get snapshots
    snapshots = await db.snapshots.find(
        {"project_id": project_id},
        {"_id": 0, "id": 1, "name": 1, "created_at": 1, "auto": 1, "stats": 1}
    ).sort("created_at", -1).to_list(50)
    
    # Get rollbacks
    rollbacks = await db.rollback_jobs.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("started_at", -1).to_list(20)
    
    # Combine into timeline
    timeline = []
    
    for snap in snapshots:
        timeline.append({
            "type": "snapshot",
            "timestamp": snap.get("created_at"),
            "data": snap
        })
    
    for rollback in rollbacks:
        timeline.append({
            "type": "rollback",
            "timestamp": rollback.get("started_at"),
            "data": rollback
        })
    
    # Sort by timestamp
    timeline.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return {
        "project_id": project_id,
        "total_snapshots": len(snapshots),
        "total_rollbacks": len(rollbacks),
        "timeline": timeline
    }


@router.delete("/snapshot/{snapshot_id}")
async def delete_snapshot(snapshot_id: str):
    """Delete a snapshot"""
    result = await db.snapshots.delete_one({"id": snapshot_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return {"status": "deleted", "snapshot_id": snapshot_id}
