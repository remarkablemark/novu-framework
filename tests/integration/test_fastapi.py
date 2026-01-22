import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from novu_framework import workflow
from novu_framework.fastapi import serve
from novu_framework.workflow import workflow_registry


@pytest.fixture
def client():
    # Clear registry
    workflow_registry.clear()

    app = FastAPI()

    @workflow("integration-workflow")
    async def integration_workflow(payload, step):
        await step.in_app("step-1", {"message": f"Hello {payload['name']}"})
        return {"processed": True}

    serve(app, workflows=[integration_workflow])
    return TestClient(app)


def test_full_workflow_execution_via_api(client):
    """
    Test full workflow execution via FastAPI endpoint.
    """
    # 1. Discover workflows
    response = client.get("/api/novu")
    assert response.status_code == 200
    data = response.json()
    assert data["discovered"]["workflows"] == 1
    assert data["discovered"]["steps"] == 1

    # 2. Execute workflow
    response = client.post(
        "/api/novu/workflows/integration-workflow/execute",
        json={"to": "user-integration", "payload": {"name": "World"}},
    )

    assert response.status_code == 200
    result = response.json()

    assert result["status"] == "completed"
    assert result["workflow_id"] == "integration-workflow"
    assert result["step_results"]["step-1"] == {"message": "Hello World"}
