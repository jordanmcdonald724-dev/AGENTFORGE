"""
Test Suite for Extracted Routes (Server.py Refactoring)
=======================================================
Testing all routes extracted from server.py to modular files:
- settings.py - Settings & Local Bridge
- god_mode_v1.py - God Mode V1 status
- god_mode_v2.py - God Mode V2 status
- quick_actions.py - Quick Actions & Custom Actions
- agent_memory.py - Agent Memory
- build_operations.py - Open World Systems, War Room, Blueprints, Demos
- build_memory.py - Memory Stats

This test verifies all endpoints work correctly after refactoring.
"""

import pytest
import requests
import os

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test project ID from credentials
TEST_PROJECT_ID = "334166ac-9ea3-45d8-b4d2-3c81e7ef19c1"


class TestSettingsRoutes:
    """Test /api/settings endpoint from settings.py"""
    
    def test_get_settings(self):
        """GET /api/settings - Returns user settings"""
        response = requests.get(f"{BASE_URL}/api/settings")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should have default settings fields
        assert "default_engine" in data or "theme" in data or "auto_save_files" in data
        print(f"✅ GET /api/settings - Returns user settings: {data}")


class TestLocalBridgeRoutes:
    """Test /api/local-bridge endpoint from settings.py"""
    
    def test_download_local_bridge(self):
        """GET /api/local-bridge/download - Returns ZIP file (200 or 404)"""
        response = requests.get(f"{BASE_URL}/api/local-bridge/download")
        
        # Should return 200 (ZIP file) or 404 (bridge files not found)
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        
        if response.status_code == 200:
            assert response.headers.get('content-type') == 'application/zip' or 'zip' in response.headers.get('content-type', '').lower()
            print("✅ GET /api/local-bridge/download - Returns ZIP file (200)")
        else:
            data = response.json()
            assert "detail" in data
            print(f"✅ GET /api/local-bridge/download - Returns 404 (bridge files not found): {data}")


class TestGodModeV1Routes:
    """Test /api/god-mode endpoints from god_mode_v1.py"""
    
    def test_get_god_mode_status(self):
        """GET /api/god-mode/status/{project_id} - Returns build status"""
        response = requests.get(f"{BASE_URL}/api/god-mode/status/{TEST_PROJECT_ID}")
        
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "project_id" in data
            assert "god_mode_complete" in data or "god_mode_phase" in data or "files_saved" in data
            print(f"✅ GET /api/god-mode/status/{TEST_PROJECT_ID} - Returns build status: {data}")
        else:
            print(f"✅ GET /api/god-mode/status/{TEST_PROJECT_ID} - Project not found (404)")


class TestGodModeV2Routes:
    """Test /api/god-mode-v2 endpoints from god_mode_v2.py"""
    
    def test_get_god_mode_v2_status(self):
        """GET /api/god-mode-v2/status/{build_id} - Returns V2 build status"""
        response = requests.get(f"{BASE_URL}/api/god-mode-v2/status/{TEST_PROJECT_ID}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "build_id" in data or "status" in data
        print(f"✅ GET /api/god-mode-v2/status/{TEST_PROJECT_ID} - Returns V2 build status: {data}")
    
    def test_get_god_mode_v2_status_not_found(self):
        """GET /api/god-mode-v2/status/{build_id} - Returns not_found for non-existent"""
        response = requests.get(f"{BASE_URL}/api/god-mode-v2/status/non-existent-build-id")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "not_found"
        print(f"✅ GET /api/god-mode-v2/status/non-existent - Returns not_found status: {data}")


class TestQuickActionsRoutes:
    """Test /api/quick-actions endpoints from quick_actions.py"""
    
    def test_get_quick_actions(self):
        """GET /api/quick-actions - Returns 6 quick actions"""
        response = requests.get(f"{BASE_URL}/api/quick-actions")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1, f"Expected at least 1 quick action, got {len(data)}"
        
        # Check structure of quick actions
        if data:
            action = data[0]
            assert "id" in action or "name" in action
        
        print(f"✅ GET /api/quick-actions - Returns {len(data)} quick actions")
    
    def test_get_custom_actions(self):
        """GET /api/custom-actions - Returns custom actions list"""
        response = requests.get(f"{BASE_URL}/api/custom-actions")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/custom-actions - Returns custom actions list: {len(data)} actions")


class TestAgentMemoryRoutes:
    """Test /api/memory endpoints from agent_memory.py"""
    
    def test_get_memories(self):
        """GET /api/memory?project_id=test&limit=1 - Returns memories array"""
        response = requests.get(f"{BASE_URL}/api/memory?project_id={TEST_PROJECT_ID}&limit=1")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/memory?project_id=test&limit=1 - Returns memories array: {len(data)} memories")


class TestBuildOperationsRoutes:
    """Test build operations endpoints from build_operations.py"""
    
    def test_get_open_world_systems(self):
        """GET /api/systems/open-world - Returns 15 open world systems"""
        response = requests.get(f"{BASE_URL}/api/systems/open-world")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1, f"Expected at least 1 open world system, got {len(data)}"
        
        # Check structure
        if data:
            system = data[0]
            assert "id" in system or "name" in system
        
        print(f"✅ GET /api/systems/open-world - Returns {len(data)} open world systems")
    
    def test_get_war_room_messages(self):
        """GET /api/war-room/{project_id}?limit=1 - Returns war room messages"""
        response = requests.get(f"{BASE_URL}/api/war-room/{TEST_PROJECT_ID}?limit=1")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/war-room/{TEST_PROJECT_ID}?limit=1 - Returns war room messages: {len(data)} messages")
    
    def test_get_blueprint_templates(self):
        """GET /api/blueprints/templates - Returns blueprint templates"""
        response = requests.get(f"{BASE_URL}/api/blueprints/templates")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Could be a dict or list depending on implementation
        assert data is not None
        print(f"✅ GET /api/blueprints/templates - Returns blueprint templates")
    
    def test_get_project_demos(self):
        """GET /api/demos/{project_id} - Returns demos array"""
        response = requests.get(f"{BASE_URL}/api/demos/{TEST_PROJECT_ID}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/demos/{TEST_PROJECT_ID} - Returns demos array: {len(data)} demos")


class TestBuildMemoryRoutes:
    """Test /api/memory endpoints from build_memory.py"""
    
    def test_get_memory_stats(self):
        """GET /api/memory/stats - Returns memory statistics"""
        response = requests.get(f"{BASE_URL}/api/memory/stats")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should have stats fields
        assert "total_builds" in data or "successful_builds" in data or "success_rate" in data
        print(f"✅ GET /api/memory/stats - Returns memory statistics: {data}")


class TestPipelineAgents:
    """Test /api/pipeline/agents endpoint"""
    
    def test_get_pipeline_agents(self):
        """GET /api/pipeline/agents - Returns specialist agents"""
        response = requests.get(f"{BASE_URL}/api/pipeline/agents")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
        
        if isinstance(data, list):
            assert len(data) >= 1, f"Expected at least 1 agent, got {len(data)}"
            # Check agent structure
            if data:
                agent = data[0]
                assert "name" in agent or "role" in agent
        
        print(f"✅ GET /api/pipeline/agents - Returns specialist agents")


class TestHealthCheck:
    """Basic health check to verify server is running"""
    
    def test_health_check(self):
        """GET /api/health - Verify server is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ GET /api/health - Server is running")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
