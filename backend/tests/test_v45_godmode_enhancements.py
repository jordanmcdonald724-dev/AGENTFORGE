"""
Test suite for God Mode V2 Enhancements (Iteration 20)
- Build status endpoint
- Memory system integration
- Agent performance tracking
- Pipeline agents configuration
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGodModeV2Enhancements:
    """Test the enhanced God Mode V2 features"""
    
    # Test project ID from previous builds
    TEST_PROJECT_ID = "334166ac-9ea3-45d8-b4d2-3c81e7ef19c1"
    
    def test_build_status_for_existing_project(self):
        """GET /api/god-mode-v2/status/{build_id} - Returns build status"""
        response = requests.get(f"{BASE_URL}/api/god-mode-v2/status/{self.TEST_PROJECT_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "build_id" in data
        assert data["build_id"] == self.TEST_PROJECT_ID
        assert "status" in data
        # Status could be not_started, in_progress, complete, etc.
        assert data["status"] in ["not_started", "in_progress", "complete", "not_found"]
        print(f"✅ Build status for existing project: {data['status']}")
    
    def test_build_status_for_nonexistent_project(self):
        """GET /api/god-mode-v2/status/{build_id} - Returns not_found for non-existent"""
        response = requests.get(f"{BASE_URL}/api/god-mode-v2/status/nonexistent-build-12345")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "not_found"
        print("✅ Build status correctly returns 'not_found' for non-existent project")


class TestMemorySystem:
    """Test the memory system endpoints"""
    
    def test_memory_stats(self):
        """GET /api/memory/stats - Returns memory system statistics"""
        response = requests.get(f"{BASE_URL}/api/memory/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_builds" in data
        assert "successful_builds" in data
        assert "success_rate" in data
        assert "total_insights" in data
        assert "by_project_type" in data
        
        # All values should be numbers
        assert isinstance(data["total_builds"], int)
        assert isinstance(data["successful_builds"], int)
        assert isinstance(data["success_rate"], (int, float))
        assert isinstance(data["total_insights"], int)
        print(f"✅ Memory stats: {data['total_builds']} total builds, {data['success_rate']}% success rate")
    
    def test_memory_recommendations_game(self):
        """GET /api/memory/recommendations/game - Returns recommendations for game type"""
        response = requests.get(f"{BASE_URL}/api/memory/recommendations/game")
        assert response.status_code == 200
        
        data = response.json()
        assert "recommended_architecture" in data
        assert "recommended_tech_stack" in data
        assert "patterns_that_work" in data
        assert "patterns_to_avoid" in data
        assert "best_performing_agents" in data
        assert "insights" in data
        
        # patterns should be lists
        assert isinstance(data["patterns_that_work"], list)
        assert isinstance(data["patterns_to_avoid"], list)
        assert isinstance(data["best_performing_agents"], list)
        assert isinstance(data["insights"], list)
        print(f"✅ Game recommendations retrieved with {len(data['best_performing_agents'])} top agents")
    
    def test_memory_recommendations_web(self):
        """GET /api/memory/recommendations/web - Returns recommendations for web type"""
        response = requests.get(f"{BASE_URL}/api/memory/recommendations/web")
        assert response.status_code == 200
        
        data = response.json()
        assert "recommended_architecture" in data
        assert "patterns_that_work" in data
        print("✅ Web recommendations retrieved successfully")
    
    def test_agent_performance_update(self):
        """POST /api/memory/agent/performance/update - Updates agent performance"""
        params = {
            "agent_name": "TEST_AGENT_PERFORMANCE",
            "agent_role": "test_role",
            "task_successful": True,
            "quality_score": 90,
            "time_seconds": 60
        }
        response = requests.post(f"{BASE_URL}/api/memory/agent/performance/update", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        print("✅ Agent performance updated successfully")
    
    def test_agent_performance_retrieval(self):
        """GET /api/memory/agent/performance/{agent_name} - Retrieves agent performance"""
        response = requests.get(f"{BASE_URL}/api/memory/agent/performance/TEST_AGENT_PERFORMANCE")
        assert response.status_code == 200
        
        data = response.json()
        assert "agent_name" in data
        print(f"✅ Agent performance retrieved: {data.get('total_tasks', 0)} total tasks")


class TestPipelineAgents:
    """Test the pipeline specialist agents configuration"""
    
    def test_get_all_specialist_agents(self):
        """GET /api/pipeline/agents - Returns all 10 specialist agents"""
        response = requests.get(f"{BASE_URL}/api/pipeline/agents")
        assert response.status_code == 200
        
        data = response.json()
        
        # Should have exactly 10 specialist agents
        assert len(data) == 10
        
        # Verify all expected agents exist
        expected_agents = [
            "director", "architect", "frontend", "backend", "game_engine",
            "ai_engineer", "devops", "reviewer", "refactor", "tester"
        ]
        for agent_key in expected_agents:
            assert agent_key in data, f"Missing agent: {agent_key}"
            
            agent = data[agent_key]
            assert "name" in agent
            assert "role" in agent
            assert "prompt" in agent
            assert "specialization" in agent
            assert "color" in agent
        
        # Verify agent names
        agent_names = [data[key]["name"] for key in expected_agents]
        expected_names = ["DIRECTOR", "ATLAS", "PIXEL", "NEXUS", "TITAN", 
                         "SYNAPSE", "DEPLOY", "SENTINEL", "PHOENIX", "PROBE"]
        assert agent_names == expected_names
        
        print(f"✅ All 10 specialist agents verified: {', '.join(expected_names)}")
    
    def test_agent_has_required_fields(self):
        """Verify each agent has all required configuration fields"""
        response = requests.get(f"{BASE_URL}/api/pipeline/agents")
        data = response.json()
        
        for key, agent in data.items():
            assert "name" in agent, f"{key} missing 'name'"
            assert "role" in agent, f"{key} missing 'role'"
            assert "prompt" in agent, f"{key} missing 'prompt'"
            assert "specialization" in agent, f"{key} missing 'specialization'"
            assert "color" in agent, f"{key} missing 'color'"
            
            # Specialization should be a list
            assert isinstance(agent["specialization"], list)
            # Color should be a hex color
            assert agent["color"].startswith("#")
        
        print("✅ All agents have required fields (name, role, prompt, specialization, color)")


class TestHealthAndBasicEndpoints:
    """Test basic health and project endpoints"""
    
    def test_health_check(self):
        """GET /api/health - Health check passes"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health check passed")
    
    def test_projects_list(self):
        """GET /api/projects - Projects list returns"""
        response = requests.get(f"{BASE_URL}/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Projects list returned {len(data)} projects")
    
    def test_get_test_project(self):
        """GET /api/projects/{id} - Test project retrieved"""
        response = requests.get(f"{BASE_URL}/api/projects/334166ac-9ea3-45d8-b4d2-3c81e7ef19c1")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        print(f"✅ Test project retrieved: {data.get('name')}")


class TestBuildCancellation:
    """Test build cancellation endpoint"""
    
    def test_cancel_nonexistent_build(self):
        """POST /api/god-mode-v2/cancel/{build_id} - Returns failure for non-existent"""
        response = requests.post(f"{BASE_URL}/api/god-mode-v2/cancel/nonexistent-build-12345")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "not found" in data["message"].lower() or "already completed" in data["message"].lower()
        print("✅ Cancel correctly fails for non-existent build")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
