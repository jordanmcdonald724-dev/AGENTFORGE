"""
Test suite for AgentForge Pipeline, God Mode V2, Memory System, and Settings APIs
Tests for new AI Software Factory features:
- Pipeline with 10 specialist agents
- God Mode V2 streaming recursive build
- Memory system statistics
- Settings management
- Local bridge download
"""

import pytest
import requests
import os
import json

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    pytest.skip("REACT_APP_BACKEND_URL not set", allow_module_level=True)

# Test project ID provided in requirements
TEST_PROJECT_ID = "62d21bbb-119c-4938-91ba-5d796d8aa0fd"


class TestPipelineAgents:
    """Test Pipeline API - Specialist Agents System"""
    
    def test_get_all_specialist_agents(self):
        """GET /api/pipeline/agents - Should return all 10 specialist agents"""
        response = requests.get(f"{BASE_URL}/api/pipeline/agents")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Should have specialist agents
        assert isinstance(data, dict), "Response should be a dictionary"
        
        # Check for the expected 10 agents
        expected_agents = ['director', 'architect', 'frontend', 'backend', 'game_engine', 
                          'ai_engineer', 'devops', 'reviewer', 'refactor', 'tester']
        
        for agent_key in expected_agents:
            assert agent_key in data, f"Missing agent: {agent_key}"
            
        # Verify agent structure
        director = data.get('director', {})
        assert 'name' in director, "Agent should have 'name'"
        assert 'role' in director, "Agent should have 'role'"
        assert 'prompt' in director, "Agent should have 'prompt'"
        assert 'specialization' in director, "Agent should have 'specialization'"
        assert 'color' in director, "Agent should have 'color'"
        
        # Verify specific agent names
        assert data['director']['name'] == 'DIRECTOR', "Director name should be DIRECTOR"
        assert data['architect']['name'] == 'ATLAS', "Architect name should be ATLAS"
        assert data['frontend']['name'] == 'PIXEL', "Frontend name should be PIXEL"
        assert data['backend']['name'] == 'NEXUS', "Backend name should be NEXUS"
        assert data['game_engine']['name'] == 'TITAN', "Game engine name should be TITAN"
        assert data['ai_engineer']['name'] == 'SYNAPSE', "AI engineer name should be SYNAPSE"
        assert data['devops']['name'] == 'DEPLOY', "DevOps name should be DEPLOY"
        assert data['reviewer']['name'] == 'SENTINEL', "Reviewer name should be SENTINEL"
        assert data['refactor']['name'] == 'PHOENIX', "Refactor name should be PHOENIX"
        assert data['tester']['name'] == 'PROBE', "Tester name should be PROBE"
        
        print(f"✅ All 10 specialist agents verified: {list(data.keys())}")


