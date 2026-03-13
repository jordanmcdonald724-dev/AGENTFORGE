"""
P3 Voice Control and Celery Features Tests
Tests voice commands API, parsing, and Celery worker functionality
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealth:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        """Test that health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Health check passed: {data['status']}")


class TestVoiceCommands:
    """Voice control API tests"""
    
    def test_get_voice_commands(self):
        """Test GET /api/voice/commands returns 12 commands"""
        response = requests.get(f"{BASE_URL}/api/voice/commands")
        assert response.status_code == 200
        data = response.json()
        
        # Verify 12 commands
        assert "commands" in data
        assert data["total"] == 12
        assert len(data["commands"]) == 12
        
        # Verify command structure
        for cmd in data["commands"]:
            assert "name" in cmd
            assert "action" in cmd
            assert "description" in cmd
            assert "example_phrases" in cmd
        
        print(f"✅ Voice commands: {data['total']} commands returned")
    
    def test_voice_commands_content(self):
        """Verify all expected voice commands are present"""
        response = requests.get(f"{BASE_URL}/api/voice/commands")
        assert response.status_code == 200
        data = response.json()
        
        expected_commands = [
            "create_project", "run_build", "deploy", "create_file", "delete_file",
            "run_tests", "show_status", "list_files", "open_file", 
            "generate_image", "ask_agent", "help"
        ]
        
        command_names = [cmd["name"] for cmd in data["commands"]]
        for expected in expected_commands:
            assert expected in command_names, f"Missing command: {expected}"
        
        print(f"✅ All 12 expected commands present")


class TestVoiceParsing:
    """Voice command parsing tests"""
    
    def test_parse_create_project(self):
        """Test parsing 'create project' command"""
        response = requests.post(f"{BASE_URL}/api/voice/parse?text=create%20a%20new%20project%20called%20MyGame")
        assert response.status_code == 200
        data = response.json()
        
        assert data["parsed_command"]["command"] == "create_project"
        assert "mygame" in data["parsed_command"]["parameters"]
        assert data["parsed_command"]["confidence"] == 1.0
        
        print(f"✅ Parse create_project: {data['parsed_command']}")
    
    def test_parse_run_tests(self):
        """Test parsing 'run tests' command"""
        response = requests.post(f"{BASE_URL}/api/voice/parse?text=run%20the%20tests")
        assert response.status_code == 200
        data = response.json()
        
        assert data["parsed_command"]["command"] == "run_tests"
        assert data["execution_hint"]["endpoint"] == "/api/celery/jobs/submit?project_id=test-project&job_type=test"
        
        print(f"✅ Parse run_tests: {data['parsed_command']['command']}")
    
    def test_parse_deploy_vercel(self):
        """Test parsing 'deploy to vercel' command"""
        response = requests.post(f"{BASE_URL}/api/voice/parse?text=deploy%20to%20vercel")
        assert response.status_code == 200
        data = response.json()
        
        assert data["parsed_command"]["command"] == "deploy"
        assert "vercel" in data["parsed_command"]["parameters"]
        
        print(f"✅ Parse deploy: {data['parsed_command']}")
    
    def test_parse_help_command(self):
        """Test parsing 'help' command"""
        response = requests.post(f"{BASE_URL}/api/voice/parse?text=help")
        assert response.status_code == 200
        data = response.json()
        
        assert data["parsed_command"]["command"] == "help"
        assert data["execution_hint"]["endpoint"] == "/api/voice/commands"
        
        print(f"✅ Parse help: {data['parsed_command']['command']}")
    
    def test_parse_generate_image(self):
        """Test parsing 'generate image' command"""
        response = requests.post(f"{BASE_URL}/api/voice/parse?text=generate%20an%20image%20of%20a%20spaceship")
        assert response.status_code == 200
        data = response.json()
        
        assert data["parsed_command"]["command"] == "generate_image"
        assert len(data["parsed_command"]["parameters"]) > 0
        
        print(f"✅ Parse generate_image: {data['parsed_command']}")
    
    def test_parse_ask_agent(self):
        """Test parsing 'ask agent' command"""
        response = requests.post(f"{BASE_URL}/api/voice/parse?text=ask%20commander%20to%20start%20planning")
        assert response.status_code == 200
        data = response.json()
        
        assert data["parsed_command"]["command"] == "ask_agent"
        
        print(f"✅ Parse ask_agent: {data['parsed_command']}")
    
    def test_parse_unrecognized_as_chat(self):
        """Test that unrecognized text becomes chat command"""
        response = requests.post(f"{BASE_URL}/api/voice/parse?text=hello%20how%20are%20you")
        assert response.status_code == 200
        data = response.json()
        
        assert data["parsed_command"]["command"] == "chat"
        assert data["parsed_command"]["confidence"] == 0.5
        
        print(f"✅ Unrecognized text parsed as chat")


