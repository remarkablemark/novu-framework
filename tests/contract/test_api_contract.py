import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from flask import Flask

from novu_framework import workflow
from novu_framework.constants import FRAMEWORK_VERSION, SDK_VERSION
from novu_framework.fastapi import serve
from novu_framework.flask import serve as flask_serve
from novu_framework.workflow import workflow_registry


@pytest.fixture
def client():
    # Clear registry to avoid conflicts
    workflow_registry.clear()

    app = FastAPI()

    @workflow("test-workflow")
    async def test_workflow(payload, step):
        pass

    serve(app, workflows=[test_workflow])
    return TestClient(app)


def test_health_check_endpoint_structure(client):
    """
    Test that the health check endpoint returns the correct structure matching
    HealthCheckResponse.
    """
    response = client.get("/api/novu")
    assert response.status_code == 200
    data = response.json()

    expected = {
        "status": "ok",
        "frameworkVersion": FRAMEWORK_VERSION,
        "sdkVersion": SDK_VERSION,
        "discovered": {"workflows": 1, "steps": 0},
    }
    assert data == expected


def test_execution_endpoint_structure(client):
    """
    Test that the execution endpoint accepts the correct structure.
    """
    # We need to mock the handler or ensure it runs successfully.
    # Our test_workflow has a pass handler, so it should be fine.

    response = client.post(
        "/api/novu/workflows/test-workflow/execute",
        json={"to": "user-123", "payload": {"foo": "bar"}},
    )

    assert response.status_code == 200
    # The response from execute_workflow is just the result of workflow.trigger
    # which returns a dict.
    data = response.json()
    assert data["status"] == "completed"
    assert data["workflow_id"] == "test-workflow"


@pytest.fixture
def flask_client():
    # Clear registry to avoid conflicts
    workflow_registry.clear()

    app = Flask(__name__)

    @workflow("test-workflow-flask")
    async def test_workflow_flask(payload, step):
        pass

    flask_serve(app, workflows=[test_workflow_flask])
    return app.test_client()


def test_flask_health_check_endpoint_structure(flask_client):
    """
    Test that the Flask health check endpoint returns the correct structure matching
    HealthCheckResponse and is compatible with FastAPI.
    """
    response = flask_client.get("/api/novu")
    assert response.status_code == 200
    data = response.get_json()

    expected = {
        "status": "ok",
        "frameworkVersion": FRAMEWORK_VERSION,
        "sdkVersion": SDK_VERSION,
        "discovered": {"workflows": 1, "steps": 0},
    }
    assert data == expected


def test_flask_execution_endpoint_structure(flask_client):
    """
    Test that the Flask execution endpoint accepts the correct structure
    and is compatible with FastAPI.
    """
    response = flask_client.post(
        "/api/novu/workflows/test-workflow-flask/execute",
        json={"to": "user-123", "payload": {"foo": "bar"}},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "completed"
    assert data["workflow_id"] == "test-workflow-flask"


def test_flask_error_handling_compatibility(flask_client):
    """
    Test that Flask error handling matches FastAPI error format.
    """
    # Test 404 error
    response = flask_client.post(
        "/api/novu/workflows/non-existent-workflow/execute",
        json={"to": "user-123", "payload": {"foo": "bar"}},
    )
    assert response.status_code == 404
    data = response.get_json()
    assert "detail" in data
    assert "non-existent-workflow" in data["detail"]

    # Test 400 error
    response = flask_client.post(
        "/api/novu/workflows/test-workflow-flask/execute",
        json={},  # Missing required fields
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "detail" in data
