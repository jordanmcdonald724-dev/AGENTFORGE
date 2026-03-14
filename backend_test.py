#!/usr/bin/env python3
"""
AI Agent Dev Team Platform - Backend API Testing
Tests all endpoints systematically for functionality and integration
"""

import requests
import json
import time
import sys
from typing import Dict, List, Optional
from datetime import datetime

class AgentTeamAPITester:
    def __init__(self, base_url="https://file-examiner-10.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.project_id = None
        self.agent_ids = {}
        
    def log_test(self, name: str, passed: bool, details: str = "", response_data: dict = None):
        """Log test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED {details}")
        else:
            print(f"❌ {name}: FAILED {details}")
            
        self.test_results.append({
            "name": name,
            "passed": passed,
            "details": details,
            "response_data": response_data
        })

    def make_request(self, method: str, endpoint: str, data: dict = None, expected_status: int = 200) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                return False, {}, 0
                
            success = response.status_code == expected_status
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_response": response.text}
                
            return success, response_data, response.status_code
            
        except Exception as e:
            return False, {"error": str(e)}, 0

    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n🔍 Testing Basic Connectivity...")
        
        # Test root endpoint
        success, data, status = self.make_request("GET", "/")
        self.log_test("Root endpoint", success, f"Status: {status}", data)
        
        # Test new features in root endpoint
        if success and data:
            features = data.get("features", [])
            expected_features = ["streaming", "delegation", "image_generation"]
            features_present = all(feature in features for feature in expected_features)
            self.log_test("New features in root endpoint", features_present, f"Features: {features}")
        
        # Test health endpoint
        success, data, status = self.make_request("GET", "/health")
        self.log_test("Health check", success, f"Status: {status}", data)
        
        return success

    def test_agent_management(self):
        """Test agent-related endpoints"""
        print("\n🤖 Testing Agent Management...")
        
        # Get all agents (should initialize default agents)
        success, data, status = self.make_request("GET", "/agents")
        self.log_test("Get agents", success, f"Status: {status}, Count: {len(data) if success else 0}")
        
        if success and data:
            # Store agent IDs for later tests
            for agent in data:
                self.agent_ids[agent['role']] = agent['id']
            
            # Check all 6 agents are present
            expected_roles = ['lead', 'architect', 'developer', 'reviewer', 'tester', 'artist']
            found_roles = [agent['role'] for agent in data]
            all_present = all(role in found_roles for role in expected_roles)
            self.log_test("All 6 agents present", all_present, f"Found roles: {found_roles}")
            
            # Check agent names
            expected_names = ['COMMANDER', 'ATLAS', 'FORGE', 'SENTINEL', 'PROBE', 'PRISM']
            found_names = [agent['name'] for agent in data]
            names_correct = all(name in found_names for name in expected_names)
            self.log_test("Agent names correct", names_correct, f"Found names: {found_names}")
            
            # Test get individual agent
            if self.agent_ids:
                first_agent_id = list(self.agent_ids.values())[0]
                success, data, status = self.make_request("GET", f"/agents/{first_agent_id}")
                self.log_test("Get individual agent", success, f"Agent: {data.get('name', 'Unknown')}")
                
            # Test agent status update
            if self.agent_ids:
                lead_id = self.agent_ids.get('lead')
                if lead_id:
                    success, data, status = self.make_request("PATCH", f"/agents/{lead_id}/status?status=thinking")
                    self.log_test("Update agent status", success, f"Status update")
                    
                    # Reset status
                    self.make_request("PATCH", f"/agents/{lead_id}/status?status=idle")
        
        return success

    def test_project_management(self):
        """Test project CRUD operations"""
        print("\n📁 Testing Project Management...")
        
        # Test create project
        project_data = {
            "name": "Test AI Game Project",
            "description": "A test project for the AI development team",
            "type": "game"
        }
        
        success, data, status = self.make_request("POST", "/projects", project_data, 200)
        self.log_test("Create project", success, f"Project ID: {data.get('id', 'None') if success else 'Failed'}")
        
        if success and data:
            self.project_id = data['id']
            
            # Test get all projects
            success, projects, status = self.make_request("GET", "/projects")
            self.log_test("Get all projects", success, f"Count: {len(projects) if success else 0}")
            
            # Test get individual project
            success, project, status = self.make_request("GET", f"/projects/{self.project_id}")
            self.log_test("Get individual project", success, f"Name: {project.get('name', 'None')}")
            
            # Test update project
            update_data = {"status": "in_progress"}
            success, data, status = self.make_request("PATCH", f"/projects/{self.project_id}", update_data)
            self.log_test("Update project", success, "Status updated")
        
        return success

    def test_task_management(self):
        """Test task CRUD operations"""
        print("\n📋 Testing Task Management...")
        
        if not self.project_id:
            self.log_test("Task management", False, "No project ID available")
            return False
            
        # Test create task
        task_data = {
            "project_id": self.project_id,
            "title": "Design game architecture",
            "description": "Create the initial game architecture and technical specifications",
            "priority": "high"
        }
        
        success, data, status = self.make_request("POST", "/tasks", task_data, 200)
        task_id = data.get('id') if success else None
        self.log_test("Create task", success, f"Task ID: {task_id}")
        
        if success and task_id:
            # Test get tasks for project
            success, tasks, status = self.make_request("GET", f"/tasks?project_id={self.project_id}")
            self.log_test("Get project tasks", success, f"Count: {len(tasks) if success else 0}")
            
            # Test update task
            update_data = {"status": "in_progress"}
            success, data, status = self.make_request("PATCH", f"/tasks/{task_id}", update_data)
            self.log_test("Update task status", success, "Status updated to in_progress")
            
            # Test delete task
            success, data, status = self.make_request("DELETE", f"/tasks/{task_id}", expected_status=200)
            self.log_test("Delete task", success, "Task deleted")
        
        return success

    def test_chat_functionality(self):
        """Test AI chat integration with fal.ai"""
        print("\n💬 Testing Chat Functionality...")
        
        if not self.project_id:
            self.log_test("Chat functionality", False, "No project ID available")
            return False
            
        # Test chat with team (PM agent)
        chat_data = {
            "project_id": self.project_id,
            "message": "Hello team! I want to build a simple 2D platformer game. Can you help me plan this project?",
            "context": "Initial project discussion"
        }
        
        print("   Sending message to AI team...")
        success, data, status = self.make_request("POST", "/chat", chat_data, 200)
        self.log_test("Chat with PM team", success, f"Response received: {bool(data.get('response')) if success else 'No response'}")
        
        if success and data:
            response_length = len(data.get('response', ''))
            agent_info = data.get('agent', {})
            self.log_test("Lead agent response quality", response_length > 50, f"Response length: {response_length} chars")
            self.log_test("Lead agent identification", agent_info.get('name') == 'COMMANDER', f"Agent: {agent_info.get('name')}")
            
        return success

    def test_streaming_chat(self):
        """Test streaming chat endpoint with SSE"""
        print("\n🌊 Testing Streaming Chat...")
        
        if not self.project_id:
            self.log_test("Streaming chat", False, "No project ID available")
            return False
            
        # Test streaming endpoint availability
        chat_data = {
            "project_id": self.project_id,
            "message": "Tell me about yourself briefly.",
        }
        
        # Since we can't easily test SSE streaming in requests, test endpoint accepts the request
        url = f"{self.base_url}/chat/stream"
        
        try:
            response = self.session.post(url, json=chat_data, stream=True)
            success = response.status_code == 200
            
            # Check for SSE headers
            content_type = response.headers.get('content-type', '')
            is_sse = 'text/event-stream' in content_type
            
            self.log_test("Streaming chat endpoint", success, f"Status: {response.status_code}")
            self.log_test("SSE content type", is_sse, f"Content-Type: {content_type}")
            
            # Try to read first few chunks to verify streaming works
            chunks_received = 0
            if success:
                for chunk in response.iter_lines(decode_unicode=True):
                    if chunk and chunks_received < 3:  # Just test first few chunks
                        if chunk.startswith('data: '):
                            chunks_received += 1
                    if chunks_received >= 3:
                        break
                        
            self.log_test("SSE chunks received", chunks_received > 0, f"Chunks: {chunks_received}")
            
        except Exception as e:
            self.log_test("Streaming chat endpoint", False, f"Error: {str(e)}")
            success = False
            
        return success

    def test_delegation_endpoint(self):
        """Test agent delegation functionality"""
        print("\n🤝 Testing Agent Delegation...")
        
        if not self.project_id:
            self.log_test("Delegation", False, "No project ID available")
            return False
            
        # Test delegation to FORGE agent
        delegation_data = {
            "project_id": self.project_id,
            "message": "Create a simple player class for a 2D platformer game",
            "delegate_to": "FORGE"
        }
        
        success, data, status = self.make_request("POST", "/delegate", delegation_data, 200)
        self.log_test("Delegate to FORGE", success, f"Status: {status}")
        
        if success and data:
            response_content = data.get('response', '')
            agent_info = data.get('agent', {})
            code_blocks = data.get('code_blocks', [])
            
            self.log_test("Delegation response received", len(response_content) > 0, f"Response length: {len(response_content)}")
            self.log_test("Delegated agent identified", agent_info.get('name') == 'FORGE', f"Agent: {agent_info.get('name')}")
            self.log_test("Code blocks in delegation", len(code_blocks) > 0, f"Code blocks: {len(code_blocks)}")
            
        return success

    def test_image_generation(self):
        """Test image generation with fal.ai"""
        print("\n🎨 Testing Image Generation...")
        
        if not self.project_id:
            self.log_test("Image generation", False, "No project ID available")
            return False
            
        # Test image generation
        image_data = {
            "project_id": self.project_id,
            "prompt": "A simple 2D platformer game character sprite, pixel art style",
            "category": "character",
            "width": 512,
            "height": 512
        }
        
        print("   Generating image with fal.ai...")
        success, data, status = self.make_request("POST", "/images/generate", image_data, 200)
        self.log_test("Generate image", success, f"Status: {status}")
        
        if success and data:
            image_id = data.get('id')
            image_url = data.get('url')
            prompt_match = data.get('prompt') == image_data['prompt']
            
            self.log_test("Image ID generated", bool(image_id), f"Image ID: {image_id}")
            self.log_test("Image URL returned", bool(image_url), f"URL present: {bool(image_url)}")
            self.log_test("Prompt preserved", prompt_match, f"Prompt match: {prompt_match}")
            
            # Test get images for project
            success, images, status = self.make_request("GET", f"/images?project_id={self.project_id}")
            self.log_test("Get project images", success, f"Image count: {len(images) if success else 0}")
            
            # Test delete image
            if image_id:
                success, data, status = self.make_request("DELETE", f"/images/{image_id}", expected_status=200)
                self.log_test("Delete generated image", success, "Image deleted")
        
        return success

    def test_message_persistence(self):
        """Test message storage and retrieval"""
        print("\n📜 Testing Message Persistence...")
        
        if not self.project_id:
            self.log_test("Message persistence", False, "No project ID available")
            return False
            
        # Get messages for project
        success, messages, status = self.make_request("GET", f"/messages?project_id={self.project_id}")
        self.log_test("Get project messages", success, f"Message count: {len(messages) if success else 0}")
        
        # Note: Message creation is handled automatically by chat endpoints
        # Manual message creation endpoint may not exist in this version
        
        return success

    def test_code_auto_save(self):
        """Test code block auto-save from chat responses"""
        print("\n💾 Testing Code Auto-Save...")
        
        if not self.project_id:
            self.log_test("Code auto-save", False, "No project ID available")
            return False
            
        # Test auto-save endpoint
        code_blocks = [
            {
                "language": "python",
                "filepath": "/src/game.py",
                "filename": "game.py",
                "content": "# Auto-saved game code\nclass Game:\n    def __init__(self):\n        self.running = True"
            }
        ]
        
        auto_save_data = {
            "project_id": self.project_id,
            "code_blocks": code_blocks,
            "agent_id": self.agent_ids.get('developer', 'test-agent'),
            "agent_name": "FORGE"
        }
        
        success, data, status = self.make_request("POST", "/files/from-chat", auto_save_data, 200)
        self.log_test("Code block auto-save", success, f"Saved files: {data.get('saved_files', []) if success else 'None'}")
        
        if success:
            # Verify file was created
            success, files, status = self.make_request("GET", f"/files?project_id={self.project_id}")
            auto_saved_file = any(f.get('filepath') == '/src/game.py' for f in files) if files else False
            self.log_test("Auto-saved file exists", auto_saved_file, "File found in project")
        
        return success

    def test_file_management(self):
        """Test file operations"""
        print("\n📄 Testing File Management...")
        
        if not self.project_id:
            self.log_test("File management", False, "No project ID available")
            return False
            
        # Test get files for project
        success, files, status = self.make_request("GET", f"/files?project_id={self.project_id}")
        self.log_test("Get project files", success, f"File count: {len(files) if success else 0}")
        
        # Test create file
        file_data = {
            "project_id": self.project_id,
            "filename": "main.py",
            "filepath": "/src/main.py",
            "content": "# Game main entry point\nprint('Hello Game World!')",
            "language": "python",
            "created_by_agent_id": self.agent_ids.get('developer', 'test-agent')
        }
        
        success, data, status = self.make_request("POST", "/files", file_data, 200)
        file_id = data.get('id') if success else None
        self.log_test("Create file", success, f"File ID: {file_id}")
        
        if success and file_id:
            # Test get individual file
            success, file_data, status = self.make_request("GET", f"/files/{file_id}")
            self.log_test("Get individual file", success, f"Filename: {file_data.get('filename', 'None')}")
        
        return success

    def test_project_export(self):
        """Test project export as ZIP"""
        print("\n📦 Testing Project Export...")
        
        if not self.project_id:
            self.log_test("Project export", False, "No project ID available")
            return False
            
        # Test export project
        success, data, status = self.make_request("GET", f"/projects/{self.project_id}/export", expected_status=200)
        self.log_test("Export project as ZIP", success, f"Export successful" if success else "Export failed")
        
        return success

    def test_quick_actions_v22(self):
        """Test Quick Actions v2.2 feature"""
        print("\n⚡ Testing Quick Actions v2.2...")
        
        # Test get quick actions
        success, data, status = self.make_request("GET", "/quick-actions")
        self.log_test("Get quick actions", success, f"Status: {status}")
        
        if success:
            actions_count = len(data) if isinstance(data, list) else 0
            self.log_test("8 Quick Actions available", actions_count == 8, f"Found {actions_count} actions")
            
            # Check expected action IDs
            if isinstance(data, list) and actions_count > 0:
                action_ids = [action.get('id') for action in data]
                expected_ids = ['player_controller', 'inventory_system', 'save_system', 'health_system', 
                              'ai_behavior', 'dialogue_system', 'ui_framework', 'audio_manager']
                ids_correct = all(expected_id in action_ids for expected_id in expected_ids)
                self.log_test("All expected action IDs present", ids_correct, f"Found: {action_ids}")
                
                # Test quick action execution (non-streaming)
                if self.project_id and action_ids:
                    execute_data = {
                        "project_id": self.project_id,
                        "action_id": "player_controller",
                        "parameters": {}
                    }
                    success, data, status = self.make_request("POST", "/quick-actions/execute", execute_data, 200)
                    self.log_test("Execute quick action", success, f"Status: {status}")
                    
                    if success:
                        results = data.get('results', [])
                        self.log_test("Quick action results", len(results) > 0, f"Results count: {len(results)}")
        
        return success

    def test_agent_chains_v22(self):
        """Test Agent Chains v2.2 feature"""
        print("\n🔗 Testing Agent Chains v2.2...")
        
        if not self.project_id:
            self.log_test("Agent chains", False, "No project ID available")
            return False
        
        # Test agent chain execution
        chain_data = {
            "project_id": self.project_id,
            "message": "Create a simple health system for the game",
            "chain": ["COMMANDER", "FORGE"],
            "auto_execute": True
        }
        
        success, data, status = self.make_request("POST", "/chain", chain_data, 200)
        self.log_test("Execute agent chain", success, f"Status: {status}")
        
        if success:
            chain_results = data.get('results', [])
            total_code_blocks = data.get('total_code_blocks', 0)
            
            self.log_test("Chain results received", len(chain_results) > 0, f"Results: {len(chain_results)}")
            self.log_test("Code blocks generated", total_code_blocks > 0, f"Code blocks: {total_code_blocks}")
            
            # Verify chain executed agents in sequence
            if chain_results:
                executed_agents = [result.get('agent') for result in chain_results]
                expected_sequence = ["COMMANDER", "FORGE"]
                sequence_correct = executed_agents == expected_sequence
                self.log_test("Agent chain sequence", sequence_correct, f"Executed: {executed_agents}")
        
        return success

    def test_github_push_v22(self):
        """Test GitHub Push v2.2 feature"""
        print("\n🐙 Testing GitHub Push v2.2...")
        
        if not self.project_id:
            self.log_test("GitHub push", False, "No project ID available")
            return False
        
        # Test GitHub push endpoint (will fail without valid token, but endpoint should accept request)
        github_data = {
            "project_id": self.project_id,
            "github_token": "fake-token-for-testing",
            "repo_name": "test-repo",
            "commit_message": "Test commit from AgentForge",
            "branch": "main",
            "create_repo": True
        }
        
        success, data, status = self.make_request("POST", "/github/push", github_data, 400)
        # Expect 400 due to invalid token, but endpoint should process the request
        valid_error_status = status in [400, 401, 403]  # GitHub auth errors
        self.log_test("GitHub push endpoint available", valid_error_status, f"Status: {status}")
        
        if not valid_error_status:
            # Try to check if it's a different error (like missing files)
            error_detail = data.get('detail', '')
            no_files_error = 'No files to push' in str(error_detail)
            self.log_test("GitHub push validates files", no_files_error, f"Error: {error_detail}")
            
        return valid_error_status or 'No files' in str(data.get('detail', ''))

    def test_live_preview_v22(self):
        """Test Live Preview v2.2 feature"""
        print("\n👁️  Testing Live Preview v2.2...")
        
        if not self.project_id:
            self.log_test("Live preview", False, "No project ID available")
            return False
        
        # First create a web project for testing
        web_project_data = {
            "name": "Test Web Project",
            "description": "A test web project for live preview",
            "type": "web_app"
        }
        
        success, project_data, status = self.make_request("POST", "/projects", web_project_data, 200)
        web_project_id = project_data.get('id') if success else None
        
        if success and web_project_id:
            # Test live preview data endpoint
            success, data, status = self.make_request("GET", f"/projects/{web_project_id}/preview-data")
            self.log_test("Get preview data", success, f"Status: {status}")
            
            if success:
                has_html_key = 'html' in data
                has_css_key = 'css' in data  
                has_js_key = 'js' in data
                has_project_type = 'project_type' in data
                
                self.log_test("Preview data structure", 
                            has_html_key and has_css_key and has_js_key and has_project_type,
                            f"Keys present: {list(data.keys())}")
            
            # Test live preview HTML endpoint
            success, html_data, status = self.make_request("GET", f"/projects/{web_project_id}/preview")
            self.log_test("Get preview HTML", success, f"Status: {status}")
            
            # Cleanup web project
            self.make_request("DELETE", f"/projects/{web_project_id}")
        else:
            self.log_test("Create web project for preview", success, "Failed to create test web project")
            return False
            
        return success

    def test_error_handling(self):
        """Test API error handling"""
        print("\n⚠️  Testing Error Handling...")
        
        # Test non-existent project
        success, data, status = self.make_request("GET", "/projects/non-existent-id", expected_status=404)
        self.log_test("Non-existent project 404", success, f"Correct 404 status")
        
        # Test non-existent agent
        success, data, status = self.make_request("GET", "/agents/non-existent-id", expected_status=404)
        self.log_test("Non-existent agent 404", success, f"Correct 404 status")
        
        # Test invalid project creation
        invalid_project = {"name": ""}  # Missing required fields
        success, data, status = self.make_request("POST", "/projects", invalid_project, expected_status=422)
        expected_error = status in [400, 422]  # Either is acceptable for validation error
        self.log_test("Invalid project validation", expected_error, f"Status: {status}")
        
        return True

    def cleanup(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        if self.project_id:
            success, data, status = self.make_request("DELETE", f"/projects/{self.project_id}", expected_status=200)
            self.log_test("Cleanup project", success, "Test project deleted")

    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting AI Agent Dev Team API Tests")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run test categories
        connectivity_ok = self.test_basic_connectivity()
        if not connectivity_ok:
            print("\n❌ Basic connectivity failed - stopping tests")
            return False
            
        agents_ok = self.test_agent_management()
        projects_ok = self.test_project_management()
        tasks_ok = self.test_task_management()
        
        # Only test chat if basic functionality works
        chat_ok = True
        streaming_ok = True
        delegation_ok = True
        image_gen_ok = True
        messages_ok = True
        code_save_ok = True
        export_ok = True
        # v2.2 features
        quick_actions_ok = True
        agent_chains_ok = True
        github_push_ok = True
        live_preview_ok = True
        
        if projects_ok:
            chat_ok = self.test_chat_functionality()
            streaming_ok = self.test_streaming_chat()
            delegation_ok = self.test_delegation_endpoint()
            image_gen_ok = self.test_image_generation()
            messages_ok = self.test_message_persistence()
            code_save_ok = self.test_code_auto_save()
            export_ok = self.test_project_export()
            
            # Test v2.2 features
            quick_actions_ok = self.test_quick_actions_v22()
            agent_chains_ok = self.test_agent_chains_v22()
            github_push_ok = self.test_github_push_v22()
            live_preview_ok = self.test_live_preview_v22()
            
        files_ok = self.test_file_management()
        errors_ok = self.test_error_handling()
        
        # Cleanup
        self.cleanup()
        
        # Results summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.tests_passed}/{self.tests_run}")
        print(f"⏱️  Duration: {duration:.1f}s")
        print(f"🎯 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Detailed breakdown
        print("\n📊 Category Results:")
        category_results = {
            "🔌 Connectivity": connectivity_ok,
            "🤖 Agent Management": agents_ok,
            "📁 Project Management": projects_ok,
            "📋 Task Management": tasks_ok,
            "💬 Chat/AI Integration": chat_ok,
            "🌊 Streaming Chat": streaming_ok,
            "🤝 Agent Delegation": delegation_ok,
            "🎨 Image Generation": image_gen_ok,
            "📜 Message Persistence": messages_ok,
            "💾 Code Auto-Save": code_save_ok,
            "📦 Project Export": export_ok,
            "📄 File Management": files_ok,
            "⚠️  Error Handling": errors_ok,
            # v2.2 features
            "⚡ Quick Actions v2.2": quick_actions_ok,
            "🔗 Agent Chains v2.2": agent_chains_ok,
            "🐙 GitHub Push v2.2": github_push_ok,
            "👁️  Live Preview v2.2": live_preview_ok,
        }
        
        for category, result in category_results.items():
            status = "✅" if result else "❌"
            print(f"   {status} {category}")
        
        # Critical issues
        critical_failures = []
        if not connectivity_ok:
            critical_failures.append("API not accessible")
        if not agents_ok:
            critical_failures.append("Agent system not working")
        if not projects_ok:
            critical_failures.append("Project management broken")
        if not chat_ok:
            critical_failures.append("AI chat integration failing")
        if not streaming_ok:
            critical_failures.append("Streaming chat not working")
        if not delegation_ok:
            critical_failures.append("Agent delegation broken")
        if not image_gen_ok:
            critical_failures.append("Image generation failing")
        if not quick_actions_ok:
            critical_failures.append("Quick Actions v2.2 not working")
        if not agent_chains_ok:
            critical_failures.append("Agent Chains v2.2 not working")
        if not github_push_ok:
            critical_failures.append("GitHub Push v2.2 not working")
        if not live_preview_ok:
            critical_failures.append("Live Preview v2.2 not working")
            
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in critical_failures:
                print(f"   • {issue}")
        else:
            print(f"\n🎉 All critical systems operational!")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = AgentTeamAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⏸️  Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())