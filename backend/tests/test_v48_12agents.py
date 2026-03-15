"""
Test suite for AgentForge v48 - 12 Agent Verification
Tests:
- GET /api/agents returns exactly 12 agents with correct names
- COMMANDER system prompt contains all 12 agent names and routing rules
- POST /api/agents/reset works and recreates all 12 agents
- PATCH /api/agents/{agent_id} allows updating system_prompt field
- /api/delegate/stream works for each of the 12 agent names
- Routing logic check via COMMANDER system prompt content
"""

import pytest
import requests
import json
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_PROJECT_ID = "878a623f-111e-45df-a837-7821bace9c1a"

# All 12 expected agent names
EXPECTED_AGENTS = [
    "COMMANDER", "ATLAS", "FORGE", "SENTINEL", "PROBE",
    "PRISM", "TERRA", "KINETIC", "SONIC", "NEXUS", "CHRONICLE", "VERTEX"
]


@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestGet12Agents:
    """Tests for GET /api/agents — must return exactly 12 agents"""

    def test_get_agents_returns_200(self, api_client):
        """GET /api/agents must return 200"""
        response = api_client.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        print(f"✅ GET /api/agents returns 200")

    def test_get_agents_returns_exactly_12(self, api_client):
        """GET /api/agents must return exactly 12 agents"""
        response = api_client.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        assert len(data) == 12, f"Expected 12 agents, got {len(data)}. Names: {[a.get('name') for a in data]}"
        print(f"✅ GET /api/agents returns exactly 12 agents")

    def test_get_agents_has_all_correct_names(self, api_client):
        """GET /api/agents must have all 12 correct agent names"""
        response = api_client.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        names = [a.get("name", "").upper() for a in data]
        print(f"  Agent names found: {names}")
        for expected in EXPECTED_AGENTS:
            assert expected in names, f"Missing agent: {expected}. Found: {names}"
        print(f"✅ All 12 agent names present: {names}")

    def test_get_agents_commander_has_correct_role(self, api_client):
        """COMMANDER must have role='lead'"""
        response = api_client.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        commander = next((a for a in data if a.get("name", "").upper() == "COMMANDER"), None)
        assert commander is not None, "COMMANDER agent not found"
        assert commander.get("role") == "lead", f"Expected role='lead', got '{commander.get('role')}'"
        print(f"✅ COMMANDER has correct role='lead'")

    def test_commander_system_prompt_contains_all_12_agents(self, api_client):
        """COMMANDER system prompt must reference all 12 agent names"""
        response = api_client.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        commander = next((a for a in data if a.get("name", "").upper() == "COMMANDER"), None)
        assert commander is not None, "COMMANDER not found"

        system_prompt = commander.get("system_prompt", "")
        assert len(system_prompt) > 100, f"System prompt too short: {len(system_prompt)} chars"

        # Check all 12 agent names are mentioned (except COMMANDER itself)
        specialist_agents = [a for a in EXPECTED_AGENTS if a != "COMMANDER"]
        missing_from_prompt = []
        for agent_name in specialist_agents:
            if agent_name not in system_prompt:
                missing_from_prompt.append(agent_name)

        assert len(missing_from_prompt) == 0, \
            f"COMMANDER prompt missing these agent names: {missing_from_prompt}"
        print(f"✅ COMMANDER system prompt contains all 12 agent names")

    def test_commander_system_prompt_has_routing_rules(self, api_client):
        """COMMANDER system prompt must contain game vs web routing rules"""
        response = api_client.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        commander = next((a for a in data if a.get("name", "").upper() == "COMMANDER"), None)
        assert commander is not None
        system_prompt = commander.get("system_prompt", "")

        # Check for routing keyword indicators
        assert "GAME" in system_prompt.upper() or "game" in system_prompt.lower(), \
            "COMMANDER prompt should mention GAME routing"
        assert "WEB" in system_prompt.upper() or "web" in system_prompt.lower(), \
            "COMMANDER prompt should mention WEB routing"

        # Check for delegation format marker
        assert "[DELEGATE:" in system_prompt, \
            "COMMANDER prompt should contain [DELEGATE:AGENT_NAME] format"

        print(f"✅ COMMANDER system prompt has GAME and WEB routing rules + delegation format")

    def test_all_agents_have_required_fields(self, api_client):
        """Each agent must have id, name, role, system_prompt, avatar"""
        response = api_client.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        required_fields = ["id", "name", "role", "system_prompt", "avatar"]
        for agent in data:
            agent_name = agent.get("name", "unknown")
            for field in required_fields:
                assert field in agent, f"Agent '{agent_name}' missing field '{field}'"
        print(f"✅ All 12 agents have required fields: {required_fields}")