class TestPipelineOperations:
    """Test Pipeline creation and management"""
    
    def test_create_build_pipeline_game(self):
        """POST /api/pipeline/create - Create a game build pipeline"""
        response = requests.post(
            f"{BASE_URL}/api/pipeline/create",
            params={
                "project_id": TEST_PROJECT_ID,
                "build_type": "game"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert 'id' in data, "Pipeline should have 'id'"
        assert 'project_id' in data, "Pipeline should have 'project_id'"
        assert data['project_id'] == TEST_PROJECT_ID, "Project ID should match"
        assert 'phases' in data, "Pipeline should have 'phases'"
        assert isinstance(data['phases'], list), "Phases should be a list"
        assert len(data['phases']) > 0, "Should have at least one phase"
        
        # Store pipeline ID for next test
        self.__class__.pipeline_id = data['id']
        print(f"✅ Game pipeline created with {len(data['phases'])} phases")
        
    def test_create_build_pipeline_web(self):
        """POST /api/pipeline/create - Create a web build pipeline"""
        response = requests.post(
            f"{BASE_URL}/api/pipeline/create",
            params={
                "project_id": TEST_PROJECT_ID,
                "build_type": "web"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert len(data['phases']) > 0, "Should have phases for web build"
        print(f"✅ Web pipeline created with {len(data['phases'])} phases")
        
    def test_get_pipeline_status(self):
        """GET /api/pipeline/{id} - Get pipeline status"""
        if not hasattr(self.__class__, 'pipeline_id'):
            pytest.skip("No pipeline ID from previous test")
            
        response = requests.get(f"{BASE_URL}/api/pipeline/{self.pipeline_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['id'] == self.pipeline_id, "Pipeline ID should match"
        assert 'status' in data, "Should have status"
        assert 'phases' in data, "Should have phases"
        print(f"✅ Pipeline status: {data['status']}")
        
    def test_get_pipeline_not_found(self):
        """GET /api/pipeline/{id} - Non-existent pipeline returns 404"""
        response = requests.get(f"{BASE_URL}/api/pipeline/non-existent-id-12345")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✅ Non-existent pipeline returns 404")


class TestGodModeV2:
    """Test God Mode V2 - Streaming recursive build"""
    
    def test_god_mode_v2_build_stream_endpoint_exists(self):
        """POST /api/god-mode-v2/build/stream - Endpoint should exist"""
        # Just verify the endpoint exists and accepts the request
        # We won't actually stream the full build as it takes time
        response = requests.post(
            f"{BASE_URL}/api/god-mode-v2/build/stream",
            json={
                "project_id": TEST_PROJECT_ID,
                "iterations": 1,
                "auto_review": False,
                "quality_target": 80
            },
            stream=True,
            timeout=10
        )
        
        # Should start streaming or return project not found
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        
        if response.status_code == 200:
            # Check content type for SSE
            assert 'text/event-stream' in response.headers.get('Content-Type', ''), \
                "Should return event stream"
            print("✅ God Mode V2 streaming endpoint working")
        else:
            print("✅ God Mode V2 endpoint exists (project not found)")


class TestMemorySystem:
    """Test Build Memory/Learning System APIs"""
    
    def test_get_memory_stats(self):
        """GET /api/memory/stats - Memory system statistics"""
        response = requests.get(f"{BASE_URL}/api/memory/stats")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'total_builds' in data, "Should have total_builds"
        assert 'successful_builds' in data, "Should have successful_builds"
        assert 'success_rate' in data, "Should have success_rate"
        assert 'total_insights' in data, "Should have total_insights"
        
        print(f"✅ Memory stats: {data['total_builds']} builds, {data['success_rate']}% success rate")
        
    def test_get_build_recommendations(self):
        """GET /api/memory/recommendations/{project_type} - Build recommendations"""
        response = requests.get(f"{BASE_URL}/api/memory/recommendations/game")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Should have recommendation fields even if empty
        assert isinstance(data, dict), "Response should be a dictionary"
        assert 'recommended_architecture' in data or 'patterns_that_work' in data, \
            "Should have recommendation fields"
            
        print(f"✅ Build recommendations retrieved for game projects")
        
    def test_get_build_recommendations_web(self):
        """GET /api/memory/recommendations/web - Web build recommendations"""
        response = requests.get(f"{BASE_URL}/api/memory/recommendations/web")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ Web build recommendations retrieved")
        
    def test_update_agent_performance(self):
        """POST /api/memory/agent/performance/update - Update agent performance"""
        response = requests.post(
            f"{BASE_URL}/api/memory/agent/performance/update",
            params={
                "agent_name": "TITAN",
                "agent_role": "game_engine_engineer",
                "task_successful": True,
                "quality_score": 85,
                "time_seconds": 120
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get('success') == True, "Should return success"
        print("✅ Agent performance updated successfully")
        
    def test_get_learning_insights(self):
        """GET /api/memory/insights - Learning insights"""
        response = requests.get(f"{BASE_URL}/api/memory/insights")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return a list of insights"
        print(f"✅ Retrieved {len(data)} learning insights")


class TestSettingsAPI:
    """Test Settings API"""
    
    def test_get_settings(self):
        """GET /api/settings - Get user settings"""
        response = requests.get(f"{BASE_URL}/api/settings")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Should have default fields
        assert 'default_engine' in data or 'theme' in data, "Should have settings fields"
        print(f"✅ Settings retrieved: engine={data.get('default_engine')}, theme={data.get('theme')}")
        
    def test_save_settings(self):
        """POST /api/settings - Save settings"""
        settings = {
            "default_engine": "unreal",
            "theme": "dark",
            "auto_save_files": True,
            "streaming_mode": "sse"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/settings",
            json=settings
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get('success') == True, "Should return success"
        print("✅ Settings saved successfully")
        
    def test_verify_settings_persisted(self):
        """GET /api/settings - Verify settings were persisted"""
        response = requests.get(f"{BASE_URL}/api/settings")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get('default_engine') == 'unreal', "Engine setting should persist"
        print("✅ Settings persistence verified")


class TestGodModeDownload:
    """Test God Mode Download - ZIP file generation"""
    
    def test_download_endpoint_exists(self):
        """GET /api/god-mode/download/{project_id} - Download endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/god-mode/download/{TEST_PROJECT_ID}",
            allow_redirects=False
        )
        
        # Could be 200 (with files) or 404 (no files) or 500 (project not found)
        assert response.status_code in [200, 404, 500], \
            f"Unexpected status: {response.status_code}"
            
        if response.status_code == 200:
            # Check if it's a ZIP file
            content_type = response.headers.get('Content-Type', '')
            assert 'zip' in content_type.lower() or 'octet-stream' in content_type.lower(), \
                "Should return ZIP file"
            print("✅ Download endpoint returns ZIP")
        else:
            print(f"✅ Download endpoint exists (status: {response.status_code})")


class TestLocalBridge:
    """Test Local Bridge endpoints"""
    
    def test_local_bridge_download_endpoint(self):
        """GET /api/local-bridge/download - Download local bridge"""
        response = requests.get(f"{BASE_URL}/api/local-bridge/download")
        
        # Might be 404 if bridge files not present, 200 if present
        assert response.status_code in [200, 404], \
            f"Unexpected status: {response.status_code}"
            
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            assert 'zip' in content_type.lower() or 'octet-stream' in content_type.lower(), \
                "Should return ZIP file"
            print("✅ Local bridge download working")
        else:
            print("✅ Local bridge endpoint exists (files not found - expected)")


class TestHealthAndMisc:
    """Verify core endpoints still work"""
    
    def test_health_check(self):
        """GET /api/health - Health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get('status') == 'healthy', "Should be healthy"
        print("✅ Health check passed")
        
    def test_get_projects_list(self):
        """GET /api/projects - Verify projects list works"""
        response = requests.get(f"{BASE_URL}/api/projects")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return list of projects"
        print(f"✅ Projects list: {len(data)} projects")
        
    def test_get_test_project(self):
        """GET /api/projects/{id} - Get test project"""
        response = requests.get(f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}")
        
        # Project may or may not exist
        if response.status_code == 200:
            data = response.json()
            assert 'id' in data, "Project should have ID"
            print(f"✅ Test project found: {data.get('name', 'Unknown')}")
        else:
            print(f"ℹ️ Test project not found (status: {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
