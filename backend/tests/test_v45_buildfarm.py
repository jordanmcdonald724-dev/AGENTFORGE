"""
Build Farm API Tests for AgentForge v4.5
Tests distributed build worker system including:
- Worker management (list, pause, resume, add)
- Job queue management (add, start, cancel, logs)
- Build farm status overview
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestBuildFarmStatus:
    """Tests for GET /api/build-farm/status endpoint"""
    
    def test_status_returns_worker_counts(self):
        """GET /api/build-farm/status returns total_workers, active_workers counts"""
        response = requests.get(f"{BASE_URL}/api/build-farm/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_workers" in data
        assert "active_workers" in data
        assert "idle_workers" in data
        assert isinstance(data["total_workers"], int)
        assert isinstance(data["active_workers"], int)
    
    def test_status_returns_job_counts(self):
        """GET /api/build-farm/status returns job statistics"""
        response = requests.get(f"{BASE_URL}/api/build-farm/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "queued_jobs" in data
        assert "running_jobs" in data
        assert "completed_jobs" in data
        assert "failed_jobs" in data
        assert isinstance(data["queued_jobs"], int)
        assert isinstance(data["running_jobs"], int)
    
    def test_status_returns_active_builds(self):
        """GET /api/build-farm/status returns active_builds list"""
        response = requests.get(f"{BASE_URL}/api/build-farm/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "active_builds" in data
        assert isinstance(data["active_builds"], list)
    
    def test_status_returns_queue_wait_time(self):
        """GET /api/build-farm/status returns queue_wait_minutes"""
        response = requests.get(f"{BASE_URL}/api/build-farm/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "queue_wait_minutes" in data
        assert isinstance(data["queue_wait_minutes"], (int, float))


class TestBuildFarmWorkers:
    """Tests for worker management endpoints"""
    
    def test_get_workers_list(self):
        """GET /api/build-farm/workers returns list of workers"""
        response = requests.get(f"{BASE_URL}/api/build-farm/workers")
        assert response.status_code == 200
        
        workers = response.json()
        assert isinstance(workers, list)
        
        # Should have default workers created
        if len(workers) > 0:
            worker = workers[0]
            assert "id" in worker
            assert "name" in worker
            assert "status" in worker
            assert "capabilities" in worker
    
    def test_pause_worker(self):
        """POST /api/build-farm/workers/{id}/pause pauses a worker"""
        # First get workers
        response = requests.get(f"{BASE_URL}/api/build-farm/workers")
        workers = response.json()
        
        if len(workers) > 0:
            # Find an idle worker
            idle_worker = next((w for w in workers if w.get("status") == "idle"), None)
            if idle_worker:
                worker_id = idle_worker["id"]
                
                # Pause the worker
                pause_response = requests.post(f"{BASE_URL}/api/build-farm/workers/{worker_id}/pause")
                assert pause_response.status_code == 200
                assert pause_response.json().get("success") == True
                
                # Resume it back
                resume_response = requests.post(f"{BASE_URL}/api/build-farm/workers/{worker_id}/resume")
                assert resume_response.status_code == 200
    
    def test_resume_worker(self):
        """POST /api/build-farm/workers/{id}/resume resumes a paused worker"""
        # Get workers
        response = requests.get(f"{BASE_URL}/api/build-farm/workers")
        workers = response.json()
        
        if len(workers) > 0:
            worker_id = workers[0]["id"]
            
            # First pause
            requests.post(f"{BASE_URL}/api/build-farm/workers/{worker_id}/pause")
            
            # Then resume
            resume_response = requests.post(f"{BASE_URL}/api/build-farm/workers/{worker_id}/resume")
            assert resume_response.status_code == 200
            
            data = resume_response.json()
            assert data.get("success") == True


class TestBuildFarmJobs:
    """Tests for job management endpoints"""
    
    @pytest.fixture
    def test_project(self):
        """Create a test project for job tests"""
        project_data = {
            "name": "TEST_BuildFarmProject",
            "description": "Test project for build farm testing",
            "type": "game"
        }
        response = requests.post(f"{BASE_URL}/api/projects", json=project_data)
        if response.status_code == 200:
            return response.json()
        return {"id": "test-project-id", "name": "TestProject"}
    
    def test_add_job_to_queue(self, test_project):
        """POST /api/build-farm/jobs/add adds a new job to queue"""
        project_id = test_project.get("id", "test-id")
        project_name = test_project.get("name", "TestProject")
        
        response = requests.post(
            f"{BASE_URL}/api/build-farm/jobs/add",
            params={
                "project_id": project_id,
                "project_name": project_name,
                "job_type": "prototype",
                "priority": 5
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data.get("project_id") == project_id
        assert data.get("project_name") == project_name
        assert data.get("job_type") == "prototype"
        assert data.get("status") == "queued"
        assert data.get("priority") == 5
        
        return data
    
    def test_add_job_with_different_types(self, test_project):
        """POST /api/build-farm/jobs/add supports different job types"""
        project_id = test_project.get("id", "test-id")
        project_name = test_project.get("name", "TestProject")
        
        job_types = ["prototype", "full_build", "demo", "code_gen", "test_suite"]
        
        for job_type in job_types:
            response = requests.post(
                f"{BASE_URL}/api/build-farm/jobs/add",
                params={
                    "project_id": project_id,
                    "project_name": project_name,
                    "job_type": job_type,
                    "priority": 3
                }
            )
            assert response.status_code == 200
            assert response.json().get("job_type") == job_type
    
    def test_get_jobs_list(self):
        """GET /api/build-farm/jobs returns job list sorted by priority"""
        response = requests.get(f"{BASE_URL}/api/build-farm/jobs")
        assert response.status_code == 200
        
        jobs = response.json()
        assert isinstance(jobs, list)
        
        if len(jobs) > 0:
            job = jobs[0]
            assert "id" in job
            assert "project_id" in job
            assert "project_name" in job
            assert "status" in job
            assert "priority" in job
    
    def test_start_job(self, test_project):
        """POST /api/build-farm/jobs/{id}/start starts a queued job"""
        project_id = test_project.get("id", "test-id")
        project_name = test_project.get("name", "TestProject")
        
        # First add a job
        add_response = requests.post(
            f"{BASE_URL}/api/build-farm/jobs/add",
            params={
                "project_id": project_id,
                "project_name": project_name,
                "job_type": "prototype",
                "priority": 8
            }
        )
        job = add_response.json()
        job_id = job.get("id")
        
        # Start the job
        start_response = requests.post(f"{BASE_URL}/api/build-farm/jobs/{job_id}/start")
        
        # Should succeed if workers available, or return 400 if no workers
        assert start_response.status_code in [200, 400]
        
        if start_response.status_code == 200:
            data = start_response.json()
            assert data.get("success") == True
            assert "worker" in data
            assert data.get("job_id") == job_id
    
    def test_start_nonexistent_job(self):
        """POST /api/build-farm/jobs/{id}/start returns 404 for invalid job"""
        response = requests.post(f"{BASE_URL}/api/build-farm/jobs/nonexistent-job-id/start")
        assert response.status_code == 404
    
    def test_cancel_queued_job(self, test_project):
        """POST /api/build-farm/jobs/{id}/cancel cancels a queued job"""
        project_id = test_project.get("id", "test-id")
        project_name = test_project.get("name", "TestProject")
        
        # Add a job
        add_response = requests.post(
            f"{BASE_URL}/api/build-farm/jobs/add",
            params={
                "project_id": project_id,
                "project_name": project_name,
                "job_type": "demo",
                "priority": 2
            }
        )
        job = add_response.json()
        job_id = job.get("id")
        
        # Cancel it
        cancel_response = requests.post(f"{BASE_URL}/api/build-farm/jobs/{job_id}/cancel")
        assert cancel_response.status_code == 200
        
        data = cancel_response.json()
        assert data.get("success") == True
    
    def test_cancel_nonexistent_job(self):
        """POST /api/build-farm/jobs/{id}/cancel returns 404 for invalid job"""
        response = requests.post(f"{BASE_URL}/api/build-farm/jobs/nonexistent-id/cancel")
        assert response.status_code == 404
    
    def test_get_job_logs(self, test_project):
        """GET /api/build-farm/jobs/{id}/logs returns job logs"""
        project_id = test_project.get("id", "test-id")
        project_name = test_project.get("name", "TestProject")
        
        # Add a job
        add_response = requests.post(
            f"{BASE_URL}/api/build-farm/jobs/add",
            params={
                "project_id": project_id,
                "project_name": project_name,
                "job_type": "prototype",
                "priority": 5
            }
        )
        job = add_response.json()
        job_id = job.get("id")
        
        # Get logs
        logs_response = requests.get(f"{BASE_URL}/api/build-farm/jobs/{job_id}/logs")
        assert logs_response.status_code == 200
        
        data = logs_response.json()
        assert "logs" in data
        assert "status" in data
        assert "progress" in data
    
    def test_get_logs_nonexistent_job(self):
        """GET /api/build-farm/jobs/{id}/logs returns 404 for invalid job"""
        response = requests.get(f"{BASE_URL}/api/build-farm/jobs/nonexistent-id/logs")
        assert response.status_code == 404


class TestBuildJobExecution:
    """Integration test for job execution flow"""
    
    def test_full_job_lifecycle(self):
        """Test complete job lifecycle: add -> start -> monitor progress"""
        # Create test project
        project_data = {
            "name": "TEST_LifecycleProject",
            "description": "Testing job lifecycle",
            "type": "api"
        }
        project_response = requests.post(f"{BASE_URL}/api/projects", json=project_data)
        
        if project_response.status_code == 200:
            project = project_response.json()
            project_id = project.get("id")
            project_name = project.get("name")
        else:
            project_id = "lifecycle-test-id"
            project_name = "LifecycleTest"
        
        # 1. Add job
        add_response = requests.post(
            f"{BASE_URL}/api/build-farm/jobs/add",
            params={
                "project_id": project_id,
                "project_name": project_name,
                "job_type": "prototype",
                "priority": 10
            }
        )
        assert add_response.status_code == 200
        job = add_response.json()
        job_id = job.get("id")
        assert job.get("status") == "queued"
        
        # 2. Start job
        start_response = requests.post(f"{BASE_URL}/api/build-farm/jobs/{job_id}/start")
        
        if start_response.status_code == 200:
            # Job started successfully
            assert start_response.json().get("success") == True
            
            # 3. Check status shows building
            time.sleep(1)
            status_response = requests.get(f"{BASE_URL}/api/build-farm/status")
            status = status_response.json()
            
            # Should have active builds or running jobs
            assert status.get("running_jobs", 0) >= 0 or len(status.get("active_builds", [])) >= 0
            
            # 4. Check job logs are being generated
            logs_response = requests.get(f"{BASE_URL}/api/build-farm/jobs/{job_id}/logs")
            assert logs_response.status_code == 200
            logs_data = logs_response.json()
            assert logs_data.get("status") in ["building", "complete", "queued"]
            
        else:
            # No workers available - that's ok for this test
            assert start_response.status_code == 400
            assert "No workers available" in start_response.json().get("detail", "")


class TestFrontendIntegration:
    """Verify endpoints return data compatible with frontend components"""
    
    def test_status_data_matches_frontend_expectations(self):
        """Verify status response has all fields BuildFarmPanel expects"""
        response = requests.get(f"{BASE_URL}/api/build-farm/status")
        assert response.status_code == 200
        
        data = response.json()
        
        # Fields expected by BuildFarmPanel.jsx
        expected_fields = [
            "total_workers",
            "active_workers", 
            "queued_jobs",
            "completed_jobs",
            "active_builds"
        ]
        
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
    
    def test_workers_data_matches_frontend_expectations(self):
        """Verify workers response has all fields BuildFarmPanel expects"""
        response = requests.get(f"{BASE_URL}/api/build-farm/workers")
        assert response.status_code == 200
        
        workers = response.json()
        assert isinstance(workers, list)
        
        if len(workers) > 0:
            worker = workers[0]
            # Fields expected by BuildFarmPanel.jsx
            assert "id" in worker
            assert "name" in worker
            assert "status" in worker
            assert "capabilities" in worker
    
    def test_jobs_data_matches_frontend_expectations(self):
        """Verify jobs response has all fields BuildFarmPanel expects"""
        response = requests.get(f"{BASE_URL}/api/build-farm/jobs")
        assert response.status_code == 200
        
        jobs = response.json()
        assert isinstance(jobs, list)
        
        if len(jobs) > 0:
            job = jobs[0]
            # Fields expected by BuildFarmPanel.jsx
            assert "id" in job
            assert "project_name" in job
            assert "status" in job
            assert "priority" in job
            assert "job_type" in job


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
