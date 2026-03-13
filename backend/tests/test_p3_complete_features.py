"""
P3 Complete Features Tests - Iteration 26
Testing Unreal Engine, Research Mode, Hardware, Auto-Deploy, AI Review APIs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """Test API health"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ Health endpoint working")


class TestUnrealEngineAPIs:
    """Unreal Engine Integration Tests - 5 Game Templates"""
    
    def test_get_templates(self):
        """Test GET /api/unreal/templates - should return 5 game templates"""
        response = requests.get(f"{BASE_URL}/api/unreal/templates")
        assert response.status_code == 200
        templates = response.json()
        
        # Should have 5 templates as per PRD
        assert len(templates) == 5, f"Expected 5 templates, got {len(templates)}"
        
        # Check expected templates exist
        expected = ["fps_shooter", "platformer_3d", "rpg_adventure", "racing", "puzzle"]
        for key in expected:
            assert key in templates, f"Missing template: {key}"
            
        print(f"✅ Unreal Engine: {len(templates)} game templates available")
        
    def test_get_blueprint_types(self):
        """Test GET /api/unreal/blueprint-types"""
        response = requests.get(f"{BASE_URL}/api/unreal/blueprint-types")
        assert response.status_code == 200
        types = response.json()
        
        # Check expected blueprint types
        expected = ["character", "weapon", "vehicle", "ui", "game_mode", "level"]
        for key in expected:
            assert key in types, f"Missing blueprint type: {key}"
            
        print(f"✅ Unreal Engine: {len(types)} blueprint types available")
        
    def test_list_projects(self):
        """Test GET /api/unreal/projects"""
        response = requests.get(f"{BASE_URL}/api/unreal/projects")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✅ Unreal Engine: Projects list endpoint working")
        
    def test_create_project(self):
        """Test POST /api/unreal/projects/create"""
        payload = {
            "name": "TEST_Game_Project",
            "description": "Test game for automated testing",
            "genre": "platformer",
            "art_style": "stylized",
            "platforms": ["windows"]
        }
        response = requests.post(f"{BASE_URL}/api/unreal/projects/create", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data
        assert data.get("status") == "initializing"
        print(f"✅ Unreal Engine: Created project {data.get('project_id')}")


class TestResearchModeAPIs:
    """Research Mode Tests - arXiv Integration"""
    
    def test_get_categories(self):
        """Test GET /api/research/categories - arXiv categories"""
        response = requests.get(f"{BASE_URL}/api/research/categories")
        assert response.status_code == 200
        categories = response.json()
        
        # Check expected arXiv categories
        expected = ["cs.AI", "cs.LG", "cs.SE", "cs.CV", "cs.CL"]
        for cat in expected:
            assert cat in categories, f"Missing arXiv category: {cat}"
            
        print(f"✅ Research Mode: {len(categories)} arXiv categories available")
        
    def test_list_searches(self):
        """Test GET /api/research/searches"""
        response = requests.get(f"{BASE_URL}/api/research/searches")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✅ Research Mode: Searches list endpoint working")
        
    def test_list_prototypes(self):
        """Test GET /api/research/prototypes"""
        response = requests.get(f"{BASE_URL}/api/research/prototypes")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✅ Research Mode: Prototypes list endpoint working")
        
    def test_search_arxiv(self):
        """Test POST /api/research/search - arXiv search functionality"""
        payload = {
            "topic": "transformer attention",
            "categories": ["cs.AI", "cs.LG"],
            "max_papers": 5,
            "auto_prototype": False
        }
        response = requests.post(f"{BASE_URL}/api/research/search", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "search_id" in data
        assert data.get("status") == "searching"
        print(f"✅ Research Mode: Started search {data.get('search_id')}")


class TestHardwareAPIs:
    """Hardware Integration Tests - Arduino/Raspberry Pi"""
    
    def test_get_platforms(self):
        """Test GET /api/hardware/platforms - should return 4+ platforms"""
        response = requests.get(f"{BASE_URL}/api/hardware/platforms")
        assert response.status_code == 200
        platforms = response.json()
        
        # Should have at least 4 platforms as per PRD
        assert len(platforms) >= 4, f"Expected 4+ platforms, got {len(platforms)}"
        
        # Check expected platforms exist
        expected = ["arduino_uno", "arduino_mega", "esp32", "raspberry_pi_4"]
        for key in expected:
            assert key in platforms, f"Missing platform: {key}"
            
        print(f"✅ Hardware: {len(platforms)} platforms available")
        
    def test_get_sensors(self):
        """Test GET /api/hardware/sensors"""
        response = requests.get(f"{BASE_URL}/api/hardware/sensors")
        assert response.status_code == 200
        sensors = response.json()
        
        # Check some expected sensors
        expected = ["dht11", "dht22", "bmp280", "mpu6050"]
        for key in expected:
            assert key in sensors, f"Missing sensor: {key}"
            
        print(f"✅ Hardware: {len(sensors)} sensors available")
        
    def test_get_actuators(self):
        """Test GET /api/hardware/actuators"""
        response = requests.get(f"{BASE_URL}/api/hardware/actuators")
        assert response.status_code == 200
        actuators = response.json()
        assert len(actuators) > 0
        print(f"✅ Hardware: {len(actuators)} actuators available")
        
    def test_list_projects(self):
        """Test GET /api/hardware/projects"""
        response = requests.get(f"{BASE_URL}/api/hardware/projects")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✅ Hardware: Projects list endpoint working")
        
    def test_create_project(self):
        """Test POST /api/hardware/projects/create"""
        payload = {
            "name": "TEST_Arduino_Project",
            "description": "Test hardware project",
            "platform": "arduino_uno",
            "project_type": "sensor",
            "sensors": ["dht11"],
            "actuators": ["led"]
        }
        response = requests.post(f"{BASE_URL}/api/hardware/projects/create", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data
        print(f"✅ Hardware: Created project {data.get('project_id')}")


class TestAutoDeployAPIs:
    """Auto-Deploy Tests - Vercel/Railway"""
    
    def test_get_platforms(self):
        """Test GET /api/auto-deploy/platforms - deploy platforms"""
        response = requests.get(f"{BASE_URL}/api/auto-deploy/platforms")
        assert response.status_code == 200
        platforms = response.json()
        
        # Check expected platforms exist
        expected = ["vercel", "railway", "netlify"]
        for key in expected:
            assert key in platforms, f"Missing deploy platform: {key}"
            
        print(f"✅ Auto-Deploy: {len(platforms)} platforms available")
        
    def test_list_deployments(self):
        """Test GET /api/auto-deploy/deployments"""
        response = requests.get(f"{BASE_URL}/api/auto-deploy/deployments")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✅ Auto-Deploy: Deployments list endpoint working")
        
    def test_get_config(self):
        """Test GET /api/auto-deploy/config/vercel"""
        response = requests.get(f"{BASE_URL}/api/auto-deploy/config/vercel")
        assert response.status_code == 200
        config = response.json()
        assert "platform" in config
        print("✅ Auto-Deploy: Config endpoint working")


class TestAIReviewAPIs:
    """AI Code Review Tests - Pattern-based Analysis"""
    
    def test_get_patterns(self):
        """Test GET /api/ai-review/patterns - code review patterns"""
        response = requests.get(f"{BASE_URL}/api/ai-review/patterns")
        assert response.status_code == 200
        patterns = response.json()
        
        # Check patterns for different languages
        expected_langs = ["react", "python", "javascript", "general"]
        for lang in expected_langs:
            assert lang in patterns, f"Missing patterns for: {lang}"
            
        print(f"✅ AI Review: {len(patterns)} language patterns available")
        
    def test_review_single_file(self):
        """Test POST /api/ai-review/review-file - quick file analysis"""
        payload = {
            "content": """
import React from 'react';

const Component = () => {
    const items = [1, 2, 3];
    console.log('debug');
    
    return items.map(item => <div>{item}</div>);
};
""",
            "filename": "Test.jsx",
            "language": "react"
        }
        response = requests.post(f"{BASE_URL}/api/ai-review/review-file", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "issues" in data
        assert "summary" in data
        print(f"✅ AI Review: File review found {len(data.get('issues', []))} issues")


class TestMissionControlPanels:
    """Test all 11 panels are accessible - via existing routes"""
    
    def test_agents_endpoint(self):
        """Test /api/agents - War Room agents"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) >= 6, f"Expected 6+ agents, got {len(agents)}"
        print(f"✅ War Room: {len(agents)} agents available")


# Run all tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
