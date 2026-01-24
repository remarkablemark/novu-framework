"""
Unit tests for Flask integration module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

from novu_framework.flask import count_steps_in_workflow, serve
from novu_framework.workflow import Workflow


class TestCountStepsInWorkflow:
    """Test the count_steps_in_workflow function."""

    def test_count_steps_empty_workflow(self):
        """Test counting steps in a workflow with no steps."""
        workflow = MagicMock(spec=Workflow)
        workflow.handler = lambda: None  # Simple function with no steps

        count = count_steps_in_workflow(workflow)
        assert count == 0

    def test_count_steps_single_step(self):
        """Test counting steps in a workflow with one step."""
        workflow_source = """
def test_workflow(payload, step):
    step.in_app("notification", {"message": "test"})
"""
        workflow = MagicMock(spec=Workflow)
        workflow.handler = MagicMock()
        workflow.handler.__name__ = "test_workflow"

        with patch("inspect.getsource", return_value=workflow_source):
            count = count_steps_in_workflow(workflow)
            assert count == 1

    def test_count_steps_multiple_steps(self):
        """Test counting steps in a workflow with multiple steps."""
        workflow_source = """
def test_workflow(payload, step):
    step.in_app("notification1", {"message": "test1"})
    step.email("notification2", lambda: {"subject": "test"})
    step.sms("notification3", {"message": "test3"})
"""
        workflow = MagicMock(spec=Workflow)
        workflow.handler = MagicMock()
        workflow.handler.__name__ = "test_workflow"

        with patch("inspect.getsource", return_value=workflow_source):
            count = count_steps_in_workflow(workflow)
            assert count == 3

    def test_count_steps_with_decorator(self):
        """Test counting steps when workflow has decorators."""
        workflow_source = """
@workflow("test-workflow")
def test_workflow(payload, step):
    step.in_app("notification", {"message": "test"})
"""
        workflow = MagicMock(spec=Workflow)
        workflow.handler = MagicMock()
        workflow.handler.__name__ = "test_workflow"

        with patch("inspect.getsource", return_value=workflow_source):
            count = count_steps_in_workflow(workflow)
            assert count == 1

    def test_count_steps_invalid_source(self):
        """Test handling of invalid source code."""
        workflow = MagicMock(spec=Workflow)
        workflow.handler = MagicMock(side_effect=OSError("Cannot read source"))

        count = count_steps_in_workflow(workflow)
        assert count == 0

    def test_count_steps_syntax_error(self):
        """Test handling of syntax errors in source code."""
        workflow_source = """
def test_workflow(payload, step):
    step.in_app("notification", {"message": "test"})
    invalid syntax here
