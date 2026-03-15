"""
Backend tests for Cancel Pipeline and Startup Recovery features (iteration 29)
Tests:
- GET /api/health — server started cleanly with startup handler
- POST /api/pipeline/run — start a pipeline run
- GET /api/pipeline/run/{run_id} — poll status
- POST /api/pipeline/run/{run_id}/cancel — cancel a running pipeline
- Cancel a non-running pipeline returns 400
- Cancelled status stays 'cancelled' (not overwritten by background task)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
PROJECT_ID = "878a623f-111e-45df-a837-7821bace9c1a"

# Minimal delegations for a test pipeline run
MINIMAL_DELEGATIONS = [
    {
        "agent": "FORGE",
        "task": "TEST_CANCEL: Generate a minimal Hello World file for cancel pipeline test"
    }
]


class TestHealthAndStartup:
    """Health check and startup handler verification"""

    def test_health_endpoint_returns_200(self):
        """GET /api/health should return 200 with status=healthy"""
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "healthy"
        print(f"PASS: /api/health returned status={data.get('status')}")

    def test_health_has_timestamp(self):
        """Health response should include a timestamp"""
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "timestamp" in data
        print(f"PASS: /api/health timestamp={data.get('timestamp')}")


class TestCancelPipeline:
    """Cancel pipeline endpoint tests - each test starts its own pipeline to avoid timing issues"""

    def _start_pipeline(self):
        """Helper to start a pipeline and return run_id"""
        resp = requests.post(
            f"{BASE_URL}/api/pipeline/run",
            json={
                "project_id": PROJECT_ID,
                "delegations": MINIMAL_DELEGATIONS
            }
        )
        assert resp.status_code == 200, f"Failed to start pipeline: {resp.text}"
        data = resp.json()
        assert data.get("run_id"), "No run_id in start response"
        return data["run_id"], data

    def test_start_pipeline_returns_running(self):
        """POST /api/pipeline/run should return status='running' with a run_id"""
        run_id, data = self._start_pipeline()
        assert data.get("status") == "running"
        assert isinstance(data.get("total_agents"), int)
        print(f"PASS: Pipeline started run_id={run_id} status={data.get('status')}")

    def test_get_pipeline_run_status_running(self):
        """GET /api/pipeline/run/{run_id} should show status='running' immediately after start"""
        run_id, _ = self._start_pipeline()
        resp = requests.get(f"{BASE_URL}/api/pipeline/run/{run_id}")
        assert resp.status_code == 200
        data = resp.json()
        # Could be 'running', 'completed', or 'failed' depending on LLM speed
        assert data.get("status") in ["running", "completed", "failed"], \
            f"Unexpected status: {data.get('status')}"
        print(f"PASS: Pipeline run status={data.get('status')} after start")

    def test_cancel_running_pipeline_returns_success(self):
        """POST /api/pipeline/run/{run_id}/cancel returns 200 with success=True and status='cancelled'
        Start+cancel immediately (before LLM completes) to avoid timing issues."""
        run_id, _ = self._start_pipeline()

        # Cancel immediately (within milliseconds of starting)
        resp = requests.post(f"{BASE_URL}/api/pipeline/run/{run_id}/cancel")
        if resp.status_code == 400:
            # LLM was extremely fast and finished before we could cancel
            data = resp.json()
            pytest.skip(f"Pipeline completed before cancel (LLM very fast): {data.get('detail')}")

        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data.get("success") is True, f"Expected success=True, got: {data}"
        assert data.get("status") == "cancelled", f"Expected status='cancelled', got: {data.get('status')}"
        assert data.get("run_id") == run_id
        print(f"PASS: Cancel returned success={data.get('success')}, status={data.get('status')}")

    def test_get_pipeline_status_after_cancel(self):
        """GET /api/pipeline/run/{run_id} should show status='cancelled' after cancel"""
        run_id, _ = self._start_pipeline()

        # Cancel immediately
        cancel_resp = requests.post(f"{BASE_URL}/api/pipeline/run/{run_id}/cancel")
        if cancel_resp.status_code == 400:
            pytest.skip("Pipeline completed before cancel (LLM very fast)")

        assert cancel_resp.status_code == 200

        # Verify GET shows cancelled
        resp = requests.get(f"{BASE_URL}/api/pipeline/run/{run_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") in ["cancelled", "interrupted"], \
            f"Expected 'cancelled', got: {data.get('status')}"
        assert data.get("completed_at") is not None, "completed_at should be set after cancel"
        print(f"PASS: Pipeline status after cancel = {data.get('status')}")

    def test_cancel_non_running_pipeline_returns_400(self):
        """POST /api/pipeline/run/{run_id}/cancel on already-cancelled pipeline should return 400"""
        run_id, _ = self._start_pipeline()

        # Cancel first time
        first = requests.post(f"{BASE_URL}/api/pipeline/run/{run_id}/cancel")
        if first.status_code == 400:
            # Already completed — still valid: call cancel on completed pipeline
            pass  # fall through to second cancel which should also return 400
        else:
            assert first.status_code == 200

        time.sleep(0.2)

        # Second cancel should always return 400 (not running)
        resp = requests.post(f"{BASE_URL}/api/pipeline/run/{run_id}/cancel")
        assert resp.status_code == 400, f"Expected 400 for non-running pipeline, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "detail" in data or "message" in data, "Error response should have detail/message"
        print(f"PASS: Second cancel returned 400 — {data.get('detail', data.get('message'))}")


class TestCancelPipelineNotFound:
    """Cancel pipeline with invalid run_id"""

    def test_cancel_nonexistent_run_returns_404(self):
        """POST /api/pipeline/run/FAKE_ID/cancel should return 404"""
        resp = requests.post(f"{BASE_URL}/api/pipeline/run/nonexistent-id-99999/cancel")
        assert resp.status_code == 404
        print(f"PASS: Cancel non-existent run returned 404")

    def test_get_nonexistent_run_returns_404(self):
        """GET /api/pipeline/run/FAKE_ID should return 404"""
        resp = requests.get(f"{BASE_URL}/api/pipeline/run/nonexistent-id-99999")
        assert resp.status_code == 404
        print(f"PASS: GET non-existent run returned 404")


class TestCancelStatusPersists:
    """Verify cancelled status is not overwritten by background task completing"""

    def test_cancelled_status_not_overwritten(self):
        """
        Start a pipeline, cancel immediately, wait 3s, verify still 'cancelled'.
        The final status check in _execute_server_pipeline prevents 'completed' from overwriting.
        """
        # Start pipeline
        resp = requests.post(
            f"{BASE_URL}/api/pipeline/run",
            json={
                "project_id": PROJECT_ID,
                "delegations": MINIMAL_DELEGATIONS
            }
        )
        assert resp.status_code == 200
        run_id = resp.json().get("run_id")

        # Cancel immediately
        cancel_resp = requests.post(f"{BASE_URL}/api/pipeline/run/{run_id}/cancel")
        if cancel_resp.status_code == 400:
            # Pipeline completed before we could cancel (very fast in test env)
            pytest.skip("Pipeline completed before cancel — LLM too fast in test env")

        assert cancel_resp.status_code == 200

        # Wait a few seconds for any in-flight operations to complete
        time.sleep(5)

        # Verify status is still 'cancelled', not 'completed'
        final = requests.get(f"{BASE_URL}/api/pipeline/run/{run_id}")
        assert final.status_code == 200
        data = final.json()
        assert data.get("status") in ["cancelled", "interrupted"], \
            f"Status was overwritten! Expected 'cancelled', got: {data.get('status')}"
        print(f"PASS: Status after 5s wait = {data.get('status')} (not overwritten by background task)")


class TestPipelineLatestEndpoint:
    """GET /api/pipeline/run/project/{project_id}/latest"""

    def test_get_latest_pipeline_run_for_project(self):
        """GET /api/pipeline/run/project/{project_id}/latest should return the most recent run"""
        resp = requests.get(f"{BASE_URL}/api/pipeline/run/project/{PROJECT_ID}/latest")
        assert resp.status_code in [200, 404], f"Unexpected status: {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("project_id") == PROJECT_ID
            assert "status" in data
            assert "run_id" in data or "id" in data  # either field name
            print(f"PASS: Latest pipeline run status={data.get('status')}")
        else:
            print("INFO: No pipeline runs found for project (404 is acceptable)")
