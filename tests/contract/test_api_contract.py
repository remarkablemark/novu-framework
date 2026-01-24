import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from novu_framework import workflow
from novu_framework.constants import FRAMEWORK_VERSION, SDK_VERSION
from novu_framework.fastapi import serve
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
