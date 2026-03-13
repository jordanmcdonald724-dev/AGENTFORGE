"""
AgentForge v3.0 Backend Tests
Testing: Simulation Mode, War Room, Autonomous Builds, Open World Systems
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_PROJECT_ID = "0e16897f-e287-402d-a7bc-aa57ba9c294f"


class TestAPIHealth:
    """Basic health and version checks"""
    
    def test_api_root_version(self):
        """API root should return v3.0.0 with new features"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "3.0.0"
        assert "simulation_mode" in data["features"]
        assert "war_room" in data["features"]
        assert "autonomous_builds" in data["features"]
        assert "open_world_systems" in data["features"]
    
    def test_health_endpoint(self):
        """Health check should return healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestOpenWorldSystems:
    """Open World Game Systems endpoint tests"""
    
    def test_get_open_world_systems_returns_15_systems(self):
        """GET /api/systems/open-world should return 15 game systems"""
        response = requests.get(f"{BASE_URL}/api/systems/open-world")
        assert response.status_code == 200
        systems = response.json()
        assert isinstance(systems, list)
        assert len(systems) == 15
        
        # Verify system structure
        expected_systems = ["terrain", "npc_population", "quest_system", "vehicle_system", 
                          "day_night_cycle", "combat_system", "crafting_system", "economy_system",
                          "stealth_system", "mount_system", "building_system", "skill_tree",
                          "fast_travel", "photo_mode", "multiplayer"]
        
        system_ids = [s["id"] for s in systems]
        for expected in expected_systems:
            assert expected in system_ids, f"Missing system: {expected}"
        
        # Verify system properties
        for system in systems:
            assert "id" in system
            assert "name" in system
            assert "description" in system
            assert "files_estimate" in system
            assert "time_estimate_minutes" in system
            assert "dependencies" in system
            assert "subsystems" in system


class TestBuildStages:
    """Build Stages endpoint tests"""
    
    def test_unreal_build_stages_returns_8_stages(self):
        """GET /api/build-stages/unreal should return 8 build stages"""
        response = requests.get(f"{BASE_URL}/api/build-stages/unreal")
        assert response.status_code == 200
        stages = response.json()
        assert isinstance(stages, list)
        assert len(stages) == 8
        
        # Verify stage names
        expected_stages = ["Project Setup", "Core Framework", "Game Systems", "AI & NPCs",
                         "UI/UX", "World Building", "Audio Integration", "Polish & Testing"]
        stage_names = [s["name"] for s in stages]
        for expected in expected_stages:
            assert expected in stage_names
        
        # Verify stage structure
        for stage in stages:
            assert "name" in stage
            assert "duration_minutes" in stage
            assert "tasks" in stage
            assert isinstance(stage["tasks"], list)
    
    def test_unity_build_stages_returns_8_stages(self):
        """GET /api/build-stages/unity should return 8 build stages"""
        response = requests.get(f"{BASE_URL}/api/build-stages/unity")
        assert response.status_code == 200
        stages = response.json()
        assert isinstance(stages, list)
        assert len(stages) == 8


class TestSimulation:
    """Simulation Mode endpoint tests"""
    
    def test_simulate_with_no_dependencies_returns_full_result(self):
        """POST /api/simulate with systems having no dependencies should return feasibility 100"""
        response = requests.post(f"{BASE_URL}/api/simulate", json={
            "project_id": TEST_PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "include_systems": ["terrain", "day_night_cycle", "skill_tree", "photo_mode"]
        })
        assert response.status_code == 200
        data = response.json()
        
        # Verify simulation result structure
        assert "id" in data
        assert "project_id" in data
        assert data["project_id"] == TEST_PROJECT_ID
        assert "estimated_build_time" in data
        assert "estimated_build_minutes" in data
        assert "file_count" in data
        assert "total_size_kb" in data
        assert "warnings" in data
        assert "architecture_summary" in data
        assert "phases" in data
        assert "feasibility_score" in data
        assert "ready_to_build" in data
        
        # With no dependencies missing, should be ready to build
        assert data["feasibility_score"] == 100
        assert data["ready_to_build"] == True
        assert len(data["warnings"]) == 0
    
    def test_simulate_with_missing_dependencies_returns_warnings(self):
        """POST /api/simulate with missing dependencies should return warnings"""
        response = requests.post(f"{BASE_URL}/api/simulate", json={
            "project_id": TEST_PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "include_systems": ["npc_population", "combat_system", "crafting_system"]
        })
        assert response.status_code == 200
        data = response.json()
        
        # Should have warnings for missing dependencies
        assert len(data["warnings"]) > 0
        assert data["high_severity_warnings"] > 0
        assert data["feasibility_score"] < 100
        assert data["ready_to_build"] == False
        
        # Verify warning structure
        for warning in data["warnings"]:
            assert "type" in warning
            assert "severity" in warning
            assert "message" in warning
            assert "suggestion" in warning
    
    def test_simulate_returns_required_assets(self):
        """POST /api/simulate should return required assets per system"""
        response = requests.post(f"{BASE_URL}/api/simulate", json={
            "project_id": TEST_PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "include_systems": ["terrain"]
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "required_assets" in data
        assert len(data["required_assets"]) > 0
        
        # Verify asset structure
        for asset in data["required_assets"]:
            assert "system" in asset
            assert "assets" in asset
            assert "type" in asset


class TestAutonomousBuilds:
    """Autonomous Build endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def cleanup_builds(self):
        """Clean up test builds before and after each test"""
        # Cancel any existing builds before test
        current = requests.get(f"{BASE_URL}/api/builds/{TEST_PROJECT_ID}/current")
        if current.status_code == 200 and current.json():
            build_id = current.json().get("id")
            if build_id:
                requests.post(f"{BASE_URL}/api/builds/{build_id}/cancel")
        yield
        # Cancel any running builds after test
        current = requests.get(f"{BASE_URL}/api/builds/{TEST_PROJECT_ID}/current")
        if current.status_code == 200 and current.json():
            build_id = current.json().get("id")
            if build_id:
                requests.post(f"{BASE_URL}/api/builds/{build_id}/cancel")
    
    def test_start_build_creates_build_with_stages(self):
        """POST /api/builds/start should create a new build with stages"""
        response = requests.post(f"{BASE_URL}/api/builds/start", json={
            "project_id": TEST_PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "systems_to_build": ["terrain", "day_night_cycle"],
            "estimated_hours": 2
        })
        assert response.status_code == 200
        data = response.json()
        
        # Verify build structure
        assert "id" in data
        assert data["project_id"] == TEST_PROJECT_ID
        assert data["status"] == "queued"
        assert data["build_type"] == "full"
        assert data["target_engine"] == "unreal"
        assert "stages" in data
        assert len(data["stages"]) == 8
        assert data["total_stages"] == 8
        assert data["progress_percent"] == 0
        
        # Verify stage structure
        for stage in data["stages"]:
            assert "name" in stage
            assert "status" in stage
            assert stage["status"] == "pending"
    
    def test_get_current_build(self):
        """GET /api/builds/{project_id}/current should return current build"""
        # First create a build
        requests.post(f"{BASE_URL}/api/builds/start", json={
            "project_id": TEST_PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "systems_to_build": ["terrain"],
            "estimated_hours": 1
        })
        
        response = requests.get(f"{BASE_URL}/api/builds/{TEST_PROJECT_ID}/current")
        assert response.status_code == 200
        data = response.json()
        
        assert data is not None
        assert data["project_id"] == TEST_PROJECT_ID
    
    def test_pause_build(self):
        """POST /api/builds/{build_id}/pause should pause the build"""
        # First create a build
        create_response = requests.post(f"{BASE_URL}/api/builds/start", json={
            "project_id": TEST_PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "systems_to_build": ["terrain"],
            "estimated_hours": 1
        })
        build_id = create_response.json()["id"]
        
        response = requests.post(f"{BASE_URL}/api/builds/{build_id}/pause")
        assert response.status_code == 200
        assert response.json()["success"] == True
        
        # Verify build is paused
        current = requests.get(f"{BASE_URL}/api/builds/{TEST_PROJECT_ID}/current")
        assert current.json()["status"] == "paused"
    
    def test_resume_build(self):
        """POST /api/builds/{build_id}/resume should resume the build"""
        # First create and pause a build
        create_response = requests.post(f"{BASE_URL}/api/builds/start", json={
            "project_id": TEST_PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "systems_to_build": ["terrain"],
            "estimated_hours": 1
        })
        build_id = create_response.json()["id"]
        requests.post(f"{BASE_URL}/api/builds/{build_id}/pause")
        
        response = requests.post(f"{BASE_URL}/api/builds/{build_id}/resume")
        assert response.status_code == 200
        assert response.json()["success"] == True
        
        # Verify build is running
        current = requests.get(f"{BASE_URL}/api/builds/{TEST_PROJECT_ID}/current")
        assert current.json()["status"] == "running"


