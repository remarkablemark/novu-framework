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

class ControlSchema(BaseModel):
    prefix: str = 'Notification'

@workflow('comment-notification')
def comment_workflow(payload: CommentPayload, step):
    # In-app notification step
    step.in_app('new-comment', {
        'body': f'New comment on your post: {payload.comment}',
        'action_url': f'/posts/{payload.post_id}'
    })

    # Email notification step
    step.email(
        'comment-email',
        lambda controls: {
            'subject': f'{controls.prefix} - New Comment',
            'body': f'You received a new comment: {payload.comment}'
        },
        control_schema=ControlSchema
    )
```

### 2. Trigger Your Workflow

```python
# Import your workflow
from your_workflows import comment_workflow

# Trigger workflow
comment_workflow.trigger(
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

class PayloadSchema(BaseModel):
    activity: str
    user_id: str

class ControlSchema(BaseModel):
    prefix: str = 'Weekly Digest'

@workflow('weekly-activity-digest')
def activity_digest_workflow(payload: PayloadSchema, step):
    # Immediate in-app notification
    step.in_app('activity', {
        'body': f'New activity: {payload.activity}'
    })

    # Weekly digest
    weekly_digest = step.digest('weekly-summary', {
        'cron': CronExpression.EVERY_WEEK,
        'timezone': 'UTC'
    })

    # Email digest (skipped if no activities)
    step.email(
        'weekly-email',
        lambda controls: {
            'subject': f'{controls.prefix} - Weekly Activity Summary',
            'body': f'Activities this week: {len(weekly_digest.events)}'
        },
        skip=lambda controls: len(weekly_digest.events) == 0,
        control_schema=ControlSchema,
    )
```

### Conditional Step Execution

```python
@workflow('conditional-notifications')
def conditional_workflow(payload: PayloadSchema, step):
    # Only send in-app for active users
    step.in_app(
        'conditional-in-app',
        {
            'body': f'Comment: {payload.comment}'
        },
        skip=lambda controls: payload.comment.startswith('[spam]')
    )

    # Always send email to moderators
    step.email('moderator-alert', {
        'subject': 'New Comment Requires Review',
        'body': f'Comment: {payload.comment}'
    })
```

### Custom Step Types

```python
from novu_framework.steps.base import BaseStep

class CustomSlackStep(BaseStep):
    step_type = 'SLACK'

    def execute(self, context):
        # Custom Slack integration logic
        message = self.config.get('message', 'Default message')
        self.send_slack_message(message)
        return {'status': 'sent', 'message': message}

# Register custom step
from novu_framework import register_step_type
register_step_type('SLACK', CustomSlackStep)

@workflow('slack-workflow')
def slack_workflow(payload: PayloadSchema, step):
    step.slack('slack-notification', {
        'message': f'New comment: {payload.comment}'
    })
```

## Testing

### Unit Tests

```python
import pytest
from novu_framework.testing import WorkflowTestClient
from your_workflows import comment_workflow

def test_comment_workflow():
    client = WorkflowTestClient()

    # Test workflow execution
    result = client.trigger_workflow(
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
from httpx import AsyncClient
from your_app import app

def test_workflow_api():
    with AsyncClient(app=app, base_url="https://example.com") as client:
        response = client.get("/api/novu")
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

- Configure appropriate timeouts

### 3. Security

- Validate all input data
- Use secure communication channels
- Implement proper authentication