"""
        workflow = MagicMock(spec=Workflow)
        workflow.handler = MagicMock()
        workflow.handler.__name__ = "test_workflow"

        with patch("inspect.getsource", return_value=workflow_source):
            count = count_steps_in_workflow(workflow)
            assert count == 0


class TestServe:
    """Test the serve function."""

    def test_serve_basic_setup(self):
        """Test basic Flask app setup with workflows."""
        from flask import Flask

        app = Flask(__name__)
        workflow1 = MagicMock(spec=Workflow)
        workflow1.workflow_id = "test-workflow-1"
        workflow1._workflow = workflow1

        workflow2 = MagicMock(spec=Workflow)
        workflow2.workflow_id = "test-workflow-2"

        # Mock workflow function that returns the workflow object
        workflow_func = MagicMock()
        workflow_func._workflow = workflow2

        serve(app, workflows=[workflow1, workflow_func])

        # Check that blueprint was registered
        assert "novu" in app.blueprints

    def test_serve_with_route_prefix(self):
        """Test serve with custom route prefix."""
        from flask import Flask

        app = Flask(__name__)
        workflow = MagicMock(spec=Workflow)
        workflow.workflow_id = "test-workflow"
        workflow._workflow = workflow

        serve(app, route="/custom/novu", workflows=[workflow])

        # Check that blueprint was registered with correct prefix
        blueprint = app.blueprints["novu"]
        assert blueprint.url_prefix == "/custom/novu"

    @patch("novu_framework.flask.count_steps_in_workflow")
    def test_health_check_endpoint(self, mock_count_steps):
        """Test health check endpoint functionality."""
        from flask import Flask

        app = Flask(__name__)
        workflow = MagicMock(spec=Workflow)
        workflow.workflow_id = "test-workflow"
        workflow._workflow = workflow

        mock_count_steps.return_value = 2

        serve(app, workflows=[workflow])

        with app.test_client() as client:
            response = client.get("/api/novu")
            assert response.status_code == 200

            data = response.get_json()
            assert data["discovered"]["workflows"] == 1
            assert data["discovered"]["steps"] == 2
            mock_count_steps.assert_called_once()

    @patch("novu_framework.flask.count_steps_in_workflow")
    def test_workflow_execution_endpoint(self, mock_count_steps):
        """Test workflow execution endpoint."""
        from flask import Flask

        app = Flask(__name__)
        workflow = MagicMock(spec=Workflow)
        workflow.workflow_id = "test-workflow"
        workflow._workflow = workflow
        workflow.trigger = AsyncMock(return_value={"status": "completed"})

        mock_count_steps.return_value = 1

        serve(app, workflows=[workflow])

        with app.test_client() as client:
            response = client.post(
                "/api/novu/workflows/test-workflow/execute",
                json={"to": "user-123", "payload": {"test": "data"}},
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "completed"
            workflow.trigger.assert_called_once()

    def test_workflow_execution_not_found(self):
        """Test workflow execution with non-existent workflow."""
        from flask import Flask

        app = Flask(__name__)
        workflow = MagicMock(spec=Workflow)
        workflow.workflow_id = "test-workflow"
        workflow._workflow = workflow

        serve(app, workflows=[workflow])

        with app.test_client() as client:
            response = client.post(
                "/api/novu/workflows/non-existent/execute",
                json={"to": "user-123", "payload": {}},
            )

            assert response.status_code == 404
            data = response.get_json()
            assert "detail" in data

    def test_workflow_execution_invalid_payload(self):
        """Test workflow execution with invalid payload."""
        from flask import Flask

        app = Flask(__name__)
        workflow = MagicMock(spec=Workflow)
        workflow.workflow_id = "test-workflow"
        workflow._workflow = workflow

        serve(app, workflows=[workflow])

        with app.test_client() as client:
            response = client.post(
                "/api/novu/workflows/test-workflow/execute",
                json={},  # Missing required fields
            )

            assert response.status_code == 400
            data = response.get_json()
            assert "detail" in data

    @patch("novu_framework.flask.count_steps_in_workflow")
    def test_workflow_execution_internal_error(self, mock_count_steps):
        """Test workflow execution with internal error."""
        from flask import Flask

        app = Flask(__name__)
        workflow = MagicMock(spec=Workflow)
        workflow.workflow_id = "test-workflow"
        workflow._workflow = workflow
        workflow.trigger = AsyncMock(side_effect=Exception("Internal error"))

        mock_count_steps.return_value = 1

        serve(app, workflows=[workflow])

        with app.test_client() as client:
            response = client.post(
                "/api/novu/workflows/test-workflow/execute",
                json={"to": "user-123", "payload": {"test": "data"}},
            )

            assert response.status_code == 500
            data = response.get_json()
            assert "detail" in data
            assert "Internal error" in data["detail"]


class TestCountStepsInWorkflowEdgeCases:
    """Test edge cases for count_steps_in_workflow function."""

    def test_count_steps_empty_lines(self):
        """Test counting steps when func_lines is empty."""
        workflow = MagicMock(spec=Workflow)
        workflow.handler = MagicMock()

        with patch("inspect.getsource", return_value="def test_function():"):
            count = count_steps_in_workflow(workflow)
            assert count == 0


class TestFlaskValidationErrorHandling:
    """Test ValidationError handling in Flask endpoints."""

    def test_workflow_execution_validation_error(self):
        """Test workflow execution with Pydantic ValidationError."""
        from flask import Flask
        from pydantic import ValidationError

        app = Flask(__name__)
        workflow = MagicMock(spec=Workflow)
        workflow.workflow_id = "test-workflow"
        workflow._workflow = workflow

        serve(app, workflows=[workflow])

        with app.test_client() as client:
            # Create a ValidationError that will trigger the exact error handling code
            validation_error = ValidationError.from_exception_data(
                "Validation failed",
                [{"loc": ("to",), "msg": "field required", "type": "missing"}],
            )

            # Mock the TriggerPayload to raise ValidationError
            with patch(
                "novu_framework.flask.TriggerPayload", side_effect=validation_error
            ):
                response = client.post(
                    "/api/novu/workflows/test-workflow/execute",
                    json={
                        "to": "test",
                        "payload": {},
                    },  # Valid JSON but will fail validation
                )

                assert response.status_code == 400
                data = response.get_json()
                assert "detail" in data
                # Verify the specific ValidationError handling logic
                assert "Validation error:" in data["detail"]
                assert "to: Field required" in data["detail"]
