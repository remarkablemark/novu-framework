import pytest
from pydantic import BaseModel

from novu_framework.workflow import workflow, workflow_registry


class SimpleTestPayload(BaseModel):
    name: str


def test_workflow_decorator_basic():
    """Test basic workflow decorator functionality."""
    # Clear any existing workflows
    workflow_registry.clear()

    @workflow("basic-workflow")
    async def basic_workflow(payload, step):
        return {"processed": True}

    # Check that workflow was registered
    workflow_obj = workflow_registry.get("basic-workflow")
    assert workflow_obj is not None
    assert workflow_obj.workflow_id == "basic-workflow"


def test_workflow_decorator_with_explicit_schema():
    """Test workflow decorator with explicitly provided schema."""
    workflow_registry.clear()

    @workflow("explicit-schema-workflow", payload_schema=SimpleTestPayload)
    async def explicit_workflow(payload, step):
        return {"processed": True}

    workflow_obj = workflow_registry.get("explicit-schema-workflow")
    assert workflow_obj is not None
    assert workflow_obj.payload_schema == SimpleTestPayload


def test_workflow_decorator_with_name():
    """Test workflow decorator with custom name."""
    workflow_registry.clear()

    @workflow("named-workflow", name="Custom Workflow Name")
    async def named_workflow(payload, step):
        return {"processed": True}

    workflow_obj = workflow_registry.get("named-workflow")
    assert workflow_obj is not None
    assert workflow_obj.name == "Custom Workflow Name"


@pytest.mark.asyncio
async def test_workflow_trigger_full_execution():
    """Test full workflow trigger execution."""
    workflow_registry.clear()

    @workflow("full-execution-workflow", payload_schema=SimpleTestPayload)
    async def full_workflow(payload: SimpleTestPayload, step):
        await step.in_app("test-step", lambda: {"message": f"Hello {payload.name}"})
        return {"processed": True}

    result = await full_workflow.trigger(
        to="user-123", payload={"name": "Test User"}, metadata={"source": "test"}
    )

    assert result["status"] == "completed"
    assert result["workflow_id"] == "full-execution-workflow"
    assert "step_results" in result
    assert result["step_results"]["test-step"] == {"message": "Hello Test User"}
