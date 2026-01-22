import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from novu_framework import workflow
from novu_framework.constants import FRAMEWORK_VERSION, SDK_VERSION
from novu_framework.fastapi import serve
from novu_framework.workflow import workflow_registry


class PayloadSchema(BaseModel):
    name: str


@pytest.fixture
def client():
    workflow_registry.clear()
    app = FastAPI()
    serve(app, workflows=[])
    return TestClient(app)


def test_health_check_empty_workflows(client):
    """Test discovery endpoint with no workflows."""
    response = client.get("/api/novu")
    assert response.status_code == 200
    data = response.json()
    assert data["workflows"] == []
    assert data["frameworkVersion"] == FRAMEWORK_VERSION
    assert data["sdkVersion"] == SDK_VERSION


def test_health_check_with_payload_schema():
    """Test discovery endpoint with workflow that has payload schema."""
    workflow_registry.clear()
    app = FastAPI()

    @workflow("schema-workflow", payload_schema=PayloadSchema)
    async def schema_workflow(payload: PayloadSchema, step):
        await step.in_app("step-1", lambda: {"message": f"Hello {payload.name}"})
        return {"processed": True}

    serve(app, workflows=[schema_workflow])
    client = TestClient(app)

    response = client.get("/api/novu")
    assert response.status_code == 200
    data = response.json()
    assert len(data["workflows"]) == 1
    workflow_data = data["workflows"][0]
    assert workflow_data["workflowId"] == "schema-workflow"
    assert "payloadSchema" in workflow_data
    assert workflow_data["payloadSchema"]["type"] == "object"
    assert workflow_data["payloadSchema"]["properties"]["name"]["type"] == "string"


def test_health_check_payload_schema_fallback():
    """Test discovery endpoint with workflow that has non-Pydantic payload schema."""
    workflow_registry.clear()
    app = FastAPI()

    class NonPydanticSchema:
        pass

    @workflow("fallback-workflow", payload_schema=NonPydanticSchema)
    async def fallback_workflow(payload, step):
        await step.in_app("step-1", lambda: {"message": "fallback"})
        return {"processed": True}

    serve(app, workflows=[fallback_workflow])
    client = TestClient(app)

    response = client.get("/api/novu")
    assert response.status_code == 200
    data = response.json()
    workflow_data = data["workflows"][0]
    assert workflow_data["payloadSchema"] == {}


def test_execute_workflow_not_found(client):
    """Test executing a workflow that doesn't exist."""
    response = client.post(
        "/api/novu/workflows/nonexistent/execute",
        json={"to": "user-123", "payload": {"name": "World"}},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_execute_workflow_with_error():
    """Test executing a workflow that raises an exception."""
    workflow_registry.clear()
    app = FastAPI()

    @workflow("error-workflow")
    async def error_workflow(payload, step):
        raise ValueError("Test error")

    serve(app, workflows=[error_workflow])
    client = TestClient(app)

    response = client.post(
        "/api/novu/workflows/error-workflow/execute",
        json={"to": "user-123", "payload": {"name": "World"}},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Test error"


def test_serve_with_workflow_objects():
    """Test serve function with workflow objects (not wrapped functions)."""
    workflow_registry.clear()
    app = FastAPI()

    from novu_framework.workflow import Workflow

    async def handler(payload, step):
        await step.in_app("step-1", lambda: {"message": "direct object"})
        return {"processed": True}

    workflow_obj = Workflow("direct-workflow", handler)
    serve(app, workflows=[workflow_obj])
    client = TestClient(app)

    response = client.get("/api/novu")
    assert response.status_code == 200
    data = response.json()
    assert len(data["workflows"]) == 1
    assert data["workflows"][0]["workflowId"] == "direct-workflow"
