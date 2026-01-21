import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from novu_framework import workflow
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
    Test that the discovery endpoint returns the correct structure matching
    HealthCheckResponse.
    """
    response = client.get("/api/novu")
    assert response.status_code == 200
    data = response.json()

    # Check top-level fields
    assert "workflows" in data
    assert "frameworkVersion" in data
    assert "sdkVersion" in data
    assert isinstance(data["workflows"], list)

    # Check workflow structure
    if len(data["workflows"]) > 0:
        workflow = data["workflows"][0]
        assert "workflowId" in workflow
        assert "name" in workflow
        assert "steps" in workflow
        assert "payloadSchema" in workflow


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
