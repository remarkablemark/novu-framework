import pytest

from novu_framework.workflow import workflow


@pytest.mark.asyncio
async def test_workflow_trigger_execution():
    """Test that trigger executes the workflow handler."""

    execution_flag = {"executed": False, "payload": None}

    @workflow("trigger-test")
    def my_workflow(payload, step):
        execution_flag["executed"] = True
        execution_flag["payload"] = payload
        return {"status": "success"}

    payload_data = {"foo": "bar"}
    result = await my_workflow.trigger(to="user-123", payload=payload_data)

    assert execution_flag["executed"] is True
    assert execution_flag["payload"] == payload_data
    assert result["status"] == "completed"
    assert result["workflow_id"] == "trigger-test"
    assert result["payload"] == payload_data
