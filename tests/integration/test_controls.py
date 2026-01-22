import pytest
from pydantic import BaseModel

from novu_framework import workflow


class CommentPayload(BaseModel):
    comment: str
    post_id: str


@pytest.mark.asyncio
async def test_workflow_with_controls_integration():
    """Test complete workflow with controls functionality."""

    @workflow("comment-notification")
    async def comment_workflow(payload: CommentPayload, step):
        # In-app notification step
        await step.in_app(
            "new-comment",
            lambda: {
                "body": f"New comment: {payload.comment}",
                "action_url": f"/posts/{payload.post_id}",
            },
        )

        # Email notification step with controls
        await step.email(
            "comment-email",
            lambda controls: {
                "subject": controls.get("subject", "New Comment"),
                "body": f"You received a new comment: {payload.comment}",
            },
            controlSchema={
                "type": "object",
                "properties": {"subject": {"type": "string", "default": "New Comment"}},
            },
        )

    # Trigger the workflow
    result = await comment_workflow.trigger(
        to="subscriber_id_123",
        payload={"comment": "This is a great post!", "post_id": "post_id_456"},
    )

    assert result["workflow_id"] == "comment-notification"
    assert result["status"] == "completed"
    assert "new-comment" in result["step_results"]
    assert "comment-email" in result["step_results"]

    # Verify the email step used the default subject (no controls provided)
    email_result = result["step_results"]["comment-email"]
    assert email_result["subject"] == "New Comment"
    assert "This is a great post!" in email_result["body"]


@pytest.mark.asyncio
async def test_workflow_with_controls_default_values():
    """Test workflow with controls using default values."""

    @workflow("test-controls-default")
    async def test_workflow(payload: dict, step):
        await step.email(
            "test-email",
            lambda controls: {
                "subject": controls.get("subject", "Default Subject"),
                "body": "Test body",
            },
            controlSchema={
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "default": "Default Subject"}
                },
            },
        )

    # Trigger without providing controls (should use defaults)
    result = await test_workflow.trigger(
        to="subscriber_id_123", payload={"test": "data"}
    )

    email_result = result["step_results"]["test-email"]
    assert email_result["subject"] == "Default Subject"