class TestAgentsReset:
    """Tests for POST /api/agents/reset"""

    def test_reset_agents_returns_200(self, api_client):
        """POST /api/agents/reset must return 200"""
        response = api_client.post(f"{BASE_URL}/api/agents/reset")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        data = response.json()
        assert "success" in data, f"Response missing 'success' field: {data}"
        assert data["success"] is True, f"Expected success=True, got {data['success']}"
        print(f"✅ POST /api/agents/reset returns 200 with success=True")

    def test_reset_agents_creates_exactly_12(self, api_client):
        """After reset, exactly 12 agents must exist"""
        # Call reset
        reset_response = api_client.post(f"{BASE_URL}/api/agents/reset")
        assert reset_response.status_code == 200
        reset_data = reset_response.json()

        # Check agents_created field
        assert "agents_created" in reset_data, f"Missing 'agents_created' in response: {reset_data.keys()}"
        assert reset_data["agents_created"] == 12, \
            f"Expected 12 agents created, got {reset_data['agents_created']}"

        # Verify via GET /api/agents
        get_response = api_client.get(f"{BASE_URL}/api/agents")
        assert get_response.status_code == 200
        agents = get_response.json()
        assert len(agents) == 12, f"After reset, expected 12 agents, got {len(agents)}"
        print(f"✅ After reset, exactly 12 agents exist")

    def test_reset_agents_recreates_all_names(self, api_client):
        """After reset, all 12 agent names must be present"""
        api_client.post(f"{BASE_URL}/api/agents/reset")
        get_response = api_client.get(f"{BASE_URL}/api/agents")
        agents = get_response.json()
        names = [a.get("name", "").upper() for a in agents]
        for expected in EXPECTED_AGENTS:
            assert expected in names, f"After reset, missing agent: {expected}"
        print(f"✅ After reset, all 12 agent names present: {names}")

    def test_reset_response_includes_agent_names_list(self, api_client):
        """Reset response must include 'agents' list with agent names"""
        response = api_client.post(f"{BASE_URL}/api/agents/reset")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data, f"Missing 'agents' field in reset response: {data.keys()}"
        assert isinstance(data["agents"], list)
        assert len(data["agents"]) == 12, f"Expected 12 agent names in response, got {len(data['agents'])}"
        # All expected names should be in response
        returned_names = [n.upper() for n in data["agents"]]
        for expected in EXPECTED_AGENTS:
            assert expected in returned_names, f"Reset response missing agent: {expected}"
        print(f"✅ Reset response includes all 12 agent names: {returned_names}")


