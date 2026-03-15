#!/usr/bin/env python3
"""
AgentForge Backend API Testing Suite
===================================

Comprehensive testing for all key AgentForge v4.5 API endpoints.
Tests based on the review request requirements.
"""

import asyncio
import aiohttp
import json
import sys
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

# Test Configuration
BACKEND_URL = "https://premium-os.preview.emergentagent.com/api"
TEST_PROJECT_ID = "334166ac-9ea3-45d8-b4d2-3c81e7ef19c1"

class APITestRunner:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results: Dict[str, Any] = {}
        self.passed = 0
        self.failed = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def log_test(self, test_name: str, success: bool, details: Dict[str, Any] = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
            
        self.test_results[test_name] = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        if details and not success:
            print(f"    Error: {details.get('error', 'Unknown error')}")
    
    async def test_get_request(self, endpoint: str, test_name: str, expected_keys: list = None):
        """Test GET endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                success = response.status == 200
                data = await response.json()
                
                details = {
                    "status_code": response.status,
                    "response_size": len(str(data)) if data else 0,
                    "endpoint": endpoint
                }
                
                if success and expected_keys:
                    if isinstance(data, list) and data:
                        # Check first item in list
                        for key in expected_keys:
                            if key not in data[0]:
                                success = False
                                details["error"] = f"Missing expected key: {key}"
                                break
                    elif isinstance(data, dict):
                        for key in expected_keys:
                            if key not in data:
                                success = False
                                details["error"] = f"Missing expected key: {key}"
                                break
                
                if success:
                    details["data_type"] = type(data).__name__
                    details["item_count"] = len(data) if isinstance(data, (list, dict)) else 1
                else:
                    details["error"] = details.get("error", f"HTTP {response.status}")
                    
                await self.log_test(test_name, success, details)
                return success, data
                
        except Exception as e:
            await self.log_test(test_name, False, {"error": str(e), "endpoint": endpoint})
            return False, None

    async def test_post_request(self, endpoint: str, test_name: str, payload: dict, expected_keys: list = None):
        """Test POST endpoint"""
        try:
            headers = {"Content-Type": "application/json"}
            async with self.session.post(f"{BACKEND_URL}{endpoint}", json=payload, headers=headers) as response:
                success = response.status in [200, 201]
                
                try:
                    data = await response.json()
                except:
                    data = {"text": await response.text()}
                
                details = {
                    "status_code": response.status,
                    "endpoint": endpoint,
                    "payload_size": len(json.dumps(payload))
                }
                
                if success and expected_keys and isinstance(data, dict):
                    for key in expected_keys:
                        if key not in data:
                            success = False
                            details["error"] = f"Missing expected key: {key}"
                            break
                
                if not success:
                    details["error"] = details.get("error", f"HTTP {response.status}")
                    details["response"] = str(data)[:200] if data else "No response"
                
                await self.log_test(test_name, success, details)
                return success, data
                
        except Exception as e:
            await self.log_test(test_name, False, {"error": str(e), "endpoint": endpoint})
            return False, None

    async def test_patch_request(self, endpoint: str, test_name: str, payload: dict, expected_keys: list = None):
        """Test PATCH endpoint"""
        try:
            headers = {"Content-Type": "application/json"}
            async with self.session.patch(f"{BACKEND_URL}{endpoint}", json=payload, headers=headers) as response:
                success = response.status in [200, 201]
                
                try:
                    data = await response.json()
                except:
                    data = {"text": await response.text()}
                
                details = {
                    "status_code": response.status,
                    "endpoint": endpoint,
                    "payload_size": len(json.dumps(payload))
                }
                
                if success and expected_keys and isinstance(data, dict):
                    for key in expected_keys:
                        if key not in data:
                            success = False
                            details["error"] = f"Missing expected key: {key}"
                            break
                
                if not success:
                    details["error"] = details.get("error", f"HTTP {response.status}")
                    details["response"] = str(data)[:200] if data else "No response"
                
                await self.log_test(test_name, success, details)
                return success, data
                
        except Exception as e:
            await self.log_test(test_name, False, {"error": str(e), "endpoint": endpoint})
            return False, None

    async def test_stream_request(self, endpoint: str, test_name: str, payload: dict):
        """Test streaming endpoint"""
        try:
            headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}
            async with self.session.post(f"{BACKEND_URL}{endpoint}", json=payload, headers=headers) as response:
                success = response.status == 200
                
                if not success:
                    await self.log_test(test_name, False, {
                        "error": f"HTTP {response.status}",
                        "endpoint": endpoint
                    })
                    return False, None
                
                # Read first few chunks to verify streaming works
                chunks_received = 0
                has_data = False
                async for chunk in response.content.iter_chunked(1024):
                    chunks_received += 1
                    if chunk:
                        has_data = True
                        # Parse SSE data
                        chunk_text = chunk.decode('utf-8', errors='ignore')
                        if 'data:' in chunk_text:
                            # Successfully receiving SSE data
                            break
                    
                    if chunks_received >= 5:  # Don't wait too long
                        break
                
                success = has_data
                details = {
                    "status_code": response.status,
                    "chunks_received": chunks_received,
                    "has_sse_data": has_data,
                    "endpoint": endpoint
                }
                
                if not success:
                    details["error"] = "No SSE data received"
                
                await self.log_test(test_name, success, details)
                return success, {"chunks": chunks_received}
                
        except Exception as e:
            await self.log_test(test_name, False, {"error": str(e), "endpoint": endpoint})
            return False, None

    async def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting AgentForge Backend API Tests")
        print(f"📍 Backend URL: {BACKEND_URL}")
        print(f"🔍 Test Project ID: {TEST_PROJECT_ID}")
        print("=" * 60)
        
        # Test 1: Health Check
        await self.test_get_request("/", "Health Check", ["message", "version", "features"])
        
        # Test 2: Projects CRUD API (HIGH PRIORITY)
        print("\n📂 PROJECTS API TESTS")
        
        # GET /api/projects
        success, projects = await self.test_get_request("/projects", "Get All Projects", [])
        
        # POST /api/projects - Create new project
        new_project_payload = {
            "name": "Test Project",
            "type": "unreal",
            "engine_version": "5.4",
            "description": "Test project for API testing"
        }
        await self.test_post_request("/projects", "Create Project", new_project_payload, ["id", "name"])
        
        # GET /api/projects/{id} - Get single project
        await self.test_get_request(f"/projects/{TEST_PROJECT_ID}", "Get Single Project", ["id", "name"])
        
        # PUT /api/projects/{id} - Update project (using PATCH)
        update_payload = {"description": "Updated description"}
        await self.test_patch_request(f"/projects/{TEST_PROJECT_ID}", "Update Project", update_payload, ["success"])
        
        # Test 3: Agents API (HIGH PRIORITY)
        print("\n🤖 AGENTS API TESTS")
        
        # GET /api/agents - Should return 6 agents
        success, agents_data = await self.test_get_request("/agents", "Get All Agents", ["name", "role"])
        if success and agents_data:
            expected_agents = ["COMMANDER", "ATLAS", "FORGE", "SENTINEL", "PROBE", "PRISM"]
            agent_names = [agent.get("name") for agent in agents_data if isinstance(agent, dict)]
            found_agents = [name for name in expected_agents if name in agent_names]
            
            await self.log_test("Verify 6 Agents Present", len(found_agents) >= 6, {
                "expected": expected_agents,
                "found": found_agents,
                "total_agents": len(agent_names)
            })
        
        # Test 4: Chat Streaming API (HIGH PRIORITY)
        print("\n💬 CHAT API TESTS")
        
        # POST /api/chat/stream
        chat_payload = {
            "project_id": TEST_PROJECT_ID,
            "message": "Hello, can you help me?",
            "phase": "clarification"
        }
        await self.test_stream_request("/chat/stream", "Chat Streaming", chat_payload)
        
        # Test 5: Quick Actions API (HIGH PRIORITY)
        print("\n⚡ QUICK ACTIONS API TESTS")
        
        # GET /api/quick-actions
        await self.test_get_request("/quick-actions", "Get Quick Actions", ["id", "name"])
        
        # POST /api/quick-actions/execute/stream
        quick_action_payload = {
            "project_id": TEST_PROJECT_ID,
            "action_id": "player_controller",
            "parameters": {}
        }
        await self.test_stream_request("/quick-actions/execute/stream", "Execute Quick Action Stream", quick_action_payload)
        
        # Test 6: Files API (HIGH PRIORITY)
        print("\n📄 FILES API TESTS")
        
        # GET /api/files?project_id=xxx
        await self.test_get_request(f"/files?project_id={TEST_PROJECT_ID}", "Get Project Files", [])
        
        # Test 7: God Mode V2 Build Stream (HIGH PRIORITY)
        print("\n🔮 GOD MODE V2 TESTS")
        
        # POST /api/god-mode-v2/build/stream
        god_mode_payload = {
            "project_id": TEST_PROJECT_ID,
            "iterations": 1
        }
        await self.test_stream_request("/god-mode-v2/build/stream", "God Mode V2 Build Stream", god_mode_payload)
        
        # Test 8: Builds API (MEDIUM PRIORITY)
        print("\n🔨 BUILDS API TESTS")
        
        # GET /api/builds/{project_id} - Get builds for specific project
        await self.test_get_request(f"/builds/{TEST_PROJECT_ID}", "Get Project Builds", [])
        
        # POST /api/builds/start - Start a build
        build_start_payload = {
            "project_id": TEST_PROJECT_ID,
            "build_type": "prototype",
            "target_engine": "unreal",
            "estimated_hours": 2
        }
        await self.test_post_request("/builds/start", "Start Build", build_start_payload, ["id", "status"])
        
        # Test 9: Game Engine API (MEDIUM PRIORITY)
        print("\n🎮 GAME ENGINE API TESTS")
        
        # GET /api/game-engine/detect
        await self.test_get_request("/game-engine/detect", "Detect Game Engines", [])
        
        # GET /api/game-engine/config
        await self.test_get_request("/game-engine/config", "Get Game Engine Config", [])
        
        # Test 10: Settings API (LOW PRIORITY)
        print("\n⚙️ SETTINGS API TESTS")
        
        # GET /api/settings
        await self.test_get_request("/settings", "Get Settings", [])
        
        # PUT /api/settings (using POST)
        settings_payload = {
            "default_engine": "unreal",
            "theme": "dark",
            "auto_save_files": True
        }
        await self.test_post_request("/settings", "Update Settings", settings_payload, ["success"])
        
        # Test 11: Research API (LOW PRIORITY)
        print("\n🔬 RESEARCH API TESTS")
        
        # POST /api/research/search
        research_payload = {
            "query": "transformers",
            "source": "arxiv",
            "max_results": 5
        }
        await self.test_post_request("/research/search", "Research Search", research_payload, ["source", "results"])
        
        # Print Results Summary
        print("\n" + "=" * 60)
        print(f"📊 TEST RESULTS SUMMARY")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {self.passed/(self.passed + self.failed)*100:.1f}%")
        
        # List failed tests
        if self.failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for test_name, result in self.test_results.items():
                if not result["success"]:
                    error = result["details"].get("error", "Unknown")
                    print(f"   - {test_name}: {error}")
        
        return self.passed, self.failed

async def main():
    """Main test runner"""
    try:
        async with APITestRunner() as runner:
            passed, failed = await runner.run_all_tests()
            
            # Return appropriate exit code
            if failed > 0:
                print(f"\n⚠️  {failed} tests failed. See details above.")
                sys.exit(1)
            else:
                print(f"\n🎉 All {passed} tests passed!")
                sys.exit(0)
                
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())