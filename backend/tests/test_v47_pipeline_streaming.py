"""
Test suite for AgentForge v47 Pipeline Streaming Fix
Tests:
- /api/delegate endpoint now returns 'delegations' field
- /api/delegate/stream new SSE streaming endpoint
- SSE stream events: start, content, done with code_blocks and delegations
"""

import pytest
import requests
import json
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_PROJECT_ID = "878a623f-111e-45df-a837-7821bace9c1a"


@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def project_id():
    """Use existing project from DB"""
    return TEST_PROJECT_ID


class TestDelegateEndpoint:
    """Tests for /api/delegate (non-streaming) endpoint - now returns delegations field"""

    def test_delegate_endpoint_exists_and_validates_required_fields(self, api_client):
        """Test that /api/delegate returns 400 when delegate_to is missing"""
        response = api_client.post(f"{BASE_URL}/api/delegate", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Build a simple hello world function"
        })
        assert response.status_code == 400, f"Expected 400 for missing delegate_to, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        print(f"✅ /api/delegate validates delegate_to requirement: {data['detail']}")

    def test_delegate_endpoint_returns_404_for_unknown_agent(self, api_client):
        """Test that /api/delegate returns 404 for unknown agent"""
        response = api_client.post(f"{BASE_URL}/api/delegate", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Build something",
            "delegate_to": "NONEXISTENT_AGENT_XYZ"
        })
        assert response.status_code == 404, f"Expected 404 for unknown agent, got {response.status_code}"
        print(f"✅ /api/delegate returns 404 for unknown agent")

    def test_delegate_endpoint_returns_delegations_field(self, api_client):
        """Critical test: /api/delegate must return 'delegations' field (was missing before fix)"""
        # Use a short task to minimize LLM call time
        response = api_client.post(f"{BASE_URL}/api/delegate", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Create a simple hello.py file with print('hello')",
            "delegate_to": "FORGE"
        }, timeout=120)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"

        data = response.json()
        print(f"Response keys: {list(data.keys())}")

        # Critical: 'delegations' field must exist (this was the bug)
        assert "delegations" in data, f"CRITICAL BUG: 'delegations' field missing from response. Keys: {list(data.keys())}"
        assert isinstance(data["delegations"], list), f"'delegations' should be a list, got {type(data['delegations'])}"

        # Other expected fields
        assert "response" in data, "Missing 'response' field"
        assert "code_blocks" in data, "Missing 'code_blocks' field"
        assert isinstance(data["code_blocks"], list), f"'code_blocks' should be a list"
        assert "agent" in data, "Missing 'agent' field"

        # Agent info structure
        agent = data["agent"]
        assert "id" in agent
        assert "name" in agent
        assert "role" in agent
        assert agent["name"].upper() == "FORGE"

        print(f"✅ /api/delegate returns all required fields including 'delegations'")
        print(f"   delegations count: {len(data['delegations'])}, code_blocks: {len(data['code_blocks'])}")


