# Quickstart Guide: Python Framework Package

**Purpose**: Get started with the Python notification workflow framework in minutes
**Date**: 2026-01-20
**Version**: 1.0.0

## Installation

```bash
pip install novu-framework
```

## Basic Usage

### 1. Define Your First Workflow

```python
from novu_framework import workflow
from pydantic import BaseModel

class PayloadSchema(BaseModel):
    comment: str
    post_id: str

@workflow('comment-notification')
async def comment_workflow(payload: CommentPayload, step):
    # In-app notification step
    await step.in_app('new-comment', async () => ({
        'body': f'New comment on your post: {payload.comment}',
        'action_url': f'/posts/{payload.post_id}'
    }))

    # Email notification step
    await step.email(
        'comment-email',
        async (controls) => ({
            'subject': f'{controls.prefix} - New Comment',
            'body': f'You received a new comment: {payload.comment}'
        }),
        control_schema={
            'prefix': {
                'type': 'string',
                'description': 'Email subject prefix',
                'default': 'Notification'
            }
        }
    )
```

### 2. Trigger Your Workflow

```python
# Import your workflow
from your_workflows import comment_workflow

# Trigger workflow
await comment_workflow.trigger(
    to='subscriber_id_123',
    payload={
        'comment': 'This is a great post!',
        'post_id': 'post_id_456'
    }
)
```

### 3. FastAPI Integration

```python
# Import your workflow
from your_workflows import comment_workflow

# Create FastAPI app with Novu workflows
from fastapi import FastAPI
from novu_framework.fastapi import serve

app = FastAPI()
serve(app, route='/api/novu', workflows=[comment_workflow])
```

## Advanced Features

### Multi-Step Workflows with Digests

```python
from novu_framework import workflow, CronExpression
from pydantic import BaseModel

class ActivityPayload(BaseModel):
    activity: str
    user_id: str

@workflow('weekly-activity-digest')
async def activity_digest_workflow(payload: ActivityPayload, step):
    # Immediate in-app notification
    await step.in_app('activity', async () => ({
        'body': f'New activity: {payload.activity}'
    }))

    # Weekly digest
    weekly_digest = await step.digest('weekly-summary', async () => ({
        'cron': CronExpression.EVERY_WEEK,
        'timezone': 'UTC'
    }))

    # Email digest (skipped if no activities)
    await step.email(
        'weekly-email',
        async (controls) => ({
            'subject': f'{controls.prefix} - Weekly Activity Summary',
            'body': f'Activities this week: {len(weekly_digest.events)}'
        }),
        skip=lambda: len(weekly_digest.events) == 0,
        control_schema={
            'prefix': {
                'type': 'string',
                'description': 'Email subject prefix',
                'default': 'Weekly Digest'
            }
        }
    )
```

### Conditional Step Execution

```python
@workflow('conditional-notifications')
async def conditional_workflow(payload: CommentPayload, step):
    # Only send in-app for active users
    await step.in_app(
        'conditional-in-app',
        async () => ({
            'body': f'Comment: {payload.comment}'
        }),
        skip=lambda: payload.comment.startswith('[spam]')
    )

    # Always send email to moderators
    await step.email('moderator-alert', async () => ({
        'subject': 'New Comment Requires Review',
        'body': f'Comment: {payload.comment}'
    }))
```

### Custom Step Types

```python
from novu_framework.steps.base import BaseStep

class CustomSlackStep(BaseStep):
    step_type = 'SLACK'

    async def execute(self, context):
        # Custom Slack integration logic
        message = self.config.get('message', 'Default message')
        await self.send_slack_message(message)
        return {'status': 'sent', 'message': message}

# Register custom step
from novu_framework import register_step_type
register_step_type('SLACK', CustomSlackStep)

@workflow('slack-workflow')
async def slack_workflow(payload: CommentPayload, step):
    await step.slack('slack-notification', async () => ({
        'message': f'New comment: {payload.comment}'
    }))
```

## Testing

### Unit Tests

```python
import pytest
from novu_framework.testing import WorkflowTestClient
from your_workflows import comment_workflow

@pytest.mark.asyncio
async def test_comment_workflow():
    client = WorkflowTestClient()

    # Test workflow execution
    result = await client.trigger_workflow(
        workflow=comment_workflow,
        recipient='user:123',
        data={
            'comment': 'Test comment',
            'post_id': 'post-456'
        }
    )

    assert result.status == 'completed'
    assert 'in_app' in result.step_results
    assert 'email' in result.step_results
```

### Integration Tests

```python
import pytest
from httpx import AsyncClient
from your_app import app

@pytest.mark.asyncio
async def test_workflow_api():
    async with AsyncClient(app=app, base_url="https://example.com") as client:
        response = await client.get("/api/novu")
        assert response.status_code == 200
        content = response.json()
        assert "sdkVersion" in content
        assert "frameworkVersion" in content
        assert content["status"] == "ok"
        assert content["discovered"]["workflows"] > 0
        assert content["discovered"]["steps"] > 0
```

## Best Practices

### 1. Workflow Design

- Keep workflows focused on single business logic
- Use descriptive workflow and step names
- Validate payloads with Pydantic models
- Handle errors gracefully with try/catch blocks

### 2. Performance

- Use async/await for I/O operations
- Configure appropriate timeouts

### 3. Security

- Validate all input data
- Use secure communication channels
- Implement proper authentication
