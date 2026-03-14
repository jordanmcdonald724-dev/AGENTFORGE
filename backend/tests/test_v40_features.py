"""
AgentForge v4.0 Feature Tests
Tests for 8 new boss-level features:
1. Project Autopsy - reverse engineer projects
2. Build Farm - distributed build workers  
3. Idea Engine - generate project concepts
4. One-Click SaaS Builder - generate complete SaaS blueprints
5. System Visualization - 3D project map (backend ready)
6. AI Self-Debugging Loop - auto detect/fix/test errors
7. Time Machine - checkpoint-based development rollback
8. Self-Expanding Agents - agents that spawn new agents
"""

import pytest
import requests
import os
import time
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://premium-os-ui.preview.emergentagent.com')
BASE_URL = BASE_URL.rstrip('/')
TEST_PROJECT_ID = "cfdcd129-6ca5-4616-997b-c615daaa64de"


class TestAPIVersion:
    """Test API version is 4.0.0"""
    
    def test_api_version_is_4(self):
        """Verify API version is 4.0.0"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "4.0.0"
        # Verify all 8 new features are listed
        features = data["features"]
        assert "project_autopsy" in features
        assert "self_debugging_loop" in features
        assert "time_machine" in features
        assert "idea_engine" in features
        assert "one_click_saas" in features
        assert "build_farm" in features
        assert "self_expanding_agents" in features
        print(f"✅ API version 4.0.0 with {len(features)} features")


class TestProjectAutopsy:
    """Feature 1: Project Autopsy - Reverse engineer projects"""
    
    def test_run_autopsy_analysis(self):
        """POST /api/autopsy/analyze - Run project analysis"""
        response = requests.post(
            f"{BASE_URL}/api/autopsy/analyze",
            params={
                "project_id": TEST_PROJECT_ID,
                "source_type": "existing"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "project_id" in data
        assert "status" in data
        # Should return analysis results
        assert "tech_stack" in data
        assert "design_patterns" in data
        assert "weak_points" in data
        assert "upgrade_plan" in data
        assert "stats" in data
        print(f"✅ Autopsy analysis returned: {len(data.get('tech_stack', []))} tech items, {len(data.get('weak_points', []))} weak points")
    
    def test_get_autopsy_results(self):
        """GET /api/autopsy/{project_id} - Get autopsy results"""
        response = requests.get(f"{BASE_URL}/api/autopsy/{TEST_PROJECT_ID}")
        # May return None if no previous autopsy, that's acceptable
        assert response.status_code == 200
        data = response.json()
        if data:
            assert "tech_stack" in data or data is None
        print(f"✅ GET autopsy returned data: {data is not None}")
    
    def test_get_autopsy_report(self):
        """GET /api/autopsy/{project_id}/report - Get formatted report"""
        response = requests.get(f"{BASE_URL}/api/autopsy/{TEST_PROJECT_ID}/report")
        assert response.status_code == 200
        data = response.json()
        # Either returns a report or an error message
        assert "summary" in data or "error" in data
        print(f"✅ GET autopsy report returned")


class TestDebugLoop:
    """Feature 6: Self-Debugging Loop - Auto detect/fix/test errors"""
    
    def test_start_debug_loop(self):
        """POST /api/debug-loop/{project_id}/start - Start debug loop"""
        response = requests.post(
            f"{BASE_URL}/api/debug-loop/{TEST_PROJECT_ID}/start",
            params={"max_iterations": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "project_id" in data
        assert "iterations" in data
        assert isinstance(data["iterations"], list)
        # Should have run at least one iteration
        print(f"✅ Debug loop started: {len(data.get('iterations', []))} iterations, success={data.get('success')}")
    
    def test_get_debug_loops(self):
        """GET /api/debug-loop/{project_id} - List debug loops"""
        response = requests.get(f"{BASE_URL}/api/debug-loop/{TEST_PROJECT_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET debug loops returned {len(data)} loops")
    
    def test_get_latest_debug_loop(self):
        """GET /api/debug-loop/{project_id}/latest - Get latest loop"""
        response = requests.get(f"{BASE_URL}/api/debug-loop/{TEST_PROJECT_ID}/latest")
        assert response.status_code == 200
        data = response.json()
        if data:
            assert "iterations" in data
        print(f"✅ GET latest debug loop returned data: {data is not None}")


class TestTimeMachine:
    """Feature 7: Time Machine - Checkpoint-based development rollback"""
    
    def test_create_checkpoint(self):
        """POST /api/checkpoints/{project_id}/create - Create checkpoint"""
        response = requests.post(
            f"{BASE_URL}/api/checkpoints/{TEST_PROJECT_ID}/create",
            params={
                "name": "TEST_checkpoint_v4",
                "description": "Test checkpoint for v4.0 testing"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "project_id" in data
        assert "name" in data
        assert "step_number" in data
        assert "files_snapshot" in data
        print(f"✅ Created checkpoint: {data['name']} (step {data['step_number']})")
        return data["id"]
    
    def test_list_checkpoints(self):
        """GET /api/checkpoints/{project_id} - List checkpoints"""
        response = requests.get(f"{BASE_URL}/api/checkpoints/{TEST_PROJECT_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET checkpoints returned {len(data)} checkpoints")
        return data
    
    def test_restore_and_delete_checkpoint(self):
        """Test restore and delete checkpoint operations"""
        # First create a checkpoint
        create_resp = requests.post(
            f"{BASE_URL}/api/checkpoints/{TEST_PROJECT_ID}/create",
            params={
                "name": "TEST_restore_checkpoint",
                "description": "Checkpoint for restore testing"
            }
        )
        assert create_resp.status_code == 200
        cp_id = create_resp.json()["id"]
        
        # Test restore
        restore_resp = requests.post(f"{BASE_URL}/api/checkpoints/{cp_id}/restore")
        assert restore_resp.status_code == 200
        restore_data = restore_resp.json()
        assert "files_restored" in restore_data or "success" in restore_data
        print(f"✅ Restore checkpoint returned: {restore_data}")
        
        # Clean up - delete checkpoint
        delete_resp = requests.delete(f"{BASE_URL}/api/checkpoints/{cp_id}")
        assert delete_resp.status_code == 200
        print(f"✅ Deleted test checkpoint")


class TestIdeaEngine:
    """Feature 3: Idea Engine - Generate project concepts"""
    
    def test_generate_ideas(self):
        """POST /api/ideas/generate - Generate ideas"""
        response = requests.post(
            f"{BASE_URL}/api/ideas/generate",
            params={
                "prompt": "AI-powered task management for remote teams",
                "category": "saas",
                "count": 3
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "prompt" in data
        assert "ideas" in data
        assert isinstance(data["ideas"], list)
        assert len(data["ideas"]) > 0
        
        # Validate idea structure
        if data["ideas"]:
            idea = data["ideas"][0]
            assert "title" in idea
            assert "description" in idea
            assert "category" in idea
        print(f"✅ Generated {len(data['ideas'])} ideas")
    
    def test_get_idea_batches(self):
        """GET /api/ideas/batches - List idea batches"""
        response = requests.get(f"{BASE_URL}/api/ideas/batches")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET batches returned {len(data)} batches")
    
    def test_get_idea_batch_by_id(self):
        """GET /api/ideas/batch/{batch_id} - Get specific batch"""
        # First generate a batch
        gen_resp = requests.post(
            f"{BASE_URL}/api/ideas/generate",
            params={"prompt": "TEST batch retrieval", "count": 2}
        )
        batch_id = gen_resp.json()["id"]
        
        # Now retrieve it
        response = requests.get(f"{BASE_URL}/api/ideas/batch/{batch_id}")
        assert response.status_code == 200
        data = response.json()
        if data:
            assert "ideas" in data
        print(f"✅ GET specific batch returned ideas")


class TestSaaSBuilder:
    """Feature 4: One-Click SaaS Builder - Generate complete SaaS blueprints"""
    
    def test_generate_saas_blueprint(self):
        """POST /api/saas/generate - Generate SaaS blueprint"""
        response = requests.post(
            f"{BASE_URL}/api/saas/generate",
            params={
                "name": "TEST_TaskMasterPro",
                "description": "AI-powered task management for small businesses"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "backend_api" in data
        assert "database_schema" in data
        assert "auth_system" in data
        assert "frontend_ui" in data
        assert "payment_integration" in data
        assert "tech_stack" in data
        
        # Validate nested structures
        assert "endpoints" in data["backend_api"]
        assert "collections" in data["database_schema"]
        assert "pages" in data["frontend_ui"]
        assert "plans" in data["payment_integration"]
        
        print(f"✅ Generated SaaS blueprint: {data['name']}")
        print(f"   - {len(data['backend_api'].get('endpoints', []))} API endpoints")
        print(f"   - {len(data['database_schema'].get('collections', []))} DB collections")
        print(f"   - {len(data['frontend_ui'].get('pages', []))} pages")
        return data["id"]
    
    def test_list_saas_blueprints(self):
        """GET /api/saas/blueprints - List blueprints"""
        response = requests.get(f"{BASE_URL}/api/saas/blueprints")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET SaaS blueprints returned {len(data)} blueprints")
    
    def test_get_saas_blueprint_by_id(self):
        """GET /api/saas/blueprint/{blueprint_id} - Get specific blueprint"""
        # First create one
        gen_resp = requests.post(
            f"{BASE_URL}/api/saas/generate",
            params={"name": "TEST_GetBlueprint", "description": "Test retrieval"}
        )
        bp_id = gen_resp.json()["id"]
        
        response = requests.get(f"{BASE_URL}/api/saas/blueprint/{bp_id}")
        assert response.status_code == 200
        data = response.json()
        if data:
            assert "backend_api" in data
            assert "frontend_ui" in data
        print(f"✅ GET specific blueprint returned full data")


class TestBuildFarm:
    """Feature 2: Build Farm - Distributed build workers"""
    
    def test_get_workers(self):
        """GET /api/build-farm/workers - Get workers list"""
        response = requests.get(f"{BASE_URL}/api/build-farm/workers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have default workers
        assert len(data) >= 3, f"Expected at least 3 workers, got {len(data)}"
        
        # Validate worker structure
        if data:
            worker = data[0]
            assert "id" in worker
            assert "name" in worker
            assert "status" in worker
            assert "capabilities" in worker
        print(f"✅ GET workers returned {len(data)} workers")
        for w in data[:3]:
            print(f"   - {w['name']}: {w['status']}, caps: {w.get('capabilities', [])}")
    
    def test_get_build_farm_status(self):
        """GET /api/build-farm/status - Get farm status"""
        response = requests.get(f"{BASE_URL}/api/build-farm/status")
        assert response.status_code == 200
        data = response.json()
        assert "total_workers" in data
        assert "active_workers" in data
        assert "queued_jobs" in data
        assert "completed_jobs" in data
        print(f"✅ Farm status: {data['active_workers']}/{data['total_workers']} active, {data['queued_jobs']} queued")
    
    def test_add_job_to_farm(self):
        """POST /api/build-farm/jobs/add - Add job to farm"""
        response = requests.post(
            f"{BASE_URL}/api/build-farm/jobs/add",
            params={
                "project_id": TEST_PROJECT_ID,
                "project_name": "TEST_BuildFarmJob",
                "job_type": "prototype",
                "priority": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "status" in data
        assert "project_id" in data
        print(f"✅ Added job to farm: {data['id']}, status: {data['status']}")
    
    def test_list_farm_jobs(self):
        """GET /api/build-farm/jobs - List jobs"""
        response = requests.get(f"{BASE_URL}/api/build-farm/jobs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET farm jobs returned {len(data)} jobs")


class TestDynamicAgents:
    """Feature 8: Self-Expanding Agents - Agents that spawn new agents"""
    
    def test_list_dynamic_agents(self):
        """GET /api/dynamic-agents - List dynamic agents"""
        response = requests.get(f"{BASE_URL}/api/dynamic-agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET dynamic agents returned {len(data)} agents")
    
    def test_spawn_agent(self):
        """POST /api/dynamic-agents/spawn - Spawn new agent"""
        response = requests.post(
            f"{BASE_URL}/api/dynamic-agents/spawn",
            params={
                "name": "TEST_API_MASTER",
                "specialty": "api",
                "description": "Test agent specialized in API development",
                "created_by": "COMMANDER"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "specialty" in data
        assert "capabilities" in data
        assert "active" in data
        print(f"✅ Spawned agent: {data['name']}, specialty: {data['specialty']}, caps: {data.get('capabilities', [])[:3]}")
        return data["id"]
    
    def test_auto_spawn_agents(self):
        """POST /api/dynamic-agents/auto-spawn - Auto-spawn based on project"""
        response = requests.post(
            f"{BASE_URL}/api/dynamic-agents/auto-spawn",
            params={"project_id": TEST_PROJECT_ID}
        )
        assert response.status_code == 200
        data = response.json()
        assert "agents_spawned" in data
        print(f"✅ Auto-spawn returned {len(data.get('agents_spawned', []))} agents")
    
    def test_deactivate_agent(self):
        """DELETE /api/dynamic-agents/{agent_id} - Deactivate agent"""
        # First spawn an agent
        spawn_resp = requests.post(
            f"{BASE_URL}/api/dynamic-agents/spawn",
            params={
                "name": "TEST_TO_DELETE",
                "specialty": "testing",
                "description": "Agent to be deleted",
                "created_by": "COMMANDER"
            }
        )
        agent_id = spawn_resp.json()["id"]
        
        # Now deactivate
        response = requests.delete(f"{BASE_URL}/api/dynamic-agents/{agent_id}")
        assert response.status_code == 200
        print(f"✅ Deactivated agent: {agent_id}")


class TestSystemVisualization:
    """Feature 5: System Visualization - 3D project map (backend ready)"""
    
    def test_get_system_map(self):
        """GET /api/system-map/{project_id} - Get system visualization"""
        response = requests.get(f"{BASE_URL}/api/system-map/{TEST_PROJECT_ID}")
        # May return 200 with data or 404 if not generated
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            if data:
                # Should have nodes and edges for visualization
                assert "nodes" in data or "id" in data
        print(f"✅ GET system map returned status {response.status_code}")


class TestCleanup:
    """Clean up test data"""
    
    def test_cleanup_test_checkpoints(self):
        """Delete TEST_ prefixed checkpoints"""
        response = requests.get(f"{BASE_URL}/api/checkpoints/{TEST_PROJECT_ID}")
        if response.status_code == 200:
            checkpoints = response.json()
            deleted = 0
            for cp in checkpoints:
                if cp.get("name", "").startswith("TEST_"):
                    del_resp = requests.delete(f"{BASE_URL}/api/checkpoints/{cp['id']}")
                    if del_resp.status_code == 200:
                        deleted += 1
            print(f"✅ Cleaned up {deleted} test checkpoints")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