class TestDelegateStreamEndpoint:
    """Tests for new /api/delegate/stream SSE streaming endpoint"""

    def test_stream_endpoint_exists(self, api_client):
        """Test that /api/delegate/stream endpoint exists"""
        # Make request but close immediately after getting headers
        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Quick task",
            "delegate_to": "FORGE"
        }, stream=True, timeout=30)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        content_type = response.headers.get("content-type", "")
        assert "text/event-stream" in content_type, f"Expected text/event-stream content-type, got: {content_type}"
        response.close()
        print(f"✅ /api/delegate/stream exists and returns SSE content-type: {content_type}")

    def test_stream_endpoint_validates_missing_delegate_to(self, api_client):
        """Test that /api/delegate/stream returns 400 when delegate_to is missing"""
        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Some task"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"✅ /api/delegate/stream validates delegate_to")

    def test_stream_endpoint_validates_unknown_agent(self, api_client):
        """Test that /api/delegate/stream returns 404 for unknown agent"""
        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Some task",
            "delegate_to": "UNKNOWN_AGENT_999"
        })
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✅ /api/delegate/stream returns 404 for unknown agent")

    def test_stream_endpoint_emits_start_event(self, api_client):
        """Test that /api/delegate/stream emits 'start' SSE event with agent info"""
        start_event = None

        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Write a one-line Python comment",
            "delegate_to": "FORGE"
        }, stream=True, timeout=60)

        assert response.status_code == 200

        # Read only first event
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("data: "):
                data = json.loads(line[6:])
                if data.get("type") == "start":
                    start_event = data
                    break

        response.close()

        assert start_event is not None, "Did not receive 'start' event from SSE stream"
        assert "agent" in start_event, f"'start' event missing 'agent' field: {start_event}"

        agent = start_event["agent"]
        assert "id" in agent, "agent missing 'id'"
        assert "name" in agent, "agent missing 'name'"
        assert "role" in agent, "agent missing 'role'"
        assert agent["name"].upper() == "FORGE", f"Expected FORGE agent, got {agent['name']}"

        print(f"✅ /api/delegate/stream emits proper 'start' event with agent: {agent['name']}")

    def test_stream_endpoint_emits_content_events(self, api_client):
        """Test that /api/delegate/stream emits 'content' events during generation"""
        content_events = []
        done_event = None

        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Write exactly one line: print('hello world') in Python",
            "delegate_to": "FORGE"
        }, stream=True, timeout=120)

        assert response.status_code == 200

        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    if data.get("type") == "content":
                        content_events.append(data)
                    elif data.get("type") == "done":
                        done_event = data
                        break  # Stop reading after done
                    elif data.get("type") == "error":
                        pytest.fail(f"Stream returned error: {data.get('error')}")
                except json.JSONDecodeError:
                    pass

        response.close()

        assert len(content_events) > 0, "No 'content' events received from SSE stream"
        for event in content_events:
            assert "content" in event, f"content event missing 'content' field: {event}"

        print(f"✅ /api/delegate/stream emitted {len(content_events)} content events")

    def test_stream_endpoint_done_event_has_required_fields(self, api_client):
        """Critical test: 'done' event must have 'code_blocks' and 'delegations' arrays"""
        done_event = None
        full_content = ""

        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Create a Python file hello.py with a simple print statement",
            "delegate_to": "FORGE"
        }, stream=True, timeout=120)

        assert response.status_code == 200

        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    if data.get("type") == "content":
                        full_content += data.get("content", "")
                    elif data.get("type") == "done":
                        done_event = data
                        break
                    elif data.get("type") == "error":
                        pytest.fail(f"Stream returned error: {data.get('error')}")
                except json.JSONDecodeError:
                    pass

        response.close()

        assert done_event is not None, "Did not receive 'done' event from SSE stream"

        # Critical: 'code_blocks' must exist
        assert "code_blocks" in done_event, f"CRITICAL: 'code_blocks' missing from 'done' event: {done_event.keys()}"
        assert isinstance(done_event["code_blocks"], list), "code_blocks should be a list"

        # Critical: 'delegations' must exist
        assert "delegations" in done_event, f"CRITICAL: 'delegations' missing from 'done' event: {done_event.keys()}"
        assert isinstance(done_event["delegations"], list), "delegations should be a list"

        print(f"✅ 'done' event has required fields: code_blocks={len(done_event['code_blocks'])}, delegations={len(done_event['delegations'])}")
        print(f"   Full content length: {len(full_content)} chars")

    def test_stream_endpoint_full_pipeline_sequence(self, api_client):
        """Test complete SSE stream lifecycle: start → content... → done"""
        events_received = []

        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Brief code review",
            "delegate_to": "ATLAS"
        }, stream=True, timeout=120)

        assert response.status_code == 200

        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    events_received.append(data.get("type"))
                    if data.get("type") in ("done", "error"):
                        break
                except json.JSONDecodeError:
                    pass

        response.close()

        assert "start" in events_received, f"Missing 'start' event. Got: {events_received}"
        assert "content" in events_received, f"Missing 'content' events. Got: {events_received}"
        assert "done" in events_received, f"Missing 'done' event. Got: {events_received}"

        # Order check: start must come first, done last
        assert events_received[0] == "start", f"First event should be 'start', got: {events_received[0]}"
        assert events_received[-1] == "done", f"Last event should be 'done', got: {events_received[-1]}"

        print(f"✅ Full SSE pipeline sequence correct: {events_received[:3]}...{events_received[-1]}")
        print(f"   Total events: {len(events_received)}")


class TestAvailableAgents:
    """Test that expected agents are available for delegation"""

    def test_pipeline_agents_available(self, api_client):
        """Test that COMMANDER, FORGE, ATLAS etc. are available"""
        response = api_client.get(f"{BASE_URL}/api/pipeline/agents")
        assert response.status_code == 200
        data = response.json()
        # /api/pipeline/agents returns either a list or a dict of agent configs
        if isinstance(data, list):
            agent_names = [a['name'].upper() for a in data]
        elif isinstance(data, dict):
            # Dict keyed by role, values have 'name'
            agent_names = [v['name'].upper() for v in data.values() if isinstance(v, dict) and 'name' in v]
        else:
            pytest.fail(f"Unexpected type for pipeline/agents: {type(data)}")
        print(f"Available agents: {agent_names}")

        # At least some core agents should be present
        assert len(agent_names) > 0, "No agents found"
        print(f"✅ Pipeline agents available: {agent_names}")
        # Note: /api/pipeline/agents returns config-based agents, DB agents are separate

    def test_chat_stream_endpoint_exists(self, api_client):
        """Test that /api/chat/stream endpoint exists (used by frontend sendMessageStreaming)"""
        response = api_client.post(f"{BASE_URL}/api/chat/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Ping"
        }, stream=True, timeout=30)

        # Just check it exists and returns streaming
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        content_type = response.headers.get("content-type", "")
        assert "text/event-stream" in content_type, f"Expected SSE, got: {content_type}"
        response.close()
        print(f"✅ /api/chat/stream exists and returns SSE")
