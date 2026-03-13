"""
Kubernetes Scaling Routes
=========================
Routes for managing Kubernetes deployments and scaling Celery workers.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
import os
import tempfile

router = APIRouter(prefix="/k8s", tags=["kubernetes"])


@router.get("/status")
async def get_k8s_status():
    """Get Kubernetes cluster status"""
    from core.k8s_scaling import k8s_scaler
    
    return {
        "k8s_available": k8s_scaler.is_available,
        "workers": k8s_scaler.get_worker_status() if k8s_scaler.is_available else None,
        "hpas": k8s_scaler.get_hpa_status() if k8s_scaler.is_available else []
    }


@router.post("/scale/{queue}")
async def scale_workers(queue: str, replicas: int):
    """Manually scale Celery workers for a specific queue"""
    from core.k8s_scaling import k8s_scaler
    
    if not k8s_scaler.is_available:
        raise HTTPException(
            status_code=503, 
            detail="Kubernetes not available. Run in a K8s cluster or configure kubeconfig."
        )
    
    if replicas < 0 or replicas > 50:
        raise HTTPException(status_code=400, detail="Replicas must be between 0 and 50")
    
    success = k8s_scaler.scale_workers(queue, replicas)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to scale workers")
    
    return {"success": True, "queue": queue, "replicas": replicas}


@router.get("/manifests")
async def get_manifests():
    """Get all Kubernetes manifests as JSON"""
    from core.k8s_scaling import generate_all_manifests
    
    return {"manifests": generate_all_manifests()}


@router.get("/manifests/download")
async def download_manifests():
    """Download Kubernetes manifests as YAML files"""
    from core.k8s_scaling import export_manifests
    import shutil
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = os.path.join(tmpdir, "kubernetes")
        files = export_manifests(output_dir)
        
        zip_path = os.path.join(tmpdir, "agentforge-k8s-manifests.zip")
        shutil.make_archive(zip_path.replace('.zip', ''), 'zip', output_dir)
        
        with open(zip_path, 'rb') as f:
            content = f.read()
    
    return {
        "message": "Manifests generated",
        "files": files,
        "download_hint": "Use /api/k8s/manifests/yaml/{filename} to get individual files"
    }


@router.get("/manifests/yaml/{filename}")
async def get_manifest_yaml(filename: str):
    """Get a specific manifest as YAML"""
    from core.k8s_scaling import (
        generate_namespace, generate_redis_deployment, generate_redis_service,
        generate_backend_deployment, generate_backend_service,
        generate_celery_worker_deployment, generate_worker_hpa
    )
    import yaml
    
    manifest_generators = {
        "namespace.yaml": [generate_namespace()],
        "redis.yaml": [generate_redis_deployment(), generate_redis_service()],
        "backend.yaml": [generate_backend_deployment(), generate_backend_service()],
    }
    
    if filename == "workers.yaml":
        manifests = []
        for queue in ['default', 'builds', 'assets', 'tests']:
            manifests.append(generate_celery_worker_deployment(queue))
        return yaml.dump_all(manifests, default_flow_style=False)
    
    if filename == "autoscaling.yaml":
        manifests = []
        for queue in ['default', 'builds', 'assets', 'tests']:
            manifests.append(generate_worker_hpa(queue))
        return yaml.dump_all(manifests, default_flow_style=False)
    
    if filename not in manifest_generators:
        raise HTTPException(status_code=404, detail=f"Manifest {filename} not found")
    
    return yaml.dump_all(manifest_generators[filename], default_flow_style=False)


@router.post("/apply")
async def apply_manifests(dry_run: bool = True):
    """Apply Kubernetes manifests (requires K8s access)"""
    from core.k8s_scaling import k8s_scaler
    
    if not k8s_scaler.is_available:
        raise HTTPException(
            status_code=503,
            detail="Kubernetes not available. Configure kubeconfig or run in-cluster."
        )
    
    if dry_run:
        return {
            "message": "Dry run - no changes applied",
            "would_create": [
                "Namespace: agentforge",
                "Deployment: redis",
                "Service: redis",
                "Deployment: backend",
                "Service: backend",
                "Deployment: celery-worker-default (2 replicas)",
                "Deployment: celery-worker-builds (3 replicas)",
                "Deployment: celery-worker-assets (2 replicas)",
                "Deployment: celery-worker-tests (2 replicas)",
                "HPA: celery-worker-default-hpa",
                "HPA: celery-worker-builds-hpa",
                "HPA: celery-worker-assets-hpa",
                "HPA: celery-worker-tests-hpa"
            ]
        }
    
    return {"message": "Apply not yet implemented - use kubectl apply -f"}


@router.get("/queues")
async def get_queue_config():
    """Get configuration for all Celery queues"""
    return {
        "queues": [
            {
                "name": "default",
                "description": "General purpose tasks",
                "default_replicas": 2,
                "max_replicas": 10
            },
            {
                "name": "builds",
                "description": "Build jobs (highest priority)",
                "default_replicas": 3,
                "max_replicas": 20
            },
            {
                "name": "assets",
                "description": "Asset processing (images, audio)",
                "default_replicas": 2,
                "max_replicas": 10
            },
            {
                "name": "tests",
                "description": "Test suite execution",
                "default_replicas": 2,
                "max_replicas": 10
            }
        ]
    }
