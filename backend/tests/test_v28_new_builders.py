"""
Test Suite for AgentForge AI OS - Iteration 28
Testing: Mobile Builder, Cloud Builder, Auto Deploy, AI Review APIs
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMobileBuilderAPI:
    """Mobile Builder API Tests - React Native, Flutter, Native iOS/Android support"""
    
    def test_get_frameworks(self):
        """Test GET /api/mobile-builder/frameworks"""
        response = requests.get(f"{BASE_URL}/api/mobile-builder/frameworks")
        assert response.status_code == 200
        data = response.json()
        # Verify frameworks exist
        assert 'react_native' in data
        assert 'flutter' in data
        assert 'native_ios' in data
        assert 'native_android' in data
        # Verify structure
        assert data['react_native']['name'] == 'React Native'
        assert 'JavaScript' in data['react_native']['language']
        print("PASS: Mobile Builder frameworks endpoint working")
    
    def test_get_templates(self):
        """Test GET /api/mobile-builder/templates"""
        response = requests.get(f"{BASE_URL}/api/mobile-builder/templates")
        assert response.status_code == 200
        data = response.json()
        # Verify templates exist
        assert 'social' in data
        assert 'ecommerce' in data
        assert 'fitness' in data
        assert 'delivery' in data
        assert 'news' in data
        assert 'blank' in data
        # Verify structure
        assert 'name' in data['social']
        assert 'screens' in data['social']
        assert 'features' in data['social']
        print("PASS: Mobile Builder templates endpoint working")
    
    def test_get_screen_types(self):
        """Test GET /api/mobile-builder/screen-types"""
        response = requests.get(f"{BASE_URL}/api/mobile-builder/screen-types")
        assert response.status_code == 200
        data = response.json()
        # Verify screen types
        assert 'home' in data
        assert 'list' in data
        assert 'detail' in data
        assert 'form' in data
        assert 'profile' in data
        print("PASS: Mobile Builder screen-types endpoint working")
    
    def test_create_mobile_app(self):
        """Test POST /api/mobile-builder/apps"""
        payload = {
            "name": f"TEST_MobileApp_{uuid.uuid4().hex[:8]}",
            "description": "Test mobile app for iteration 28",
            "framework": "react_native",
            "platforms": ["ios", "android"],
            "features": ["Authentication"],
            "style": "modern"
        }
        response = requests.post(f"{BASE_URL}/api/mobile-builder/apps", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'app_id' in data
        assert data['status'] == 'generating'
        assert data['framework'] == 'React Native'
        print(f"PASS: Created mobile app with ID: {data['app_id']}")
        return data['app_id']
    
    def test_list_mobile_apps(self):
        """Test GET /api/mobile-builder/apps"""
        response = requests.get(f"{BASE_URL}/api/mobile-builder/apps")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Listed {len(data)} mobile apps")
    
    def test_get_mobile_app_detail(self):
        """Test GET /api/mobile-builder/apps/{app_id} and DELETE"""
        # First create an app
        app_id = self.test_create_mobile_app()
        
        # Get app details
        response = requests.get(f"{BASE_URL}/api/mobile-builder/apps/{app_id}")
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == app_id
        assert 'framework' in data
        assert 'name' in data
        print(f"PASS: Got mobile app details for {app_id}")
        
        # Cleanup - Delete the app
        delete_response = requests.delete(f"{BASE_URL}/api/mobile-builder/apps/{app_id}")
        assert delete_response.status_code == 200
        print(f"PASS: Deleted mobile app {app_id}")
    
    def test_get_nonexistent_app(self):
        """Test GET /api/mobile-builder/apps/{nonexistent}"""
        response = requests.get(f"{BASE_URL}/api/mobile-builder/apps/nonexistent-app-id")
        assert response.status_code == 404
        print("PASS: 404 returned for nonexistent mobile app")


class TestCloudBuilderAPI:
    """Cloud Builder API Tests - AWS, GCP, Azure with Terraform"""
    
    def test_get_providers(self):
        """Test GET /api/cloud-builder/providers"""
        response = requests.get(f"{BASE_URL}/api/cloud-builder/providers")
        assert response.status_code == 200
        data = response.json()
        # Verify providers
        assert 'aws' in data
        assert 'gcp' in data
        assert 'azure' in data
        # Verify AWS structure
        assert data['aws']['name'] == 'Amazon Web Services'
        assert 'regions' in data['aws']
        assert 'services' in data['aws']
        # Verify services categories
        assert 'compute' in data['aws']['services']
        assert 'database' in data['aws']['services']
        print("PASS: Cloud Builder providers endpoint working")
    
    def test_get_architecture_templates(self):
        """Test GET /api/cloud-builder/templates"""
        response = requests.get(f"{BASE_URL}/api/cloud-builder/templates")
        assert response.status_code == 200
        data = response.json()
        # Verify templates
        assert 'web_app' in data
        assert 'microservices' in data
        assert 'serverless' in data
        assert 'data_pipeline' in data
        assert 'ml_platform' in data
        # Verify structure
        assert 'name' in data['web_app']
        assert 'components' in data['web_app']
        print("PASS: Cloud Builder architecture templates endpoint working")
    
    def test_get_provider_services(self):
        """Test GET /api/cloud-builder/providers/{provider}/services"""
        for provider in ['aws', 'gcp', 'azure']:
            response = requests.get(f"{BASE_URL}/api/cloud-builder/providers/{provider}/services")
            assert response.status_code == 200
            data = response.json()
            assert 'compute' in data
            assert 'database' in data
            assert 'storage' in data
            print(f"PASS: Got services for {provider}")
    
    def test_get_invalid_provider_services(self):
        """Test GET /api/cloud-builder/providers/{invalid}/services"""
        response = requests.get(f"{BASE_URL}/api/cloud-builder/providers/invalid_provider/services")
        assert response.status_code == 400
        print("PASS: 400 returned for invalid provider")
    
    def test_create_infrastructure(self):
        """Test POST /api/cloud-builder/infrastructures"""
        payload = {
            "name": f"TEST_Infra_{uuid.uuid4().hex[:8]}",
            "description": "Test infrastructure for iteration 28",
            "provider": "aws",
            "iac_tool": "terraform",
            "region": "us-east-1",
            "components": ["compute", "database"],
            "environment": "development"
        }
        response = requests.post(f"{BASE_URL}/api/cloud-builder/infrastructures", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'infra_id' in data
        assert data['status'] == 'generating'
        assert data['provider'] == 'Amazon Web Services'
        print(f"PASS: Created infrastructure with ID: {data['infra_id']}")
        return data['infra_id']
    
    def test_list_infrastructures(self):
        """Test GET /api/cloud-builder/infrastructures"""
        response = requests.get(f"{BASE_URL}/api/cloud-builder/infrastructures")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Listed {len(data)} infrastructures")
    
    def test_get_infrastructure_detail(self):
        """Test GET /api/cloud-builder/infrastructures/{infra_id} and DELETE"""
        # First create an infrastructure
        infra_id = self.test_create_infrastructure()
        
        # Get infrastructure details
        response = requests.get(f"{BASE_URL}/api/cloud-builder/infrastructures/{infra_id}")
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == infra_id
        assert 'provider' in data
        assert 'components' in data or 'status' in data
        print(f"PASS: Got infrastructure details for {infra_id}")
        
        # Cleanup - Delete the infrastructure
        delete_response = requests.delete(f"{BASE_URL}/api/cloud-builder/infrastructures/{infra_id}")
        assert delete_response.status_code == 200
        print(f"PASS: Deleted infrastructure {infra_id}")
    
    def test_get_nonexistent_infrastructure(self):
        """Test GET /api/cloud-builder/infrastructures/{nonexistent}"""
        response = requests.get(f"{BASE_URL}/api/cloud-builder/infrastructures/nonexistent-infra-id")
        assert response.status_code == 404
        print("PASS: 404 returned for nonexistent infrastructure")


class TestAutoDeployAPI:
    """Auto Deploy API Tests - Vercel, Railway, Netlify deployment"""
    
    def test_get_platforms(self):
        """Test GET /api/auto-deploy/platforms"""
        response = requests.get(f"{BASE_URL}/api/auto-deploy/platforms")
        assert response.status_code == 200
        data = response.json()
        # Verify platforms
        assert 'vercel' in data
        assert 'railway' in data
        assert 'netlify' in data
        # Verify structure
        assert data['vercel']['name'] == 'Vercel'
        assert 'features' in data['vercel']
        assert 'deploy_url' in data['vercel']
        print("PASS: Auto Deploy platforms endpoint working")
    
    def test_list_deployments(self):
        """Test GET /api/auto-deploy/deployments"""
        response = requests.get(f"{BASE_URL}/api/auto-deploy/deployments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Listed {len(data)} deployments")
    
    def test_get_config(self):
        """Test GET /api/auto-deploy/config/{platform}"""
        for platform in ['vercel', 'railway', 'netlify']:
            response = requests.get(f"{BASE_URL}/api/auto-deploy/config/{platform}")
            assert response.status_code == 200
            data = response.json()
            assert 'platform' in data or 'configured' in data
            print(f"PASS: Got config for {platform}")
    
    def test_save_config(self):
        """Test POST /api/auto-deploy/config"""
        payload = {
            "platform": "vercel",
            "api_key": "test_key_12345",
            "auto_deploy_enabled": True
        }
        response = requests.post(f"{BASE_URL}/api/auto-deploy/config", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'saved'
        assert data['platform'] == 'vercel'
        print("PASS: Saved deploy config")
    
    def test_deploy_without_session(self):
        """Test POST /api/auto-deploy/deploy with nonexistent session"""
        payload = {
            "god_mode_session_id": "nonexistent-session-id",
            "platform": "vercel",
            "project_name": "test-project"
        }
        response = requests.post(f"{BASE_URL}/api/auto-deploy/deploy", json=payload)
        # Should return 404 for nonexistent session
        assert response.status_code == 404
        print("PASS: 404 returned for nonexistent God Mode session")
    
    def test_get_nonexistent_deployment(self):
        """Test GET /api/auto-deploy/deployments/{nonexistent}"""
        response = requests.get(f"{BASE_URL}/api/auto-deploy/deployments/nonexistent-deploy-id")
        assert response.status_code == 404
        print("PASS: 404 returned for nonexistent deployment")


class TestAIReviewAPI:
    """AI Code Review API Tests - Pattern-based code analysis"""
    
    def test_get_patterns(self):
        """Test GET /api/ai-review/patterns"""
        response = requests.get(f"{BASE_URL}/api/ai-review/patterns")
        assert response.status_code == 200
        data = response.json()
        # Verify language patterns exist
        assert 'react' in data
        assert 'python' in data
        assert 'javascript' in data
        assert 'general' in data
        # Verify pattern structure
        assert len(data['react']) > 0
        assert 'message' in data['react'][0]
        assert 'severity' in data['react'][0]
        assert 'category' in data['react'][0]
        print("PASS: AI Review patterns endpoint working")
    
    def test_review_single_file(self):
        """Test POST /api/ai-review/review-file"""
        payload = {
            "content": """