class TestCeleryIntegration:
    """Celery worker and job processing tests"""
    
    def test_celery_stats(self):
        """Test Celery is available and stats endpoint works"""
        response = requests.get(f"{BASE_URL}/api/celery/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert data["celery_available"] == True
        assert "total_jobs" in data
        assert "queued" in data
        assert "running" in data
        assert "completed" in data
        
        print(f"✅ Celery available: {data['celery_available']}, Total jobs: {data['total_jobs']}")
    
    def test_celery_workers(self):
        """Test Celery workers endpoint"""
        response = requests.get(f"{BASE_URL}/api/celery/workers")
        assert response.status_code == 200
        data = response.json()
        
        # Workers endpoint should return list or status
        assert isinstance(data, (list, dict))
        
        print(f"✅ Celery workers endpoint functional")
    
    def test_submit_job(self):
        """Test submitting a job to Celery"""
        # Get a project ID first
        projects_response = requests.get(f"{BASE_URL}/api/projects")
        assert projects_response.status_code == 200
        projects = projects_response.json()
        
        if projects:
            project_id = projects[0]["id"]
            response = requests.post(
                f"{BASE_URL}/api/celery/jobs/submit",
                params={"project_id": project_id, "job_type": "build"}
            )
            assert response.status_code == 200
            data = response.json()
            
            assert "id" in data
            assert data["project_id"] == project_id
            assert data["job_type"] == "build"
            assert data["status"] in ["queued", "running"]
            
            print(f"✅ Job submitted: {data['id']}, status: {data['status']}")
        else:
            pytest.skip("No projects available for job submission test")
    
    def test_get_job_status(self):
        """Test getting job status"""
        # Submit a job first
        projects_response = requests.get(f"{BASE_URL}/api/projects")
        projects = projects_response.json()
        
        if projects:
            project_id = projects[0]["id"]
            submit_response = requests.post(
                f"{BASE_URL}/api/celery/jobs/submit",
                params={"project_id": project_id, "job_type": "build"}
            )
            
            if submit_response.status_code == 200:
                job_id = submit_response.json()["id"]
                
                status_response = requests.get(f"{BASE_URL}/api/celery/jobs/{job_id}")
                assert status_response.status_code == 200
                data = status_response.json()
                
                assert data["id"] == job_id
                assert "status" in data
                
                print(f"✅ Job status retrieved: {data['status']}")
            else:
                pytest.skip("Job submission failed")
        else:
            pytest.skip("No projects available")


class TestExistingFeatures:
    """Tests to verify existing features still work"""
    
    def test_projects_endpoint(self):
        """Test GET /api/projects works"""
        response = requests.get(f"{BASE_URL}/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        print(f"✅ Projects endpoint: {len(data)} projects")
    
    def test_agents_endpoint(self):
        """Test GET /api/agents returns agents"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 6
        
        # Verify agent structure
        for agent in data:
            assert "id" in agent
            assert "name" in agent
            assert "role" in agent
        
        print(f"✅ Agents endpoint: {len(data)} agents")
    
    def test_root_endpoint(self):
        """Test root endpoint returns app info"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        
        # Root returns message and version for AgentForge
        assert "message" in data or "version" in data or "features" in data
        
        print(f"✅ Root endpoint functional: {data.get('message', 'OK')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
