# Quickstart Guide: GET Request Handler

**Feature**: GET Request Handler | **Date**: 2025-01-24 | **Phase**: 1

## Overview

The GET Request Handler adds three new GET endpoints to the Novu Python framework, enabling webhook validation, health monitoring, and code discovery through simple HTTP requests.

## Supported Actions

### 1. Discover Workflows

```bash
GET /?action=discover
```

Returns information about all registered workflows and their steps.

### 2. Health Check

```bash
GET /?action=health-check
```

Returns system health status and basic metrics.

### 3. Code Information

```bash
GET /?action=code&workflow_id={id}&step_id={id}
```

Returns code or configuration for a specific workflow step.

## FastAPI Integration

### Basic Setup

```python
from fastapi import FastAPI
from novu_framework import serve, Workflow
from novu_framework.steps import email, in_app

# Define your workflow
@workflow
def welcome_workflow():
    step.in_app("show-welcome")
    step.email("send-welcome", template_id="welcome-template")

app = FastAPI()

# Serve with GET endpoint support
serve(app, route="/api/novu", workflows=[welcome_workflow])
```

### Testing GET Endpoints

```python
import httpx

# Test health check
response = httpx.get("http://localhost:8000/api/novu?action=health-check")
print(response.json())
# Output: {"status": "healthy", "timestamp": "...", "version": "...", "discovered": {...}}

# Test discover
response = httpx.get("http://localhost:8000/api/novu?action=discover")
print(response.json())
# Output: {"discovered": {"workflows": 1, "steps": 2, "workflow_details": [...]}, "status": "healthy"}

# Test code (requires workflow_id and step_id)
response = httpx.get("http://localhost:8000/api/novu?action=code&workflow_id=welcome-workflow&step_id=send-welcome")
print(response.json())
# Output: {"workflow_id": "welcome-workflow", "step_id": "send-welcome", "code": "...", "metadata": {...}}
```

## Flask Integration

### Basic Setup

```python
from flask import Flask
from novu_framework import serve as flask_serve, Workflow
from novu_framework.steps import email, in_app

# Define your workflow
@workflow
def welcome_workflow():
    step.in_app("show-welcome")
    step.email("send-welcome", template_id="welcome-template")

app = Flask(__name__)

# Serve with GET endpoint support
flask_serve(app, route="/api/novu", workflows=[welcome_workflow])
```

### Testing GET Endpoints

```python
import requests

# Test health check
response = requests.get("http://localhost:5000/api/novu?action=health-check")
print(response.json())

# Test discover
response = requests.get("http://localhost:5000/api/novu?action=discover")
print(response.json())

# Test code
response = requests.get("http://localhost:5000/api/novu?action=code&workflow_id=welcome-workflow&step_id=send-welcome")
print(response.json())
```

## Response Formats

### Discover Response

GET `?action=discover`

```json
{
  "workflows": [
    {
      "workflowId": "test-notification",
      "severity": "none",
      "steps": [
        {
          "stepId": "test-in-app",
          "type": "in_app",
          "controls": {
            "schema": {
              "type": "object",
              "properties": {},
              "required": [],
              "additionalProperties": false
            },
            "unknownSchema": {
              "type": "object",
              "properties": {},
              "required": [],
              "additionalProperties": false
            }
          },
          "outputs": {
            "schema": {
              "type": "object",
              "properties": {
                "subject": {
                  "type": "string",
                  "minLength": 1
                },
                "body": {
                  "type": "string",
                  "minLength": 1
                }
              },
              "required": ["subject"],
              "additionalProperties": false
            },
            "unknownSchema": {
              "type": "object",
              "properties": {
                "subject": {
                  "type": "string",
                  "minLength": 1
                },
                "body": {
                  "type": "string",
                  "minLength": 1
                }
              },
              "required": ["subject"],
              "additionalProperties": false
            }
          },
          "results": {
            "schema": {
              "type": "object",
              "properties": {
                "seen": {
                  "type": "boolean"
                },
                "read": {
                  "type": "boolean"
                }
              },
              "required": ["seen", "read"],
              "additionalProperties": false
            },
            "unknownSchema": {
              "type": "object",
              "properties": {
                "seen": {
                  "type": "boolean"
                },
                "read": {
                  "type": "boolean"
                }
              },
              "required": ["seen", "read"],
              "additionalProperties": false
            }
          },
          "code": "() => ({ body: 'Test in-app notification' })",
          "options": {},
          "providers": []
        },
        {
          "stepId": "test-email",
          "type": "email",
          "controls": {
            "schema": {
              "type": "object",
              "properties": {},
              "required": [],
              "additionalProperties": false
            },
            "unknownSchema": {
              "type": "object",
              "properties": {},
              "required": [],
              "additionalProperties": false
            }
          },
          "outputs": {
            "schema": {
              "type": "object",
              "properties": {
                "subject": {
                  "type": "string",
                  "minLength": 1
                },
                "body": {
                  "type": "string"
                }
              },
              "required": ["subject", "body"],
              "additionalProperties": false
            },
            "unknownSchema": {
              "type": "object",
              "properties": {
                "subject": {
                  "type": "string",
                  "minLength": 1
                },
                "body": {
                  "type": "string"
                }
              },
              "required": ["subject", "body"],
              "additionalProperties": false
            }
          },
          "results": {
            "schema": {
              "type": "object",
              "properties": {},
              "required": [],
              "additionalProperties": false
            },
            "unknownSchema": {
              "type": "object",
              "properties": {},
              "required": [],
              "additionalProperties": false
            }
          },
          "code": "async () => ({ subject: 'Test email', body: 'Test body' })",
          "options": {},
          "providers": []
        }
      ],
      "code": "async ({ step, payload }) => { await step.inApp('test-in-app', () => ({ body: 'Test' })); await step.email('test-email', () => ({ subject: 'Test', body: 'Test' })); }",
      "payload": {
        "schema": {
          "type": "object",
          "properties": {
            "firstName": {
              "type": "string"
            }
          },
          "additionalProperties": false
        },
        "unknownSchema": {
          "type": "object",
          "properties": {
            "firstName": {
              "type": "string"
            }
          },
          "additionalProperties": false
        }
      },
      "controls": {
        "schema": {
          "type": "object",
          "properties": {},
          "required": [],
          "additionalProperties": false
        },
        "unknownSchema": {
          "type": "object",
          "properties": {},
          "required": [],
          "additionalProperties": false
        }
      },
      "tags": [],
      "preferences": {}
    }
  ]
}
```

