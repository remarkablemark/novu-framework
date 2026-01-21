import pytest
from pydantic import BaseModel, ValidationError

from novu_framework.workflow import Workflow


class ValidationPayload(BaseModel):
    name: str
    age: int


@pytest.mark.asyncio
async def test_workflow_trigger_validation_error():
    """Test workflow trigger with payload validation error."""

    async def handler(payload, step):
        return {"processed": True}

    workflow_obj = Workflow("validation-error-workflow", handler, ValidationPayload)

    # Test with invalid payload that should raise ValidationError
    with pytest.raises(ValidationError):
        await workflow_obj.trigger(
            to="user-123",
            payload={"age": 30},  # Missing required 'name' field
            metadata={"source": "test"},
        )


@pytest.mark.asyncio
async def test_workflow_trigger_without_schema():
    """Test workflow trigger without payload schema (uses raw dict)."""

    async def handler(payload, step):
        await step.in_app(
            "test-step", lambda: {"message": f"Hello {payload.get('name', 'Unknown')}"}
        )
        return {"processed": True}

    workflow_obj = Workflow("no-schema-workflow", handler)

    result = await workflow_obj.trigger(
        to="user-123",
        payload={"name": "Test User", "extra": "data"},
        metadata={"source": "test"},
    )

    assert result["status"] == "completed"
    assert result["workflow_id"] == "no-schema-workflow"
    assert result["step_results"]["test-step"] == {"message": "Hello Test User"}
