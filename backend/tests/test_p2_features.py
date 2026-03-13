"""
P2 Features Backend Tests
=========================
Tests for:
- Redis/Celery setup (GET /api/celery/stats, POST /api/celery/jobs/submit)
- Expanded SaaS templates (24 total)
- Cloudflare Pages deployment option
- Core APIs health check
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


# ==============================================================================
# Fixtures
# ==============================================================================
@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def test_project_id(api_client):
    """Get or create a test project for job submission tests"""
    # First try to get existing projects
    response = api_client.get(f"{BASE_URL}/api/projects")
    if response.status_code == 200:
        projects = response.json()
        if projects and len(projects) > 0:
            return projects[0].get("id")
    
    # Create a test project if none exist
    response = api_client.post(f"{BASE_URL}/api/projects", json={
        "name": "TEST_P2_Project",
        "description": "Test project for P2 features"
    })
    if response.status_code in [200, 201]:
        return response.json().get("id")
    
    return None


# ==============================================================================
# Core Health Check Tests
# ==============================================================================
class TestCoreAPIs:
    """Verify core APIs are still working after P2 changes"""
    
    def test_health_endpoint(self, api_client):
        """GET /api/health - Returns healthy status"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✅ Health check passed: {data}")
    
    def test_projects_endpoint(self, api_client):
        """GET /api/projects - Returns projects list"""
        response = api_client.get(f"{BASE_URL}/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Projects endpoint working: {len(data)} projects")
    
    def test_agents_endpoint(self, api_client):
        """GET /api/agents - Returns agents list"""
        response = api_client.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 6  # Should have at least 6 agents
        print(f"✅ Agents endpoint working: {len(data)} agents")