### Health Check Response

GET `?action=health-check`

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

### Code Response

GET `?action=code&workflow_id=welcome-workflow&step_id=send-welcome`

```json
{
  "code": "async ({ step, payload }) => {\n    await step.inApp('send-welcome', () => ({\n        body: 'Welcome to our platform!',\n    }));\n}"
}
```

## Error Handling

### Invalid Action

```bash
GET /?action=invalid
```

Response:

```json
{
  "detail": "Invalid action parameter",
  "code": "INVALID_ACTION"
}
```

### Missing Parameters for Code Action

```bash
GET /?action=code
```

Response:

```json
{
  "detail": "workflow_id and step_id are required for code action",
  "code": "MISSING_PARAMETERS"
}
```

### Workflow Not Found

```bash
GET /?action=code&workflow_id=nonexistent&step_id=step
```

Response:

```json
{
  "detail": "Workflow 'nonexistent' not found",
  "code": "WORKFLOW_NOT_FOUND"
}
```

## Advanced Usage

### Custom Route Prefix

```python
# FastAPI
serve(app, route="/webhooks/novu", workflows=[workflow])

# Flask
flask_serve(app, route="/webhooks/novu", workflows=[workflow])
```

### Multiple Workflows

```python
workflows = [welcome_workflow, password_reset_workflow, notification_workflow]
serve(app, route="/api/novu", workflows=workflows)
```

### CORS Support

The GET endpoints automatically include CORS headers for cross-origin requests from browsers.

## Integration with Novu Cloud

These GET endpoints are designed to work seamlessly with Novu cloud service:

1. **Webhook Validation**: Novu cloud can validate bridge endpoints using `?action=health-check`
2. **Workflow Discovery**: Novu cloud can discover available workflows using `?action=discover`
3. **Code Inspection**: Development tools can inspect workflow code using `?action=code`

## Testing

### Unit Tests

```python
import pytest
from fastapi.testclient import TestClient
from novu_framework.fastapi import serve

def test_health_check():
    app = FastAPI()
    serve(app, workflows=[workflow])
    client = TestClient(app)

    response = client.get("/api/novu?action=health-check")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Integration Tests

```python
def test_full_workflow_discovery():
    response = client.get("/api/novu?action=discover")
    data = response.json()

    assert data["discovered"]["workflows"] > 0
    assert data["discovered"]["steps"] > 0
    assert len(data["discovered"]["workflow_details"]) > 0
```

## Migration from POST-only

If you're already using the Novu framework with POST endpoints, no changes are required. The GET endpoints are additive and don't affect existing POST workflow execution.

Your existing POST endpoints continue to work unchanged:

```bash
POST /api/novu/workflows/{workflow_id}/execute
```

## Next Steps

1. Add GET endpoints to your existing FastAPI/Flask applications
2. Test with Novu cloud service for webhook validation
3. Monitor health check endpoints in production
4. Use discover endpoints for debugging and development tools