class TestAgentUpdate:
    """Tests for PATCH /api/agents/{agent_id} — update system_prompt"""

    def test_patch_agent_system_prompt(self, api_client):
        """PATCH /api/agents/{agent_id} with system_prompt field must work"""
        # First get an agent ID (FORGE)
        agents = api_client.get(f"{BASE_URL}/api/agents").json()
        forge = next((a for a in agents if a.get("name", "").upper() == "FORGE"), None)
        assert forge is not None, "FORGE agent not found"

        agent_id = forge["id"]
        original_prompt = forge.get("system_prompt", "")

        # Update the system_prompt
        new_prompt = original_prompt + "\n# TEST_PATCH_MARKER"
        patch_response = api_client.patch(
            f"{BASE_URL}/api/agents/{agent_id}",
            json={"system_prompt": new_prompt}
        )
        assert patch_response.status_code == 200, \
            f"Expected 200, got {patch_response.status_code}: {patch_response.text[:200]}"
        patch_data = patch_response.json()
        assert "success" in patch_data, f"Missing 'success' in response: {patch_data}"
        assert patch_data["success"] is True

        # Verify the update persisted via GET
        get_response = api_client.get(f"{BASE_URL}/api/agents/{agent_id}")
        assert get_response.status_code == 200
        updated_agent = get_response.json()
        assert "TEST_PATCH_MARKER" in updated_agent.get("system_prompt", ""), \
            "system_prompt update did not persist"

        print(f"✅ PATCH /api/agents/{agent_id} updates system_prompt successfully")

        # Cleanup: restore original prompt
        api_client.patch(
            f"{BASE_URL}/api/agents/{agent_id}",
            json={"system_prompt": original_prompt}
        )

    def test_patch_agent_rejects_invalid_fields(self, api_client):
        """PATCH /api/agents/{agent_id} should return 400 for invalid fields"""
        agents = api_client.get(f"{BASE_URL}/api/agents").json()
        forge = next((a for a in agents if a.get("name", "").upper() == "FORGE"), None)
        assert forge is not None
        agent_id = forge["id"]

        patch_response = api_client.patch(
            f"{BASE_URL}/api/agents/{agent_id}",
            json={"invalid_field_xyz": "some value"}
        )
        assert patch_response.status_code == 400, \
            f"Expected 400 for invalid fields, got {patch_response.status_code}"
        print(f"✅ PATCH /api/agents/{agent_id} rejects invalid fields with 400")

    def test_patch_agent_not_found(self, api_client):
        """PATCH /api/agents/{agent_id} with nonexistent ID should return 404 or handle gracefully"""
        # FastAPI patch won't 404 unless we check - let's at least verify it doesn't crash
        patch_response = api_client.patch(
            f"{BASE_URL}/api/agents/nonexistent-agent-id-999",
            json={"system_prompt": "test"}
        )
        # API might return 200 with no-op or 404 — just not 500
        assert patch_response.status_code != 500, \
            f"Server error on nonexistent agent patch: {patch_response.text[:200]}"
        print(f"✅ PATCH with nonexistent ID handled gracefully: {patch_response.status_code}")


class TestCommanderRouting:
    """Tests for COMMANDER routing rules via system prompt content analysis"""

    def test_commander_knows_game_routing(self, api_client):
        """COMMANDER system prompt must define FULL GAME PROJECT routing"""
        response = api_client.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        commander = next((a for a in agents if a.get("name", "").upper() == "COMMANDER"), None)
        assert commander is not None
        prompt = commander.get("system_prompt", "")

        # Check for game project routing (should deploy 10+ agents)
        assert "NEXUS" in prompt, "COMMANDER should mention NEXUS for game projects"
        assert "TERRA" in prompt, "COMMANDER should mention TERRA for game projects"
        assert "KINETIC" in prompt, "COMMANDER should mention KINETIC for game projects"
        assert "SONIC" in prompt, "COMMANDER should mention SONIC for game projects"
        assert "CHRONICLE" in prompt, "COMMANDER should mention CHRONICLE for game projects"
        assert "VERTEX" in prompt, "COMMANDER should mention VERTEX for game projects"
        print(f"✅ COMMANDER knows all game-specific agents: NEXUS, TERRA, KINETIC, SONIC, CHRONICLE, VERTEX")

    def test_commander_knows_web_routing(self, api_client):
        """COMMANDER system prompt must define WEB APP routing (ATLAS+FORGE+PRISM+SENTINEL+PROBE)"""
        response = api_client.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        commander = next((a for a in agents if a.get("name", "").upper() == "COMMANDER"), None)
        assert commander is not None
        prompt = commander.get("system_prompt", "")

        # Web routing should include these 5 agents
        web_agents = ["ATLAS", "FORGE", "PRISM", "SENTINEL", "PROBE"]
        for agent in web_agents:
            assert agent in prompt, f"COMMANDER prompt missing web routing agent: {agent}"
        print(f"✅ COMMANDER knows WEB APP routing: ATLAS+FORGE+PRISM+SENTINEL+PROBE")

    def test_commander_delegation_format_present(self, api_client):
        """COMMANDER system prompt must include [DELEGATE:AGENT_NAME] format instruction"""
        response = api_client.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        agents = response.json()
        commander = next((a for a in agents if a.get("name", "").upper() == "COMMANDER"), None)
        assert commander is not None
        prompt = commander.get("system_prompt", "")

        assert "[DELEGATE:" in prompt, "Missing [DELEGATE:AGENT_NAME] format in COMMANDER prompt"
        assert "[/DELEGATE]" in prompt, "Missing [/DELEGATE] closing tag in COMMANDER prompt"
        print(f"✅ COMMANDER prompt has proper [DELEGATE:AGENT_NAME]...[/DELEGATE] format")