# ==============================================================================
# Redis/Celery Tests
# ==============================================================================
class TestCeleryIntegration:
    """Tests for Celery task queue functionality"""
    
    def test_celery_stats_endpoint(self, api_client):
        """GET /api/celery/stats - Returns Celery statistics"""
        response = api_client.get(f"{BASE_URL}/api/celery/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected stats fields
        assert "total_jobs" in data
        assert "queued" in data
        assert "running" in data
        assert "completed" in data
        assert "failed" in data
        assert "celery_available" in data
        
        print(f"✅ Celery stats: {data}")
    
    def test_celery_job_submission(self, api_client, test_project_id):
        """POST /api/celery/jobs/submit - Submit a job to queue"""
        if not test_project_id:
            pytest.skip("No test project available")
        
        response = api_client.post(
            f"{BASE_URL}/api/celery/jobs/submit",
            params={
                "project_id": test_project_id,
                "job_type": "build",
                "priority": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify job was created
        assert "id" in data
        assert data.get("project_id") == test_project_id
        assert data.get("job_type") == "build"
        assert data.get("status") == "queued"
        assert data.get("priority") == 5
        
        print(f"✅ Job submitted successfully: {data['id']}")
        return data["id"]
    
    def test_celery_job_retrieval(self, api_client, test_project_id):
        """Test submitting and then retrieving a job"""
        if not test_project_id:
            pytest.skip("No test project available")
        
        # Submit a job first
        submit_response = api_client.post(
            f"{BASE_URL}/api/celery/jobs/submit",
            params={
                "project_id": test_project_id,
                "job_type": "test",
                "priority": 3
            }
        )
        assert submit_response.status_code == 200
        job_id = submit_response.json().get("id")
        
        # Retrieve the job
        get_response = api_client.get(f"{BASE_URL}/api/celery/jobs/{job_id}")
        assert get_response.status_code == 200
        job_data = get_response.json()
        
        assert job_data.get("id") == job_id
        assert job_data.get("project_id") == test_project_id
        print(f"✅ Job retrieved: {job_id}")
    
    def test_celery_workers_endpoint(self, api_client):
        """GET /api/celery/workers - Returns workers list"""
        response = api_client.get(f"{BASE_URL}/api/celery/workers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Note: workers list may be empty if no Celery workers are running
        print(f"✅ Celery workers endpoint: {len(data)} workers")


# ==============================================================================
# SaaS Templates Tests (Expanded to 24)
# ==============================================================================
class TestSaaSTemplates:
    """Tests for expanded SaaS template collection"""
    
    def test_templates_endpoint(self, api_client):
        """GET /api/saas-factory/templates - Returns 24 templates"""
        response = api_client.get(f"{BASE_URL}/api/saas-factory/templates")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        template_count = len(data)
        assert template_count == 24, f"Expected 24 templates, got {template_count}"
        
        print(f"✅ SaaS templates count: {template_count}")
        return data
    
    def test_original_templates_present(self, api_client):
        """Verify original 8 templates are still present"""
        response = api_client.get(f"{BASE_URL}/api/saas-factory/templates")
        assert response.status_code == 200
        data = response.json()
        
        original_templates = [
            "analytics", "marketplace", "subscription_box", "saas_boilerplate",
            "ai_tool", "community", "course_platform", "appointment_booking"
        ]
        
        for template in original_templates:
            assert template in data, f"Original template '{template}' missing"
        
        print(f"✅ All 8 original templates present")
    
    def test_new_templates_present(self, api_client):
        """Verify 16 new templates are present"""
        response = api_client.get(f"{BASE_URL}/api/saas-factory/templates")
        assert response.status_code == 200
        data = response.json()
        
        new_templates = [
            "crm", "project_management", "helpdesk", "invoice_billing",
            "email_marketing", "survey_forms", "hr_platform", "social_scheduler",
            "link_shortener", "newsletter", "job_board", "document_signing",
            "fitness_app", "event_platform", "real_estate", "podcast_platform"
        ]
        
        for template in new_templates:
            assert template in data, f"New template '{template}' missing"
            # Verify template structure
            template_data = data[template]
            assert "name" in template_data
            assert "description" in template_data
            assert "features" in template_data
            assert "pricing_tiers" in template_data
            assert "tech_stack" in template_data
        
        print(f"✅ All 16 new templates present with correct structure")
    
    def test_crm_template_details(self, api_client):
        """Verify CRM template has correct structure"""
        response = api_client.get(f"{BASE_URL}/api/saas-factory/templates")
        assert response.status_code == 200
        data = response.json()
        
        crm = data.get("crm")
        assert crm is not None
        assert crm["name"] == "CRM System"
        assert "contacts" in crm["features"]
        assert "deals" in crm["features"]
        assert "pipeline" in crm["features"]
        print(f"✅ CRM template verified: {crm['name']}")
    
    def test_project_management_template_details(self, api_client):
        """Verify Project Management template"""
        response = api_client.get(f"{BASE_URL}/api/saas-factory/templates")
        assert response.status_code == 200
        data = response.json()
        
        pm = data.get("project_management")
        assert pm is not None
        assert pm["name"] == "Project Management"
        assert "tasks" in pm["features"]
        assert "boards" in pm["features"]
        print(f"✅ Project Management template verified: {pm['name']}")
    
    def test_helpdesk_template_details(self, api_client):
        """Verify Helpdesk template"""
        response = api_client.get(f"{BASE_URL}/api/saas-factory/templates")
        assert response.status_code == 200
        data = response.json()
        
        helpdesk = data.get("helpdesk")
        assert helpdesk is not None
        assert helpdesk["name"] == "Helpdesk & Support"
        assert "tickets" in helpdesk["features"]
        assert "live_chat" in helpdesk["features"]
        print(f"✅ Helpdesk template verified: {helpdesk['name']}")
    
    def test_invoice_billing_template_details(self, api_client):
        """Verify Invoice & Billing template"""
        response = api_client.get(f"{BASE_URL}/api/saas-factory/templates")
        assert response.status_code == 200
        data = response.json()
        
        invoice = data.get("invoice_billing")
        assert invoice is not None
        assert invoice["name"] == "Invoice & Billing"
        assert "invoices" in invoice["features"]
        assert "recurring_billing" in invoice["features"]
        print(f"✅ Invoice & Billing template verified: {invoice['name']}")
    
    def test_email_marketing_template_details(self, api_client):
        """Verify Email Marketing template"""
        response = api_client.get(f"{BASE_URL}/api/saas-factory/templates")
        assert response.status_code == 200
        data = response.json()
        
        email = data.get("email_marketing")
        assert email is not None
        assert email["name"] == "Email Marketing"
        assert "campaigns" in email["features"]
        assert "automation" in email["features"]
        print(f"✅ Email Marketing template verified: {email['name']}")


# ==============================================================================
# Cloud Deploy Tests (Cloudflare Option)
# ==============================================================================
class TestCloudDeploy:
    """Tests for Cloud Deployment with Cloudflare option"""
    
    def test_deploy_status_endpoint(self, api_client):
        """GET /api/cloud-deploy/status - Returns deployment platform status"""
        response = api_client.get(f"{BASE_URL}/api/cloud-deploy/status")
        assert response.status_code == 200
        data = response.json()
        
        # Verify Vercel platform
        assert "vercel" in data
        assert "connected" in data["vercel"]
        assert "features" in data["vercel"]
        
        # Verify Cloudflare platform
        assert "cloudflare" in data
        assert "connected" in data["cloudflare"]
        assert "features" in data["cloudflare"]
        
        # Verify Cloudflare has expected features
        cloudflare_features = data["cloudflare"]["features"]
        assert "pages" in cloudflare_features
        assert "workers" in cloudflare_features
        assert "r2_storage" in cloudflare_features
        
        print(f"✅ Cloud deploy status: Vercel={data['vercel']['connected']}, Cloudflare={data['cloudflare']['connected']}")
    
    def test_deployments_list_endpoint(self, api_client):
        """GET /api/cloud-deploy/deployments - Returns deployments list"""
        response = api_client.get(f"{BASE_URL}/api/cloud-deploy/deployments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Deployments list: {len(data)} deployments")


# ==============================================================================
# SaaS Factory Integration Tests
# ==============================================================================
class TestSaaSFactoryIntegrations:
    """Tests for SaaS Factory integration status"""
    
    def test_integrations_endpoint(self, api_client):
        """GET /api/saas-factory/integrations - Returns integration status"""
        response = api_client.get(f"{BASE_URL}/api/saas-factory/integrations")
        assert response.status_code == 200
        data = response.json()
        
        # Verify Stripe integration info
        assert "stripe" in data
        assert "connected" in data["stripe"]
        assert "features" in data["stripe"]
        
        # Verify Supabase integration info
        assert "supabase" in data
        assert "connected" in data["supabase"]
        assert "features" in data["supabase"]
        
        # Verify Vercel integration info  
        assert "vercel" in data
        assert "connected" in data["vercel"]
        assert "features" in data["vercel"]
        
        print(f"✅ Integrations: Stripe={data['stripe']['connected']}, Supabase={data['supabase']['connected']}, Vercel={data['vercel']['connected']}")
    
    def test_saas_builds_endpoint(self, api_client):
        """GET /api/saas-factory/builds - Returns SaaS builds list"""
        response = api_client.get(f"{BASE_URL}/api/saas-factory/builds")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ SaaS builds list: {len(data)} builds")


# ==============================================================================
# Run all tests if executed directly
# ==============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