import React from 'react';

const TestComponent = () => {
    const [state, setState] = React.useState(null);
    console.log('debug');  // TODO: remove this
    
    return items.map(item => <div>{item}</div>);
};

export default TestComponent;
            """,
            "filename": "TestComponent.jsx",
            "language": "react"
        }
        response = requests.post(f"{BASE_URL}/api/ai-review/review-file", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'filename' in data
        assert 'issues' in data
        assert 'summary' in data
        # Should find console.log and TODO
        assert len(data['issues']) > 0
        assert 'grade' in data['summary']
        assert 'health_score' in data['summary']
        print(f"PASS: Code review found {len(data['issues'])} issues, grade: {data['summary']['grade']}")
    
    def test_review_python_file(self):
        """Test POST /api/ai-review/review-file with Python code"""
        payload = {
            "content": """
def process_data(data):
    try:
        result = eval(data)
        password = "secret123"
    except:
        pass
    return result
            """,
            "filename": "processor.py",
            "language": "auto"
        }
        response = requests.post(f"{BASE_URL}/api/ai-review/review-file", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data['language'] == 'python'
        # Should find bare except, eval, and hardcoded secret
        assert len(data['issues']) >= 2
        print(f"PASS: Python code review found {len(data['issues'])} issues")
    
    def test_review_clean_code(self):
        """Test POST /api/ai-review/review-file with clean code"""
        payload = {
            "content": """
