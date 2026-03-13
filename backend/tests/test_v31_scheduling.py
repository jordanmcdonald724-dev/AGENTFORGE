"""
AgentForge v3.1 - Build Scheduling Tests
Testing:
- Extended build time (12+ hours / 930 minutes minimum)
- Scheduled builds with scheduled_at parameter
- GET /api/builds/scheduled endpoint
- POST /api/builds/{build_id}/start-scheduled endpoint
- War Room scheduled build messages from COMMANDER
"""

import pytest
import requests
import os
import time
from datetime import datetime, timedelta, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_PROJECT_ID = "0e16897f-e287-402d-a7bc-aa57ba9c294f"

class TestBuildStagesExtended:
    """Tests for extended build time (15+ hours)"""
    
    def test_unreal_stages_count(self):
        """GET /api/build-stages/unreal - should return 8 stages"""
        response = requests.get(f"{BASE_URL}/api/build-stages/unreal")
        assert response.status_code == 200
        stages = response.json()
        assert len(stages) == 8, f"Expected 8 stages, got {len(stages)}"
        print(f"✅ Unreal has {len(stages)} build stages")
    
    def test_unreal_stages_total_time_15_hours(self):
        """GET /api/build-stages/unreal - should total 15+ hours (930+ minutes)"""
        response = requests.get(f"{BASE_URL}/api/build-stages/unreal")
        assert response.status_code == 200
        stages = response.json()
        
        total_minutes = sum(stage.get("duration_minutes", 0) for stage in stages)
        assert total_minutes >= 930, f"Expected at least 930 minutes (15.5h), got {total_minutes} minutes"
        
        hours = total_minutes // 60
        mins = total_minutes % 60
        print(f"✅ Unreal build total time: {total_minutes} minutes ({hours}h {mins}m)")
    
    def test_unity_stages_count(self):
        """GET /api/build-stages/unity - should return 8 stages"""
        response = requests.get(f"{BASE_URL}/api/build-stages/unity")
        assert response.status_code == 200
        stages = response.json()
        assert len(stages) == 8, f"Expected 8 stages, got {len(stages)}"
        print(f"✅ Unity has {len(stages)} build stages")
    
    def test_unity_stages_total_time_15_hours(self):
        """GET /api/build-stages/unity - should total 15+ hours (930+ minutes)"""
        response = requests.get(f"{BASE_URL}/api/build-stages/unity")
        assert response.status_code == 200
        stages = response.json()
        
        total_minutes = sum(stage.get("duration_minutes", 0) for stage in stages)
        assert total_minutes >= 930, f"Expected at least 930 minutes (15.5h), got {total_minutes} minutes"
        
        hours = total_minutes // 60
        mins = total_minutes % 60
        print(f"✅ Unity build total time: {total_minutes} minutes ({hours}h {mins}m)")


class TestScheduledBuilds:
    """Tests for build scheduling (v3.1 feature)"""
    
    def test_create_scheduled_build(self):
        """POST /api/builds/start with scheduled_at - creates scheduled build"""
        # First, check for existing running/scheduled builds and cancel them
        current_build = requests.get(f"{BASE_URL}/api/builds/{TEST_PROJECT_ID}/current").json()
        if current_build and current_build.get("status") in ["running", "scheduled"]:
            requests.post(f"{BASE_URL}/api/builds/{current_build['id']}/cancel")
            time.sleep(1)
        
        # Schedule build for 1 hour from now
        scheduled_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        
        response = requests.post(f"{BASE_URL}/api/builds/start", json={
            "project_id": TEST_PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "systems_to_build": ["terrain", "day_night_cycle"],
            "scheduled_at": scheduled_time
        })
        
        assert response.status_code == 200, f"Failed to create scheduled build: {response.text}"
        build = response.json()
        
        assert build["status"] == "scheduled", f"Expected status 'scheduled', got '{build['status']}'"
        assert build.get("scheduled_at") is not None, "scheduled_at should be set"
        assert build["total_stages"] == 8, f"Expected 8 stages, got {build['total_stages']}"
        
        print(f"✅ Created scheduled build {build['id']} for {build['scheduled_at']}")
        
        # Store build ID for other tests
        TestScheduledBuilds.test_build_id = build["id"]
        return build["id"]
    
    def test_get_scheduled_builds(self):
        """GET /api/builds/scheduled - returns builds ready to start"""
        response = requests.get(f"{BASE_URL}/api/builds/scheduled")
        assert response.status_code == 200
        
        builds = response.json()
        # This returns builds that are past their scheduled time and ready to start
        print(f"✅ GET /api/builds/scheduled returns {len(builds)} ready builds")
    
    def test_start_scheduled_build(self):
        """POST /api/builds/{build_id}/start-scheduled - starts a scheduled build"""
        # Get current build
        response = requests.get(f"{BASE_URL}/api/builds/{TEST_PROJECT_ID}/current")
        assert response.status_code == 200
        
        build = response.json()
        if not build or build.get("status") != "scheduled":
            # Create a new scheduled build for this test
            scheduled_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            create_resp = requests.post(f"{BASE_URL}/api/builds/start", json={
                "project_id": TEST_PROJECT_ID,
                "build_type": "full",
                "target_engine": "unreal",
                "systems_to_build": ["terrain"],
                "scheduled_at": scheduled_time
            })
            if create_resp.status_code != 200:
                pytest.skip("Could not create scheduled build for test")
            build = create_resp.json()
        
        build_id = build["id"]
        
        # Start the scheduled build
        start_response = requests.post(f"{BASE_URL}/api/builds/{build_id}/start-scheduled")
        assert start_response.status_code == 200, f"Failed to start scheduled build: {start_response.text}"
        
        result = start_response.json()
        assert result.get("success") == True, f"Expected success: true, got {result}"
        
        print(f"✅ Started scheduled build {build_id}")
        
        # Verify build is now running
        time.sleep(1)
        verify_response = requests.get(f"{BASE_URL}/api/builds/{TEST_PROJECT_ID}/current")
        current_build = verify_response.json()
        assert current_build["status"] in ["running", "completed", "partial"], f"Build should be running, got {current_build['status']}"
        
        print(f"✅ Build status is now: {current_build['status']}")
        
        # Cancel the build for cleanup
        requests.post(f"{BASE_URL}/api/builds/{build_id}/cancel")
    
    def test_scheduled_build_war_room_message(self):
        """War Room shows COMMANDER scheduled build message"""
        # Cancel any existing builds first
        current_build = requests.get(f"{BASE_URL}/api/builds/{TEST_PROJECT_ID}/current").json()
        if current_build and current_build.get("status") in ["running", "scheduled"]:
            requests.post(f"{BASE_URL}/api/builds/{current_build['id']}/cancel")
            time.sleep(1)
        
        # Create a new scheduled build
        scheduled_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        create_resp = requests.post(f"{BASE_URL}/api/builds/start", json={
            "project_id": TEST_PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "systems_to_build": ["terrain", "day_night_cycle"],
            "scheduled_at": scheduled_time
        })
        assert create_resp.status_code == 200, f"Failed to create build: {create_resp.text}"
        build = create_resp.json()
        
        # Check war room for COMMANDER message
        time.sleep(1)
        response = requests.get(f"{BASE_URL}/api/war-room/{TEST_PROJECT_ID}")
        assert response.status_code == 200
        
        messages = response.json()
        commander_messages = [m for m in messages if m.get("from_agent") == "COMMANDER" and "SCHEDULED" in m.get("content", "")]
        
        assert len(commander_messages) > 0, "Expected COMMANDER scheduled message in war room"
        
        latest_scheduled = commander_messages[-1]
        assert "⏰" in latest_scheduled["content"], "Message should contain clock emoji"
        assert "SCHEDULED" in latest_scheduled["content"], "Message should mention 'SCHEDULED'"
        assert "15h" in latest_scheduled["content"] or "930" in latest_scheduled["content"], "Message should mention build time"
        
        print(f"✅ War Room COMMANDER message: {latest_scheduled['content'][:100]}...")
        
        # Cleanup
        requests.post(f"{BASE_URL}/api/builds/{build['id']}/cancel")


