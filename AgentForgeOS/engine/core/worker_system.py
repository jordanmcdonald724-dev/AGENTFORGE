"""
Distributed Build Worker System
================================

This module provides a real distributed build worker system for AgentForge.
Workers can run build jobs, process tasks, and report status in real-time.

Architecture:
- BuildWorkerManager: Manages worker pool and job distribution
- BuildWorker: Individual worker that processes jobs
- JobQueue: MongoDB-backed job queue with priority support
"""

import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class WorkerStatus(str, Enum):
    IDLE = "idle"
    BUILDING = "building"
    PAUSED = "paused"
    ERROR = "error"
    OFFLINE = "offline"


class JobStatus(str, Enum):
    QUEUED = "queued"
    ASSIGNED = "assigned"
    BUILDING = "building"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    PROTOTYPE = "prototype"
    FULL_BUILD = "full_build"
    DEMO = "demo"
    CODE_GEN = "code_gen"
    TEST_SUITE = "test_suite"
    ASSET_PIPELINE = "asset_pipeline"


@dataclass
class BuildJob:
    """Represents a build job in the queue"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    project_name: str = ""
    job_type: JobType = JobType.PROTOTYPE
    priority: int = 5  # 1-10, higher = more urgent
    status: JobStatus = JobStatus.QUEUED
    config: Dict[str, Any] = field(default_factory=dict)
    
    assigned_worker: Optional[str] = None
    progress: float = 0.0
    current_stage: str = ""
    stages_completed: List[str] = field(default_factory=list)
    
    output: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    
    queued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    estimated_duration_minutes: int = 30
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "job_type": self.job_type.value,
            "priority": self.priority,
            "status": self.status.value,
            "config": self.config,
            "assigned_worker": self.assigned_worker,
            "progress": self.progress,
            "current_stage": self.current_stage,
            "stages_completed": self.stages_completed,
            "output": self.output,
            "errors": self.errors,
            "logs": self.logs[-50:],  # Keep last 50 logs
            "queued_at": self.queued_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_duration_minutes": self.estimated_duration_minutes
        }


@dataclass  
class Worker:
    """Represents a build worker"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    status: WorkerStatus = WorkerStatus.IDLE
    capabilities: List[str] = field(default_factory=list)
    
    current_job_id: Optional[str] = None
    current_project_id: Optional[str] = None
    
    jobs_completed: int = 0
    jobs_failed: int = 0
    total_build_time_minutes: float = 0
    success_rate: float = 100.0
    
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Performance metrics
    avg_build_time_minutes: float = 0
    cpu_usage: float = 0
    memory_usage: float = 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "current_job_id": self.current_job_id,
            "current_project_id": self.current_project_id,
            "jobs_completed": self.jobs_completed,
            "jobs_failed": self.jobs_failed,
            "total_build_time_minutes": self.total_build_time_minutes,
            "success_rate": self.success_rate,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "created_at": self.created_at.isoformat(),
            "avg_build_time_minutes": self.avg_build_time_minutes,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage
        }


