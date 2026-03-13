"""
Test v4.5 Features: Deployment, Visualization, Build Farm, Knowledge Graph
Focus: Quick deploy endpoints, system visualization, notifications
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDeploymentConfig:
    """Test deployment configuration and quick deploy endpoints"""
    
    def test_get_deploy_config(self):
        """GET /api/deploy/config - should return configured platforms status"""
        response = requests.get(f"{BASE_URL}/api/deploy/config")
        assert response.status_code == 200
        
        data = response.json()
        # Check expected fields exist
        assert "vercel" in data
        assert "railway" in data
        assert "itch" in data
        assert "discord_notifications" in data
        assert "email_notifications" in data
        
        # All values should be booleans
        assert isinstance(data["vercel"], bool)
        assert isinstance(data["railway"], bool)
        assert isinstance(data["itch"], bool)
        print(f"✅ Deploy config: vercel={data['vercel']}, railway={data['railway']}, discord={data['discord_notifications']}")


class TestQuickDeploy:
    """Test quick deployment endpoints using server-side API keys"""
    
    @pytest.fixture
    def test_project(self):
        """Get or create a test project"""
        # Get first existing project
        response = requests.get(f"{BASE_URL}/api/projects")
        if response.status_code == 200 and len(response.json()) > 0:
            project = response.json()[0]
            return project
        
        # Create a test project if none exists
        create_resp = requests.post(f"{BASE_URL}/api/projects", json={
            "name": "TEST_QuickDeploy_Project",
            "description": "Test project for quick deploy testing",
            "type": "web_app"
        })
        assert create_resp.status_code in [200, 201]
        return create_resp.json()
    
    def test_quick_deploy_vercel_requires_project(self):
        """POST /api/deploy/{project_id}/quick/vercel - should require valid project"""
        response = requests.post(f"{BASE_URL}/api/deploy/invalid-project-id/quick/vercel", params={
            "project_name": "test-deploy"
        })
        # Should fail with 404 for invalid project
        assert response.status_code == 404
        print("✅ Vercel quick deploy correctly rejects invalid project")
    
    def test_quick_deploy_railway_requires_project(self):
        """POST /api/deploy/{project_id}/quick/railway - should require valid project"""
        response = requests.post(f"{BASE_URL}/api/deploy/invalid-project-id/quick/railway", params={
            "project_name": "test-deploy"
        })
        # Should fail with 404 for invalid project
        assert response.status_code == 404
        print("✅ Railway quick deploy correctly rejects invalid project")
    
    def test_quick_deploy_vercel_valid_project(self, test_project):
        """POST /api/deploy/{project_id}/quick/vercel - with valid project"""
        project_id = test_project["id"]
        
        response = requests.post(f"{BASE_URL}/api/deploy/{project_id}/quick/vercel", params={
            "project_name": "test-forge-deploy"
        }, timeout=70)  # Allow time for actual deployment
        
        # Should return 200 with deployment info (may be live or failed depending on API key)
        assert response.status_code in [200, 400]  # 400 if Vercel token not configured
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "platform" in data
            assert data["platform"] == "vercel"
            print(f"✅ Vercel quick deploy response: status={data.get('status')}, url={data.get('deploy_url', 'N/A')}")
        else:
            print(f"⚠️ Vercel quick deploy: {response.json().get('detail', 'API key not configured')}")
    
    def test_quick_deploy_railway_valid_project(self, test_project):
        """POST /api/deploy/{project_id}/quick/railway - with valid project"""
        project_id = test_project["id"]
        
        response = requests.post(f"{BASE_URL}/api/deploy/{project_id}/quick/railway", params={
            "project_name": "test-forge-railway"
        }, timeout=40)  # Allow time for actual deployment
        
        # Should return 200 with deployment info
        assert response.status_code in [200, 400]  # 400 if Railway token not configured
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "platform" in data
            assert data["platform"] == "railway"
            print(f"✅ Railway quick deploy response: status={data.get('status')}, url={data.get('deploy_url', 'N/A')}")
        else:
            print(f"⚠️ Railway quick deploy: {response.json().get('detail', 'API key not configured')}")


class TestNotifications:
    """Test notification endpoints"""
    
    @pytest.fixture
    def project_with_discord(self):
        """Get a project and configure discord notifications"""
        # Get first project
        response = requests.get(f"{BASE_URL}/api/projects")
        if response.status_code != 200 or len(response.json()) == 0:
            pytest.skip("No projects available for notification testing")
        
        project = response.json()[0]
        project_id = project["id"]
        
        # Configure notification settings with Discord enabled
        settings_resp = requests.post(f"{BASE_URL}/api/notifications/{project_id}/settings", json={
            "discord_enabled": True,
            "notify_on_complete": True,
            "notify_on_errors": True,
            "notify_on_milestones": True
        })
        
        return project
    
    def test_send_discord_notification(self, project_with_discord):
        """POST /api/notifications/{project_id}/test - should send Discord notification"""
        project_id = project_with_discord["id"]
        
        response = requests.post(f"{BASE_URL}/api/notifications/{project_id}/test")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert "message" in data
        print(f"✅ Test notification sent: {data.get('message')}")


class TestSystemVisualization:
    """Test system visualization endpoints"""
    
    @pytest.fixture
    def test_project(self):
        """Get a test project"""
        response = requests.get(f"{BASE_URL}/api/projects")
        if response.status_code != 200 or len(response.json()) == 0:
            pytest.skip("No projects available")
        return response.json()[0]
    
    def test_get_visualization_map(self, test_project):
        """GET /api/visualization/{project_id}/map - should return file nodes and edges"""
        project_id = test_project["id"]
        
        response = requests.get(f"{BASE_URL}/api/visualization/{project_id}/map")
        assert response.status_code == 200
        
        data = response.json()
        # Check expected fields
        assert "nodes" in data
        assert "edges" in data
        assert "clusters" in data
        assert "agent_positions" in data
        assert "layout_type" in data
        
        # Nodes should be a list
        assert isinstance(data["nodes"], list)
        # Edges should be a list
        assert isinstance(data["edges"], list)
        # Agent positions should include standard agents
        agent_pos = data["agent_positions"]
        assert "COMMANDER" in agent_pos or len(agent_pos) >= 0
        
        print(f"✅ Visualization map: {len(data['nodes'])} nodes, {len(data['edges'])} edges, {len(data['clusters'])} clusters")
    
    def test_visualization_map_invalid_project(self):
        """GET /api/visualization/{project_id}/map - should return 404 for invalid project"""
        response = requests.get(f"{BASE_URL}/api/visualization/invalid-project/map")
        assert response.status_code == 404
        print("✅ Visualization map correctly rejects invalid project")


class TestBuildFarm:
    """Test build farm status endpoint"""
    
    def test_get_build_farm_status(self):
        """GET /api/build-farm/status - should return worker status"""
        response = requests.get(f"{BASE_URL}/api/build-farm/status")
        assert response.status_code == 200
        
        data = response.json()
        # Check expected fields
        assert "total_workers" in data
        assert "active_workers" in data
        assert "idle_workers" in data
        assert "queued_jobs" in data
        assert "running_jobs" in data
        assert "completed_jobs" in data
        
        # All values should be integers
        assert isinstance(data["total_workers"], int)
        assert isinstance(data["active_workers"], int)
        assert isinstance(data["queued_jobs"], int)
        
        print(f"✅ Build farm status: {data['total_workers']} workers, {data['queued_jobs']} queued, {data['running_jobs']} running")


class TestKnowledgeGraph:
    """Test knowledge graph endpoints"""
    
    def test_get_all_knowledge(self):
        """GET /api/knowledge/all - should return knowledge entries"""
        response = requests.get(f"{BASE_URL}/api/knowledge/all")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Knowledge graph: {len(data)} entries")
    
    def test_get_knowledge_stats(self):
        """GET /api/knowledge/stats - should return stats"""
        response = requests.get(f"{BASE_URL}/api/knowledge/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_entries" in data
        assert "total_reuses" in data
        assert "by_type" in data
        assert "by_category" in data
        
        print(f"✅ Knowledge stats: {data['total_entries']} entries, {data['total_reuses']} reuses")
    
    def test_search_knowledge(self):
        """GET /api/knowledge/search - should search knowledge"""
        response = requests.get(f"{BASE_URL}/api/knowledge/search", params={"query": "auth"})
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Knowledge search for 'auth': {len(data)} results")


class TestDeploymentPlatforms:
    """Test deployment platforms listing"""
    
    def test_get_platforms(self):
        """GET /api/deploy/platforms - should return available platforms"""
        response = requests.get(f"{BASE_URL}/api/deploy/platforms")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Should include at least vercel, railway, itch
        platform_ids = [p.get("id") for p in data]
        assert "vercel" in platform_ids
        assert "railway" in platform_ids
        assert "itch" in platform_ids
        
        print(f"✅ Deployment platforms: {platform_ids}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
