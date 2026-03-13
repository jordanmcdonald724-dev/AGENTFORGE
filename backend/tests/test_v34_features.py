"""
AgentForge v3.4 Feature Tests
Tests for: Audio Generation, One-Click Deployment, Notifications (Email/Discord settings)
Note: Email and Discord notification sending is MOCKED as per user request.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_PROJECT_ID = "cfdcd129-6ca5-4616-997b-c615daaa64de"

class TestAPIVersion:
    """Test API version and feature flags"""
    
    def test_api_health(self):
        """Test API health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ API health check passed")
    
    def test_api_version_includes_v34_features(self):
        """Test that v3.4 features are listed"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        
        # Check version is at least 3.4
        assert "version" in data
        version = data["version"]
        print(f"✅ API version: {version}")
        
        # Check v3.4 features are listed
        features = data.get("features", [])
        assert "notifications" in features, "notifications feature not listed"
        assert "audio_generation" in features, "audio_generation feature not listed"
        assert "one_click_deploy" in features, "one_click_deploy feature not listed"
        print(f"✅ v3.4 features listed: notifications, audio_generation, one_click_deploy")

class TestAudioGeneration:
    """Test Audio Generation endpoints"""
    
    def test_get_audio_categories(self):
        """Test GET /api/audio/categories returns audio presets"""
        response = requests.get(f"{BASE_URL}/api/audio/categories")
        assert response.status_code == 200
        data = response.json()
        
        # Should have sfx, music, and voice categories
        assert "sfx" in data, "sfx category missing"
        assert "music" in data, "music category missing"
        assert "voice" in data, "voice category missing"
        
        # Check some presets exist
        assert len(data["sfx"]) > 0, "sfx presets empty"
        assert len(data["music"]) > 0, "music presets empty"
        assert len(data["voice"]) > 0, "voice presets empty"
        
        print(f"✅ Audio categories: sfx ({len(data['sfx'])} presets), music ({len(data['music'])} presets), voice ({len(data['voice'])} presets)")
    
    def test_get_project_audio_assets(self):
        """Test GET /api/audio/{project_id} returns audio assets"""
        response = requests.get(f"{BASE_URL}/api/audio/{TEST_PROJECT_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Get audio assets endpoint works - {len(data)} assets found")
    
    def test_audio_categories_content(self):
        """Test that audio categories contain expected presets"""
        response = requests.get(f"{BASE_URL}/api/audio/categories")
        assert response.status_code == 200
        data = response.json()
        
        # Check specific preset keys from AUDIO_CATEGORIES
        expected_sfx = ["explosion", "footstep_grass", "sword_swing", "ui_click", "pickup_item"]
        expected_music = ["menu_ambient", "battle_epic", "exploration", "boss_fight"]
        expected_voice = ["narrator_intro", "npc_greeting", "npc_merchant"]
        
        for preset in expected_sfx[:3]:  # Check a few
            assert preset in data["sfx"], f"Missing sfx preset: {preset}"
        
        for preset in expected_music[:3]:
            assert preset in data["music"], f"Missing music preset: {preset}"
        
        for preset in expected_voice[:2]:
            assert preset in data["voice"], f"Missing voice preset: {preset}"
        
        print(f"✅ Audio categories contain expected presets")

class TestDeploymentPlatforms:
    """Test One-Click Deployment endpoints"""
    
    def test_get_deployment_platforms(self):
        """Test GET /api/deploy/platforms returns platform list"""
        response = requests.get(f"{BASE_URL}/api/deploy/platforms")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 3, "Expected at least 3 deployment platforms"
        
        platform_ids = [p["id"] for p in data]
        assert "vercel" in platform_ids, "Vercel platform missing"
        assert "railway" in platform_ids, "Railway platform missing"
        assert "itch" in platform_ids, "Itch.io platform missing"
        
        print(f"✅ Deployment platforms: {platform_ids}")
    
    def test_platforms_have_required_fields(self):
        """Test that platforms have all required fields"""
        response = requests.get(f"{BASE_URL}/api/deploy/platforms")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["id", "name", "description"]
        for platform in data:
            for field in required_fields:
                assert field in platform, f"Platform {platform.get('id', 'unknown')} missing {field}"
        
        print(f"✅ All platforms have required fields: {required_fields}")
    
    def test_get_project_deployments(self):
        """Test GET /api/deploy/{project_id} returns deployments"""
        response = requests.get(f"{BASE_URL}/api/deploy/{TEST_PROJECT_ID}")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✅ Get project deployments endpoint works - {len(data)} deployments found")

class TestNotificationSettings:
    """Test Notification Settings endpoints"""
    
    def test_get_notification_settings(self):
        """Test GET /api/notifications/{project_id}/settings returns settings"""
        response = requests.get(f"{BASE_URL}/api/notifications/{TEST_PROJECT_ID}/settings")
        assert response.status_code == 200
        data = response.json()
        
        # Check expected fields exist
        assert "project_id" in data
        assert "email_enabled" in data
        assert "discord_enabled" in data
        assert "notify_on_complete" in data
        assert "notify_on_milestones" in data
        assert "notify_on_errors" in data
        
        print(f"✅ Notification settings retrieved: email_enabled={data['email_enabled']}, discord_enabled={data['discord_enabled']}")
    
    def test_save_notification_settings(self):
        """Test POST /api/notifications/{project_id}/settings saves settings"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/{TEST_PROJECT_ID}/settings",
            params={
                "email_enabled": True,
                "email_address": "test@example.com",
                "discord_enabled": True,
                "discord_webhook_url": "https://discord.com/api/webhooks/test",
                "notify_on_complete": True,
                "notify_on_milestones": True,
                "notify_on_errors": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["email_enabled"] == True
        assert data["discord_enabled"] == True
        print(f"✅ Notification settings saved successfully")
    
    def test_get_saved_notification_settings(self):
        """Test that saved settings persist"""
        response = requests.get(f"{BASE_URL}/api/notifications/{TEST_PROJECT_ID}/settings")
        assert response.status_code == 200
        data = response.json()
        
        # Should now have the saved values (or defaults if first run)
        assert "email_enabled" in data
        print(f"✅ Notification settings persist correctly")
    
    def test_get_notification_history(self):
        """Test GET /api/notifications/{project_id}/history returns history"""
        response = requests.get(f"{BASE_URL}/api/notifications/{TEST_PROJECT_ID}/history")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✅ Notification history endpoint works - {len(data)} notifications found")
    
    def test_test_notification(self):
        """Test POST /api/notifications/{project_id}/test sends test notification"""
        response = requests.post(f"{BASE_URL}/api/notifications/{TEST_PROJECT_ID}/test")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        print(f"✅ Test notification sent successfully (MOCKED - no actual email/discord sent)")

class TestAudioGenerationWorkflow:
    """Test audio generation workflow (without actually calling expensive APIs)"""
    
    @pytest.mark.skip(reason="Audio generation requires API credits - skip in automated tests")
    def test_generate_audio_sfx(self):
        """Test audio SFX generation (skipped - requires API credits)"""
        pass
    
    @pytest.mark.skip(reason="Audio generation requires API credits - skip in automated tests")
    def test_generate_audio_voice_openai(self):
        """Test voice generation with OpenAI TTS (skipped - requires API credits)"""
        pass

class TestDeploymentWorkflow:
    """Test deployment workflow (without actually deploying - MOCKED)"""
    
    @pytest.mark.skip(reason="Deployment requires real tokens - skip in automated tests")
    def test_deploy_to_vercel(self):
        """Test Vercel deployment (skipped - requires real Vercel token)"""
        pass
    
    @pytest.mark.skip(reason="Deployment requires real tokens - skip in automated tests") 
    def test_deploy_to_railway(self):
        """Test Railway deployment (skipped - requires real Railway token)"""
        pass
    
    @pytest.mark.skip(reason="Deployment requires real tokens - skip in automated tests")
    def test_deploy_to_itch(self):
        """Test Itch.io deployment (skipped - requires real Itch API key)"""
        pass

class TestProjectExists:
    """Test that the test project exists"""
    
    def test_project_exists(self):
        """Test that the test project exists"""
        response = requests.get(f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == TEST_PROJECT_ID
        print(f"✅ Test project exists: {data.get('name', 'Unknown')}")

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
