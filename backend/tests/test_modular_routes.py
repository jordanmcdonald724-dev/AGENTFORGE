"""
Backend Tests for AgentForge v4.5 Modular Routes
Tests core functionality after refactoring from monolith to modular architecture.
"""
import pytest
import requests
import os
import uuid

# Use public URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndRoot:
    """Health and root endpoint tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "timestamp" in data
        print("✅ GET /api/health - Returns healthy status")
    
    def test_root_endpoint(self):
        """Test /api/ returns API info with features list"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "features" in data
        assert isinstance(data["features"], list)
        assert len(data["features"]) > 20  # Should have many features
        print(f"✅ GET /api/ - Returns {len(data['features'])} features")


class TestProjectsCRUD:
    """Projects CRUD endpoint tests"""
    
    def test_get_projects(self):
        """Test GET /api/projects returns list"""
        response = requests.get(f"{BASE_URL}/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/projects - Returns {len(data)} projects")
    
    def test_create_project(self):
        """Test POST /api/projects creates new project"""
        project_data = {
            "name": f"TEST_Project_{uuid.uuid4().hex[:8]}",
            "description": "Test project created by automated testing",
            "type": "web_app"
        }
        response = requests.post(f"{BASE_URL}/api/projects", json=project_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == project_data["name"]
        assert data["type"] == "web_app"
        print(f"✅ POST /api/projects - Created project with ID: {data['id'][:8]}...")
        return data["id"]
    
    def test_get_project_by_id(self):
        """Test GET /api/projects/{id} returns specific project"""
        # First create a project
        project_data = {
            "name": f"TEST_GetById_{uuid.uuid4().hex[:8]}",
            "description": "Test project for get by ID",
            "type": "web_app"
        }
        create_response = requests.post(f"{BASE_URL}/api/projects", json=project_data)
        assert create_response.status_code == 200
        project_id = create_response.json()["id"]
        
        # Then get it by ID
        response = requests.get(f"{BASE_URL}/api/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == project_data["name"]
        print(f"✅ GET /api/projects/{{id}} - Retrieved project successfully")
    
    def test_delete_project(self):
        """Test DELETE /api/projects/{id}"""
        # First create a project
        project_data = {
            "name": f"TEST_ToDelete_{uuid.uuid4().hex[:8]}",
            "description": "Test project for deletion",
            "type": "web_app"
        }
        create_response = requests.post(f"{BASE_URL}/api/projects", json=project_data)
        project_id = create_response.json()["id"]
        
        # Then delete it
        response = requests.delete(f"{BASE_URL}/api/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ DELETE /api/projects/{{id}} - Deleted project successfully")


class TestAgents:
    """Agents endpoint tests - should return 6 agents"""
    
    def test_get_agents(self):
        """Test GET /api/agents returns all 6 agents"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 6, f"Expected 6 agents, got {len(data)}"
        
        # Verify agent roles
        roles = [agent["role"] for agent in data]
        expected_roles = ["lead", "architect", "developer", "reviewer", "tester", "artist"]
        for role in expected_roles:
            assert role in roles, f"Missing agent role: {role}"
        
        # Verify agent names
        names = [agent["name"] for agent in data]
        expected_names = ["COMMANDER", "ATLAS", "FORGE", "SENTINEL", "PROBE", "PRISM"]
        for name in expected_names:
            assert name in names, f"Missing agent: {name}"
        
        print(f"✅ GET /api/agents - Returns all 6 agents: {', '.join(names)}")


class TestTasks:
    """Tasks endpoint tests"""
    
    def test_get_tasks(self):
        """Test GET /api/tasks returns list"""
        response = requests.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/tasks - Returns {len(data)} tasks")


class TestFiles:
    """Files endpoint tests"""
    
    def test_get_files_requires_project_id(self):
        """Test GET /api/files with project_id"""
        # First create a project
        project_data = {
            "name": f"TEST_FilesProject_{uuid.uuid4().hex[:8]}",
            "description": "Test project for files",
            "type": "web_app"
        }
        create_response = requests.post(f"{BASE_URL}/api/projects", json=project_data)
        project_id = create_response.json()["id"]
        
        response = requests.get(f"{BASE_URL}/api/files?project_id={project_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/files - Returns files list for project")


class TestPlans:
    """Plans endpoint tests"""
    
    def test_get_plan(self):
        """Test GET /api/plans/{project_id}"""
        # First create a project
        project_data = {
            "name": f"TEST_PlanProject_{uuid.uuid4().hex[:8]}",
            "description": "Test project for plans",
            "type": "web_app"
        }
        create_response = requests.post(f"{BASE_URL}/api/projects", json=project_data)
        project_id = create_response.json()["id"]
        
        response = requests.get(f"{BASE_URL}/api/plans/{project_id}")
        # Plan may not exist, that's ok - we just need the endpoint to work
        assert response.status_code in [200, 404] or (response.status_code == 200 and response.json() is None)
        print(f"✅ GET /api/plans/{{project_id}} - Endpoint working")


class TestWorldModelLabs:
    """World Model Labs endpoint tests"""
    
    def test_get_categories(self):
        """Test GET /api/world-model/categories"""
        response = requests.get(f"{BASE_URL}/api/world-model/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        expected_categories = ["frontend", "backend", "game_engines", "infrastructure", "ai_ml"]
        for cat in expected_categories:
            assert cat in data, f"Missing category: {cat}"
        print(f"✅ GET /api/world-model/categories - Returns {len(data)} categories")
    
    def test_get_graph(self):
        """Test GET /api/world-model/graph"""
        response = requests.get(f"{BASE_URL}/api/world-model/graph")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert "stats" in data
        print(f"✅ GET /api/world-model/graph - Returns nodes, edges, stats")
    
    def test_get_insights(self):
        """Test GET /api/world-model/insights"""
        response = requests.get(f"{BASE_URL}/api/world-model/insights")
        assert response.status_code == 200
        data = response.json()
        assert "total_projects_analyzed" in data
        assert "top_technologies" in data
        assert "recommendations" in data
        print(f"✅ GET /api/world-model/insights - Returns analytics")


class TestGodModeLabs:
    """God Mode Labs endpoint tests"""
    
    def test_get_templates(self):
        """Test GET /api/god-mode/templates"""
        response = requests.get(f"{BASE_URL}/api/god-mode/templates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        expected_templates = ["analytics", "marketplace", "saas_starter", "ai_tool", "community"]
        for template in expected_templates:
            assert template in data, f"Missing template: {template}"
        print(f"✅ GET /api/god-mode/templates - Returns {len(data)} templates")


class TestDiscoveryLabs:
    """Discovery Labs endpoint tests"""
    
    def test_get_types(self):
        """Test GET /api/discovery/types"""
        response = requests.get(f"{BASE_URL}/api/discovery/types")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        expected_types = ["architecture", "ui_component", "algorithm", "integration", "game_system"]
        for exp_type in expected_types:
            assert exp_type in data, f"Missing experiment type: {exp_type}"
        print(f"✅ GET /api/discovery/types - Returns {len(data)} experiment types")
    
    def test_list_experiments(self):
        """Test GET /api/discovery/experiments"""
        response = requests.get(f"{BASE_URL}/api/discovery/experiments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/discovery/experiments - Returns {len(data)} experiments")


class TestMarketplaceLabs:
    """Marketplace Labs endpoint tests"""
    
    def test_get_categories(self):
        """Test GET /api/marketplace/categories"""
        response = requests.get(f"{BASE_URL}/api/marketplace/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        expected_categories = ["frontend", "backend", "game", "ai", "infrastructure"]
        for cat in expected_categories:
            assert cat in data, f"Missing category: {cat}"
        print(f"✅ GET /api/marketplace/categories - Returns {len(data)} categories")
    
    def test_list_modules(self):
        """Test GET /api/marketplace/modules"""
        response = requests.get(f"{BASE_URL}/api/marketplace/modules")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/marketplace/modules - Returns {len(data)} modules")


class TestSoftwareDNALabs:
    """Software DNA Labs endpoint tests"""
    
    def test_get_categories(self):
        """Test GET /api/dna/categories"""
        response = requests.get(f"{BASE_URL}/api/dna/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        expected_categories = ["auth", "ui", "data", "game", "infra", "ai"]
        for cat in expected_categories:
            assert cat in data, f"Missing gene category: {cat}"
        print(f"✅ GET /api/dna/categories - Returns {len(data)} gene categories")
    
    def test_get_library(self):
        """Test GET /api/dna/library"""
        response = requests.get(f"{BASE_URL}/api/dna/library")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "genes" in data
        assert "total_genes" in data
        assert "stats" in data
        print(f"✅ GET /api/dna/library - Returns gene library with stats")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_projects(self):
        """Clean up TEST_ prefixed projects"""
        # Get all projects
        response = requests.get(f"{BASE_URL}/api/projects")
        if response.status_code == 200:
            projects = response.json()
            test_projects = [p for p in projects if p.get("name", "").startswith("TEST_")]
            for project in test_projects:
                requests.delete(f"{BASE_URL}/api/projects/{project['id']}")
            print(f"✅ Cleaned up {len(test_projects)} test projects")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
