"""
Test suite for iteration_25:
- WorkspaceDialogs extraction verification
- Auto-expand logic dependencies (files endpoint)
- Simulate endpoint
- Pipeline phasing structure
- pipelineAgentStatus dependencies
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
PROJECT_ID = "878a623f-111e-45df-a837-7821bace9c1a"


@pytest.fixture
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ── 1. Project exists ──────────────────────────────────────────────────────────

class TestProjectExists:
    """Verify the OceanMapSurvivalGame project is accessible"""

    def test_project_loads(self, client):
        res = client.get(f"{BASE_URL}/api/projects/{PROJECT_ID}")
        assert res.status_code == 200
        data = res.json()
        assert data.get("id") == PROJECT_ID
        assert "name" in data
        print(f"Project name: {data['name']}, phase: {data.get('phase')}, type: {data.get('type')}")

    def test_project_has_expected_fields(self, client):
        res = client.get(f"{BASE_URL}/api/projects/{PROJECT_ID}")
        assert res.status_code == 200
        data = res.json()
        assert "name" in data
        assert "type" in data
        assert "phase" in data
        print(f"Project type: {data.get('type')}")


# ── 2. Files endpoint (auto-expand depends on this) ────────────────────────────

class TestFilesAutoExpand:
    """Verify files endpoint returns files with nested paths for auto-expand testing"""

    def test_files_endpoint_returns_list(self, client):
        res = client.get(f"{BASE_URL}/api/files?project_id={PROJECT_ID}")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        print(f"Total files: {len(data)}")

    def test_files_have_filepath(self, client):
        res = client.get(f"{BASE_URL}/api/files?project_id={PROJECT_ID}")
        assert res.status_code == 200
        data = res.json()
        if len(data) > 0:
            # Every file should have a filepath
            for f in data:
                assert "filepath" in f, f"File missing filepath: {f}"
            # Check for nested paths (for auto-expand to work)
            deep_paths = [f["filepath"] for f in data if f["filepath"].count("/") >= 2]
            print(f"Deep nested files (>= 2 levels): {len(deep_paths)}")
            for p in deep_paths[:5]:
                print(f"  - {p}")
        else:
            pytest.skip("No files in project - auto-expand not testable")

    def test_files_with_abyssal_shores_paths(self, client):
        """Check for the specific AbyssalShores/ deep path structure"""
        res = client.get(f"{BASE_URL}/api/files?project_id={PROJECT_ID}")
        assert res.status_code == 200
        data = res.json()
        abyssal_files = [f for f in data if "AbyssalShores" in f.get("filepath", "")]
        print(f"AbyssalShores files: {len(abyssal_files)}")
        for f in abyssal_files:
            print(f"  - {f['filepath']}")
        # If there are AbyssalShores files, verify the path depth
        if abyssal_files:
            deep = [f for f in abyssal_files if f["filepath"].count("/") >= 3]
            assert len(deep) > 0, "Expected deeply nested AbyssalShores paths (>= 3 levels)"
            print(f"Deep AbyssalShores files: {[f['filepath'] for f in deep]}")


# ── 3. Simulation endpoint ─────────────────────────────────────────────────────

class TestSimulationEndpoint:
    """Test the /api/simulate endpoint used by WorkspaceDialogs"""

    def test_simulate_single_system(self, client):
        res = client.post(f"{BASE_URL}/api/simulate", json={
            "project_id": PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "include_systems": ["terrain"]
        })
        assert res.status_code == 200
        data = res.json()
        # Check required response fields
        assert "estimated_build_time" in data, f"Missing estimated_build_time: {data}"
        assert "file_count" in data, f"Missing file_count: {data}"
        assert "feasibility_score" in data, f"Missing feasibility_score: {data}"
        assert "ready_to_build" in data, f"Missing ready_to_build: {data}"
        print(f"Simulation result: build_time={data.get('estimated_build_time')}, "
              f"files={data.get('file_count')}, feasibility={data.get('feasibility_score')}%")

    def test_simulate_multiple_systems(self, client):
        res = client.post(f"{BASE_URL}/api/simulate", json={
            "project_id": PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "include_systems": ["terrain", "combat_system", "npc_population"]
        })
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data.get("feasibility_score"), (int, float))
        assert isinstance(data.get("file_count"), (int, float))
        print(f"Multi-system simulation: {data.get('file_count')} files, "
              f"{data.get('feasibility_score')}% feasibility")

    def test_simulate_unity_engine(self, client):
        res = client.post(f"{BASE_URL}/api/simulate", json={
            "project_id": PROJECT_ID,
            "build_type": "full",
            "target_engine": "unity",
            "include_systems": ["terrain"]
        })
        assert res.status_code == 200
        data = res.json()
        assert "estimated_build_time" in data
        print(f"Unity simulation: {data.get('estimated_build_time')}")

    def test_simulate_returns_warnings_field(self, client):
        res = client.post(f"{BASE_URL}/api/simulate", json={
            "project_id": PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "include_systems": ["terrain", "combat_system", "npc_population",
                                "vehicle_system", "multiplayer", "quest_system"]
        })
        assert res.status_code == 200
        data = res.json()
        assert "warnings" in data, f"Missing warnings field: {data}"
        print(f"Warnings count: {len(data.get('warnings', []))}")

    def test_simulate_returns_architecture_summary(self, client):
        res = client.post(f"{BASE_URL}/api/simulate", json={
            "project_id": PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "include_systems": ["terrain"]
        })
        assert res.status_code == 200
        data = res.json()
        assert "architecture_summary" in data
        print(f"Architecture summary present: {bool(data.get('architecture_summary'))}")


# ── 4. Open-world systems endpoint ────────────────────────────────────────────

class TestOpenWorldSystems:
    """Verify /api/systems/open-world returns systems for the simulation dialog grid"""

    def test_open_world_systems_loads(self, client):
        res = client.get(f"{BASE_URL}/api/systems/open-world")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one open-world system"
        print(f"Open world systems: {len(data)}")

    def test_systems_have_required_fields(self, client):
        res = client.get(f"{BASE_URL}/api/systems/open-world")
        assert res.status_code == 200
        data = res.json()
        required_fields = ["id", "name", "description", "files_estimate", "time_estimate_minutes"]
        for system in data:
            for field in required_fields:
                assert field in system, f"System {system.get('id')} missing '{field}'"
        print(f"All {len(data)} systems have required fields")

    def test_systems_include_terrain_and_combat(self, client):
        res = client.get(f"{BASE_URL}/api/systems/open-world")
        assert res.status_code == 200
        data = res.json()
        system_ids = [s["id"] for s in data]
        assert "terrain" in system_ids, f"terrain not found in systems: {system_ids}"
        assert "combat_system" in system_ids, f"combat_system not found in systems: {system_ids}"
        print(f"System IDs: {system_ids}")


# ── 5. Messages endpoint (pipeline output) ────────────────────────────────────

class TestMessagesEndpoint:
    """Verify messages can be retrieved for pipeline status"""

    def test_messages_returns_list(self, client):
        res = client.get(f"{BASE_URL}/api/messages?project_id={PROJECT_ID}&limit=500")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        print(f"Total messages in project: {len(data)}")

    def test_messages_with_limit(self, client):
        res = client.get(f"{BASE_URL}/api/messages?project_id={PROJECT_ID}&limit=10")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) <= 10
        print(f"Messages with limit=10: {len(data)}")


# ── 6. Agents endpoint (used in pipeline) ─────────────────────────────────────

class TestAgentsEndpoint:
    """Verify agents endpoint - required for pipeline delegation"""

    def test_agents_loads(self, client):
        res = client.get(f"{BASE_URL}/api/agents")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) > 0
        print(f"Total agents: {len(data)}")

    def test_pipeline_agents_present(self, client):
        """Verify NEXUS, ATLAS, FORGE, SENTINEL, PROBE agents exist"""
        res = client.get(f"{BASE_URL}/api/agents")
        assert res.status_code == 200
        data = res.json()
        agent_names = [a["name"].upper() for a in data]
        expected_pipeline_agents = ["NEXUS", "ATLAS", "FORGE", "SENTINEL", "PROBE"]
        missing = [a for a in expected_pipeline_agents if a not in agent_names]
        assert len(missing) == 0, f"Missing pipeline agents: {missing}. Available: {agent_names}"
        print(f"All pipeline agents present: {expected_pipeline_agents}")

    def test_design_agents_exist(self, client):
        """NEXUS and ATLAS must be in agents list for phase-1 design phase"""
        res = client.get(f"{BASE_URL}/api/agents")
        assert res.status_code == 200
        data = res.json()
        agent_names = [a["name"].upper() for a in data]
        assert "NEXUS" in agent_names, f"NEXUS not in agents: {agent_names}"
        assert "ATLAS" in agent_names, f"ATLAS not in agents: {agent_names}"

    def test_builder_agents_exist(self, client):
        """FORGE, TERRA, PRISM etc must exist for phase-2 parallel phase"""
        res = client.get(f"{BASE_URL}/api/agents")
        assert res.status_code == 200
        data = res.json()
        agent_names = [a["name"].upper() for a in data]
        builder_agents = ["FORGE", "TERRA", "PRISM"]
        missing = [a for a in builder_agents if a not in agent_names]
        assert len(missing) == 0, f"Missing builder agents: {missing}"

    def test_review_agents_exist(self, client):
        """SENTINEL and PROBE must exist for phase-3 review phase"""
        res = client.get(f"{BASE_URL}/api/agents")
        assert res.status_code == 200
        data = res.json()
        agent_names = [a["name"].upper() for a in data]
        assert "SENTINEL" in agent_names
        assert "PROBE" in agent_names
