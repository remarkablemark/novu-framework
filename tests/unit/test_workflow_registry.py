import pytest

from novu_framework.workflow import workflow, workflow_registry


def test_workflow_registration():
    """Test that the @workflow decorator registers the workflow in the registry."""

    # Clear registry before test
    workflow_registry.clear()

    @workflow("test-workflow")
    async def my_workflow(payload, step):
        pass

    assert "test-workflow" in workflow_registry.workflows
    registered_workflow = workflow_registry.workflows["test-workflow"]
    assert registered_workflow.workflow_id == "test-workflow"


def test_duplicate_workflow_registration_error():
    """Test that registering a duplicate workflow ID raises an error."""
    workflow_registry.clear()

    @workflow("duplicate-workflow")
    async def first_workflow(payload, step):
        pass

    with pytest.raises(
        ValueError, match="Workflow with ID 'duplicate-workflow' already exists"
    ):

        @workflow("duplicate-workflow")
        async def second_workflow(payload, step):
            pass
