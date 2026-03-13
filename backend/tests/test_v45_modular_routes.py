"""
AgentForge v4.5 Modular Routes Testing
======================================
Tests for the new modular routes migrated from monolithic server.py:
- K8s scaling endpoints
- Celery job management
- Deploy routes
- Audio routes
- Assets routes
- Build Farm routes (in server.py)
- Health check endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthEndpoints:
    """Health check endpoint tests"""
    
    def test_api_root(self):
        """GET /api/ - API root returns version 4.5.0"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("version") == "4.5.0"
        assert "features" in data
        assert "build_farm" in data.get("features", [])
        print("✅ API root returns v4.5.0 with build_farm feature")
    
    def test_health_check(self):
        """GET /api/health - Returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "timestamp" in data
        print("✅ Health check returns healthy")


class TestK8sEndpoints:
    """Kubernetes scaling endpoint tests - MOCKED (k8s_available: false)"""
    
    def test_k8s_status(self):
        """GET /api/k8s/status - Returns K8s cluster status"""
        response = requests.get(f"{BASE_URL}/api/k8s/status")
        assert response.status_code == 200
        data = response.json()
        # k8s_available should be false since no K8s cluster
        assert "k8s_available" in data
        print(f"✅ K8s status returned - k8s_available: {data.get('k8s_available')}")
    
    def test_k8s_queues(self):
        """GET /api/k8s/queues - Returns queue configuration"""
        response = requests.get(f"{BASE_URL}/api/k8s/queues")
        assert response.status_code == 200
        data = response.json()
        assert "queues" in data
        queues = data.get("queues", [])
        assert len(queues) >= 4  # default, builds, assets, tests
        queue_names = [q.get("name") for q in queues]
        assert "default" in queue_names
        assert "builds" in queue_names
        print(f"✅ K8s queues returned - {len(queues)} queues configured")
    
    def test_k8s_manifests(self):
        """GET /api/k8s/manifests - Returns K8s manifests as JSON"""
        response = requests.get(f"{BASE_URL}/api/k8s/manifests")
        assert response.status_code == 200
        data = response.json()
        assert "manifests" in data
        print("✅ K8s manifests returned")


class TestCeleryEndpoints:
    """Celery job management endpoint tests - MOCKED (celery_available: false)"""
    
    def test_celery_stats(self):
        """GET /api/celery/stats - Returns Celery queue statistics"""
        response = requests.get(f"{BASE_URL}/api/celery/stats")
        assert response.status_code == 200
        data = response.json()
        assert "celery_available" in data
        assert "total" in data  # Total jobs count
        assert "queued" in data
        assert "running" in data
        assert "complete" in data
        print(f"✅ Celery stats returned - celery_available: {data.get('celery_available')}, total: {data.get('total')}")
    
    def test_celery_workers(self):
        """GET /api/celery/workers - Returns workers object with list"""
        response = requests.get(f"{BASE_URL}/api/celery/workers")
        assert response.status_code == 200
        data = response.json()
        # Response is an object with workers key
        assert "workers" in data
        assert isinstance(data.get("workers"), list)
        print(f"✅ Celery workers returned - {len(data.get('workers', []))} workers")
    
    def test_celery_job_submit_requires_project(self):
        """POST /api/celery/jobs/submit - Requires valid project_id parameter"""
        response = requests.post(
            f"{BASE_URL}/api/celery/jobs/submit",
            params={
                "project_id": "nonexistent-project",
                "job_type": "build",
                "priority": 5
            }
        )
        # Should return 404 (project not found) or 422 (validation error)
        assert response.status_code in [404, 422]
        print(f"✅ Celery job submit validation returned status {response.status_code}")


class TestDeployEndpoints:
    """Deployment routes tests"""
    
    def test_deploy_platforms(self):
        """GET /api/deploy/platforms - Returns available platforms"""
        response = requests.get(f"{BASE_URL}/api/deploy/platforms")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        platform_ids = [p.get("id") for p in data]
        assert "vercel" in platform_ids
        assert "railway" in platform_ids
        assert "itch" in platform_ids
        print(f"✅ Deploy platforms returned - {len(data)} platforms: {platform_ids}")
    
    def test_deploy_config(self):
        """GET /api/deploy/config - Returns deployment config status"""
        response = requests.get(f"{BASE_URL}/api/deploy/config")
        assert response.status_code == 200
        data = response.json()
        # Should have vercel, railway, itch keys
        assert "vercel" in data
        assert "railway" in data
        assert "itch" in data
        print(f"✅ Deploy config returned - vercel: {data.get('vercel')}, railway: {data.get('railway')}, itch: {data.get('itch')}")


class TestAudioEndpoints:
    """Audio generation routes tests"""
    
    def test_audio_categories(self):
        """GET /api/audio/categories - Returns audio categories and presets"""
        response = requests.get(f"{BASE_URL}/api/audio/categories")
        assert response.status_code == 200
        data = response.json()
        # Should have sfx, music, voice categories
        assert "sfx" in data
        assert "music" in data
        assert "voice" in data
        # Check some presets exist
        assert "explosion" in data.get("sfx", {})
        assert "battle_epic" in data.get("music", {})
        print(f"✅ Audio categories returned - {len(data)} categories")


class TestAssetsEndpoints:
    """Asset pipeline routes tests"""
    
    def test_asset_types(self):
        """GET /api/assets/types - Returns supported asset types"""
        response = requests.get(f"{BASE_URL}/api/assets/types")
        assert response.status_code == 200
        data = response.json()
        # Should have image, audio, texture, etc.
        assert "image" in data
        assert "audio" in data
        assert "texture" in data
        assert "sprite" in data
        assert "model_3d" in data
        # Check format structure
        assert "formats" in data.get("image", {})
        assert "png" in data.get("image", {}).get("formats", [])
        print(f"✅ Asset types returned - {len(data)} types: {list(data.keys())}")
    
    def test_asset_categories(self):
        """GET /api/assets/categories - Returns asset categories"""
        response = requests.get(f"{BASE_URL}/api/assets/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        category_ids = [c.get("id") for c in data]
        assert "ui" in category_ids
        assert "character" in category_ids
        assert "environment" in category_ids
        print(f"✅ Asset categories returned - {len(data)} categories: {category_ids}")


class TestBuildFarmEndpoints:
    """Build Farm routes tests (in server.py)"""
    
    def test_build_farm_status(self):
        """GET /api/build-farm/status - Returns real-time farm status"""
        response = requests.get(f"{BASE_URL}/api/build-farm/status")
        assert response.status_code == 200
        data = response.json()
        # Check required fields
        assert "total_workers" in data
        assert "active_workers" in data
        assert "queued_jobs" in data
        assert "running_jobs" in data
        assert "completed_jobs" in data
        print(f"✅ Build Farm status returned - workers: {data.get('total_workers')}, queued: {data.get('queued_jobs')}, completed: {data.get('completed_jobs')}")
    
    def test_build_farm_workers(self):
        """GET /api/build-farm/workers - Returns worker list"""
        response = requests.get(f"{BASE_URL}/api/build-farm/workers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have default workers
        assert len(data) >= 3
        worker_names = [w.get("name") for w in data]
        print(f"✅ Build Farm workers returned - {len(data)} workers: {worker_names}")


class TestModularStructure:
    """Verify modular backend structure"""
    
    def test_routes_imported(self):
        """Verify routes are properly imported via main.py"""
        # Test multiple endpoints from different route files
        endpoints = [
            "/api/health",
            "/api/k8s/status",
            "/api/celery/stats",
            "/api/deploy/platforms",
            "/api/audio/categories",
            "/api/assets/types",
            "/api/build-farm/status"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"Endpoint {endpoint} failed with status {response.status_code}"
        
        print(f"✅ All {len(endpoints)} modular endpoints responding correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
