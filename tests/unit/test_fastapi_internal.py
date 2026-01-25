"""Test cases for shared workflow functions."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from novu_framework import workflow
from novu_framework.fastapi import serve
from novu_framework.workflow import Workflow, workflow_registry
from tests.unit.test_fastapi_base import FastAPIBaseTest


class TestCountStepsInWorkflow(FastAPIBaseTest):
    """Test cases for count_steps_in_workflow function."""


class TestHandleHealthCheck(FastAPIBaseTest):
    """Test cases for handle_health_check function."""


class TestHandleDiscover(FastAPIBaseTest):
    """Test cases for handle_discover function."""


class TestExtractWorkflowDetails(FastAPIBaseTest):
    """Test cases for extract_workflow_details function."""


class TestExtractWorkflowSteps(FastAPIBaseTest):
    """Test cases for extract_workflow_steps function."""


class TestExtractSchemas(FastAPIBaseTest):
    """Test cases for schema extraction functions."""


class TestHandleCode(FastAPIBaseTest):
    """Test cases for handle_code function."""


class TestServeFunction:
    """Test cases for serve function edge cases."""

    def test_serve_with_mixed_workflow_types(self):
        """Test serve function with mixed workflow types (wrapped and unwrapped)."""
        workflow_registry.clear()
        app = FastAPI()

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
        client = TestClient(app)

        response = client.get("/api/novu")
        assert response.status_code == 200
        data = response.json()
        assert data["discovered"]["workflows"] == 2
        assert data["discovered"]["steps"] == 2

    def test_serve_with_custom_route(self):
        """Test serve function with custom route."""
        workflow_registry.clear()
        app = FastAPI()

        @workflow("custom-route-workflow")
        def custom_route_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Custom route"})
            return {"status": "completed"}

        serve(app, route="/custom/novu", workflows=[custom_route_workflow])
        client = TestClient(app)

        # Test custom route works
        response = client.get("/custom/novu")
        assert response.status_code == 200
        data = response.json()
        assert data["discovered"]["workflows"] == 1

        # Test default route doesn't work
        response = client.get("/api/novu")
        assert response.status_code == 404

    def test_serve_get_action_validation_error(self):
        """Test GET action validation error handling."""
        workflow_registry.clear()
        app = FastAPI()

        @workflow("test-workflow")
        def test_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        serve(app, workflows=[test_workflow])
        client = TestClient(app)

        # Test with invalid action (this would be caught by Pydantic validation)
        response = client.get("/api/novu?action=invalid")
        # FastAPI should return 422 for invalid enum value
        assert response.status_code == 422

    def test_serve_code_action_without_workflow_id(self):
        """Test code action without workflow_id parameter."""
        workflow_registry.clear()
        app = FastAPI()

        @workflow("test-workflow")
        def test_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        serve(app, workflows=[test_workflow])
        client = TestClient(app)

        response = client.get("/api/novu?action=code")
        assert response.status_code == 400
        assert "workflow_id is required" in response.json()["detail"]

    def test_serve_code_action_invalid_workflow_id(self):
        """Test code action with invalid workflow_id."""
        workflow_registry.clear()
        app = FastAPI()

        @workflow("test-workflow")
        def test_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        serve(app, workflows=[test_workflow])
        client = TestClient(app)

        response = client.get("/api/novu?action=code&workflow_id=invalid-workflow")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