class TestWarRoom:
    """War Room endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def cleanup_war_room(self):
        """Clean up test war room messages after each test"""
        yield
        requests.delete(f"{BASE_URL}/api/war-room/{TEST_PROJECT_ID}")
    
    def test_get_war_room_messages(self):
        """GET /api/war-room/{project_id} should return messages"""
        response = requests.get(f"{BASE_URL}/api/war-room/{TEST_PROJECT_ID}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_post_war_room_message(self):
        """POST /api/war-room/message should create a message"""
        response = requests.post(
            f"{BASE_URL}/api/war-room/message",
            params={
                "project_id": TEST_PROJECT_ID,
                "from_agent": "COMMANDER",
                "content": "Test war room message from pytest",
                "message_type": "discussion"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify message structure
        assert "id" in data
        assert data["project_id"] == TEST_PROJECT_ID
        assert data["from_agent"] == "COMMANDER"
        assert data["content"] == "Test war room message from pytest"
        assert data["message_type"] == "discussion"
        assert "timestamp" in data
    
    def test_post_war_room_handoff_message(self):
        """POST /api/war-room/message with handoff type"""
        response = requests.post(
            f"{BASE_URL}/api/war-room/message",
            params={
                "project_id": TEST_PROJECT_ID,
                "from_agent": "ATLAS",
                "to_agent": "FORGE",
                "content": "Architecture ready, passing to you for implementation",
                "message_type": "handoff"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["from_agent"] == "ATLAS"
        assert data["to_agent"] == "FORGE"
        assert data["message_type"] == "handoff"
    
    def test_clear_war_room(self):
        """DELETE /api/war-room/{project_id} should clear messages"""
        # First add a message
        requests.post(
            f"{BASE_URL}/api/war-room/message",
            params={
                "project_id": TEST_PROJECT_ID,
                "from_agent": "COMMANDER",
                "content": "Message to be deleted"
            }
        )
        
        # Then clear
        response = requests.delete(f"{BASE_URL}/api/war-room/{TEST_PROJECT_ID}")
        assert response.status_code == 200
        assert response.json()["success"] == True
        
        # Verify cleared
        messages = requests.get(f"{BASE_URL}/api/war-room/{TEST_PROJECT_ID}")
        assert len(messages.json()) == 0


class TestSimulationIntegration:
    """Integration tests for simulation with builds"""
    
    def test_simulation_phases_match_build_stages(self):
        """Simulation phases should match build stages structure"""
        # Get simulation result
        sim_response = requests.post(f"{BASE_URL}/api/simulate", json={
            "project_id": TEST_PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "include_systems": ["terrain"]
        })
        sim_data = sim_response.json()
        
        # Get build stages
        stages_response = requests.get(f"{BASE_URL}/api/build-stages/unreal")
        stages_data = stages_response.json()
        
        # Verify phases match stages
        assert len(sim_data["phases"]) == len(stages_data)
        for i, phase in enumerate(sim_data["phases"]):
            assert phase["name"] == stages_data[i]["name"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