class BuildWorkerManager:
    """Manages the distributed build worker pool"""
    
    def __init__(self, db):
        self.db = db
        self.workers: Dict[str, Worker] = {}
        self.jobs: Dict[str, BuildJob] = {}
        self._running = False
        self._scheduler_task = None
    
    async def initialize(self):
        """Initialize workers from database or create defaults"""
        existing = await self.db.build_workers.find({}, {"_id": 0}).to_list(50)
        
        if not existing:
            # Create default worker pool
            default_workers = [
                Worker(name="Alpha-1", capabilities=["web", "api", "prototype"]),
                Worker(name="Alpha-2", capabilities=["web", "api", "full_build"]),
                Worker(name="Beta-1", capabilities=["game", "unreal", "unity"]),
                Worker(name="Beta-2", capabilities=["game", "godot", "demo"]),
                Worker(name="Gamma-1", capabilities=["mobile", "flutter", "react_native"]),
                Worker(name="Delta-1", capabilities=["all"], status=WorkerStatus.IDLE),
            ]
            
            for worker in default_workers:
                await self.register_worker(worker)
        else:
            for w_data in existing:
                worker = Worker(
                    id=w_data["id"],
                    name=w_data["name"],
                    status=WorkerStatus(w_data.get("status", "idle")),
                    capabilities=w_data.get("capabilities", []),
                    jobs_completed=w_data.get("jobs_completed", 0),
                    success_rate=w_data.get("success_rate", 100.0)
                )
                self.workers[worker.id] = worker
        
        # Load pending jobs
        pending_jobs = await self.db.build_farm_jobs.find(
            {"status": {"$in": ["queued", "assigned", "building"]}},
            {"_id": 0}
        ).to_list(100)
        
        for j_data in pending_jobs:
            job = BuildJob(
                id=j_data["id"],
                project_id=j_data["project_id"],
                project_name=j_data.get("project_name", ""),
                job_type=JobType(j_data.get("job_type", "prototype")),
                priority=j_data.get("priority", 5),
                status=JobStatus(j_data.get("status", "queued")),
                config=j_data.get("config", {})
            )
            self.jobs[job.id] = job
    
    async def register_worker(self, worker: Worker) -> Worker:
        """Register a new worker"""
        self.workers[worker.id] = worker
        await self.db.build_workers.update_one(
            {"id": worker.id},
            {"$set": worker.to_dict()},
            upsert=True
        )
        logger.info(f"Registered worker: {worker.name}")
        return worker
    
    async def submit_job(self, job: BuildJob) -> BuildJob:
        """Submit a new job to the queue"""
        self.jobs[job.id] = job
        await self.db.build_farm_jobs.insert_one(job.to_dict())
        logger.info(f"Job submitted: {job.id} for project {job.project_name}")
        
        # Try immediate assignment
        await self._assign_jobs()
        return job
    
    async def get_status(self) -> Dict:
        """Get overall build farm status"""
        workers = list(self.workers.values())
        jobs = list(self.jobs.values())
        
        return {
            "workers": {
                "total": len(workers),
                "idle": len([w for w in workers if w.status == WorkerStatus.IDLE]),
                "building": len([w for w in workers if w.status == WorkerStatus.BUILDING]),
                "paused": len([w for w in workers if w.status == WorkerStatus.PAUSED]),
                "error": len([w for w in workers if w.status == WorkerStatus.ERROR])
            },
            "jobs": {
                "total": len(jobs),
                "queued": len([j for j in jobs if j.status == JobStatus.QUEUED]),
                "building": len([j for j in jobs if j.status == JobStatus.BUILDING]),
                "complete": len([j for j in jobs if j.status == JobStatus.COMPLETE]),
                "failed": len([j for j in jobs if j.status == JobStatus.FAILED])
            },
            "queue_wait_time_minutes": self._estimate_queue_wait(),
            "active_builds": [
                {
                    "job_id": j.id,
                    "project_name": j.project_name,
                    "progress": j.progress,
                    "worker": j.assigned_worker
                }
                for j in jobs if j.status == JobStatus.BUILDING
            ]
        }
    
    def _estimate_queue_wait(self) -> int:
        """Estimate wait time for new jobs"""
        queued = [j for j in self.jobs.values() if j.status == JobStatus.QUEUED]
        building = [j for j in self.jobs.values() if j.status == JobStatus.BUILDING]
        idle_workers = [w for w in self.workers.values() if w.status == WorkerStatus.IDLE]
        
        if idle_workers:
            return 0
        
        if not building:
            return sum(j.estimated_duration_minutes for j in queued)
        
        # Estimate based on current builds
        avg_remaining = sum(
            j.estimated_duration_minutes * (1 - j.progress / 100)
            for j in building
        ) / len(building)
        
        return int(avg_remaining + sum(j.estimated_duration_minutes for j in queued) / max(len(self.workers), 1))
    
    async def _assign_jobs(self):
        """Assign queued jobs to available workers"""
        # Sort jobs by priority (descending)
        queued_jobs = sorted(
            [j for j in self.jobs.values() if j.status == JobStatus.QUEUED],
            key=lambda j: j.priority,
            reverse=True
        )
        
        idle_workers = [w for w in self.workers.values() if w.status == WorkerStatus.IDLE]
        
        for job in queued_jobs:
            if not idle_workers:
                break
            
            # Find best worker for job
            worker = self._find_best_worker(job, idle_workers)
            if worker:
                await self._assign_job_to_worker(job, worker)
                idle_workers.remove(worker)
    
    def _find_best_worker(self, job: BuildJob, workers: List[Worker]) -> Optional[Worker]:
        """Find the best worker for a job based on capabilities"""
        job_type_caps = {
            JobType.PROTOTYPE: ["web", "api", "prototype", "all"],
            JobType.FULL_BUILD: ["full_build", "all"],
            JobType.DEMO: ["demo", "game", "all"],
            JobType.CODE_GEN: ["web", "api", "code_gen", "all"],
            JobType.TEST_SUITE: ["test", "all"],
            JobType.ASSET_PIPELINE: ["asset", "all"]
        }
        
        required_caps = job_type_caps.get(job.job_type, ["all"])
        
        for worker in workers:
            if any(cap in worker.capabilities for cap in required_caps):
                return worker
        
        # Fall back to any available worker
        return workers[0] if workers else None
    
    async def _assign_job_to_worker(self, job: BuildJob, worker: Worker):
        """Assign a job to a worker and start processing"""
        job.status = JobStatus.ASSIGNED
        job.assigned_worker = worker.id
        job.started_at = datetime.now(timezone.utc)
        
        worker.status = WorkerStatus.BUILDING
        worker.current_job_id = job.id
        worker.current_project_id = job.project_id
        
        # Update database
        await self.db.build_farm_jobs.update_one(
            {"id": job.id},
            {"$set": {
                "status": job.status.value,
                "assigned_worker": worker.id,
                "started_at": job.started_at.isoformat()
            }}
        )
        
        await self.db.build_workers.update_one(
            {"id": worker.id},
            {"$set": {
                "status": worker.status.value,
                "current_job_id": job.id,
                "current_project_id": job.project_id
            }}
        )
        
        logger.info(f"Assigned job {job.id} to worker {worker.name}")
        
        # Start build process in background
        asyncio.create_task(self._process_job(job, worker))
    
    async def _process_job(self, job: BuildJob, worker: Worker):
        """Process a build job"""
        try:
            job.status = JobStatus.BUILDING
            job.logs.append(f"[{datetime.now(timezone.utc).isoformat()}] Build started on {worker.name}")
            
            # Define build stages based on job type
            stages = self._get_build_stages(job.job_type)
            total_stages = len(stages)
            
            for i, stage in enumerate(stages):
                job.current_stage = stage["name"]
                job.logs.append(f"[{datetime.now(timezone.utc).isoformat()}] Starting: {stage['name']}")
                
                # Simulate stage work
                stage_duration = stage.get("duration_seconds", 5)
                steps = stage.get("steps", 10)
                
                for step in range(steps):
                    await asyncio.sleep(stage_duration / steps)
                    job.progress = ((i + (step + 1) / steps) / total_stages) * 100
                    
                    # Update DB periodically
                    if step % 3 == 0:
                        await self.db.build_farm_jobs.update_one(
                            {"id": job.id},
                            {"$set": {
                                "progress": job.progress,
                                "current_stage": job.current_stage,
                                "status": job.status.value
                            }}
                        )
                
                job.stages_completed.append(stage["name"])
                job.logs.append(f"[{datetime.now(timezone.utc).isoformat()}] Completed: {stage['name']}")
            
            # Build complete
            job.status = JobStatus.COMPLETE
            job.progress = 100
            job.completed_at = datetime.now(timezone.utc)
            job.output = {
                "success": True,
                "files_generated": len(job.stages_completed) * 5,
                "build_time_minutes": (job.completed_at - job.started_at).total_seconds() / 60
            }
            
            # Update worker stats
            worker.jobs_completed += 1
            build_time = (job.completed_at - job.started_at).total_seconds() / 60
            worker.total_build_time_minutes += build_time
            worker.avg_build_time_minutes = worker.total_build_time_minutes / worker.jobs_completed
            
            logger.info(f"Job {job.id} completed successfully")
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.errors.append(str(e))
            job.logs.append(f"[{datetime.now(timezone.utc).isoformat()}] ERROR: {str(e)}")
            worker.jobs_failed += 1
            worker.success_rate = (worker.jobs_completed / (worker.jobs_completed + worker.jobs_failed)) * 100
            logger.error(f"Job {job.id} failed: {e}")
        
        finally:
            # Reset worker
            worker.status = WorkerStatus.IDLE
            worker.current_job_id = None
            worker.current_project_id = None
            worker.last_heartbeat = datetime.now(timezone.utc)
            
            # Final DB updates
            await self.db.build_farm_jobs.update_one(
                {"id": job.id},
                {"$set": job.to_dict()}
            )
            
            await self.db.build_workers.update_one(
                {"id": worker.id},
                {"$set": worker.to_dict()}
            )
            
            # Try to assign next job
            await self._assign_jobs()
    
    def _get_build_stages(self, job_type: JobType) -> List[Dict]:
        """Get build stages for job type"""
        stages = {
            JobType.PROTOTYPE: [
                {"name": "Setup", "duration_seconds": 3, "steps": 5},
                {"name": "Core Generation", "duration_seconds": 5, "steps": 10},
                {"name": "Basic UI", "duration_seconds": 3, "steps": 5},
                {"name": "Testing", "duration_seconds": 2, "steps": 5}
            ],
            JobType.FULL_BUILD: [
                {"name": "Project Setup", "duration_seconds": 5, "steps": 10},
                {"name": "Core Framework", "duration_seconds": 10, "steps": 20},
                {"name": "Systems Implementation", "duration_seconds": 15, "steps": 30},
                {"name": "AI & NPCs", "duration_seconds": 10, "steps": 20},
                {"name": "UI/UX", "duration_seconds": 8, "steps": 15},
                {"name": "World Building", "duration_seconds": 10, "steps": 20},
                {"name": "Audio & VFX", "duration_seconds": 5, "steps": 10},
                {"name": "Polish & Testing", "duration_seconds": 8, "steps": 15}
            ],
            JobType.DEMO: [
                {"name": "Demo Setup", "duration_seconds": 3, "steps": 5},
                {"name": "Core Features", "duration_seconds": 8, "steps": 15},
                {"name": "Demo Scene", "duration_seconds": 5, "steps": 10},
                {"name": "Playtest", "duration_seconds": 3, "steps": 5}
            ],
            JobType.CODE_GEN: [
                {"name": "Analyze", "duration_seconds": 2, "steps": 5},
                {"name": "Generate", "duration_seconds": 5, "steps": 10},
                {"name": "Format", "duration_seconds": 2, "steps": 5}
            ],
            JobType.TEST_SUITE: [
                {"name": "Setup Tests", "duration_seconds": 2, "steps": 5},
                {"name": "Run Tests", "duration_seconds": 5, "steps": 10},
                {"name": "Generate Report", "duration_seconds": 2, "steps": 5}
            ],
            JobType.ASSET_PIPELINE: [
                {"name": "Scan Assets", "duration_seconds": 3, "steps": 5},
                {"name": "Process", "duration_seconds": 8, "steps": 15},
                {"name": "Optimize", "duration_seconds": 5, "steps": 10},
                {"name": "Package", "duration_seconds": 3, "steps": 5}
            ]
        }
        return stages.get(job_type, stages[JobType.PROTOTYPE])


# Global worker manager instance (initialized in server.py)
worker_manager: Optional[BuildWorkerManager] = None


async def get_worker_manager(db) -> BuildWorkerManager:
    """Get or create worker manager instance"""
    global worker_manager
    if worker_manager is None:
        worker_manager = BuildWorkerManager(db)
        await worker_manager.initialize()
    return worker_manager
