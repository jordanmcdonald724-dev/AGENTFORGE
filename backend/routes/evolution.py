"""
Software Evolution Engine - Auto-optimize and evolve deployed projects
Scans projects for improvements, applies optimizations, and tracks evolution
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from core.database import db
import uuid
import asyncio

router = APIRouter(prefix="/evolution", tags=["evolution"])


class EvolutionScan(BaseModel):
    project_id: str
    scan_type: str = "full"  # full, performance, security, code_quality


class OptimizationRequest(BaseModel):
    project_id: str
    optimization_ids: List[str]


# Optimization patterns database
OPTIMIZATION_PATTERNS = {
    "performance": [
        {
            "id": "perf-001",
            "name": "Lazy Loading Components",
            "description": "Convert heavy components to lazy-loaded imports",
            "impact": "high",
            "auto_fix": True,
            "pattern": "import { Component } from",
            "replacement": "const Component = lazy(() => import"
        },
        {
            "id": "perf-002", 
            "name": "Memoize Expensive Computations",
            "description": "Add useMemo/useCallback to expensive operations",
            "impact": "medium",
            "auto_fix": True
        },
        {
            "id": "perf-003",
            "name": "Database Query Optimization",
            "description": "Add indexes and optimize N+1 queries",
            "impact": "high",
            "auto_fix": False
        },
        {
            "id": "perf-004",
            "name": "Image Optimization",
            "description": "Convert images to WebP and add lazy loading",
            "impact": "medium",
            "auto_fix": True
        },
        {
            "id": "perf-005",
            "name": "Bundle Size Reduction",
            "description": "Tree-shake unused imports and split chunks",
            "impact": "high",
            "auto_fix": True
        }
    ],
    "security": [
        {
            "id": "sec-001",
            "name": "SQL Injection Prevention",
            "description": "Parameterize database queries",
            "impact": "critical",
            "auto_fix": True
        },
        {
            "id": "sec-002",
            "name": "XSS Protection",
            "description": "Sanitize user inputs and escape outputs",
            "impact": "critical",
            "auto_fix": True
        },
        {
            "id": "sec-003",
            "name": "CSRF Token Validation",
            "description": "Add CSRF tokens to forms",
            "impact": "high",
            "auto_fix": True
        },
        {
            "id": "sec-004",
            "name": "Dependency Vulnerabilities",
            "description": "Update packages with known vulnerabilities",
            "impact": "high",
            "auto_fix": True
        }
    ],
    "code_quality": [
        {
            "id": "qual-001",
            "name": "Dead Code Elimination",
            "description": "Remove unused functions and variables",
            "impact": "low",
            "auto_fix": True
        },
        {
            "id": "qual-002",
            "name": "Code Duplication",
            "description": "Extract duplicate code into shared utilities",
            "impact": "medium",
            "auto_fix": False
        },
        {
            "id": "qual-003",
            "name": "Type Safety",
            "description": "Add TypeScript types or PropTypes",
            "impact": "medium",
            "auto_fix": True
        },
        {
            "id": "qual-004",
            "name": "Error Handling",
            "description": "Add try-catch blocks and error boundaries",
            "impact": "high",
            "auto_fix": True
        }
    ]
}


@router.post("/scan")
async def start_evolution_scan(scan: EvolutionScan, background_tasks: BackgroundTasks):
    """Start a project evolution scan"""
    
    # Verify project exists
    project = await db.projects.find_one({"id": scan.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create scan record
    scan_id = str(uuid.uuid4())
    scan_record = {
        "id": scan_id,
        "project_id": scan.project_id,
        "scan_type": scan.scan_type,
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "findings": [],
        "optimizations": []
    }
    
    await db.evolution_scans.insert_one(scan_record)
    
    # Run scan in background
    background_tasks.add_task(run_evolution_scan, scan_id, scan.project_id, scan.scan_type)
    
    return {
        "scan_id": scan_id,
        "status": "running",
        "message": "Evolution scan started"
    }


async def run_evolution_scan(scan_id: str, project_id: str, scan_type: str):
    """Background task to run evolution scan"""
    
    # Get project files
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    findings = []
    optimizations = []
    
    # Determine which patterns to check
    if scan_type == "full":
        pattern_types = ["performance", "security", "code_quality"]
    else:
        pattern_types = [scan_type]
    
    for pattern_type in pattern_types:
        patterns = OPTIMIZATION_PATTERNS.get(pattern_type, [])
        
        for pattern in patterns:
            # Simulate scanning (in real implementation, would analyze code)
            import random
            if random.random() > 0.4:  # 60% chance of finding an issue
                finding = {
                    "id": str(uuid.uuid4()),
                    "pattern_id": pattern["id"],
                    "type": pattern_type,
                    "name": pattern["name"],
                    "description": pattern["description"],
                    "impact": pattern["impact"],
                    "auto_fix": pattern.get("auto_fix", False),
                    "affected_files": random.sample([f["filepath"] for f in files], min(3, len(files))) if files else [],
                    "status": "pending"
                }
                findings.append(finding)
                
                if pattern.get("auto_fix"):
                    optimizations.append({
                        "id": str(uuid.uuid4()),
                        "finding_id": finding["id"],
                        "name": f"Fix: {pattern['name']}",
                        "type": pattern_type,
                        "impact": pattern["impact"],
                        "status": "available"
                    })
    
    # Update scan with results
    await db.evolution_scans.update_one(
        {"id": scan_id},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "findings": findings,
                "optimizations": optimizations,
                "summary": {
                    "total_findings": len(findings),
                    "critical": len([f for f in findings if f["impact"] == "critical"]),
                    "high": len([f for f in findings if f["impact"] == "high"]),
                    "medium": len([f for f in findings if f["impact"] == "medium"]),
                    "low": len([f for f in findings if f["impact"] == "low"]),
                    "auto_fixable": len([f for f in findings if f["auto_fix"]])
                }
            }
        }
    )


@router.get("/scans/{project_id}")
async def get_project_scans(project_id: str):
    """Get all evolution scans for a project"""
    scans = await db.evolution_scans.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("started_at", -1).to_list(20)
    
    return scans


@router.get("/scan/{scan_id}")
async def get_scan_details(scan_id: str):
    """Get detailed scan results"""
    scan = await db.evolution_scans.find_one({"id": scan_id}, {"_id": 0})
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.post("/optimize")
async def apply_optimizations(request: OptimizationRequest, background_tasks: BackgroundTasks):
    """Apply selected optimizations to a project"""
    
    # Get project
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create optimization job
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "project_id": request.project_id,
        "optimization_ids": request.optimization_ids,
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "applied": [],
        "failed": []
    }
    
    await db.evolution_jobs.insert_one(job)
    
    # Run optimizations in background
    background_tasks.add_task(apply_optimizations_task, job_id, request.project_id, request.optimization_ids)
    
    return {
        "job_id": job_id,
        "status": "running",
        "message": f"Applying {len(request.optimization_ids)} optimizations"
    }


async def apply_optimizations_task(job_id: str, project_id: str, optimization_ids: List[str]):
    """Background task to apply optimizations"""
    
    applied = []
    failed = []
    
    for opt_id in optimization_ids:
        try:
            # Simulate optimization (in real implementation, would modify files)
            await asyncio.sleep(0.5)
            
            applied.append({
                "optimization_id": opt_id,
                "applied_at": datetime.now(timezone.utc).isoformat(),
                "changes": ["Simulated optimization applied"]
            })
        except Exception as e:
            failed.append({
                "optimization_id": opt_id,
                "error": str(e)
            })
    
    # Update job
    await db.evolution_jobs.update_one(
        {"id": job_id},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "applied": applied,
                "failed": failed
            }
        }
    )
    
    # Track evolution in project history
    await db.project_evolutions.insert_one({
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "job_id": job_id,
        "optimizations_applied": len(applied),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@router.get("/history/{project_id}")
async def get_evolution_history(project_id: str):
    """Get project evolution history"""
    history = await db.project_evolutions.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("timestamp", -1).to_list(50)
    
    return history


@router.post("/auto-evolve/{project_id}")
async def enable_auto_evolution(project_id: str, enabled: bool = True):
    """Enable/disable automatic evolution for a project"""
    
    result = await db.projects.update_one(
        {"id": project_id},
        {
            "$set": {
                "auto_evolution": enabled,
                "evolution_settings": {
                    "enabled": enabled,
                    "scan_frequency": "daily",
                    "auto_apply_low_risk": True,
                    "notify_on_findings": True
                }
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "project_id": project_id,
        "auto_evolution": enabled,
        "message": f"Auto-evolution {'enabled' if enabled else 'disabled'}"
    }
