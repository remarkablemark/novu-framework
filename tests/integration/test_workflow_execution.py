import pytest

from novu_framework import workflow
from novu_framework.workflow import workflow_registry


@pytest.mark.asyncio
async def test_multi_step_workflow_execution():
    """Test execution of a workflow with multiple steps."""

    # Clear registry before test
    workflow_registry.clear()

    @workflow("multi-step-workflow")
    def multi_step_workflow(payload, step):
        step.in_app("in-app-step", lambda: {"body": "Hello"})
        step.email("email-step", lambda: {"subject": "Hi", "body": "There"})
        step.sms("sms-step", lambda: {"body": "SMS"}, skip=lambda: True)

    result = await multi_step_workflow.trigger(to="user-1", payload={"some": "data"})

    assert result["status"] == "completed"
    assert result["workflow_id"] == "multi-step-workflow"
    assert "in-app-step" in result["step_results"]
    assert result["step_results"]["in-app-step"] == {"body": "Hello"}
    assert "email-step" in result["step_results"]
    assert result["step_results"]["email-step"] == {"subject": "Hi", "body": "There"}
    assert "sms-step" in result["step_results"]
    assert result["step_results"]["sms-step"] == {"skipped": True}


@pytest.mark.asyncio
async def test_workflow_skip_logic():
    """Test dynamic skip logic in steps."""

    # Clear registry before test
    workflow_registry.clear()

    @workflow("skip-logic-workflow")
    def skip_workflow(payload, step):
        # Should be executed
        step.in_app("step-1", lambda: {"val": 1}, skip=lambda: False)
        # Should be skipped
        step.in_app("step-2", lambda: {"val": 2}, skip=lambda: True)
        # Should be skipped based on payload
        step.in_app("step-3", lambda: {"val": 3}, skip=lambda: payload["should_skip"])

    result = await skip_workflow.trigger(to="user-1", payload={"should_skip": True})

    results = result["step_results"]
    assert results["step-1"] == {"val": 1}
    assert results["step-2"] == {"skipped": True}
    assert results["step-3"] == {"skipped": True}
