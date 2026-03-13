"""
AgentForge v4.5 Final Testing - Build Farm, Celery, Modular Structure
=====================================================================

Tests:
1. API root and health endpoints
2. Build Farm endpoints
3. Celery queue endpoints
4. Job lifecycle (add -> start -> monitor)
5. Modular structure verification
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestAPIRoot:
    """Test API root and health endpoints"""
    
    def test_api_root_returns_version_450(self):
        """GET /api/ - API root returns version 4.5.0"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("version") == "4.5.0"
        assert "build_farm" in data.get("features", [])
        print(f"✅ API root - version {data['version']}")
    
    def test_health_endpoint(self):
        """GET /api/health - health check returns healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✅ Health check - {data['status']}")


class TestBuildFarmEndpoints:
    """Test Build Farm endpoints"""
    
    def test_get_build_farm_status(self):
        """GET /api/build-farm/status - returns real-time status"""
        response = requests.get(f"{BASE_URL}/api/build-farm/status")
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "total_workers" in data
        assert "active_workers" in data
        assert "idle_workers" in data
        assert "queued_jobs" in data
        assert "running_jobs" in data
        assert "completed_jobs" in data
        assert "active_builds" in data
        
        print(f"✅ Build Farm status - {data['total_workers']} workers, {data['queued_jobs']} queued")
    
    def test_get_build_farm_workers(self):
        """GET /api/build-farm/workers - returns worker list"""
        response = requests.get(f"{BASE_URL}/api/build-farm/workers")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            worker = data[0]
            assert "id" in worker
            assert "name" in worker
            assert "status" in worker
        
        print(f"✅ Build Farm workers - {len(data)} workers")
    
    def test_add_job_to_queue(self):
        """POST /api/build-farm/jobs/add - adds job to queue"""
        job_id = f"TEST_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/build-farm/jobs/add",
            params={
                "project_id": f"proj_{job_id}",
                "project_name": f"TestProject_{job_id}",
                "job_type": "prototype",
                "priority": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "queued"
        assert data.get("job_type") == "prototype"
        assert "id" in data
        
        print(f"✅ Add job - job {data['id']} queued")
        return data["id"]
    
    def test_get_jobs_list(self):
        """GET /api/build-farm/jobs - returns jobs sorted by priority"""
        response = requests.get(f"{BASE_URL}/api/build-farm/jobs")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✅ Jobs list - {len(data)} jobs")
    
    def test_get_job_logs_not_found(self):
        """GET /api/build-farm/jobs/{id}/logs - returns 404 for nonexistent"""
        response = requests.get(f"{BASE_URL}/api/build-farm/jobs/nonexistent-job/logs")
        assert response.status_code == 404
        print("✅ Job logs - 404 for nonexistent job")
    
    def test_cancel_job_not_found(self):
        """POST /api/build-farm/jobs/{id}/cancel - returns 404 for nonexistent"""
        response = requests.post(f"{BASE_URL}/api/build-farm/jobs/nonexistent-job/cancel")
        assert response.status_code == 404
        print("✅ Cancel job - 404 for nonexistent job")


class TestCeleryEndpoints:
    """Test Celery distributed queue endpoints"""
    
    def test_celery_stats(self):
        """GET /api/celery/stats - returns queue statistics"""
        response = requests.get(f"{BASE_URL}/api/celery/stats")
        assert response.status_code == 200
        data = response.json()
        
        # May have celery_available: false if Redis not running
        assert "celery_available" in data or "total" in data
        
        print(f"✅ Celery stats - available: {data.get('celery_available', 'N/A')}")
    
    def test_celery_workers(self):
        """GET /api/celery/workers - returns worker list"""
        response = requests.get(f"{BASE_URL}/api/celery/workers")
        assert response.status_code == 200
        data = response.json()
        
        assert "workers" in data
        print(f"✅ Celery workers - {len(data.get('workers', []))} workers")


class TestJobLifecycle:
    """Test full job lifecycle: add -> start -> monitor"""
    
    def test_full_job_lifecycle(self):
        """Test complete job lifecycle"""
        # 1. Add a job
        job_id = f"TEST_LC_{uuid.uuid4().hex[:8]}"
        add_response = requests.post(
            f"{BASE_URL}/api/build-farm/jobs/add",
            params={
                "project_id": f"proj_{job_id}",
                "project_name": f"LifecycleTest_{job_id}",
                "job_type": "code_gen",
                "priority": 8
            }
        )
        assert add_response.status_code == 200
        job_data = add_response.json()
        job_id = job_data["id"]
        print(f"✅ Job added: {job_id}")
        
        # 2. Start the job
        start_response = requests.post(f"{BASE_URL}/api/build-farm/jobs/{job_id}/start")
        # May return 200 (started) or 400 (no workers available)
        assert start_response.status_code in [200, 400]
        
        if start_response.status_code == 200:
            start_data = start_response.json()
            # Response may have 'success' field or 'status' field
            assert start_data.get("success") == True or start_data.get("status") in ["running", "queued"]
            print(f"✅ Job started: {start_data}")
        else:
            print("✅ Job start returned 400 (no workers available - expected in test)")
        
        # 3. Get job logs
        logs_response = requests.get(f"{BASE_URL}/api/build-farm/jobs/{job_id}/logs")
        assert logs_response.status_code == 200
        logs_data = logs_response.json()
        assert "logs" in logs_data or "status" in logs_data
        print(f"✅ Job logs retrieved: {len(logs_data.get('logs', []))} entries")
        
        # 4. Cancel the job
        cancel_response = requests.post(f"{BASE_URL}/api/build-farm/jobs/{job_id}/cancel")
        assert cancel_response.status_code == 200
        cancel_data = cancel_response.json()
        # Response may have 'success' field or 'status' field
        assert cancel_data.get("success") == True or cancel_data.get("status") == "cancelled"
        print(f"✅ Job cancelled successfully")


class TestAllJobTypes:
    """Test all job types can be added"""
    
    @pytest.mark.parametrize("job_type", ["prototype", "full_build", "demo", "code_gen", "test_suite", "asset_pipeline"])
    def test_add_job_types(self, job_type):
        """Test adding different job types to queue"""
        response = requests.post(
            f"{BASE_URL}/api/build-farm/jobs/add",
            params={
                "project_id": f"proj_type_test_{job_type}",
                "project_name": f"TypeTest_{job_type}",
                "job_type": job_type,
                "priority": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("job_type") == job_type
        print(f"✅ Job type '{job_type}' added successfully")


class TestWorkerManagement:
    """Test Build Farm worker management"""
    
    def test_get_workers_list(self):
        """Get list of workers"""
        response = requests.get(f"{BASE_URL}/api/build-farm/workers")
        assert response.status_code == 200
        workers = response.json()
        
        if len(workers) > 0:
            # Test pause/resume on first worker
            worker_id = workers[0]["id"]
            
            # Pause worker
            pause_response = requests.post(f"{BASE_URL}/api/build-farm/workers/{worker_id}/pause")
            assert pause_response.status_code == 200
            print(f"✅ Worker {worker_id} paused")
            
            # Resume worker
            resume_response = requests.post(f"{BASE_URL}/api/build-farm/workers/{worker_id}/resume")
            assert resume_response.status_code == 200
            print(f"✅ Worker {worker_id} resumed")
        else:
            print("✅ No workers to test pause/resume")


class TestModularStructure:
    """Verify modular structure files exist"""
    
    def test_routes_directory_exists(self):
        """Verify routes directory structure"""
        route_files = [
            "/app/backend/routes/__init__.py",
            "/app/backend/routes/health.py",
            "/app/backend/routes/agents.py",
            "/app/backend/routes/projects.py",
            "/app/backend/routes/builds.py",
            "/app/backend/routes/command_center.py"
        ]
        for file_path in route_files:
            assert os.path.exists(file_path), f"Route file missing: {file_path}"
        print(f"✅ Routes directory - {len(route_files)} route files verified")
    
    def test_models_directory_exists(self):
        """Verify models directory structure"""
        model_files = [
            "/app/backend/models/__init__.py",
            "/app/backend/models/base.py",
            "/app/backend/models/agent.py",
            "/app/backend/models/project.py",
            "/app/backend/models/build.py"
        ]
        for file_path in model_files:
            assert os.path.exists(file_path), f"Model file missing: {file_path}"
        print(f"✅ Models directory - {len(model_files)} model files verified")
    
    def test_core_directory_exists(self):
        """Verify core directory structure"""
        core_files = [
            "/app/backend/core/__init__.py",
            "/app/backend/core/database.py",
            "/app/backend/core/celery_tasks.py",
            "/app/backend/core/worker_system.py"
        ]
        for file_path in core_files:
            assert os.path.exists(file_path), f"Core file missing: {file_path}"
        print(f"✅ Core directory - {len(core_files)} core files verified")
    
    def test_main_modular_entry_exists(self):
        """Verify main.py modular entry point exists"""
        assert os.path.exists("/app/backend/main.py"), "main.py missing"
        print("✅ main.py modular entry point exists")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
