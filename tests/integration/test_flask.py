"""
Integration tests for Flask integration.
"""

import pytest
from flask import Flask

from novu_framework import workflow
from novu_framework.flask import serve
from novu_framework.workflow import workflow_registry


@pytest.fixture
def flask_app():
    # Clear registry to avoid conflicts
    workflow_registry.clear()

    app = Flask(__name__)

    @workflow("integration-test-workflow")
    def integration_workflow(payload, step):
        step.in_app("test-notification", {"message": "test message"})
        return {"status": "completed", "workflow_id": "integration-test-workflow"}

    @workflow("multi-step-workflow")
    def multi_step_workflow(payload, step):
        step.in_app("step1", {"message": "step 1"})
        step.email("step2", lambda: {"subject": "test", "body": "test body"})
        return {"status": "completed", "workflow_id": "multi-step-workflow"}

    serve(app, workflows=[integration_workflow, multi_step_workflow])
    return app


def test_flask_app_setup(flask_app):
    """Test that Flask app is properly set up with Novu workflows."""
    with flask_app.test_client() as client:
        response = client.get("/api/novu")
        assert response.status_code == 200
        data = response.get_json()
        assert data["discovered"]["workflows"] == 2


def test_workflow_discovery(flask_app):
    """Test workflow discovery endpoint."""
    with flask_app.test_client() as client:
        response = client.get("/api/novu")
        assert response.status_code == 200
        data = response.get_json()

        # Should discover both workflows
        assert data["discovered"]["workflows"] == 2
        # Should count steps correctly
        assert data["discovered"]["steps"] == 3  # 1 step + 2 steps


def test_workflow_execution(flask_app):
    """Test workflow execution endpoint."""
    with flask_app.test_client() as client:
        response = client.post(
            "/api/novu/workflows/integration-test-workflow/execute",
            json={"to": "user-123", "payload": {"test": "data"}},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "completed"
        assert data["workflow_id"] == "integration-test-workflow"


def test_multi_step_workflow_execution(flask_app):
    """Test execution of multi-step workflows."""
    with flask_app.test_client() as client:
        response = client.post(
            "/api/novu/workflows/multi-step-workflow/execute",
            json={"to": "user-456", "payload": {"test": "multi-step"}},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "completed"
        assert data["workflow_id"] == "multi-step-workflow"


def test_workflow_not_found(flask_app):
    """Test 404 error for non-existent workflow."""
    with flask_app.test_client() as client:
        response = client.post(
            "/api/novu/workflows/non-existent/execute",
            json={"to": "user-123", "payload": {}},
        )

        assert response.status_code == 404
        data = response.get_json()
        assert "detail" in data
        assert "non-existent" in data["detail"]


def test_invalid_payload(flask_app):
    """Test 400 error for invalid payload."""
    with flask_app.test_client() as client:
        response = client.post(
            "/api/novu/workflows/integration-test-workflow/execute",
            json={},  # Missing required 'to' and 'payload' fields
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "detail" in data


def test_invalid_json(flask_app):
    """Test 400 error for invalid JSON."""
    with flask_app.test_client() as client:
        response = client.post(
            "/api/novu/workflows/integration-test-workflow/execute",
            data="invalid json",
            content_type="application/json",
        )

        assert response.status_code == 400
