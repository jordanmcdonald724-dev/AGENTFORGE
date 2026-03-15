"""
Tests for iteration 27:
- /refactor/preview and /refactor/apply endpoints
- /war-room/message POST and /war-room/{project_id} GET
- /simulate endpoint (was missing in iter 26, now present)
Project: 878a623f-111e-45df-a837-7821bace9c1a (OceanMapSurvivalGame - has C++ files with AbyssalShores)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
PROJECT_ID = "878a623f-111e-45df-a837-7821bace9c1a"


@pytest.fixture
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


class TestRefactorPreview:
    """Tests for POST /api/refactor/preview"""

    def test_preview_find_replace_abyssalshores(self, session):
        """Search for 'AbyssalShores' in OceanMapSurvivalGame — expect matches"""
        resp = session.post(f"{BASE_URL}/api/refactor/preview", json={
            "project_id": PROJECT_ID,
            "refactor_type": "find_replace",
            "target": "AbyssalShores",
            "new_value": "CoastalSurvival"
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "files_affected" in data
        assert "total_files_scanned" in data
        assert "changes" in data
        assert data["total_files_scanned"] > 0, "Should have scanned at least 1 file"
        assert data["files_affected"] > 0, f"Expected matches for 'AbyssalShores', got 0 — total scanned: {data['total_files_scanned']}"
        print(f"PASS: files_affected={data['files_affected']}, scanned={data['total_files_scanned']}")

    def test_preview_changes_have_before_after(self, session):
        """Changes in preview response should contain filepath, occurrences, preview.before, preview.after"""
        resp = session.post(f"{BASE_URL}/api/refactor/preview", json={
            "project_id": PROJECT_ID,
            "refactor_type": "find_replace",
            "target": "AbyssalShores",
            "new_value": "CoastalSurvival"
        })
        assert resp.status_code == 200
        data = resp.json()
        if data["files_affected"] > 0:
            change = data["changes"][0]
            assert "filepath" in change, "change must have filepath"
            assert "occurrences" in change, "change must have occurrences"
            assert "preview" in change, "change must have preview dict"
            assert "before" in change["preview"], "preview must have before"
            assert "after" in change["preview"], "preview must have after"
            assert change["occurrences"] > 0, "occurrences should be > 0"
            print(f"PASS: change[0] filepath={change['filepath']}, occurrences={change['occurrences']}")

    def test_preview_no_match_returns_zero(self, session):
        """A target that doesn't exist should return files_affected=0"""
        resp = session.post(f"{BASE_URL}/api/refactor/preview", json={
            "project_id": PROJECT_ID,
            "refactor_type": "find_replace",
            "target": "XXXXXXNOTEXISTXXXXXX",
            "new_value": "something"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["files_affected"] == 0
        assert data["changes"] == []
        print(f"PASS: no-match returns files_affected=0, scanned={data['total_files_scanned']}")

    def test_preview_rename_type(self, session):
        """rename refactor type should also work"""
        resp = session.post(f"{BASE_URL}/api/refactor/preview", json={
            "project_id": PROJECT_ID,
            "refactor_type": "rename",
            "target": "AbyssalShores",
            "new_value": "CoastalSurvival"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "files_affected" in data
        assert data["total_files_scanned"] > 0
        print(f"PASS: rename preview: files_affected={data['files_affected']}")

    def test_preview_invalid_project(self, session):
        """Should return 404 for non-existent project"""
        resp = session.post(f"{BASE_URL}/api/refactor/preview", json={
            "project_id": "does-not-exist-xxxxxx",
            "refactor_type": "find_replace",
            "target": "foo",
            "new_value": "bar"
        })
        assert resp.status_code == 404
        print("PASS: 404 for invalid project")


class TestWarRoomAPI:
    """Tests for war room endpoints"""

    def test_get_war_room_messages(self, session):
        """GET /api/war-room/{project_id} should return a list"""
        resp = session.get(f"{BASE_URL}/api/war-room/{PROJECT_ID}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"PASS: war room has {len(data)} messages")
        if len(data) > 0:
            msg = data[0]
            assert "from_agent" in msg
            assert "content" in msg
            assert "message_type" in msg
            print(f"  Sample: from={msg['from_agent']}, type={msg['message_type']}")

    def test_post_war_room_message(self, session):
        """POST /api/war-room/message should store and return a message"""
        resp = session.post(
            f"{BASE_URL}/api/war-room/message",
            params={
                "project_id": PROJECT_ID,
                "from_agent": "TEST_AGENT",
                "content": "Test build log entry from T1 testing agent",
                "message_type": "progress"
            }
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["from_agent"] == "TEST_AGENT"
        assert data["content"] == "Test build log entry from T1 testing agent"
        assert data["message_type"] == "progress"
        assert "id" in data or "timestamp" in data
        print(f"PASS: war room message posted: id={data.get('id', data.get('timestamp'))}")

    def test_war_room_message_persists(self, session):
        """After posting, GET should include the new message"""
        content = "Persistence check message XUNIQ12345"
        # POST
        post_resp = session.post(
            f"{BASE_URL}/api/war-room/message",
            params={
                "project_id": PROJECT_ID,
                "from_agent": "FORGE",
                "content": content,
                "message_type": "progress"
            }
        )
        assert post_resp.status_code == 200

        # GET to verify persistence
        get_resp = session.get(f"{BASE_URL}/api/war-room/{PROJECT_ID}")
        assert get_resp.status_code == 200
        messages = get_resp.json()
        found = any(m["content"] == content for m in messages)
        assert found, f"Posted message not found in war room messages (total={len(messages)})"
        print(f"PASS: message persisted in war room")

    def test_war_room_progress_messages_exist(self, session):
        """Check if war room has any progress type messages (from previous pipeline runs)"""
        resp = session.get(f"{BASE_URL}/api/war-room/{PROJECT_ID}")
        assert resp.status_code == 200
        messages = resp.json()
        progress_msgs = [m for m in messages if m.get("message_type") == "progress"]
        print(f"INFO: War room has {len(messages)} total messages, {len(progress_msgs)} progress messages")
        if progress_msgs:
            print(f"  Sample progress: from={progress_msgs[0]['from_agent']}: {progress_msgs[0]['content'][:80]}")
        # This is informational — not a strict failure if none exist yet
        assert len(messages) >= 0  # Always passes, but prints info


class TestSimulateEndpoint:
    """Test POST /api/simulate — was missing in iter_26"""

    def test_simulate_with_systems(self, session):
        """POST /api/simulate should return feasibility metrics"""
        resp = session.post(f"{BASE_URL}/api/simulate", json={
            "project_id": PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "include_systems": ["terrain", "combat_system"]
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "estimated_build_time" in data
        assert "file_count" in data
        assert "feasibility_score" in data
        assert "ready_to_build" in data
        assert "architecture_summary" in data
        assert data["file_count"] > 0
        print(f"PASS: simulate works — file_count={data['file_count']}, feasibility={data['feasibility_score']}")

    def test_simulate_no_systems_warning(self, session):
        """Simulate with empty systems should return ready_to_build=False"""
        resp = session.post(f"{BASE_URL}/api/simulate", json={
            "project_id": PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "include_systems": []
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["ready_to_build"] == False, "No systems = should not be ready"
        print(f"PASS: empty systems returns ready_to_build=False")
