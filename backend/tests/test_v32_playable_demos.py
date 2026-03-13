"""
AgentForge v3.2 - Playable Demo Tests
Tests for demo generation endpoints and PlayableDemo model
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_PROJECT_ID = "0e16897f-e287-402d-a7bc-aa57ba9c294f"

class TestAPIVersion:
    """Test API version includes playable_demos feature"""
    
    def test_api_version_is_3_2_0(self):
        """API should return version 3.2.0"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "3.2.0", f"Expected version 3.2.0, got {data['version']}"
        print(f"✅ API version is 3.2.0")
    
    def test_api_features_include_playable_demos(self):
        """API features should include playable_demos"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "playable_demos" in data["features"], "playable_demos not in features list"
        print(f"✅ playable_demos feature is listed in API features")


class TestDemoEndpoints:
    """Test demo CRUD and generation endpoints"""
    
    def test_get_demos_returns_list(self):
        """GET /api/demos/{project_id} should return a list (possibly empty)"""
        response = requests.get(f"{BASE_URL}/api/demos/{TEST_PROJECT_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✅ GET /api/demos/{TEST_PROJECT_ID} returns list with {len(data)} demos")
    
    def test_get_latest_demo(self):
        """GET /api/demos/{project_id}/latest should return latest ready demo or null"""
        response = requests.get(f"{BASE_URL}/api/demos/{TEST_PROJECT_ID}/latest")
        assert response.status_code == 200
        data = response.json()
        # Can be null if no demo exists, or a demo object
        if data is not None:
            assert "id" in data, "Demo should have id field"
            assert "status" in data, "Demo should have status field"
            assert "project_id" in data, "Demo should have project_id field"
            assert "build_id" in data, "Demo should have build_id field"
            assert data["status"] == "ready", f"Latest demo should be ready, got {data['status']}"
            print(f"✅ GET /api/demos/{TEST_PROJECT_ID}/latest returns ready demo with id: {data['id']}")
        else:
            print(f"✅ GET /api/demos/{TEST_PROJECT_ID}/latest returns null (no demo yet)")
    
    def test_get_web_demo_html(self):
        """GET /api/demos/{project_id}/web should return HTML or 404"""
        response = requests.get(f"{BASE_URL}/api/demos/{TEST_PROJECT_ID}/web")
        # Can be 200 with HTML or 404 if no demo
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        
        if response.status_code == 200:
            assert "<!DOCTYPE html>" in response.text or "<html" in response.text, "Response should be HTML"
            print(f"✅ GET /api/demos/{TEST_PROJECT_ID}/web returns valid HTML ({len(response.text)} chars)")
        else:
            print(f"✅ GET /api/demos/{TEST_PROJECT_ID}/web returns 404 (no web demo available)")
    
    def test_regenerate_demo_success(self):
        """POST /api/demos/{project_id}/regenerate should start demo regeneration"""
        response = requests.post(f"{BASE_URL}/api/demos/{TEST_PROJECT_ID}/regenerate")
        # Can be 200 if build exists or 404 if no completed build
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] == True, "Regeneration should succeed"
            assert "message" in data, "Response should have message"
            assert "build_id" in data, "Response should have build_id"
            print(f"✅ POST /api/demos/{TEST_PROJECT_ID}/regenerate started: {data['message']}")
        else:
            data = response.json()
            assert "detail" in data, "404 response should have detail"
            print(f"✅ POST /api/demos/{TEST_PROJECT_ID}/regenerate returned 404 (no completed build)")
    
    def test_regenerate_demo_nonexistent_project(self):
        """POST /api/demos/{project_id}/regenerate for non-existent project"""
        fake_project_id = "00000000-0000-0000-0000-000000000000"
        response = requests.post(f"{BASE_URL}/api/demos/{fake_project_id}/regenerate")
        assert response.status_code == 404, f"Expected 404 for non-existent project, got {response.status_code}"
        print(f"✅ POST /api/demos/fake_project/regenerate returns 404 correctly")


class TestPlayableDemoModel:
    """Test PlayableDemo model structure from API responses"""
    
    def test_demo_model_structure(self):
        """Verify PlayableDemo model has all required fields"""
        response = requests.get(f"{BASE_URL}/api/demos/{TEST_PROJECT_ID}/latest")
        assert response.status_code == 200
        
        data = response.json()
        if data is None:
            pytest.skip("No demo available to test model structure")
        
        # Required fields from PlayableDemo model
        required_fields = [
            "id", "project_id", "build_id", "status", "demo_type", "target_engine"
        ]
        for field in required_fields:
            assert field in data, f"Demo missing required field: {field}"
        
        # Optional but expected fields
        expected_fields = [
            "web_demo_html", "systems_included", "demo_features", "controls_guide",
            "web_demo_url", "executable_url", "executable_size_mb", "platform",
            "created_at", "generated_at"
        ]
        for field in expected_fields:
            assert field in data, f"Demo missing expected field: {field}"
        
        print(f"✅ PlayableDemo model has all required and expected fields")
    
    def test_demo_has_systems_included(self):
        """Demo should list systems that were included from the build"""
        response = requests.get(f"{BASE_URL}/api/demos/{TEST_PROJECT_ID}/latest")
        data = response.json()
        
        if data is None:
            pytest.skip("No demo available")
        
        assert "systems_included" in data, "Demo should have systems_included field"
        assert isinstance(data["systems_included"], list), "systems_included should be a list"
        print(f"✅ Demo includes {len(data['systems_included'])} systems: {data['systems_included'][:3]}...")
    
    def test_demo_has_features_list(self):
        """Demo should list demo features"""
        response = requests.get(f"{BASE_URL}/api/demos/{TEST_PROJECT_ID}/latest")
        data = response.json()
        
        if data is None:
            pytest.skip("No demo available")
        
        assert "demo_features" in data, "Demo should have demo_features field"
        assert isinstance(data["demo_features"], list), "demo_features should be a list"
        print(f"✅ Demo features: {data['demo_features']}")
    
    def test_demo_has_controls_guide(self):
        """Demo should have controls guide string"""
        response = requests.get(f"{BASE_URL}/api/demos/{TEST_PROJECT_ID}/latest")
        data = response.json()
        
        if data is None:
            pytest.skip("No demo available")
        
        assert "controls_guide" in data, "Demo should have controls_guide field"
        assert isinstance(data["controls_guide"], str), "controls_guide should be a string"
        assert len(data["controls_guide"]) > 0, "controls_guide should not be empty"
        print(f"✅ Demo has controls guide ({len(data['controls_guide'])} chars)")
    
    def test_demo_has_web_demo_html(self):
        """Demo should have web_demo_html for HTML5/WebGL demo"""
        response = requests.get(f"{BASE_URL}/api/demos/{TEST_PROJECT_ID}/latest")
        data = response.json()
        
        if data is None:
            pytest.skip("No demo available")
        
        assert "web_demo_html" in data, "Demo should have web_demo_html field"
        if data["web_demo_html"]:
            assert "<html" in data["web_demo_html"] or "<!DOCTYPE" in data["web_demo_html"], \
                "web_demo_html should contain valid HTML"
            print(f"✅ Demo has web_demo_html ({len(data['web_demo_html'])} chars)")
        else:
            print(f"✅ Demo web_demo_html is null (not yet generated)")


class TestDemoGenerationFlow:
    """Test the complete demo generation flow"""
    
    def test_demo_linked_to_build(self):
        """Demo should be properly linked to a completed build"""
        # Get latest demo
        demo_response = requests.get(f"{BASE_URL}/api/demos/{TEST_PROJECT_ID}/latest")
        demo = demo_response.json()
        
        if demo is None:
            pytest.skip("No demo available to test build linkage")
        
        build_id = demo.get("build_id")
        assert build_id is not None, "Demo should have build_id"
        
        print(f"✅ Demo is linked to build: {build_id}")
    
    def test_web_demo_endpoint_returns_html_content_type(self):
        """Web demo endpoint should return proper HTML content"""
        response = requests.get(f"{BASE_URL}/api/demos/{TEST_PROJECT_ID}/web")
        
        if response.status_code == 404:
            pytest.skip("No web demo available")
        
        assert response.status_code == 200
        # Check content type is HTML
        content_type = response.headers.get("content-type", "")
        assert "text/html" in content_type, f"Expected text/html, got {content_type}"
        print(f"✅ Web demo endpoint returns correct content-type: {content_type}")


class TestHealthCheck:
    """Basic health check to ensure API is running"""
    
    def test_api_health(self):
        """API health check should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ API is healthy: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
