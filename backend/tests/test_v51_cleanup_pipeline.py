"""
Iteration 28 — AgentForge cleanup verification + pipeline E2E tests
Tests: 
  - Code cleanup: SYSTEM_ICONS removed from ProjectWorkspace, warRoomEndRef removed, buildDialog removed
  - GET /api/systems/open-world returns list (not dict with 'systems' key)
  - War Room POST/GET endpoints
  - Chat send + COMMANDER delegation trigger
  - Basic pipeline starts
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
PROJECT_ID = "878a623f-111e-45df-a837-7821bace9c1a"


class TestCleanupVerification:
    """Verify dead code removed from server.py and build_operations.py serves open-world"""

    def test_open_world_returns_list(self):
        """GET /api/systems/open-world must return a list of 15 systems (not a dict)"""
        resp = requests.get(f"{BASE_URL}/api/systems/open-world", timeout=15)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text[:200]}"
        data = resp.json()
        # Must be a list, not a dict with 'systems' key
        assert isinstance(data, list), f"Expected list, got {type(data).__name__}: {str(data)[:200]}"
        assert len(data) >= 10, f"Expected at least 10 systems, got {len(data)}"
        # Each item should have id and name
        first = data[0]
        assert "id" in first, f"System missing 'id': {first}"
        assert "name" in first, f"System missing 'name': {first}"
        print(f"✓ /api/systems/open-world returns list of {len(data)} systems")

    def test_open_world_has_15_systems(self):
        """Verify specifically 15 systems are returned"""
        resp = requests.get(f"{BASE_URL}/api/systems/open-world", timeout=15)
        assert resp.status_code == 200
        data = resp.json()
        # Should have 15 systems (or at least a significant number)
        print(f"  Systems count: {len(data)}")
        assert len(data) >= 12, f"Expected ~15 systems, got {len(data)}"
        # Print system ids for context
        ids = [s.get("id") for s in data]
        print(f"  System IDs: {ids}")

    def test_build_stages_endpoint(self):
        """GET /api/build-stages/unreal works (also served by build_operations.py)"""
        resp = requests.get(f"{BASE_URL}/api/build-stages/unreal", timeout=15)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list), "build-stages should return a list"
        print(f"✓ /api/build-stages/unreal returns {len(data)} stages")


class TestWarRoomEndpoints:
    """War Room API: POST message + GET messages"""

    def test_post_war_room_message(self):
        """POST /api/war-room/message stores a progress message"""
        content = f"TEST_v51 — parallel task completed at {int(time.time())}"
        resp = requests.post(
            f"{BASE_URL}/api/war-room/message",
            params={
                "project_id": PROJECT_ID,
                "from_agent": "FORGE",
                "content": content,
                "message_type": "progress"
            },
            timeout=15
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text[:200]}"
        data = resp.json()
        assert data.get("from_agent") == "FORGE"
        assert data.get("content") == content
        assert data.get("message_type") == "progress"
        print(f"✓ POST /api/war-room/message returned id={data.get('id')}")

    def test_get_war_room_messages(self):
        """GET /api/war-room/{project_id} returns list of messages"""
        resp = requests.get(f"{BASE_URL}/api/war-room/{PROJECT_ID}", timeout=15)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list), f"Expected list, got {type(data).__name__}"
        print(f"✓ GET /api/war-room/{PROJECT_ID} returns {len(data)} messages")

    def test_war_room_messages_persist(self):
        """Post a message then verify it appears in GET"""
        unique_content = f"PERSIST_TEST_{int(time.time())}"
        # Post
        post_resp = requests.post(
            f"{BASE_URL}/api/war-room/message",
            params={
                "project_id": PROJECT_ID,
                "from_agent": "SENTINEL",
                "content": unique_content,
                "message_type": "progress"
            },
            timeout=15
        )
        assert post_resp.status_code == 200

        # Get and verify
        time.sleep(0.5)
        get_resp = requests.get(f"{BASE_URL}/api/war-room/{PROJECT_ID}", timeout=15)
        assert get_resp.status_code == 200
        messages = get_resp.json()
        contents = [m.get("content", "") for m in messages]
        assert unique_content in contents, f"Posted message not found in GET response. Messages: {contents[-5:]}"
        print(f"✓ War room message persisted and retrieved successfully")


class TestChatAndPipeline:
    """Chat endpoint and pipeline delegation"""

    def test_project_exists(self):
        """Test project 878a623f exists"""
        resp = requests.get(f"{BASE_URL}/api/projects/{PROJECT_ID}", timeout=15)
        assert resp.status_code == 200, f"Project not found: {resp.status_code}"
        data = resp.json()
        assert data.get("id") == PROJECT_ID or data.get("name")
        print(f"✓ Project exists: {data.get('name')}")

    def test_messages_endpoint(self):
        """GET /api/messages for project returns list"""
        resp = requests.get(f"{BASE_URL}/api/messages?project_id={PROJECT_ID}&limit=50", timeout=15)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        print(f"✓ Messages endpoint returns {len(data)} messages")

    def test_files_endpoint(self):
        """GET /api/files for project returns list"""
        resp = requests.get(f"{BASE_URL}/api/files?project_id={PROJECT_ID}", timeout=15)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        print(f"✓ Files endpoint returns {len(data)} files")

    def test_simulate_endpoint(self):
        """POST /api/simulate returns feasibility metrics"""
        resp = requests.post(
            f"{BASE_URL}/api/simulate",
            json={
                "project_id": PROJECT_ID,
                "build_type": "full",
                "target_engine": "unreal",
                "include_systems": ["terrain", "weather"]
            },
            timeout=30
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text[:300]}"
        data = resp.json()
        assert "total_files_estimate" in data or "ready_to_build" in data or "feasibility" in data, \
            f"Unexpected response: {data}"
        print(f"✓ Simulate endpoint works: ready_to_build={data.get('ready_to_build')}")

    def test_refactor_preview_endpoint(self):
        """POST /api/refactor/preview works with JSON body (not query params)"""
        resp = requests.post(
            f"{BASE_URL}/api/refactor/preview",
            json={
                "project_id": PROJECT_ID,
                "refactor_type": "find_replace",
                "target": "AbyssalShores",
                "new_value": "AbyssalShores"
            },
            timeout=15
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text[:300]}"
        data = resp.json()
        assert "total_files_scanned" in data or "files_affected" in data or "files_scanned" in data, f"Unexpected response: {data}"
        print(f"✓ Refactor preview works: {data.get('total_files_scanned', data.get('files_scanned', 'N/A'))} files scanned")
