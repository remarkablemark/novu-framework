import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from novu_framework import workflow
from novu_framework.fastapi import serve

# --- Quickstart Example 1: Define Workflow ---


class CommentPayload(BaseModel):
    comment: str
    post_id: str


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

    # Email notification step
    await step.email(
        "comment-email",
        lambda: {
            "subject": "New Comment",
            "body": f"You received a new comment: {payload.comment}",
        },
    )


# --- Tests ---


@pytest.mark.asyncio
async def test_quickstart_trigger():
    """Test Quickstart Example 2: Trigger Your Workflow"""

    # Clean registry just in case
    # Note: Registry is global, so previous definitions persist unless cleared.
    # ideally we should clear before defining the workflow but we defined it at module
    # level. Let's hope no ID conflict with other tests if run in same session,
    # but pytest collects files so module scope is usually fine if names are unique.

    result = await comment_workflow.trigger(
        to="subscriber_id_123",
        payload={"comment": "This is a great post!", "post_id": "post_id_456"},
    )

    assert result["status"] == "completed"
    assert "new-comment" in result["step_results"]
    assert result["step_results"]["new-comment"] == {
        "body": "New comment: This is a great post!",
        "action_url": "/posts/post_id_456",
    }
    assert "comment-email" in result["step_results"]


def test_quickstart_fastapi():
    """Test Quickstart Example 3: FastAPI Integration"""
    app = FastAPI()
    serve(app, route="/api/novu", workflows=[comment_workflow])

    client = TestClient(app)

    # Test discovery
    response = client.get("/api/novu")
    assert response.status_code == 200
    data = response.json()
    assert len(data["workflows"]) >= 1
    found = False
    for wf in data["workflows"]:
        if wf["workflowId"] == "comment-notification":
            found = True
            break
    assert found

    # Test execution via API
    response = client.post(
        "/api/novu/workflows/comment-notification/execute",
        json={
            "to": "subscriber_id_123",
            "payload": {"comment": "This is a great post!", "post_id": "post_id_456"},
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "completed"