const add = (a, b) => a + b;
const multiply = (a, b) => a * b;
            """,
            "filename": "math.js",
            "language": "javascript"
        }
        response = requests.post(f"{BASE_URL}/api/ai-review/review-file", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Clean code should have high score
        assert data['summary']['health_score'] >= 80
        print(f"PASS: Clean code review - health score: {data['summary']['health_score']}")
    
    def test_review_project_without_project(self):
        """Test POST /api/ai-review/review without valid project"""
        payload = {
            "project_id": "nonexistent-project-id",
            "review_type": "full",
            "severity_threshold": "low"
        }
        response = requests.post(f"{BASE_URL}/api/ai-review/review", json=payload)
        assert response.status_code == 404
        print("PASS: 404 returned for nonexistent project")
    
    def test_get_nonexistent_review(self):
        """Test GET /api/ai-review/review/{nonexistent}"""
        response = requests.get(f"{BASE_URL}/api/ai-review/review/nonexistent-review-id")
        assert response.status_code == 404
        print("PASS: 404 returned for nonexistent review")


class TestGameBuilderAPIConfirmation:
    """Confirmation tests for Game Builder API (already tested in iteration 27)"""
    
    def test_detect_endpoint(self):
        """Test GET /api/game-builder/detect"""
        response = requests.get(f"{BASE_URL}/api/game-builder/detect")
        assert response.status_code == 200
        data = response.json()
        assert 'os' in data
        assert 'engines' in data
        print("PASS: Game Builder detect endpoint working")
    
    def test_templates_endpoint(self):
        """Test GET /api/game-builder/templates/{engine}"""
        response = requests.get(f"{BASE_URL}/api/game-builder/templates/unreal")
        assert response.status_code == 200
        data = response.json()
        assert 'blank' in data
        print("PASS: Game Builder templates endpoint working")
    
    def test_projects_endpoint(self):
        """Test GET /api/game-builder/projects"""
        response = requests.get(f"{BASE_URL}/api/game-builder/projects")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("PASS: Game Builder projects endpoint working")


class TestHealthAndIntegration:
    """Health checks and cross-feature integration tests"""
    
    def test_health_endpoint(self):
        """Test GET /api/health"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        print("PASS: Health endpoint working")
    
    def test_all_new_routes_registered(self):
        """Verify all new routes are accessible"""
        endpoints = [
            "/api/mobile-builder/frameworks",
            "/api/mobile-builder/templates",
            "/api/cloud-builder/providers",
            "/api/cloud-builder/templates",
            "/api/auto-deploy/platforms",
            "/api/auto-deploy/deployments",
            "/api/ai-review/patterns",
            "/api/game-builder/detect"
        ]
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"Failed: {endpoint}"
            print(f"PASS: {endpoint} accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
