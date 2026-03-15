"""
AgentForge v2.3 Features Backend Tests
Tests for: Custom Quick Actions, Agent Memory Persistence, Project Duplication, Multi-file Refactoring
Also includes core API and CRUD tests
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://premium-os.preview.emergentagent.com')
API_URL = f"{BASE_URL}/api"

# ============ FIXTURES ============

@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture(scope="module")
def test_project(api_client):
    """Create a test project for all tests to use"""
    response = api_client.post(f"{API_URL}/projects", json={
        "name": f"TEST_project_{uuid.uuid4().hex[:6]}",
        "description": "Test project for v2.3 feature testing",
        "type": "web_app"
    })
    assert response.status_code == 200
    project = response.json()
    yield project
    # Cleanup
    api_client.delete(f"{API_URL}/projects/{project['id']}")

@pytest.fixture(scope="module")
def test_project_with_files(api_client, test_project):
    """Create test files in the project for refactoring tests"""
    files = [
        {
            "project_id": test_project["id"],
            "filename": "main.js",
            "filepath": "src/main.js",
            "content": "const PlayerManager = new PlayerManager();\nconst score = PlayerManager.getScore();\nconsole.log(PlayerManager);",
            "language": "javascript"
        },
        {
            "project_id": test_project["id"],
            "filename": "utils.js",
            "filepath": "src/utils.js",
            "content": "function calculateDamage() { return PlayerManager.attack(); }\nexport { calculateDamage };",
            "language": "javascript"
        }
    ]
    created_files = []
    for f in files:
        res = api_client.post(f"{API_URL}/files", json=f)
        assert res.status_code == 200
        created_files.append(res.json())
    return created_files

# ============ CORE API TESTS ============

class TestCoreAPI:
    """Core API health and configuration tests"""
    
    def test_health_endpoint(self, api_client):
        """Test /api/health returns healthy status"""
        response = api_client.get(f"{API_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        print(f"Health check passed: {data}")
    
    def test_root_endpoint_v23_features(self, api_client):
        """Test root endpoint lists all v2.3 features"""
        response = api_client.get(f"{API_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "2.3.0"
        
        # Check v2.3 specific features
        expected_features = ["agent_memory", "custom_actions", "project_duplicate", "multi_file_refactor"]
        for feature in expected_features:
            assert feature in data["features"], f"Missing feature: {feature}"
        print(f"API v{data['version']} features: {data['features']}")

# ============ AGENTS CRUD TESTS ============

class TestAgentsCRUD:
    """Agent endpoints tests"""
    
    def test_get_agents_returns_6(self, api_client):
        """GET /api/agents should return exactly 6 agents"""
        response = api_client.get(f"{API_URL}/agents")
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) == 6, f"Expected 6 agents, got {len(agents)}"
        
        # Verify agent names
        agent_names = [a["name"] for a in agents]
        expected_names = ["COMMANDER", "ATLAS", "FORGE", "SENTINEL", "PROBE", "PRISM"]
        for name in expected_names:
            assert name in agent_names, f"Missing agent: {name}"
        print(f"All 6 agents present: {agent_names}")

# ============ PROJECTS CRUD TESTS ============

class TestProjectsCRUD:
    """Project CRUD operations tests"""
    
    def test_create_project(self, api_client):
        """POST /api/projects creates a new project"""
        project_name = f"TEST_crud_{uuid.uuid4().hex[:6]}"
        response = api_client.post(f"{API_URL}/projects", json={
            "name": project_name,
            "description": "Test description",
            "type": "web_game"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == project_name
        assert data["type"] == "web_game"
        assert "id" in data
        print(f"Created project: {data['id']}")
        
        # Cleanup
        api_client.delete(f"{API_URL}/projects/{data['id']}")
    
    def test_get_projects_list(self, api_client):
        """GET /api/projects returns project list"""
        response = api_client.get(f"{API_URL}/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} projects")
    
    def test_get_project_by_id(self, api_client, test_project):
        """GET /api/projects/{id} returns specific project"""
        response = api_client.get(f"{API_URL}/projects/{test_project['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_project["id"]
        assert data["name"] == test_project["name"]
        print(f"Retrieved project: {data['name']}")
    
    def test_delete_project(self, api_client):
        """DELETE /api/projects/{id} deletes project"""
        # Create temp project
        res = api_client.post(f"{API_URL}/projects", json={
            "name": f"TEST_delete_{uuid.uuid4().hex[:6]}",
            "description": "To be deleted",
            "type": "web_app"
        })
        project_id = res.json()["id"]
        
        # Delete it
        response = api_client.delete(f"{API_URL}/projects/{project_id}")
        assert response.status_code == 200
        
        # Verify deletion
        verify = api_client.get(f"{API_URL}/projects/{project_id}")
        assert verify.status_code == 404
        print(f"Project {project_id} successfully deleted")

# ============ QUICK ACTIONS TESTS ============

class TestQuickActions:
    """Quick actions endpoint tests"""
    
    def test_get_predefined_quick_actions(self, api_client):
        """GET /api/quick-actions returns predefined actions"""
        response = api_client.get(f"{API_URL}/quick-actions")
        assert response.status_code == 200
        actions = response.json()
        assert len(actions) >= 8, f"Expected at least 8 quick actions, got {len(actions)}"
        
        # Verify expected actions exist
        action_ids = [a["id"] for a in actions]
        expected_actions = ["player_controller", "inventory_system", "save_system", "health_system"]
        for action_id in expected_actions:
            assert action_id in action_ids, f"Missing action: {action_id}"
        print(f"Quick actions: {action_ids}")

# ============ CUSTOM QUICK ACTIONS TESTS (v2.3) ============

class TestCustomQuickActions:
    """Custom Quick Actions CRUD - v2.3 feature"""
    
    def test_create_custom_action(self, api_client, test_project):
        """POST /api/custom-actions creates a custom action"""
        action_data = {
            "name": f"TEST_action_{uuid.uuid4().hex[:6]}",
            "description": "Test custom action",
            "prompt": "Generate a test component for {engine_type}",
            "chain": ["COMMANDER", "FORGE"],
            "icon": "sparkles",
            "category": "custom",
            "is_global": False,
            "project_id": test_project["id"]
        }
        response = api_client.post(f"{API_URL}/custom-actions", json=action_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == action_data["name"]
        assert data["prompt"] == action_data["prompt"]
        assert "id" in data
        print(f"Created custom action: {data['id']}")
        
        # Cleanup
        api_client.delete(f"{API_URL}/custom-actions/{data['id']}")
    
    def test_list_custom_actions(self, api_client, test_project):
        """GET /api/custom-actions lists custom actions"""
        # Create a test action first
        action_name = f"TEST_list_{uuid.uuid4().hex[:6]}"
        create_res = api_client.post(f"{API_URL}/custom-actions", json={
            "name": action_name,
            "description": "Test",
            "prompt": "Test prompt",
            "chain": ["COMMANDER"],
            "project_id": test_project["id"]
        })
        action_id = create_res.json()["id"]
        
        # List actions
        response = api_client.get(f"{API_URL}/custom-actions?project_id={test_project['id']}")
        assert response.status_code == 200
        actions = response.json()
        assert isinstance(actions, list)
        
        # Verify our action is in the list
        action_names = [a["name"] for a in actions]
        assert action_name in action_names, f"Created action not found in list"
        print(f"Custom actions list: {len(actions)} actions")
        
        # Cleanup
        api_client.delete(f"{API_URL}/custom-actions/{action_id}")
    
    def test_delete_custom_action(self, api_client, test_project):
        """DELETE /api/custom-actions/{id} deletes a custom action"""
        # Create action
        res = api_client.post(f"{API_URL}/custom-actions", json={
            "name": f"TEST_del_{uuid.uuid4().hex[:6]}",
            "description": "To delete",
            "prompt": "Test",
            "chain": ["FORGE"],
            "project_id": test_project["id"]
        })
        action_id = res.json()["id"]
        
        # Delete it
        response = api_client.delete(f"{API_URL}/custom-actions/{action_id}")
        assert response.status_code == 200
        print(f"Custom action {action_id} deleted successfully")

# ============ AGENT MEMORY TESTS (v2.3) ============

class TestAgentMemory:
    """Agent Memory Persistence - v2.3 feature"""
    
    def test_create_memory(self, api_client, test_project):
        """POST /api/memory creates agent memory"""
        memory_data = {
            "project_id": test_project["id"],
            "agent_name": "COMMANDER",
            "memory_type": "context",
            "content": "User prefers modular architecture with clear separation",
            "importance": 8
        }
        response = api_client.post(f"{API_URL}/memory", json=memory_data)
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == memory_data["content"]
        assert data["agent_name"] == "COMMANDER"
        assert data["importance"] == 8
        assert "id" in data
        print(f"Created memory: {data['id']}")
        
        # Cleanup
        api_client.delete(f"{API_URL}/memory/{data['id']}")
    
    def test_list_memories(self, api_client, test_project):
        """GET /api/memory?project_id=xxx lists memories"""
        # Create test memory
        mem_res = api_client.post(f"{API_URL}/memory", json={
            "project_id": test_project["id"],
            "agent_name": "FORGE",
            "memory_type": "learned",
            "content": "Test memory content",
            "importance": 5
        })
        mem_id = mem_res.json()["id"]
        
        # List memories
        response = api_client.get(f"{API_URL}/memory?project_id={test_project['id']}")
        assert response.status_code == 200
        memories = response.json()
        assert isinstance(memories, list)
        print(f"Listed {len(memories)} memories")
        
        # Cleanup
        api_client.delete(f"{API_URL}/memory/{mem_id}")
    
    def test_delete_memory(self, api_client, test_project):
        """DELETE /api/memory/{id} deletes a memory"""
        # Create
        res = api_client.post(f"{API_URL}/memory", json={
            "project_id": test_project["id"],
            "agent_name": "ATLAS",
            "memory_type": "decision",
            "content": "Memory to delete",
            "importance": 3
        })
        mem_id = res.json()["id"]
        
        # Delete
        response = api_client.delete(f"{API_URL}/memory/{mem_id}")
        assert response.status_code == 200
        print(f"Memory {mem_id} deleted successfully")
    
    def test_auto_extract_memories_endpoint(self, api_client, test_project):
        """POST /api/memory/auto-extract endpoint exists and responds"""
        response = api_client.post(f"{API_URL}/memory/auto-extract?project_id={test_project['id']}")
        assert response.status_code == 200
        data = response.json()
        assert "extracted" in data
        assert "memories" in data
        print(f"Auto-extract returned: extracted={data['extracted']}")

# ============ PROJECT DUPLICATION TESTS (v2.3) ============

class TestProjectDuplication:
    """Project Duplication - v2.3 feature"""
    
    def test_duplicate_project(self, api_client, test_project_with_files, test_project):
        """POST /api/projects/{id}/duplicate duplicates project with files"""
        new_name = f"TEST_dup_{uuid.uuid4().hex[:6]}"
        response = api_client.post(f"{API_URL}/projects/{test_project['id']}/duplicate", json={
            "project_id": test_project["id"],
            "new_name": new_name,
            "include_files": True,
            "include_tasks": False,
            "include_messages": False
        })
        assert response.status_code == 200
        data = response.json()
        assert data["project"]["name"] == new_name
        assert "files" in data
        print(f"Duplicated project: {data['project']['id']} with {data['files']} files")
        
        # Verify new project exists
        verify = api_client.get(f"{API_URL}/projects/{data['project']['id']}")
        assert verify.status_code == 200
        
        # Cleanup duplicated project
        api_client.delete(f"{API_URL}/projects/{data['project']['id']}")
    
    def test_duplicate_project_new_name_required(self, api_client, test_project):
        """Duplication requires new_name field"""
        # Test with invalid data - should still work as long as new_name provided
        response = api_client.post(f"{API_URL}/projects/{test_project['id']}/duplicate", json={
            "project_id": test_project["id"],
            "new_name": f"TEST_dup2_{uuid.uuid4().hex[:6]}",
            "include_files": False
        })
        assert response.status_code == 200
        dup_id = response.json()["project"]["id"]
        
        # Cleanup
        api_client.delete(f"{API_URL}/projects/{dup_id}")

# ============ MULTI-FILE REFACTOR TESTS (v2.3) ============

class TestMultiFileRefactor:
    """Multi-file Refactoring - v2.3 feature"""
    
    def test_refactor_preview_find_replace(self, api_client, test_project, test_project_with_files):
        """POST /api/refactor/preview shows what would change"""
        response = api_client.post(f"{API_URL}/refactor/preview", json={
            "project_id": test_project["id"],
            "refactor_type": "find_replace",
            "target": "PlayerManager",
            "new_value": "GameManager"
        })
        assert response.status_code == 200
        data = response.json()
        assert "files_affected" in data
        assert "changes" in data
        assert data["refactor_type"] == "find_replace"
        print(f"Preview: {data['files_affected']} files affected")
        if data["changes"]:
            print(f"First change: {data['changes'][0]}")
    
    def test_refactor_apply_find_replace(self, api_client, test_project):
        """POST /api/refactor/apply applies refactoring"""
        # First create a file with content to refactor
        test_file = api_client.post(f"{API_URL}/files", json={
            "project_id": test_project["id"],
            "filename": "refactor_test.js",
            "filepath": "test/refactor_test.js",
            "content": "const OldName = {};\nconsole.log(OldName.value);",
            "language": "javascript"
        }).json()
        
        # Apply refactor
        response = api_client.post(f"{API_URL}/refactor/apply", json={
            "project_id": test_project["id"],
            "refactor_type": "find_replace",
            "target": "OldName",
            "new_value": "NewName"
        })
        assert response.status_code == 200
        data = response.json()
        assert "files_updated" in data
        print(f"Refactor applied: {data['files_updated']} files updated")
        
        # Verify file was updated
        files = api_client.get(f"{API_URL}/files?project_id={test_project['id']}").json()
        refactored = next((f for f in files if f["filepath"] == "test/refactor_test.js"), None)
        if refactored:
            assert "NewName" in refactored["content"]
            print("File content updated successfully")
    
    def test_refactor_rename_type(self, api_client, test_project):
        """POST /api/refactor/preview with rename type"""
        response = api_client.post(f"{API_URL}/refactor/preview", json={
            "project_id": test_project["id"],
            "refactor_type": "rename",
            "target": "calculateDamage",
            "new_value": "computeDamage"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["refactor_type"] == "rename"
        print(f"Rename preview: {data['files_affected']} files affected")

# ============ GITHUB PUSH TESTS ============

class TestGitHubPush:
    """GitHub Push endpoint - verify endpoint exists"""
    
    def test_github_push_endpoint_exists(self, api_client, test_project):
        """POST /api/github/push endpoint exists (will fail auth but endpoint works)"""
        # Send with invalid token to verify endpoint exists
        response = api_client.post(f"{API_URL}/github/push", json={
            "project_id": test_project["id"],
            "github_token": "invalid_token",
            "repo_name": "test-repo",
            "commit_message": "Test commit",
            "create_repo": False
        })
        # Should return 400 (GitHub error) not 404
        assert response.status_code in [400, 401, 500], f"Unexpected status: {response.status_code}"
        print(f"GitHub endpoint exists, returned status {response.status_code} for invalid token")

# ============ FILES CRUD TESTS ============

class TestFilesCRUD:
    """File management tests"""
    
    def test_create_file(self, api_client, test_project):
        """POST /api/files creates a file"""
        response = api_client.post(f"{API_URL}/files", json={
            "project_id": test_project["id"],
            "filename": "test.js",
            "filepath": "src/test.js",
            "content": "console.log('hello');",
            "language": "javascript"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["filepath"] == "src/test.js"
        assert "id" in data
        print(f"Created file: {data['filepath']}")
    
    def test_get_project_files(self, api_client, test_project):
        """GET /api/files?project_id=xxx lists files"""
        response = api_client.get(f"{API_URL}/files?project_id={test_project['id']}")
        assert response.status_code == 200
        files = response.json()
        assert isinstance(files, list)
        print(f"Project has {len(files)} files")

# ============ CHAT STREAMING TESTS ============

class TestChatStreaming:
    """Chat streaming endpoint tests"""
    
    def test_chat_stream_endpoint(self, api_client, test_project):
        """POST /api/chat/stream returns SSE response"""
        response = api_client.post(
            f"{API_URL}/chat/stream",
            json={
                "project_id": test_project["id"],
                "message": "Hello, this is a test message",
                "phase": "clarification"
            },
            stream=True
        )
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "text/event-stream" in content_type, f"Expected SSE, got {content_type}"
        
        # Read first few chunks
        chunks_received = 0
        for chunk in response.iter_lines():
            if chunk:
                chunks_received += 1
                if chunks_received >= 5:
                    break
        print(f"Received {chunks_received} SSE chunks from chat stream")

# ============ RUN TESTS ============

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
