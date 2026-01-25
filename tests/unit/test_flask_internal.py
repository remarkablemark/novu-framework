"""Test cases for Flask internal functions."""

from flask import Flask

from novu_framework import workflow
from novu_framework.flask import serve
from novu_framework.workflow import Workflow, workflow_registry
from tests.unit.test_flask_base import FlaskBaseTest


class TestCountStepsInWorkflowFlask(FlaskBaseTest):
    """Test cases for count_steps_in_workflow function in Flask module."""


class TestHandleHealthCheckFlask(FlaskBaseTest):
    """Test cases for handle_health_check_flask function."""


class TestHandleDiscoverFlask(FlaskBaseTest):
    """Test cases for handle_discover_flask function."""


class TestHandleCodeFlask(FlaskBaseTest):
    """Test cases for handle_code_flask function."""


class TestExtractWorkflowDetailsFlask(FlaskBaseTest):
    """Test cases for extract_workflow_details_flask function."""


class TestExtractWorkflowStepsFlask(FlaskBaseTest):
    """Test cases for extract_workflow_steps_flask function."""


class TestExtractSchemasFlask(FlaskBaseTest):
    """Test cases for Flask schema extraction functions."""


class TestServeFlask:
    """Test cases for Flask serve function."""

    def test_serve_with_mixed_workflow_types(self):
        """Test serve function with mixed workflow types (wrapped and unwrapped)."""
        workflow_registry.clear()
        app = Flask(__name__)

        @workflow("wrapped-workflow")
        def wrapped_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Wrapped"})
            return {"status": "completed"}

        # Create unwrapped workflow object
        def unwrapped_handler(payload, step):
            step.sms("step-1", lambda: {"message": "Unwrapped"})
            return {"status": "completed"}

        unwrapped_workflow = Workflow("unwrapped-workflow", unwrapped_handler)

        serve(app, workflows=[wrapped_workflow, unwrapped_workflow])
        client = app.test_client()

        response = client.get("/api/novu")
        assert response.status_code == 200
        data = response.get_json()
        assert data["discovered"]["workflows"] == 2
        assert data["discovered"]["steps"] == 2

    def test_serve_with_custom_route(self):
        """Test serve function with custom route."""
        workflow_registry.clear()
        app = Flask(__name__)

        @workflow("custom-route-workflow")
        def custom_route_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Custom route"})
            return {"status": "completed"}

        serve(app, route="/custom/novu", workflows=[custom_route_workflow])
        client = app.test_client()

        # Test custom route works
        response = client.get("/custom/novu")
        assert response.status_code == 200
        data = response.get_json()
        assert data["discovered"]["workflows"] == 1

        # Test default route doesn't work
        response = client.get("/api/novu")
        assert response.status_code == 404

    def test_serve_get_action_validation_error(self):
        """Test GET action validation error handling."""
        workflow_registry.clear()
        app = Flask(__name__)

        @workflow("test-workflow")
        def test_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        serve(app, workflows=[test_workflow])
        client = app.test_client()

        # Test with invalid action
        response = client.get("/api/novu?action=invalid")
        assert response.status_code == 400
        assert "Invalid action" in response.get_json()["detail"]

    def test_serve_code_action_without_workflow_id(self):
        """Test code action without workflow_id parameter."""
        workflow_registry.clear()
        app = Flask(__name__)

        @workflow("test-workflow")
        def test_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        serve(app, workflows=[test_workflow])
        client = app.test_client()

        response = client.get("/api/novu?action=code")
        assert response.status_code == 400
        assert "workflow_id is required" in response.get_json()["detail"]

    def test_serve_code_action_invalid_workflow_id(self):
        """Test code action with invalid workflow_id."""
        workflow_registry.clear()
        app = Flask(__name__)

        @workflow("test-workflow")
        def test_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        serve(app, workflows=[test_workflow])
        client = app.test_client()

        response = client.get("/api/novu?action=code&workflow_id=invalid-workflow")
        assert response.status_code == 404
        assert "not found" in response.get_json()["detail"]

    def test_serve_execute_workflow_success(self):
        """Test successful workflow execution."""
        workflow_registry.clear()
        app = Flask(__name__)

        @workflow("execute-workflow")
        def execute_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Executed"})
            return {"status": "completed"}

        serve(app, workflows=[execute_workflow])
        client = app.test_client()

        response = client.post(
            "/api/novu/workflows/execute-workflow/execute",
            json={"to": "user@example.com", "payload": {"message": "Hello"}},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "completed"

    def test_serve_execute_workflow_not_found(self):
        """Test executing non-existent workflow."""
        workflow_registry.clear()
        app = Flask(__name__)
        serve(app, workflows=[])
        client = app.test_client()

        response = client.post(
            "/api/novu/workflows/nonexistent/execute",
            json={"to": "user@example.com", "payload": {"message": "Hello"}},
        )
        assert response.status_code == 404
        assert "not found" in response.get_json()["detail"]

    def test_serve_execute_workflow_invalid_json(self):
        """Test executing workflow with invalid JSON."""
        workflow_registry.clear()
        app = Flask(__name__)

        @workflow("test-workflow")
        def test_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        serve(app, workflows=[test_workflow])
        client = app.test_client()

        # Test with no JSON
        response = client.post(
            "/api/novu/workflows/test-workflow/execute",
            data="",  # Empty body
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "Invalid JSON" in response.get_json()["detail"]

    def test_serve_execute_workflow_validation_error(self):
        """Test executing workflow with validation error."""
        workflow_registry.clear()
        app = Flask(__name__)

        @workflow("test-workflow")
        def test_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        serve(app, workflows=[test_workflow])
        client = app.test_client()

        # Test with missing required fields
        response = client.post(
            "/api/novu/workflows/test-workflow/execute",
            json={"to": "user@example.com"},  # Missing payload
        )
        assert response.status_code == 400
        assert "Validation error" in response.get_json()["detail"]

    def test_serve_error_handlers(self):
        """Test Flask error handlers."""
        workflow_registry.clear()
        app = Flask(__name__)

        @workflow("test-workflow")
        def test_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        serve(app, workflows=[test_workflow])
        client = app.test_client()

        # Test 404 error handler
        response = client.get("/nonexistent-route")
        assert response.status_code == 404
        data = response.get_json()
        if data:
            assert "detail" in data

        # Test that blueprint error handlers work for workflow execution
        response = client.post(
            "/api/novu/workflows/nonexistent/execute",
            json={"to": "user@example.com", "payload": {"message": "Hello"}},
        )
        assert response.status_code == 404
        data = response.get_json()
        assert data is not None
        assert "detail" in data