class TestBuildEstimatedCompletion:
    """Tests for build estimated completion time"""
    
    def test_build_estimated_completion_format(self):
        """Build should have estimated_completion in '15h 30m' format"""
        # Cancel any existing builds first
        current_build = requests.get(f"{BASE_URL}/api/builds/{TEST_PROJECT_ID}/current").json()
        if current_build and current_build.get("status") in ["running", "scheduled"]:
            requests.post(f"{BASE_URL}/api/builds/{current_build['id']}/cancel")
            time.sleep(1)
        
        # Create a new build
        response = requests.post(f"{BASE_URL}/api/builds/start", json={
            "project_id": TEST_PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "systems_to_build": ["terrain"]
        })
        
        if response.status_code != 200:
            pytest.skip("Could not create build for test")
        
        build = response.json()
        
        # Check estimated_completion
        estimated = build.get("estimated_completion", "")
        assert estimated, "estimated_completion should be set"
        assert "h" in estimated, f"estimated_completion should be in 'Xh Ym' format, got '{estimated}'"
        
        # Parse hours
        parts = estimated.split("h")
        hours = int(parts[0].strip())
        assert hours >= 15, f"Expected at least 15 hours, got {hours}"
        
        print(f"✅ Build estimated completion: {estimated}")
        
        # Cleanup
        requests.post(f"{BASE_URL}/api/builds/{build['id']}/cancel")


class TestScheduledBuildCancelStart:
    """Tests for scheduled build start/cancel operations"""
    
    def test_cannot_start_non_scheduled_build(self):
        """POST /api/builds/{build_id}/start-scheduled fails for non-scheduled builds"""
        # Create a normal (non-scheduled) build
        current_build = requests.get(f"{BASE_URL}/api/builds/{TEST_PROJECT_ID}/current").json()
        if current_build and current_build.get("status") in ["running", "scheduled"]:
            requests.post(f"{BASE_URL}/api/builds/{current_build['id']}/cancel")
            time.sleep(1)
        
        # Create immediate build (not scheduled)
        create_resp = requests.post(f"{BASE_URL}/api/builds/start", json={
            "project_id": TEST_PROJECT_ID,
            "build_type": "full",
            "target_engine": "unreal",
            "systems_to_build": ["terrain"]
            # No scheduled_at means immediate start
        })
        
        if create_resp.status_code != 200:
            pytest.skip("Could not create build for test")
        
        build = create_resp.json()
        build_id = build["id"]
        
        # Now try to use start-scheduled on this build (should fail if not scheduled)
        # Wait for it to start running
        time.sleep(2)
        
        start_resp = requests.post(f"{BASE_URL}/api/builds/{build_id}/start-scheduled")
        
        # Should return error if build is already running
        if build["status"] != "scheduled":
            assert start_resp.status_code == 400, "Should fail for non-scheduled build"
            print(f"✅ Correctly rejected start-scheduled for non-scheduled build")
        
        # Cleanup
        requests.post(f"{BASE_URL}/api/builds/{build_id}/cancel")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
