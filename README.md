# novu-framework

[![PyPI version](https://img.shields.io/pypi/v/novu-framework)](https://pypi.org/project/novu-framework/)
[![codecov](https://codecov.io/gh/remarkablemark/novu-framework/graph/badge.svg?token=bbMOIiPMI0)](https://codecov.io/gh/remarkablemark/novu-framework)
[![lint](https://github.com/remarkablemark/novu-framework/actions/workflows/lint.yml/badge.svg)](https://github.com/remarkablemark/novu-framework/actions/workflows/lint.yml)

🔔 Novu Framework allows you to write notification workflows in your Python codebase. Inspired by [@novu/framework](https://www.npmjs.com/package/@novu/framework).

## Prerequisites

- [Python 3.8+](https://www.python.org/)

## Install

Install the package:

```sh
pip install novu-framework
```

## Quick Start

### 1. Define a Workflow

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
async def comment_workflow(payload: CommentPayload, step):
    # In-app notification step (using dict)
    await step.in_app("new-comment", {
        "body": f"New comment: {payload.comment}",
        "action_url": f"/posts/{payload.post_id}"
    })

    # Email notification step (using lambda)
    await step.email("comment-email", lambda controls: {
        "subject": controls.subject,
        "body": f"You received a new comment: {payload.comment}",
        "footer": "Thanks for using our app!" if controls.include_footer else ""
    }, controlSchema=EmailControls)
```

### 2. Trigger the Workflow

```python
await comment_workflow.trigger(
    to="subscriber_id_123",
    payload={
        "comment": "This is a great post!",
        "post_id": "post_id_456"
    }
)
```

### 3. Serve via FastAPI

```python
from fastapi import FastAPI
from novu_framework.fastapi import serve

app = FastAPI()
serve(app, route="/api/novu", workflows=[comment_workflow])
```

## Features

- **Code-First Workflows**: Define workflows using Python functions and decorators.
- **Type Safety**: Built-in support for Pydantic models for payload validation.
- **Multi-Channel Support**: Support for In-App, Email, SMS, and Push notifications.
- **FastAPI Integration**: Seamlessly integrate with FastAPI applications.
- **Async Support**: Fully asynchronous design using `asyncio`.

## License

[MIT](https://github.com/remarkablemark/novu-framework/blob/master/LICENSE)
