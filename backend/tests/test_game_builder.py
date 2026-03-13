"""
Game Builder API Tests - Unreal Engine 5 & Unity Support
Tests all game builder endpoints: detect engines, templates, projects, builds, config
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestGameBuilderDetection:
    """Tests for engine detection endpoint"""
    
    def test_detect_engines_endpoint(self):
        """Test /api/game-builder/detect returns proper structure"""
        response = requests.get(f"{BASE_URL}/api/game-builder/detect")
        assert response.status_code == 200
        
        data = response.json()
        # Validate response structure
        assert "os" in data
        assert "engines" in data
        assert "unreal_installations" in data
        assert "unity_installations" in data
        
        # engines should be a list
        assert isinstance(data["engines"], list)
        assert isinstance(data["unreal_installations"], list)
        assert isinstance(data["unity_installations"], list)
        
        print(f"Detected OS: {data['os']}")
        print(f"Engines found: {len(data['engines'])}")


class TestGameBuilderTemplates:
    """Tests for template endpoints"""
    
    def test_unreal_templates(self):
        """Test GET /api/game-builder/templates/unreal returns templates"""
        response = requests.get(f"{BASE_URL}/api/game-builder/templates/unreal")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify expected templates exist
        expected_templates = ["blank", "first_person", "third_person", "top_down"]
        for template in expected_templates:
            assert template in data, f"Missing template: {template}"
            assert "name" in data[template]
            assert "description" in data[template]
        
        print(f"Unreal templates: {list(data.keys())}")
    
    def test_unity_templates(self):
        """Test GET /api/game-builder/templates/unity returns templates"""
        response = requests.get(f"{BASE_URL}/api/game-builder/templates/unity")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify expected templates exist
        expected_templates = ["blank", "2d", "3d", "urp", "vr"]
        for template in expected_templates:
            assert template in data, f"Missing template: {template}"
            assert "name" in data[template]
            assert "description" in data[template]
        
        print(f"Unity templates: {list(data.keys())}")
    
    def test_invalid_engine_templates(self):
        """Test GET /api/game-builder/templates/invalid returns 400"""
        response = requests.get(f"{BASE_URL}/api/game-builder/templates/invalid_engine")
        assert response.status_code == 400


class TestGameBuilderPlatforms:
    """Tests for build platforms endpoints"""
    
    def test_unreal_platforms(self):
        """Test GET /api/game-builder/platforms/unreal"""
        response = requests.get(f"{BASE_URL}/api/game-builder/platforms/unreal")
        assert response.status_code == 200
        
        data = response.json()
        assert "engine" in data
        assert data["engine"] == "unreal"
        assert "platforms" in data
        assert "configurations" in data
        
        # Verify expected platforms
        assert "Win64" in data["platforms"]
        assert "Development" in data["configurations"]
        
        print(f"Unreal platforms: {data['platforms']}")
    
    def test_unity_platforms(self):
        """Test GET /api/game-builder/platforms/unity"""
        response = requests.get(f"{BASE_URL}/api/game-builder/platforms/unity")
        assert response.status_code == 200
        
        data = response.json()
        assert "engine" in data
        assert data["engine"] == "unity"
        assert "platforms" in data
        assert "configurations" in data
        
        # Verify expected platforms
        assert "StandaloneWindows64" in data["platforms"]
        assert "Debug" in data["configurations"]
        
        print(f"Unity platforms: {data['platforms']}")


class TestGameBuilderProjects:
    """Tests for project CRUD operations"""
    
    @pytest.fixture
    def created_project_id(self):
        """Fixture to create a test project and clean up after"""
        # Create an Unreal project
        payload = {
            "name": "TEST_UnrealGame",
            "description": "Test project for pytest",
            "engine": "unreal",
            "template": "blank",
            "platforms": ["Win64"]
        }
        response = requests.post(f"{BASE_URL}/api/game-builder/projects", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        project_id = data["project_id"]
        
        yield project_id
        
        # Cleanup - delete the project
        requests.delete(f"{BASE_URL}/api/game-builder/projects/{project_id}")
    
    def test_create_unreal_project(self):
        """Test POST /api/game-builder/projects with Unreal Engine"""
        payload = {
            "name": "TEST_MyUnrealGame",
            "description": "A test Unreal project",
            "engine": "unreal",
            "template": "first_person",
            "platforms": ["Win64"]
        }
        response = requests.post(f"{BASE_URL}/api/game-builder/projects", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "project_id" in data
        assert data["engine"] == "Unreal Engine 5"
        assert data["status"] == "creating"
        
        project_id = data["project_id"]
        print(f"Created Unreal project: {project_id}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/game-builder/projects/{project_id}")
    
    def test_create_unity_project(self):
        """Test POST /api/game-builder/projects with Unity"""
        payload = {
            "name": "TEST_MyUnityGame",
            "description": "A test Unity project",
            "engine": "unity",
            "template": "3d",
            "platforms": ["StandaloneWindows64"]
        }
        response = requests.post(f"{BASE_URL}/api/game-builder/projects", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "project_id" in data
        assert data["engine"] == "Unity"
        assert data["status"] == "creating"
        
        project_id = data["project_id"]
        print(f"Created Unity project: {project_id}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/game-builder/projects/{project_id}")
    
    def test_create_project_invalid_engine(self):
        """Test POST /api/game-builder/projects with invalid engine"""
        payload = {
            "name": "TEST_InvalidGame",
            "description": "Should fail",
            "engine": "invalid_engine",
            "template": "blank",
            "platforms": ["Win64"]
        }
        response = requests.post(f"{BASE_URL}/api/game-builder/projects", json=payload)
        assert response.status_code == 400
    
    def test_list_projects(self):
        """Test GET /api/game-builder/projects"""
        response = requests.get(f"{BASE_URL}/api/game-builder/projects")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"Total projects in list: {len(data)}")
    
    def test_get_project_by_id(self, created_project_id):
        """Test GET /api/game-builder/projects/{id}"""
        # Wait for project to be created
        time.sleep(1)
        
        response = requests.get(f"{BASE_URL}/api/game-builder/projects/{created_project_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == created_project_id
        assert data["name"] == "TEST_UnrealGame"
        assert data["engine"] == "unreal"
        print(f"Project status: {data['status']}")
    
    def test_get_project_not_found(self):
        """Test GET /api/game-builder/projects/{invalid_id}"""
        response = requests.get(f"{BASE_URL}/api/game-builder/projects/nonexistent-id")
        assert response.status_code == 404
    
    def test_delete_project(self):
        """Test DELETE /api/game-builder/projects/{id}"""
        # Create a project first
        payload = {
            "name": "TEST_ToBeDeleted",
            "description": "Will be deleted",
            "engine": "unreal",
            "template": "blank",
            "platforms": ["Win64"]
        }
        create_response = requests.post(f"{BASE_URL}/api/game-builder/projects", json=payload)
        project_id = create_response.json()["project_id"]
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/game-builder/projects/{project_id}")
        assert response.status_code == 200
        
        # Verify it's gone
        get_response = requests.get(f"{BASE_URL}/api/game-builder/projects/{project_id}")
        assert get_response.status_code == 404
        
        print(f"Successfully deleted project: {project_id}")


class TestGameBuilderBuilds:
    """Tests for build request endpoints"""
    
    @pytest.fixture
    def project_for_build(self):
        """Create a project for build testing"""
        payload = {
            "name": "TEST_BuildProject",
            "description": "For build testing",
            "engine": "unreal",
            "template": "blank",
            "platforms": ["Win64"]
        }
        response = requests.post(f"{BASE_URL}/api/game-builder/projects", json=payload)
        project_id = response.json()["project_id"]
        
        # Wait for project to be ready
        time.sleep(2)
        
        yield project_id
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/game-builder/projects/{project_id}")
    
    def test_start_build(self, project_for_build):
        """Test POST /api/game-builder/build"""
        payload = {
            "project_id": project_for_build,
            "platform": "Win64",
            "configuration": "Development",
            "clean_build": False
        }
        response = requests.post(f"{BASE_URL}/api/game-builder/build", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "build_id" in data
        assert data["status"] == "queued"
        
        build_id = data["build_id"]
        print(f"Started build: {build_id}")
        
        # Verify build is in list
        time.sleep(1)
        builds_response = requests.get(f"{BASE_URL}/api/game-builder/builds")
        builds = builds_response.json()
        assert any(b["id"] == build_id for b in builds)
    
    def test_build_invalid_project(self):
        """Test POST /api/game-builder/build with invalid project"""
        payload = {
            "project_id": "nonexistent-project-id",
            "platform": "Win64",
            "configuration": "Development"
        }
        response = requests.post(f"{BASE_URL}/api/game-builder/build", json=payload)
        assert response.status_code == 404
    
    def test_list_builds(self):
        """Test GET /api/game-builder/builds"""
        response = requests.get(f"{BASE_URL}/api/game-builder/builds")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"Total builds: {len(data)}")
    
    def test_get_build_status(self, project_for_build):
        """Test GET /api/game-builder/builds/{id}"""
        # Start a build first
        payload = {
            "project_id": project_for_build,
            "platform": "Win64",
            "configuration": "Development"
        }
        build_response = requests.post(f"{BASE_URL}/api/game-builder/build", json=payload)
        build_id = build_response.json()["build_id"]
        
        # Get build status
        response = requests.get(f"{BASE_URL}/api/game-builder/builds/{build_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == build_id
        assert "status" in data
        assert "progress" in data
        assert "logs" in data
        
        print(f"Build status: {data['status']}, progress: {data['progress']}%")


class TestGameBuilderConfig:
    """Tests for engine configuration"""
    
    def test_get_config(self):
        """Test GET /api/game-builder/config"""
        response = requests.get(f"{BASE_URL}/api/game-builder/config")
        assert response.status_code == 200
        
        data = response.json()
        # Should return either config or message about auto-detection
        assert "message" in data or "unreal_path" in data or "unity_path" in data
        
        print(f"Config: {data}")
    
    def test_set_engine_paths(self):
        """Test POST /api/game-builder/set-paths"""
        payload = {
            "unreal_path": "/test/path/to/unreal",
            "unity_path": "/test/path/to/unity"
        }
        response = requests.post(f"{BASE_URL}/api/game-builder/set-paths", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert data["message"] == "Engine paths configured"
        
        # Verify config was saved
        config_response = requests.get(f"{BASE_URL}/api/game-builder/config")
        config = config_response.json()
        assert config.get("unreal_path") == "/test/path/to/unreal"
        assert config.get("unity_path") == "/test/path/to/unity"
        
        print("Engine paths configured successfully")


class TestHealthCheck:
    """Basic health check"""
    
    def test_health(self):
        """Test /api/health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
