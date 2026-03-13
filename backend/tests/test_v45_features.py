"""
Test Suite for AgentForge v4.5 "SHOULDN'T EXIST" Features
Tests all 8 new features:
1. Goal Loop - autonomous run-until-done with quality thresholds
2. Global Knowledge Graph - cross-project intelligence
3. Multi-Future Build - parallel architecture exploration
4. Autonomous Refactor Engine - auto code improvement
5. Mission Control - real-time agent activity feed
6. Deployment Pipeline - CI/CD with auto-deploy
7. Self-Expansion Modules - system creates its own tools
8. Idea-to-Reality Pipeline - one-click from concept to deployed product
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
PROJECT_ID = "cfdcd129-6ca5-4616-997b-c615daaa64de"

@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestAPIVersionAndHealth:
    """Verify API version is 4.5.0 with 41 features"""
    
    def test_api_version(self, api_client):
        """Check API version is 4.5.0"""
        response = api_client.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        
        assert "version" in data
        assert data["version"] == "4.5.0", f"Expected version 4.5.0, got {data['version']}"
        
        assert "features" in data
        assert len(data["features"]) == 41, f"Expected 41 features, got {len(data['features'])}"
        
        # Check key v4.5 features are present
        expected_features = [
            "goal_loop", "knowledge_graph", "multi_future_build",
            "autonomous_refactor", "mission_control", "deployment_pipeline",
            "system_modules", "reality_pipeline"
        ]
        for feature in expected_features:
            assert feature in data["features"], f"Missing feature: {feature}"
        
        print(f"API version: {data['version']} with {len(data['features'])} features")


class TestGoalLoop:
    """Test Goal Loop - Run Until Done feature"""
    
    def test_start_goal_loop(self, api_client):
        """POST /api/goal-loop/{project_id}/start - Start autonomous goal loop"""
        goal = "Build a simple calculator app"
        response = api_client.post(
            f"{BASE_URL}/api/goal-loop/{PROJECT_ID}/start",
            params={"goal": goal, "max_cycles": 20}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "project_id" in data
        assert data["project_id"] == PROJECT_ID
        assert "goal" in data
        assert data["goal"] == goal
        assert "status" in data
        assert data["status"] in ["running", "success"]
        
        # Verify cycles
        assert "cycles" in data
        assert isinstance(data["cycles"], list)
        assert len(data["cycles"]) > 0
        
        # Verify each cycle has required fields
        cycle = data["cycles"][0]
        assert "cycle" in cycle
        assert "agent" in cycle
        assert "action" in cycle
        assert "result" in cycle
        
        # Verify metrics
        assert "current_metrics" in data
        metrics = data["current_metrics"]
        assert "tests_pass_rate" in metrics
        assert "performance_score" in metrics
        assert "code_quality" in metrics
        assert "demo_playable" in metrics
        
        # Verify thresholds tracking
        assert "thresholds_met" in data
        
        print(f"Goal Loop started: {len(data['cycles'])} cycles, status: {data['status']}")
        print(f"Metrics: tests={metrics['tests_pass_rate']}%, perf={metrics['performance_score']}%, quality={metrics['code_quality']}%")
    
    def test_get_goal_loops(self, api_client):
        """GET /api/goal-loop/{project_id} - Get all goal loops"""
        response = api_client.get(f"{BASE_URL}/api/goal-loop/{PROJECT_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} goal loops")
    
    def test_get_active_goal_loop(self, api_client):
        """GET /api/goal-loop/{project_id}/active - Get active loop"""
        response = api_client.get(f"{BASE_URL}/api/goal-loop/{PROJECT_ID}/active")
        assert response.status_code == 200
        # May be None if no active loop
        print("Active goal loop endpoint working")


class TestKnowledgeGraph:
    """Test Global Knowledge Graph feature"""
    
    def test_add_knowledge(self, api_client):
        """POST /api/knowledge/add - Add knowledge entry"""
        response = api_client.post(
            f"{BASE_URL}/api/knowledge/add",
            params={
                "entry_type": "pattern",
                "title": "TEST_Auth Pattern v4.5",
                "description": "JWT authentication pattern for testing",
                "category": "auth",
                "tags": ["auth", "jwt", "test"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["entry_type"] == "pattern"
        assert data["title"] == "TEST_Auth Pattern v4.5"
        assert data["category"] == "auth"
        assert "tags" in data
        
        print(f"Knowledge entry added: {data['id']}")
    
    def test_get_knowledge_stats(self, api_client):
        """GET /api/knowledge/stats - Get knowledge statistics"""
        response = api_client.get(f"{BASE_URL}/api/knowledge/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_entries" in data
        assert "total_reuses" in data
        assert "by_type" in data
        assert "by_category" in data
        
        print(f"Knowledge stats: {data['total_entries']} entries, {data['total_reuses']} reuses")
    
    def test_get_all_knowledge(self, api_client):
        """GET /api/knowledge/all - Get all knowledge entries"""
        response = api_client.get(f"{BASE_URL}/api/knowledge/all")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} knowledge entries")
    
    def test_search_knowledge(self, api_client):
        """GET /api/knowledge/search - Search knowledge"""
        response = api_client.get(
            f"{BASE_URL}/api/knowledge/search",
            params={"query": "auth"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Search returned {len(data)} results")
    
    def test_extract_knowledge_from_project(self, api_client):
        """POST /api/knowledge/extract/{project_id} - Extract patterns"""
        response = api_client.post(f"{BASE_URL}/api/knowledge/extract/{PROJECT_ID}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "extracted" in data
        assert "count" in data
        
        print(f"Extracted {data['count']} patterns from project")


class TestArchitectureExploration:
    """Test Multi-Future Build - Architecture Exploration"""
    
    def test_start_exploration(self, api_client):
        """POST /api/explore/{project_id}/start - Start architecture exploration"""
        response = api_client.post(
            f"{BASE_URL}/api/explore/{PROJECT_ID}/start",
            params={"goal": "Build scalable e-commerce platform"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "project_id" in data
        assert "goal" in data
        assert "status" in data
        
        # Should have 3 variants
        assert "variants" in data
        assert len(data["variants"]) == 3, f"Expected 3 variants, got {len(data['variants'])}"
        
        # Should have comparison report
        assert "comparison_report" in data
        assert "recommendation" in data
        
        print(f"Exploration started with {len(data['variants'])} architecture variants")
        print(f"Recommendation: {data['recommendation']}")
    
    def test_get_explorations(self, api_client):
        """GET /api/explore/{project_id} - Get explorations"""
        response = api_client.get(f"{BASE_URL}/api/explore/{PROJECT_ID}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} architecture explorations")


class TestRefactorEngine:
    """Test Autonomous Refactor Engine"""
    
    def test_scan_for_refactoring(self, api_client):
        """POST /api/refactor/{project_id}/scan - Scan for issues"""
        response = api_client.post(f"{BASE_URL}/api/refactor/{PROJECT_ID}/scan")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "project_id" in data
        assert "status" in data
        
        # Should detect issues
        assert "inefficiencies" in data
        assert "code_smells" in data
        assert "performance_issues" in data
        
        # Should have metrics
        assert "before_metrics" in data
        metrics = data["before_metrics"]
        assert "total_lines" in metrics or "total_files" in metrics
        
        total_issues = len(data["inefficiencies"]) + len(data["code_smells"]) + len(data["performance_issues"])
        print(f"Refactor scan complete: {total_issues} issues found")
        print(f"- Inefficiencies: {len(data['inefficiencies'])}")
        print(f"- Code smells: {len(data['code_smells'])}")
        print(f"- Performance issues: {len(data['performance_issues'])}")
    
    def test_get_refactor_jobs(self, api_client):
        """GET /api/refactor/{project_id} - Get refactor jobs"""
        response = api_client.get(f"{BASE_URL}/api/refactor/{PROJECT_ID}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} refactor jobs")


class TestMissionControl:
    """Test Mission Control - Real-time Activity Feed"""
    
    def test_get_mission_control_status(self, api_client):
        """GET /api/mission-control/{project_id}/status - Get status with agent info"""
        response = api_client.get(f"{BASE_URL}/api/mission-control/{PROJECT_ID}/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "project_id" in data
        assert "active_build" in data
        assert "active_goal_loop" in data
        
        # Verify agents are returned
        assert "agents" in data
        agents = data["agents"]
        expected_agents = ["COMMANDER", "ATLAS", "FORGE", "SENTINEL", "PROBE", "PRISM"]
        for agent_name in expected_agents:
            assert agent_name in agents, f"Missing agent: {agent_name}"
            assert "status" in agents[agent_name]
        
        # Verify event counts
        assert "recent_events" in data
        assert "errors" in data
        assert "warnings" in data
        
        print(f"Mission Control status: {len(agents)} agents tracked")
        print(f"Active build: {data['active_build']}, Active loop: {data['active_goal_loop']}")
    
    def test_get_mission_control_feed(self, api_client):
        """GET /api/mission-control/{project_id}/feed - Get event feed"""
        response = api_client.get(
            f"{BASE_URL}/api/mission-control/{PROJECT_ID}/feed",
            params={"limit": 20}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Mission control feed: {len(data)} events")
    
    def test_add_mission_control_event(self, api_client):
        """POST /api/mission-control/{project_id}/event - Add event"""
        response = api_client.post(
            f"{BASE_URL}/api/mission-control/{PROJECT_ID}/event",
            params={
                "event_type": "test_event",
                "title": "TEST_v4.5 Test Event",
                "description": "Testing event creation",
                "agent_name": "PROBE",
                "severity": "info"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["event_type"] == "test_event"
        assert data["agent_name"] == "PROBE"
        
        print(f"Mission control event added: {data['id']}")


class TestDeploymentPipeline:
    """Test Autonomous Deployment Pipeline"""
    
    def test_create_deployment_pipeline(self, api_client):
        """POST /api/pipeline/{project_id}/create - Create pipeline"""
        response = api_client.post(
            f"{BASE_URL}/api/pipeline/{PROJECT_ID}/create",
            params={"target_platform": "vercel", "auto_deploy": False}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "project_id" in data
        assert "target_platform" in data
        assert data["target_platform"] == "vercel"
        assert "status" in data
        assert "stages" in data
        
        # Verify stages structure
        stages = data["stages"]
        assert len(stages) == 5
        stage_names = [s["name"] for s in stages]
        expected_stages = ["lint", "test", "build", "deploy", "verify"]
        assert stage_names == expected_stages
        
        print(f"Pipeline created: {data['id']} with {len(stages)} stages")
        return data["id"]
    
    def test_get_project_pipelines(self, api_client):
        """GET /api/pipeline/{project_id} - Get pipelines"""
        response = api_client.get(f"{BASE_URL}/api/pipeline/{PROJECT_ID}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} deployment pipelines")


class TestSystemModules:
    """Test Self-Expansion System Modules"""
    
    def test_create_system_module(self, api_client):
        """POST /api/modules/create - Create system module"""
        response = api_client.post(
            f"{BASE_URL}/api/modules/create",
            params={
                "name": "TEST_auth_scaffold_v45",
                "module_type": "scaffold",
                "description": "Authentication scaffold for testing",
                "detected_need": "Multiple projects need auth patterns",
                "auto_created": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["name"] == "TEST_auth_scaffold_v45"
        assert data["module_type"] == "scaffold"
        assert data["auto_created"] == True
        assert "times_used" in data
        
        print(f"System module created: {data['id']}")
    
    def test_get_system_modules(self, api_client):
        """GET /api/modules - Get all active modules"""
        response = api_client.get(f"{BASE_URL}/api/modules")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} active system modules")
    
    def test_auto_generate_modules(self, api_client):
        """POST /api/modules/auto-generate/{project_id} - Auto-detect patterns"""
        response = api_client.post(f"{BASE_URL}/api/modules/auto-generate/{PROJECT_ID}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "patterns_detected" in data
        assert "modules_created" in data
        
        print(f"Patterns detected: {data['patterns_detected']}")
        print(f"Modules created: {data['modules_created']}")


class TestRealityPipeline:
    """Test Idea-to-Reality Pipeline"""
    
    def test_start_reality_pipeline(self, api_client):
        """POST /api/reality-pipeline/start - Full idea-to-deployed pipeline"""
        idea = "TEST_AI-powered task manager for remote teams"
        response = api_client.post(
            f"{BASE_URL}/api/reality-pipeline/start",
            params={"idea": idea}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "idea" in data
        assert data["idea"] == idea
        assert "status" in data
        assert data["status"] == "live"
        
        # Verify all phases completed
        assert "phases" in data
        phases = data["phases"]
        assert len(phases) == 9
        
        expected_phases = [
            "Intake", "Clarification", "Architecture", "Asset Generation",
            "Code Generation", "Code Review", "Testing", "Deployment", "Verification"
        ]
        for i, phase in enumerate(phases):
            assert phase["name"] == expected_phases[i]
            assert phase["status"] == "complete"
            assert "agent" in phase
        
        # Verify outputs
        assert "project_id" in data
        assert "deploy_url" in data
        assert data["deploy_url"] is not None
        
        assert "files_created" in data
        assert len(data["files_created"]) > 0
        
        assert "assets_generated" in data
        assert len(data["assets_generated"]) > 0
        
        assert "test_results" in data
        assert data["test_results"]["passed"] > 0
        
        print(f"Reality Pipeline complete!")
        print(f"- Deploy URL: {data['deploy_url']}")
        print(f"- Files created: {len(data['files_created'])}")
        print(f"- Assets: {len(data['assets_generated'])}")
        print(f"- Tests: {data['test_results']['passed']} passed")
    
    def test_get_reality_pipelines(self, api_client):
        """GET /api/reality-pipeline - Get all pipelines"""
        response = api_client.get(f"{BASE_URL}/api/reality-pipeline")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} reality pipelines")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_data(self, api_client):
        """Cleanup TEST_ prefixed data (informational only)"""
        # This is informational - actual cleanup would require DELETE endpoints
        # Just verify test data exists
        response = api_client.get(f"{BASE_URL}/api/knowledge/all")
        if response.status_code == 200:
            data = response.json()
            test_entries = [e for e in data if "TEST_" in e.get("title", "")]
            print(f"Test knowledge entries that would be cleaned: {len(test_entries)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
