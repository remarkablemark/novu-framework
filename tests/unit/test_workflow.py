from typing import Any, Dict

import pytest
from pydantic import BaseModel, ValidationError

from novu_framework.workflow import (  # isort:skip
    StepHandler,
    Workflow,
    WorkflowRegistry,
    workflow,
    workflow_registry,
)


class PayloadSchema(BaseModel):
    name: str
    age: int = 25


def test_workflow_initialization():
    """Test Workflow initialization with all parameters."""

    async def handler(payload, step):
        return {"processed": True}

    _workflow = Workflow(
        workflow_id="test-workflow",
        handler=handler,
        payload_schema=PayloadSchema,
        name="Test Workflow",
    )

    assert _workflow.workflow_id == "test-workflow"
    assert _workflow.handler == handler
    assert _workflow.payload_schema == PayloadSchema
    assert _workflow.name == "Test Workflow"
    assert _workflow.steps == []


def test_workflow_initialization_minimal():
    """Test Workflow initialization with minimal parameters."""

    async def handler(payload, step):
        return {"processed": True}

    _workflow = Workflow("minimal-workflow", handler)

    assert _workflow.workflow_id == "minimal-workflow"
    assert _workflow.handler == handler
    assert _workflow.payload_schema is None
    assert _workflow.name == "minimal-workflow"


async def test_workflow_trigger_with_payload_validation():
    """Test workflow trigger with payload validation."""

    async def handler(payload, step):
        await step.in_app("step-1", lambda: {"message": f"Hello {payload.name}"})
        return {"processed": True}

    _workflow = Workflow("validation-workflow", handler, PayloadSchema)

    await _workflow.trigger(
        to="user-123", payload={"name": "John", "age": 30}, metadata={"source": "test"}
    )

    # Since this is async, we need to await it in a real test
    # For now, just test the validation setup
    assert _workflow.payload_schema == PayloadSchema


def test_workflow_trigger_payload_validation_error():
    """Test workflow trigger with invalid payload."""

    async def handler(payload, step):
        return {"processed": True}

    _workflow = Workflow("error-workflow", handler, PayloadSchema)

    # Test that validation error would be raised
    with pytest.raises(ValidationError):
        # This should raise a validation error for missing required 'name' field
        _workflow.payload_schema(**{"age": 30})


def test_workflow_registry_register():
    """Test registering a workflow in the registry."""
    registry = WorkflowRegistry()

    async def handler(payload, step):
        return {"processed": True}

    _workflow = Workflow("registry-test", handler)
    registry.register(_workflow)

    assert "registry-test" in registry.workflows
    assert registry.get("registry-test") == _workflow


def test_workflow_registry_register_duplicate():
    """Test registering a duplicate workflow ID raises error."""
    registry = WorkflowRegistry()

    async def handler1(payload, step):
        return {"processed": True}

    async def handler2(payload, step):
        return {"processed": True}

    _workflow1 = Workflow("duplicate-test", handler1)
    _workflow2 = Workflow("duplicate-test", handler2)

    registry.register(_workflow1)

    with pytest.raises(ValueError, match="already exists"):
        registry.register(_workflow2)


def test_workflow_registry_get_not_found():
    """Test getting a workflow that doesn't exist."""
    registry = WorkflowRegistry()

    assert registry.get("nonexistent") is None


def test_workflow_registry_clear():
    """Test clearing the registry."""
    registry = WorkflowRegistry()

    async def handler(payload, step):
        return {"processed": True}

    _workflow = Workflow("clear-test", handler)
    registry.register(_workflow)

    assert len(registry.workflows) == 1
    registry.clear()
    assert len(registry.workflows) == 0


def test_workflow_decorator_auto_payload_schema():
    """Test workflow decorator automatically extracts payload schema."""
    # Use a fresh registry for this test
    workflow_registry.clear()

    @workflow("auto-schema-workflow")
    async def workflow_with_payload(payload: PayloadSchema, step):
        return {"processed": True}

    # Check that the workflow was registered with the correct schema
    _workflow = workflow_registry.get("auto-schema-workflow")
    assert _workflow is not None
    assert _workflow.payload_schema == PayloadSchema


def test_workflow_decorator_first_param_schema():
    """Test workflow decorator extracts schema from first parameter."""
    workflow_registry.clear()

    @workflow("first-param-workflow")
    async def workflow_with_first_param(data: PayloadSchema, step):
        return {"processed": True}

    _workflow = workflow_registry.get("first-param-workflow")
    assert _workflow is not None
    assert _workflow.payload_schema == PayloadSchema


def test_workflow_decorator_no_schema():
    """Test workflow decorator when no schema can be extracted."""
    workflow_registry.clear()

    @workflow("no-schema-workflow")
    async def workflow_without_schema(payload: Dict[str, Any], step):
        return {"processed": True}

    _workflow = workflow_registry.get("no-schema-workflow")
    assert _workflow is not None
    assert _workflow.payload_schema is None


@pytest.mark.asyncio
async def test_step_handler_skip_function():
    """Test StepHandler with skip function."""

    async def test_step():
        return {"result": "test"}

    handler = StepHandler({"test": "data"})

    # Test with skip function that returns True
    def skip_true():
        return True

    result = await handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="skip-step",
        resolver=test_step,
        skip=skip_true,
    )

    assert result == {"skipped": True}
    assert handler.step_results["skip-step"] == {"skipped": True}


@pytest.mark.asyncio
async def test_step_handler_skip_async_function():
    """Test StepHandler with async skip function."""

    async def test_step():
        return {"result": "test"}

    async def async_skip():
        return True

    handler = StepHandler({"test": "data"})

    result = await handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="async-skip-step",
        resolver=test_step,
        skip=async_skip,
    )

    assert result == {"skipped": True}


@pytest.mark.asyncio
async def test_step_handler_resolver_with_args():
    """Test StepHandler resolver that expects arguments."""
    handler = StepHandler({"test": "data"})

    def resolver_with_args(payload):
        return {"payload": payload}

    result = await handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="args-step",
        resolver=resolver_with_args,
    )

    assert result["payload"] == {"test": "data"}
