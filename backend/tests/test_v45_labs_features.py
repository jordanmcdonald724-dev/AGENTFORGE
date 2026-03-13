"""
AgentForge v4.5 Labs Features Testing
=====================================
Tests for new "shouldn't exist" features:
- World Model (Systems Graph)
- Software DNA (Genes)
- God Mode (one-prompt SaaS builder)
- Autonomous Discovery (background experiments)
- Module Marketplace
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndSetup:
    """Basic health and setup verification"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ API health check passed: {data}")

class TestWorldModel:
    """World Model / Systems Graph API tests"""
    
    def test_get_categories(self):
        """Test GET /api/world-model/categories returns system categories"""
        response = requests.get(f"{BASE_URL}/api/world-model/categories")
        assert response.status_code == 200
        data = response.json()
        # Verify main categories exist
        assert "frontend" in data
        assert "backend" in data
        assert "game_engines" in data
        assert "infrastructure" in data
        assert "ai_ml" in data
        # Verify subcategories
        assert "react" in data["frontend"]
        assert "unreal" in data["game_engines"]
        print(f"✅ World Model categories: {list(data.keys())}")
    
    def test_get_insights(self):
        """Test GET /api/world-model/insights returns analytics"""
        response = requests.get(f"{BASE_URL}/api/world-model/insights")
        assert response.status_code == 200
        data = response.json()
        # Check response structure
        assert "total_projects_analyzed" in data
        assert "top_technologies" in data
        assert "top_patterns" in data
        assert "recommendations" in data
        print(f"✅ World Model insights: projects={data['total_projects_analyzed']}, recommendations={len(data['recommendations'])}")
    
    def test_get_graph(self):
        """Test GET /api/world-model/graph returns knowledge graph"""
        response = requests.get(f"{BASE_URL}/api/world-model/graph")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert "stats" in data
        print(f"✅ World Model graph: {data['stats']['total_nodes']} nodes, {data['stats']['total_edges']} edges")


class TestSoftwareDNA:
    """Software DNA / Genes System API tests"""
    
    def test_get_categories(self):
        """Test GET /api/dna/categories returns gene categories"""
        response = requests.get(f"{BASE_URL}/api/dna/categories")
        assert response.status_code == 200
        data = response.json()
        # Verify main gene categories
        assert "auth" in data
        assert "ui" in data
        assert "data" in data
        assert "game" in data
        assert "infra" in data
        assert "ai" in data
        # Verify category structure
        assert "name" in data["auth"]
        assert "genes" in data["auth"]
        print(f"✅ DNA categories: {list(data.keys())}")
    
    def test_get_library(self):
        """Test GET /api/dna/library returns full gene library"""
        response = requests.get(f"{BASE_URL}/api/dna/library")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "genes" in data
        assert "total_genes" in data
        assert "stats" in data
        print(f"✅ DNA library: {data['total_genes']} total genes")


class TestGodMode:
    """God Mode - One-prompt SaaS Builder API tests"""
    
    def test_get_templates(self):
        """Test GET /api/god-mode/templates returns SaaS templates"""
        response = requests.get(f"{BASE_URL}/api/god-mode/templates")
        assert response.status_code == 200
        data = response.json()
        # Verify templates exist
        assert "analytics" in data
        assert "marketplace" in data
        assert "saas_starter" in data
        assert "ai_tool" in data
        assert "community" in data
        # Verify template structure
        assert "name" in data["analytics"]
        assert "components" in data["analytics"]
        assert "files_estimate" in data["analytics"]
        print(f"✅ God Mode templates: {list(data.keys())}")
    
    def test_create_saas(self):
        """Test POST /api/god-mode/create creates SaaS from prompt"""
        # API uses query params, not JSON body
        response = requests.post(
            f"{BASE_URL}/api/god-mode/create",
            params={"prompt": "Create a simple task management app"}
        )
        assert response.status_code == 200
        data = response.json()
        # Verify response structure
        assert "session_id" in data
        assert "project_id" in data
        assert "status" in data
        assert "plan" in data
        assert data["status"] == "planned"
        print(f"✅ God Mode create: session={data['session_id']}, status={data['status']}")
        return data


class TestDiscovery:
    """Autonomous Discovery / Background Experiments API tests"""
    
    def test_get_types(self):
        """Test GET /api/discovery/types returns experiment types"""
        response = requests.get(f"{BASE_URL}/api/discovery/types")
        assert response.status_code == 200
        data = response.json()
        # Verify experiment types
        assert "architecture" in data
        assert "ui_component" in data
        assert "algorithm" in data
        assert "integration" in data
        assert "game_system" in data
        # Verify type structure
        assert "name" in data["architecture"]
        assert "description" in data["architecture"]
        assert "examples" in data["architecture"]
        print(f"✅ Discovery types: {list(data.keys())}")
    
    def test_start_experiment(self):
        """Test POST /api/discovery/start starts an experiment"""
        # API uses query params, not JSON body
        response = requests.post(
            f"{BASE_URL}/api/discovery/start",
            params={
                "experiment_type": "architecture",
                "hypothesis": "Test microservices pattern for testing"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Verify response structure
        assert "id" in data
        assert "type" in data
        assert "hypothesis" in data
        assert "status" in data
        assert "iterations" in data
        print(f"✅ Discovery start: id={data['id']}, status={data['status']}")
        return data
    
    def test_list_experiments(self):
        """Test GET /api/discovery/experiments lists all experiments"""
        response = requests.get(f"{BASE_URL}/api/discovery/experiments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Discovery experiments: {len(data)} experiments found")


class TestMarketplace:
    """Module Marketplace API tests"""
    
    def test_get_categories(self):
        """Test GET /api/marketplace/categories returns module categories"""
        response = requests.get(f"{BASE_URL}/api/marketplace/categories")
        assert response.status_code == 200
        data = response.json()
        # Verify marketplace categories
        assert "frontend" in data
        assert "backend" in data
        assert "game" in data
        assert "ai" in data
        assert "infrastructure" in data
        # Verify category structure
        assert "name" in data["frontend"]
        assert "subcategories" in data["frontend"]
        print(f"✅ Marketplace categories: {list(data.keys())}")
    
    def test_get_modules(self):
        """Test GET /api/marketplace/modules returns module list"""
        response = requests.get(f"{BASE_URL}/api/marketplace/modules")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Marketplace modules: {len(data)} modules found")
    
    def test_get_modules_with_params(self):
        """Test GET /api/marketplace/modules with query params"""
        response = requests.get(f"{BASE_URL}/api/marketplace/modules?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
        print(f"✅ Marketplace modules (limited): {len(data)} modules returned")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
