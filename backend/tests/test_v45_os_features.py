"""
AgentForge v4.5 - OS Features Backend Tests
=============================================
Tests for OS-level features: GitHub Universe, Cloud Deploy, Dev Env, 
Asset Factory, SaaS Factory, Game Studio, Game Engine
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndCore:
    """Core endpoint tests - verify refactored server is working"""
    
    def test_health_endpoint(self):
        """GET /api/health - Basic health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ Health check passed")
    
    def test_projects_list(self):
        """GET /api/projects - List projects"""
        response = requests.get(f"{BASE_URL}/api/projects")
        assert response.status_code == 200, f"Projects list failed: {response.status_code}"
        print(f"✅ Projects list returned {len(response.json())} projects")
    
    def test_agents_list(self):
        """GET /api/agents - List agents"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) >= 6, "Should have at least 6 agents"
        print(f"✅ Agents list returned {len(agents)} agents")


class TestGitHubUniverse:
    """GitHub Universe Control - Phase 1 OS Feature"""
    
    def test_github_status(self):
        """GET /api/github-universe/status - Check GitHub integration status"""
        response = requests.get(f"{BASE_URL}/api/github-universe/status")
        assert response.status_code == 200, f"GitHub status failed: {response.status_code}"
        data = response.json()
        assert "connected" in data
        assert "features" in data
        assert len(data["features"]) >= 4
        print(f"✅ GitHub Universe status: connected={data.get('connected')}, features={len(data['features'])}")
    
    def test_github_scans_list(self):
        """GET /api/github-universe/scans - List past scans"""
        response = requests.get(f"{BASE_URL}/api/github-universe/scans?limit=5")
        assert response.status_code == 200
        print(f"✅ GitHub scans list returned {len(response.json())} scans")
    
    def test_github_learn_patterns(self):
        """GET /api/github-universe/learn-patterns - Learn from repos"""
        response = requests.get(f"{BASE_URL}/api/github-universe/learn-patterns?language=python&count=3")
        assert response.status_code == 200
        data = response.json()
        assert "language" in data
        assert data["language"] == "python"
        print(f"✅ Learn patterns: analyzed {data.get('repos_analyzed', 0)} repos")


class TestCloudDeploy:
    """Cloud Auto-Deployment - Phase 2 OS Feature"""
    
    def test_cloud_deploy_status(self):
        """GET /api/cloud-deploy/status - Check deployment integration status"""
        response = requests.get(f"{BASE_URL}/api/cloud-deploy/status")
        assert response.status_code == 200, f"Cloud deploy status failed: {response.status_code}"
        data = response.json()
        assert "vercel" in data
        assert "cloudflare" in data
        assert "features" in data["vercel"]
        print(f"✅ Cloud deploy status: vercel={data['vercel']['connected']}, cloudflare={data['cloudflare']['connected']}")
    
    def test_cloud_deployments_list(self):
        """GET /api/cloud-deploy/deployments - List deployments"""
        response = requests.get(f"{BASE_URL}/api/cloud-deploy/deployments?limit=5")
        assert response.status_code == 200
        print(f"✅ Cloud deployments list returned {len(response.json())} deployments")


class TestDevEnvironment:
    """Dev Environment Builder - Phase 3 OS Feature"""
    
    def test_dev_env_templates(self):
        """GET /api/dev-env/templates - Get available templates"""
        response = requests.get(f"{BASE_URL}/api/dev-env/templates")
        assert response.status_code == 200, f"Dev env templates failed: {response.status_code}"
        data = response.json()
        # Should have node, python, fastapi, react, go, rust, unreal, unity templates
        assert len(data) >= 6, f"Expected at least 6 templates, got {len(data)}"
        assert "node" in data
        assert "python" in data
        assert "fastapi" in data
        print(f"✅ Dev environment templates: {list(data.keys())}")
    
    def test_dev_env_template_details(self):
        """GET /api/dev-env/templates/{template_id} - Get specific template"""
        response = requests.get(f"{BASE_URL}/api/dev-env/templates/node")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "base_image" in data
        assert "files" in data
        print(f"✅ Node template: {data['name']}, image={data['base_image']}")
    
    def test_dev_env_environments_list(self):
        """GET /api/dev-env/environments - List environments"""
        response = requests.get(f"{BASE_URL}/api/dev-env/environments")
        assert response.status_code == 200
        print(f"✅ Dev environments list returned {len(response.json())} environments")


class TestAssetFactory:
    """AI Asset Factory - Phase 4 OS Feature"""
    
    def test_asset_pipelines(self):
        """GET /api/asset-factory/pipelines - Get asset generation pipelines"""
        response = requests.get(f"{BASE_URL}/api/asset-factory/pipelines")
        assert response.status_code == 200, f"Asset pipelines failed: {response.status_code}"
        data = response.json()
        # Should have ui_kit, texture_pack, icon_set, character_art, environment_art, audio_sfx, voice_acting
        assert len(data) >= 5, f"Expected at least 5 pipelines, got {len(data)}"
        assert "ui_kit" in data
        assert "texture_pack" in data
        print(f"✅ Asset factory pipelines: {list(data.keys())}")
    
    def test_asset_generations_list(self):
        """GET /api/asset-factory/generations - List asset generations"""
        response = requests.get(f"{BASE_URL}/api/asset-factory/generations?limit=5")
        assert response.status_code == 200
        print(f"✅ Asset generations list returned {len(response.json())} generations")
    
    def test_asset_packs_list(self):
        """GET /api/asset-factory/packs - List asset packs"""
        response = requests.get(f"{BASE_URL}/api/asset-factory/packs")
        assert response.status_code == 200
        print(f"✅ Asset packs list returned {len(response.json())} packs")


class TestSaaSFactory:
    """Autonomous SaaS Factory - Phase 5 OS Feature"""
    
    def test_saas_templates(self):
        """GET /api/saas-factory/templates - Get SaaS templates"""
        response = requests.get(f"{BASE_URL}/api/saas-factory/templates")
        assert response.status_code == 200, f"SaaS templates failed: {response.status_code}"
        data = response.json()
        # Should have analytics, marketplace, subscription_box, saas_boilerplate, ai_tool, community, course_platform, appointment_booking
        assert len(data) >= 6, f"Expected at least 6 templates, got {len(data)}"
        assert "analytics" in data
        assert "marketplace" in data
        print(f"✅ SaaS factory templates: {list(data.keys())}")
    
    def test_saas_integrations(self):
        """GET /api/saas-factory/integrations - Get integration status"""
        response = requests.get(f"{BASE_URL}/api/saas-factory/integrations")
        assert response.status_code == 200
        data = response.json()
        assert "stripe" in data
        assert "supabase" in data
        print(f"✅ SaaS integrations: stripe={data['stripe']['connected']}, supabase={data['supabase']['connected']}")
    
    def test_saas_builds_list(self):
        """GET /api/saas-factory/builds - List SaaS builds"""
        response = requests.get(f"{BASE_URL}/api/saas-factory/builds?limit=5")
        assert response.status_code == 200
        print(f"✅ SaaS builds list returned {len(response.json())} builds")


class TestGameStudio:
    """Autonomous Game Studio - Phase 6 OS Feature"""
    
    def test_game_genres(self):
        """GET /api/game-studio/genres - Get available game genres"""
        response = requests.get(f"{BASE_URL}/api/game-studio/genres")
        assert response.status_code == 200, f"Game genres failed: {response.status_code}"
        data = response.json()
        # Should have fps, rpg, platformer, racing, puzzle, survival, strategy, horror
        assert len(data) >= 6, f"Expected at least 6 genres, got {len(data)}"
        assert "fps" in data
        assert "rpg" in data
        print(f"✅ Game studio genres: {list(data.keys())}")
    
    def test_game_builds_list(self):
        """GET /api/game-studio/builds - List game builds"""
        response = requests.get(f"{BASE_URL}/api/game-studio/builds?limit=5")
        assert response.status_code == 200
        print(f"✅ Game builds list returned {len(response.json())} builds")


class TestGameEngine:
    """Game Engine Integration - Unreal, Unity, Godot"""
    
    def test_unreal_templates(self):
        """GET /api/game-engine/unreal/templates - Get Unreal templates"""
        response = requests.get(f"{BASE_URL}/api/game-engine/unreal/templates")
        assert response.status_code == 200, f"Unreal templates failed: {response.status_code}"
        data = response.json()
        # Should have fps_controller, third_person, vehicle, inventory, dialogue, ai_npc, quest, combat
        assert len(data) >= 6, f"Expected at least 6 templates, got {len(data)}"
        assert "fps_controller" in data
        print(f"✅ Unreal templates: {list(data.keys())}")
    
    def test_unity_templates(self):
        """GET /api/game-engine/unity/templates - Get Unity templates"""
        response = requests.get(f"{BASE_URL}/api/game-engine/unity/templates")
        assert response.status_code == 200, f"Unity templates failed: {response.status_code}"
        data = response.json()
        assert len(data) >= 4, f"Expected at least 4 templates, got {len(data)}"
        assert "fps_controller" in data
        print(f"✅ Unity templates: {list(data.keys())}")
    
    def test_godot_templates(self):
        """GET /api/game-engine/godot/templates - Get Godot templates"""
        response = requests.get(f"{BASE_URL}/api/game-engine/godot/templates")
        assert response.status_code == 200, f"Godot templates failed: {response.status_code}"
        data = response.json()
        assert len(data) >= 3, f"Expected at least 3 templates, got {len(data)}"
        print(f"✅ Godot templates: {list(data.keys())}")
    
    def test_engine_generations_list(self):
        """GET /api/game-engine/generations - List engine generations"""
        response = requests.get(f"{BASE_URL}/api/game-engine/generations?limit=5")
        assert response.status_code == 200
        print(f"✅ Engine generations list returned {len(response.json())} generations")


class TestLabsFeatures:
    """Labs Features - Verify still working after refactoring"""
    
    def test_world_model_categories(self):
        """GET /api/world-model/categories - World Model categories"""
        response = requests.get(f"{BASE_URL}/api/world-model/categories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4
        print(f"✅ World Model categories: {len(data)} categories")
    
    def test_god_mode_templates(self):
        """GET /api/god-mode/templates - God Mode templates"""
        response = requests.get(f"{BASE_URL}/api/god-mode/templates")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4
        print(f"✅ God Mode templates: {len(data)} templates")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