class TestDelegateStreamAllAgents:
    """Test that /api/delegate/stream works for key agents"""

    def test_stream_works_for_atlas(self, api_client):
        """ATLAS agent can receive a streaming delegation"""
        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Brief system overview for a simple game",
            "delegate_to": "ATLAS"
        }, stream=True, timeout=120)
        assert response.status_code == 200, f"Expected 200 for ATLAS, got {response.status_code}"
        content_type = response.headers.get("content-type", "")
        assert "text/event-stream" in content_type
        # Read the start event
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("data: "):
                data = json.loads(line[6:])
                if data.get("type") == "start":
                    assert data["agent"]["name"].upper() == "ATLAS"
                    break
        response.close()
        print(f"✅ /api/delegate/stream works for ATLAS")

    def test_stream_works_for_sentinel(self, api_client):
        """SENTINEL agent can receive a streaming delegation"""
        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Quick code review of a simple function",
            "delegate_to": "SENTINEL"
        }, stream=True, timeout=120)
        assert response.status_code == 200, f"Expected 200 for SENTINEL, got {response.status_code}"
        response.close()
        print(f"✅ /api/delegate/stream works for SENTINEL")

    def test_stream_works_for_prism(self, api_client):
        """PRISM agent can receive a streaming delegation"""
        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Quick UI design note",
            "delegate_to": "PRISM"
        }, stream=True, timeout=120)
        assert response.status_code == 200, f"Expected 200 for PRISM, got {response.status_code}"
        response.close()
        print(f"✅ /api/delegate/stream works for PRISM")

    def test_stream_works_for_terra(self, api_client):
        """TERRA agent (game-only) can receive a streaming delegation"""
        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Brief level overview",
            "delegate_to": "TERRA"
        }, stream=True, timeout=120)
        assert response.status_code == 200, f"Expected 200 for TERRA, got {response.status_code}"
        response.close()
        print(f"✅ /api/delegate/stream works for TERRA")

    def test_stream_works_for_nexus(self, api_client):
        """NEXUS agent (game designer) can receive a streaming delegation"""
        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Brief game design note",
            "delegate_to": "NEXUS"
        }, stream=True, timeout=120)
        assert response.status_code == 200, f"Expected 200 for NEXUS, got {response.status_code}"
        response.close()
        print(f"✅ /api/delegate/stream works for NEXUS")

    def test_stream_works_for_chronicle(self, api_client):
        """CHRONICLE agent (narrative) can receive a streaming delegation"""
        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Brief narrative note",
            "delegate_to": "CHRONICLE"
        }, stream=True, timeout=120)
        assert response.status_code == 200, f"Expected 200 for CHRONICLE, got {response.status_code}"
        response.close()
        print(f"✅ /api/delegate/stream works for CHRONICLE")

    def test_stream_works_for_vertex(self, api_client):
        """VERTEX agent (tech artist) can receive a streaming delegation"""
        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Brief VFX note",
            "delegate_to": "VERTEX"
        }, stream=True, timeout=120)
        assert response.status_code == 200, f"Expected 200 for VERTEX, got {response.status_code}"
        response.close()
        print(f"✅ /api/delegate/stream works for VERTEX")

    def test_stream_works_for_kinetic(self, api_client):
        """KINETIC agent (animator) can receive a streaming delegation"""
        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Brief animation note",
            "delegate_to": "KINETIC"
        }, stream=True, timeout=120)
        assert response.status_code == 200, f"Expected 200 for KINETIC, got {response.status_code}"
        response.close()
        print(f"✅ /api/delegate/stream works for KINETIC")

    def test_stream_works_for_sonic(self, api_client):
        """SONIC agent (audio) can receive a streaming delegation"""
        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Brief audio note",
            "delegate_to": "SONIC"
        }, stream=True, timeout=120)
        assert response.status_code == 200, f"Expected 200 for SONIC, got {response.status_code}"
        response.close()
        print(f"✅ /api/delegate/stream works for SONIC")

    def test_stream_works_for_probe(self, api_client):
        """PROBE agent (tester) can receive a streaming delegation"""
        response = api_client.post(f"{BASE_URL}/api/delegate/stream", json={
            "project_id": TEST_PROJECT_ID,
            "message": "TEST: Brief test case note",
            "delegate_to": "PROBE"
        }, stream=True, timeout=120)
        assert response.status_code == 200, f"Expected 200 for PROBE, got {response.status_code}"
        response.close()
        print(f"✅ /api/delegate/stream works for PROBE")
