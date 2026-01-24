# Flask Integration Quickstart

**Date**: 2026-01-24
**Feature**: Flask Support for novu-framework

## Overview

This guide demonstrates how to integrate the novu-framework with Flask applications, providing the same workflow serving capabilities as the FastAPI integration.

## Prerequisites

- Python 3.10+
- Flask installed (`pip install flask`)
- novu-framework installed (`pip install novu-framework[flask]`)

## 1. Define a Workflow

Workflows are defined exactly the same way as with FastAPI - no changes required:

```python
from novu_framework import workflow
from pydantic import BaseModel

class CommentPayload(BaseModel):
    comment: str
    post_id: str

class EmailControls(BaseModel):
    subject: str = "New Comment"
    include_footer: bool = True

@workflow("comment-notification")
def comment_workflow(payload: CommentPayload, step):
    # In-app notification step (using dict)
    step.in_app("new-comment", {
        "body": f"New comment: {payload.comment}",
        "action_url": f"/posts/{payload.post_id}"
    })

    # Email notification step (using lambda)
    step.email("comment-email", lambda controls: {
        "subject": controls.subject,
        "body": f"You received a new comment: {payload.comment}",
        "footer": "Thanks for using our app!" if controls.include_footer else ""
    }, controlSchema=EmailControls)
```

## 2. Create Flask Application

Create a Flask application and register your workflows:

```python
from flask import Flask
from novu_framework.flask import serve

app = Flask(__name__)

# Register workflows with Flask
serve(app, route="/api/novu", workflows=[comment_workflow])

if __name__ == "__main__":
    app.run(debug=True)
```

## 3. Run the Application

```bash
python app.py
```

The Flask application will start on `http://localhost:5000` with the Novu endpoints available at `/api/novu`.

## 4. Test the Integration

### Health Check

Check that the Flask integration is working:

```bash
curl http://localhost:5000/api/novu
```

Response:

```json
{
  "status": "ok",
  "sdkVersion": "0.1.0",
  "frameworkVersion": "2024-06-26",
  "discovered": {
    "workflows": 1,
    "steps": 2
  }
}
```

### Execute Workflow

Trigger a workflow execution:

```bash
curl -X POST http://localhost:5000/api/novu/workflows/comment-notification/execute \
  -H "Content-Type: application/json" \
  -d '{
    "to": "user_123",
    "payload": {
      "comment": "This is a great post!",
      "post_id": "post_456"
    },
    "metadata": {
      "source": "web_app"
    }
  }'
```

Response:

```json
{
  "status": "completed",
  "steps_executed": 2,
  "results": {
    "in_app": "delivered",
    "email": "sent"
  }
}
```

## 5. Advanced Usage

### Custom Route Prefix

Change the default route prefix:

```python
serve(app, route="/custom/novu", workflows=[comment_workflow])
```

### Multiple Workflows

Register multiple workflows:

```python
from novu_framework.flask import serve

# Define multiple workflows
@workflow("welcome-email")
def welcome_workflow(payload: WelcomePayload, step):
    step.email("welcome", lambda controls: {
        "subject": "Welcome to our app!",
        "body": f"Hi {payload.name}, welcome aboard!"
    })

@workflow("password-reset")
def reset_workflow(payload: ResetPayload, step):
    step.email("reset", lambda controls: {
        "subject": "Password Reset",
        "body": f"Reset your password: {payload.reset_link}"
    })

# Register all workflows
serve(app, workflows=[comment_workflow, welcome_workflow, reset_workflow])
```

### Error Handling

The Flask integration provides the same error handling as FastAPI:

```bash
# Non-existent workflow
curl -X POST http://localhost:5000/api/novu/workflows/unknown/execute \
  -H "Content-Type: application/json" \
  -d '{"to": "user_123", "payload": {}}'

# Response: 404 Not Found
{
  "detail": "Workflow 'unknown' not found"
}

# Invalid payload
curl -X POST http://localhost:5000/api/novu/workflows/comment-notification/execute \
  -H "Content-Type: application/json" \
  -d '{"to": "user_123", "payload": {}}'

# Response: 400 Bad Request
{
  "detail": "Invalid payload: 'comment' is required"
}
```

## 6. Testing

### Unit Tests

Test your Flask integration with Flask's test client:

```python
import pytest
from flask import Flask
from novu_framework.flask import serve
from your_workflows import comment_workflow

@pytest.fixture
def app():
    app = Flask(__name__)
    serve(app, workflows=[comment_workflow])
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    response = client.get('/api/novu')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['discovered']['workflows'] == 1

def test_workflow_execution(client):
    response = client.post('/api/novu/workflows/comment-notification/execute',
                           json={
                               'to': 'user_123',
                               'payload': {
                                   'comment': 'Test comment',
                                   'post_id': 'post_456'
                               }
                           })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'completed'
```

### Integration Tests

Test with real workflow execution:

```python
def test_full_workflow_execution(client):
    response = client.post('/api/novu/workflows/comment-notification/execute',
                           json={
                               'to': 'user_123',
                               'payload': {
                                   'comment': 'Integration test comment',
                                   'post_id': 'post_789'
                               },
                               'metadata': {'test': True}
                           })
    assert response.status_code == 200
    data = response.get_json()
    assert 'steps_executed' in data
    assert data['steps_executed'] == 2
```

## 7. Migration from FastAPI

If you're migrating from FastAPI to Flask, the workflow definitions remain identical. Only the integration code changes:

### FastAPI (Before)

```python
from fastapi import FastAPI
from novu_framework.fastapi import serve

app = FastAPI()
serve(app, route="/api/novu", workflows=[comment_workflow])
```

### Flask (After)

```python
from flask import Flask
from novu_framework.flask import serve

app = Flask(__name__)
serve(app, route="/api/novu", workflows=[comment_workflow])
```

## 8. Production Considerations

### Performance

- Flask with async routes provides comparable performance to FastAPI
- Use a production WSGI server like Gunicorn or uWSGI
- Consider using Gevent for async support

### Security

- Enable Flask's built-in security features
- Use HTTPS in production
- Validate and sanitize all inputs (handled by Pydantic models)

### Deployment

```bash
# Install with production server
pip install gunicorn novu-framework[flask]

# Run with Gunicorn
gunicorn -w 4 -k gevent app:app
```

## 9. Troubleshooting

### Common Issues

1. **Async Routes Not Working**: Ensure Flask 2.0+ is installed
2. **Workflow Not Found**: Check workflow ID matches exactly
3. **Validation Errors**: Verify payload structure matches workflow expectations

### Debug Mode

Enable Flask debug mode for detailed error messages:

```python
app.run(debug=True)
```

### Logging

Configure logging to monitor workflow execution:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.path}")
```

## 10. Next Steps

- Explore advanced workflow patterns
- Implement custom error handlers
- Add authentication and authorization
- Monitor workflow execution metrics
- Scale with multiple worker processes

## Support

For issues and questions:

- Check the [novu-framework documentation](https://github.com/remarkablemark/novu-framework)
- Review the [API contracts](contracts/openapi.yaml)
- Run the test suite for examples
