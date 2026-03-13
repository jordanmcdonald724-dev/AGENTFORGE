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
    def __init__(self, base_url="https://ai-agent-team.preview.emergentagent.com/api"):
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
            
            # Check all 5 agents are present
            expected_roles = ['project_manager', 'architect', 'developer', 'reviewer', 'tester']
            found_roles = [agent['role'] for agent in data]
            all_present = all(role in found_roles for role in expected_roles)
            self.log_test("All 5 agents present", all_present, f"Found roles: {found_roles}")
            
            # Check agent names
            expected_names = ['NEXUS', 'ATLAS', 'FORGE', 'SENTINEL', 'PROBE']
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
                pm_id = self.agent_ids.get('project_manager')
                if pm_id:
                    success, data, status = self.make_request("PATCH", f"/agents/{pm_id}/status?status=thinking")
                    self.log_test("Update agent status", success, f"Status update")
                    
                    # Reset status
                    self.make_request("PATCH", f"/agents/{pm_id}/status?status=idle")
        
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
            self.log_test("PM agent response quality", response_length > 50, f"Response length: {response_length} chars")
            self.log_test("PM agent identification", agent_info.get('name') == 'NEXUS', f"Agent: {agent_info.get('name')}")
            
        # Test specific agent call
        if self.agent_ids.get('architect'):
            architect_data = {
                "project_id": self.project_id,
                "message": "Can you create a technical architecture for a 2D platformer game?",
            }
            
            print("   Calling architect agent...")
            success, data, status = self.make_request("POST", f"/agents/{self.agent_ids['architect']}/call", architect_data, 200)
            self.log_test("Direct architect call", success, f"Architect response: {bool(data.get('response')) if success else 'No response'}")
        
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
        
        # Test manual message creation
        message_data = {
            "project_id": self.project_id,
            "agent_id": "test-user",
            "agent_name": "Test User",
            "agent_role": "user",
            "content": "This is a test message for persistence testing"
        }
        
        success, data, status = self.make_request("POST", "/messages", message_data, 200)
        self.log_test("Create message", success, "Message created manually")
        
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
        messages_ok = True
        if projects_ok:
            chat_ok = self.test_chat_functionality()
            messages_ok = self.test_message_persistence()
            
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
            "📜 Message Persistence": messages_ok,
            "📄 File Management": files_ok,
            "⚠️  Error Handling": errors_ok,
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