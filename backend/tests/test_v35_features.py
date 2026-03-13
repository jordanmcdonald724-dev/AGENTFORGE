"""
AgentForge v3.5 Backend Tests - Build Sandbox and Asset Pipeline
Tests the final missing features:
- Build Sandbox: isolated code execution environment
- Asset Pipeline: unified asset management for all types
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
PROJECT_ID = "cfdcd129-6ca5-4616-997b-c615daaa64de"


class TestSandboxEnvironments:
    """Build Sandbox - Environment and Session Tests"""
    
    def test_get_sandbox_environments(self):
        """GET /api/sandbox/environments should return 5 environments"""
        response = requests.get(f"{BASE_URL}/api/sandbox/environments")
        assert response.status_code == 200
        
        envs = response.json()
        assert isinstance(envs, list)
        assert len(envs) == 5
        
        # Verify all 5 expected environments
        env_ids = [e["id"] for e in envs]
        assert "web" in env_ids
        assert "node" in env_ids
        assert "python" in env_ids
        assert "unity" in env_ids
        assert "unreal" in env_ids
        
        # Each env should have id, name, icon, description
        for env in envs:
            assert "id" in env
            assert "name" in env
            assert "icon" in env
            assert "description" in env
        print(f"✅ Sandbox environments: {env_ids}")
    
    def test_create_sandbox_session(self):
        """POST /api/sandbox/{project_id}/create should create a sandbox session"""
        response = requests.post(
            f"{BASE_URL}/api/sandbox/{PROJECT_ID}/create",
            params={"environment": "web"}
        )
        assert response.status_code == 200
        
        session = response.json()
        assert session["project_id"] == PROJECT_ID
        assert session["environment"] == "web"
        assert session["status"] == "idle"
        print(f"✅ Created sandbox session: {session['id']}")
    
    def test_get_sandbox_session(self):
        """GET /api/sandbox/{project_id} should return current session"""
        # First create a session
        requests.post(
            f"{BASE_URL}/api/sandbox/{PROJECT_ID}/create",
            params={"environment": "python"}
        )
        
        response = requests.get(f"{BASE_URL}/api/sandbox/{PROJECT_ID}")
        assert response.status_code == 200
        
        session = response.json()
        if session:  # May be null if no session
            assert session["project_id"] == PROJECT_ID
            print(f"✅ Got sandbox session: {session['environment']}")
    
    def test_run_sandbox(self):
        """POST /api/sandbox/{project_id}/run should execute code and return console output"""
        # First create a session
        requests.post(
            f"{BASE_URL}/api/sandbox/{PROJECT_ID}/create",
            params={"environment": "web"}
        )
        
        response = requests.post(f"{BASE_URL}/api/sandbox/{PROJECT_ID}/run")
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "running"
        assert "console_output" in result
        assert isinstance(result["console_output"], list)
        # Console output may be empty if project has no files
        assert "variables" in result
        assert "execution_time_ms" in result
        
        # Check console output has expected format if any logs exist
        for log in result["console_output"]:
            assert "type" in log
            assert "message" in log
            assert "timestamp" in log
        
        print(f"✅ Sandbox ran with {len(result['console_output'])} console logs")
        print(f"   Variables: {result['variables']}")
        print(f"   Entry file: {result.get('entry_file', 'None (no files in project)')}")
    
    def test_stop_sandbox(self):
        """POST /api/sandbox/{project_id}/stop should stop execution"""
        # Create and run first
        requests.post(f"{BASE_URL}/api/sandbox/{PROJECT_ID}/create", params={"environment": "web"})
        requests.post(f"{BASE_URL}/api/sandbox/{PROJECT_ID}/run")
        
        response = requests.post(f"{BASE_URL}/api/sandbox/{PROJECT_ID}/stop")
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "stopped"
        print("✅ Sandbox stopped")
    
    def test_reset_sandbox(self):
        """POST /api/sandbox/{project_id}/reset should reset to initial state"""
        # Create and run first
        requests.post(f"{BASE_URL}/api/sandbox/{PROJECT_ID}/create", params={"environment": "web"})
        requests.post(f"{BASE_URL}/api/sandbox/{PROJECT_ID}/run")
        
        response = requests.post(f"{BASE_URL}/api/sandbox/{PROJECT_ID}/reset")
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "idle"
        print("✅ Sandbox reset to idle")
    
    def test_console_input(self):
        """POST /api/sandbox/{project_id}/console should accept console commands"""
        # Create and run first
        requests.post(f"{BASE_URL}/api/sandbox/{PROJECT_ID}/create", params={"environment": "python"})
        requests.post(f"{BASE_URL}/api/sandbox/{PROJECT_ID}/run")
        
        response = requests.post(
            f"{BASE_URL}/api/sandbox/{PROJECT_ID}/console",
            params={"command": "print('hello')"}
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "output" in result
        assert "result" in result
        print(f"✅ Console command executed: {result['result']['message']}")


class TestAssetPipelineTypes:
    """Asset Pipeline - Types and Categories Tests"""
    
    def test_get_asset_types(self):
        """GET /api/assets/types should return 10 asset types"""
        response = requests.get(f"{BASE_URL}/api/assets/types")
        assert response.status_code == 200
        
        types = response.json()
        assert isinstance(types, dict)
        assert len(types) == 10
        
        # Verify all 10 expected types
        expected_types = ["image", "audio", "texture", "sprite", "model_3d", 
                        "material", "animation", "font", "video", "script"]
        for t in expected_types:
            assert t in types, f"Missing asset type: {t}"
            assert "formats" in types[t]
            assert "icon" in types[t]
            assert "color" in types[t]
        
        print(f"✅ Asset types: {list(types.keys())}")
    
    def test_get_asset_categories(self):
        """GET /api/assets/categories should return 7 categories"""
        response = requests.get(f"{BASE_URL}/api/assets/categories")
        assert response.status_code == 200
        
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) == 7
        
        # Verify expected categories
        cat_ids = [c["id"] for c in categories]
        expected = ["ui", "character", "environment", "vfx", "audio", "animation", "misc"]
        for c in expected:
            assert c in cat_ids, f"Missing category: {c}"
        
        # Each category should have id, name, description
        for cat in categories:
            assert "id" in cat
            assert "name" in cat
            assert "description" in cat
        
        print(f"✅ Asset categories: {cat_ids}")


class TestAssetPipelineCRUD:
    """Asset Pipeline - CRUD Operations"""
    
    def test_get_project_assets(self):
        """GET /api/assets/{project_id} should return assets list"""
        response = requests.get(f"{BASE_URL}/api/assets/{PROJECT_ID}")
        assert response.status_code == 200
        
        assets = response.json()
        assert isinstance(assets, list)
        print(f"✅ Got {len(assets)} assets for project")
    
    def test_get_assets_with_filter(self):
        """GET /api/assets/{project_id} with type filter should work"""
        response = requests.get(
            f"{BASE_URL}/api/assets/{PROJECT_ID}",
            params={"asset_type": "image"}
        )
        assert response.status_code == 200
        
        assets = response.json()
        assert isinstance(assets, list)
        # All returned should be images
        for asset in assets:
            assert asset["asset_type"] == "image"
        print(f"✅ Filtered assets by type: {len(assets)} images")
    
    def test_get_asset_summary(self):
        """GET /api/assets/{project_id}/summary should return counts"""
        response = requests.get(f"{BASE_URL}/api/assets/{PROJECT_ID}/summary")
        assert response.status_code == 200
        
        summary = response.json()
        assert "total_assets" in summary
        assert "total_size_mb" in summary
        assert "by_type" in summary
        assert "by_category" in summary
        assert isinstance(summary["by_type"], dict)
        assert isinstance(summary["by_category"], dict)
        
        print(f"✅ Asset summary: {summary['total_assets']} assets, {summary['total_size_mb']}MB")
    
    def test_import_asset(self):
        """POST /api/assets/import should create a new asset"""
        response = requests.post(
            f"{BASE_URL}/api/assets/import",
            json={
                "project_id": PROJECT_ID,
                "name": "TEST_hero_sprite.png",
                "asset_type": "sprite",
                "category": "character",
                "url": "https://example.com/hero.png",
                "tags": ["hero", "test"]
            }
        )
        assert response.status_code == 200
        
        asset = response.json()
        assert asset["name"] == "TEST_hero_sprite.png"
        assert asset["asset_type"] == "sprite"
        assert asset["category"] == "character"
        assert "id" in asset
        
        print(f"✅ Imported asset: {asset['id']}")
        return asset["id"]
    
    def test_sync_from_files(self):
        """POST /api/assets/{project_id}/sync-from-files should sync assets"""
        response = requests.post(f"{BASE_URL}/api/assets/{PROJECT_ID}/sync-from-files")
        assert response.status_code == 200
        
        result = response.json()
        assert "synced_assets" in result
        print(f"✅ Synced {result['synced_assets']} assets from files")
    
    def test_delete_asset(self):
        """DELETE /api/assets/{asset_id} should delete asset"""
        # First import an asset to delete
        import_res = requests.post(
            f"{BASE_URL}/api/assets/import",
            json={
                "project_id": PROJECT_ID,
                "name": "TEST_to_delete.png",
                "asset_type": "image",
                "category": "misc"
            }
        )
        asset_id = import_res.json()["id"]
        
        # Now delete it
        response = requests.delete(f"{BASE_URL}/api/assets/{asset_id}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] == True
        print(f"✅ Deleted asset: {asset_id}")


class TestAssetDependencies:
    """Asset Pipeline - Dependency Management"""
    
    def test_add_dependency(self):
        """POST /api/assets/{asset_id}/add-dependency should link assets"""
        # Create two assets
        res1 = requests.post(
            f"{BASE_URL}/api/assets/import",
            json={
                "project_id": PROJECT_ID,
                "name": "TEST_material.mat",
                "asset_type": "material",
                "category": "environment"
            }
        )
        asset1_id = res1.json()["id"]
        
        res2 = requests.post(
            f"{BASE_URL}/api/assets/import",
            json={
                "project_id": PROJECT_ID,
                "name": "TEST_texture.png",
                "asset_type": "texture",
                "category": "environment"
            }
        )
        asset2_id = res2.json()["id"]
        
        # Add dependency
        response = requests.post(
            f"{BASE_URL}/api/assets/{asset1_id}/add-dependency",
            params={"dependency_id": asset2_id}
        )
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] == True
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/assets/{asset1_id}")
        requests.delete(f"{BASE_URL}/api/assets/{asset2_id}")
        
        print("✅ Added asset dependency")
    
    def test_dependency_graph(self):
        """GET /api/assets/{project_id}/dependency-graph should return graph"""
        response = requests.get(f"{BASE_URL}/api/assets/{PROJECT_ID}/dependency-graph")
        assert response.status_code == 200
        
        graph = response.json()
        assert "nodes" in graph
        assert "edges" in graph
        assert isinstance(graph["nodes"], list)
        assert isinstance(graph["edges"], list)
        
        print(f"✅ Dependency graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_assets(self):
        """Remove TEST_ prefixed assets"""
        assets = requests.get(f"{BASE_URL}/api/assets/{PROJECT_ID}").json()
        deleted = 0
        for asset in assets:
            if asset["name"].startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/assets/{asset['id']}")
                deleted += 1
        print(f"✅ Cleaned up {deleted} test assets")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
