"""Test cases for Flask internal functions."""

from unittest.mock import patch

import pytest
from flask import Flask

from novu_framework import workflow
from novu_framework.error_handling import NotFoundError, ValidationError
from novu_framework.workflow import Workflow, workflow_registry

from novu_framework.flask import (  # isort: skip
    _extract_controls_schema_flask,
    _extract_payload_schema_flask,
    _extract_workflow_details_flask,
    _extract_workflow_steps_flask,
    _handle_code_flask,
    _handle_discover_flask,
    _handle_health_check_flask,
    count_steps_in_workflow,
    serve,
)


class TestCountStepsInWorkflowFlask:
    """Test cases for count_steps_in_workflow function in Flask module."""

    def test_count_steps_in_workflow_simple(self):
        """Test counting steps in a simple workflow."""
        workflow_registry.clear()

        @workflow("test-workflow-flask")
        def test_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            step.sms("step-2", lambda: {"message": "SMS"})
            return {"status": "completed"}

        count = count_steps_in_workflow(test_workflow._workflow)
        assert count == 2

    def test_count_steps_in_workflow_all_step_types(self):
        """Test counting all supported step types."""
        workflow_registry.clear()

        @workflow("all-steps-workflow-flask")
        def all_steps_workflow(payload, step):
            step.in_app("step-1", lambda: {"message": "In app"})
            step.email("step-2", lambda: {"message": "Email"})
            step.sms("step-3", lambda: {"message": "SMS"})
            step.push("step-4", lambda: {"message": "Push"})
            return {"status": "completed"}

        count = count_steps_in_workflow(all_steps_workflow._workflow)
        assert count == 4

    def test_count_steps_in_workflow_no_steps(self):
        """Test counting steps in workflow with no steps."""
        workflow_registry.clear()

        @workflow("no-steps-workflow-flask")
        def no_steps_workflow(payload, step):
            return {"status": "completed"}

        count = count_steps_in_workflow(no_steps_workflow._workflow)
        assert count == 0

    def test_count_steps_in_workflow_exception_handling(self):
        """Test exception handling in count_steps_in_workflow."""
        workflow_obj = Workflow("test-workflow", lambda: None)

        # Test OSError
        with patch("inspect.getsource", side_effect=OSError("Cannot read source")):
            count = count_steps_in_workflow(workflow_obj)
            assert count == 0

        # Test TypeError
        with patch("inspect.getsource", side_effect=TypeError("Invalid type")):
            count = count_steps_in_workflow(workflow_obj)
            assert count == 0

        # Test SyntaxError
        with patch("inspect.getsource", return_value="invalid syntax"):
            count = count_steps_in_workflow(workflow_obj)
            assert count == 0


class TestHandleHealthCheckFlask:
    """Test cases for _handle_health_check_flask function."""

    def test_handle_health_check_empty(self):
        """Test health check with no workflows."""
        result = _handle_health_check_flask({})

        assert result["status"] == "ok"
        assert result["discovered"]["workflows"] == 0
        assert result["discovered"]["steps"] == 0

    def test_handle_health_check_with_workflows(self):
        """Test health check with workflows."""
        workflow_registry.clear()

        @workflow("health-check-workflow-flask")
        def health_check_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            step.sms("step-2", lambda: {"message": "SMS"})
            return {"status": "completed"}

        workflow_map = {"health-check-workflow-flask": health_check_workflow._workflow}
        result = _handle_health_check_flask(workflow_map)

        assert result["status"] == "ok"
        assert result["discovered"]["workflows"] == 1
        assert result["discovered"]["steps"] == 2

    def test_handle_health_check_mixed_workflows(self):
        """Test health check with mixed workflows (some with steps, some without)."""
        workflow_registry.clear()

        @workflow("with-steps-flask")
        def with_steps_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        @workflow("without-steps-flask")
        def without_steps_workflow(payload, step):
            return {"status": "completed"}

        workflow_map = {
            "with-steps-flask": with_steps_workflow._workflow,
            "without-steps-flask": without_steps_workflow._workflow,
        }
        result = _handle_health_check_flask(workflow_map)

        assert result["status"] == "ok"
        assert result["discovered"]["workflows"] == 2
        assert result["discovered"]["steps"] == 1


class TestHandleDiscoverFlask:
    """Test cases for _handle_discover_flask function."""

    def test_handle_discover_empty(self):
        """Test discover with no workflows."""
        result = _handle_discover_flask({})
        assert result["workflows"] == []

    def test_handle_discover_with_workflow(self):
        """Test discover with a workflow."""
        workflow_registry.clear()

        @workflow("discover-workflow-flask")
        def discover_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        workflow_map = {"discover-workflow-flask": discover_workflow._workflow}
        result = _handle_discover_flask(workflow_map)

        assert len(result["workflows"]) == 1
        workflow_detail = result["workflows"][0]
        assert workflow_detail["workflowId"] == "discover-workflow-flask"
        assert workflow_detail["severity"] == "none"
        assert len(workflow_detail["steps"]) == 1
        assert workflow_detail["steps"][0]["stepId"] == "step-1"
        assert workflow_detail["steps"][0]["type"] == "email"

    def test_handle_discover_multiple_workflows(self):
        """Test discover with multiple workflows."""
        workflow_registry.clear()

        @workflow("workflow-1-flask")
        def workflow_1(payload, step):
            step.email("step-1", lambda: {"message": "Email"})
            return {"status": "completed"}

        @workflow("workflow-2-flask")
        def workflow_2(payload, step):
            step.sms("step-1", lambda: {"message": "SMS"})
            step.push("step-2", lambda: {"message": "Push"})
            return {"status": "completed"}

        workflow_map = {
            "workflow-1-flask": workflow_1._workflow,
            "workflow-2-flask": workflow_2._workflow,
        }
        result = _handle_discover_flask(workflow_map)

        assert len(result["workflows"]) == 2

        # Check first workflow
        wf1 = next(
            w for w in result["workflows"] if w["workflowId"] == "workflow-1-flask"
        )
        assert len(wf1["steps"]) == 1
        assert wf1["steps"][0]["type"] == "email"

        # Check second workflow
        wf2 = next(
            w for w in result["workflows"] if w["workflowId"] == "workflow-2-flask"
        )
        assert len(wf2["steps"]) == 2
        assert wf2["steps"][0]["type"] == "sms"
        assert wf2["steps"][1]["type"] == "push"


class TestHandleCodeFlask:
    """Test cases for _handle_code_flask function."""

    def test_handle_code_success(self):
        """Test successful code retrieval."""
        workflow_registry.clear()

        @workflow("code-workflow-flask")
        def code_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        workflow_map = {"code-workflow-flask": code_workflow._workflow}
        result = _handle_code_flask(workflow_map, "code-workflow-flask")

        assert "code" in result
        assert "def code_workflow" in result["code"]

    def test_handle_code_missing_workflow_id(self):
        """Test code action with missing workflow_id."""
        with pytest.raises(ValidationError) as exc_info:
            _handle_code_flask({}, None)

        assert "workflow_id is required" in str(exc_info.value)

    def test_handle_code_workflow_not_found(self):
        """Test code action with non-existent workflow."""
        with pytest.raises(NotFoundError) as exc_info:
            _handle_code_flask({}, "nonexistent-workflow")

        assert "not found" in str(exc_info.value)

    def test_handle_code_source_exception(self):
        """Test code retrieval when source cannot be extracted."""
        workflow_obj = Workflow("test-workflow", lambda: None)
        workflow_map = {"test-workflow": workflow_obj}

        with patch("inspect.getsource", side_effect=OSError("Cannot read source")):
            result = _handle_code_flask(workflow_map, "test-workflow")

            assert (
                result["code"]
                == "# Workflow test-workflow\ndef handler(payload):\n    pass"
            )


class TestExtractWorkflowDetailsFlask:
    """Test cases for _extract_workflow_details_flask function."""

    def test_extract_workflow_details_basic(self):
        """Test basic workflow details extraction."""
        workflow_registry.clear()

        @workflow("detail-workflow-flask")
        def detail_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        details = _extract_workflow_details_flask(
            "detail-workflow-flask", detail_workflow._workflow
        )

        assert details["workflow_id"] == "detail-workflow-flask"
        assert details["severity"] == "none"
        assert details["code"] is not None
        assert "def detail_workflow" in details["code"]
        assert len(details["steps"]) == 1
        assert details["payload"]["schema"]["type"] == "object"
        assert details["controls"]["schema"]["type"] == "object"
        assert details["tags"] == []
        assert details["preferences"] == {}

    def test_extract_workflow_details_with_attributes(self):
        """Test workflow details extraction with custom attributes."""
        workflow_registry.clear()

        @workflow("attributed-workflow-flask")
        def attributed_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        # Add custom attributes to the workflow object
        attributed_workflow._workflow.tags = ["test", "email"]
        attributed_workflow._workflow.preferences = {"priority": "high"}

        details = _extract_workflow_details_flask(
            "attributed-workflow-flask", attributed_workflow._workflow
        )

        assert details["tags"] == ["test", "email"]
        assert details["preferences"] == {"priority": "high"}

    def test_extract_workflow_details_source_exception(self):
        """Test workflow details extraction when source cannot be retrieved."""
        workflow_obj = Workflow("test-workflow", lambda: None)

        with patch("inspect.getsource", side_effect=OSError("Cannot read source")):
            details = _extract_workflow_details_flask("test-workflow", workflow_obj)

            assert details["workflow_id"] == "test-workflow"
            assert (
                details["code"]
                == "# Workflow test-workflow\ndef handler(payload):\n    pass"
            )


class TestExtractWorkflowStepsFlask:
    """Test cases for _extract_workflow_steps_flask function."""

    def test_extract_workflow_steps_all_types(self):
        """Test extracting steps with all supported types."""

        @workflow("all-types-workflow")
        def all_types_workflow(payload, step):
            step.in_app("step-1", lambda: {"message": "In app"})
            step.email("step-2", lambda: {"message": "Email"})
            step.sms("step-3", lambda: {"message": "SMS"})
            step.push("step-4", lambda: {"message": "Push"})
            step.chat("step-5", lambda: {"message": "Chat"})
            return {"status": "completed"}

        steps = _extract_workflow_steps_flask(all_types_workflow._workflow)

        assert len(steps) == 5

        # Check step IDs are sequential
        assert steps[0]["step_id"] == "step-1"
        assert steps[1]["step_id"] == "step-2"
        assert steps[2]["step_id"] == "step-3"
        assert steps[3]["step_id"] == "step-4"
        assert steps[4]["step_id"] == "step-5"

        # Check step types
        assert steps[0]["type"] == "in_app"
        assert steps[1]["type"] == "email"
        assert steps[2]["type"] == "sms"
        assert steps[3]["type"] == "push"
        assert steps[4]["type"] == "chat"

        # Check step structure
        for step_detail in steps:
            assert "controls" in step_detail
            assert "outputs" in step_detail
            assert "results" in step_detail
            assert "code" in step_detail
            assert "options" in step_detail
            assert "providers" in step_detail
            assert step_detail["providers"] == [step_detail["type"]]

    def test_extract_workflow_steps_no_steps(self):
        """Test extracting steps from workflow with no steps."""
        workflow_registry.clear()

        @workflow("no-steps-workflow-flask")
        def no_steps_workflow(payload, step):
            return {"status": "completed"}

        steps = _extract_workflow_steps_flask(no_steps_workflow._workflow)
        assert steps == []

    def test_extract_workflow_steps_source_exception(self):
        """Test extracting steps when source cannot be retrieved."""
        workflow_obj = Workflow("test-workflow", lambda: None)

        with patch("inspect.getsource", side_effect=OSError("Cannot read source")):
            steps = _extract_workflow_steps_flask(workflow_obj)
            assert steps == []

    def test_extract_workflow_steps_syntax_error(self):
        """Test extracting steps when source has syntax error."""
        workflow_obj = Workflow("test-workflow", lambda: None)

        with patch("inspect.getsource", return_value="invalid syntax"):
            steps = _extract_workflow_steps_flask(workflow_obj)
            assert steps == []


class TestExtractSchemasFlask:
    """Test cases for Flask schema extraction functions."""

    def test_extract_payload_schema_flask(self):
        """Test payload schema extraction."""
        workflow_obj = Workflow("test-workflow", lambda: None)
        schema = _extract_payload_schema_flask(workflow_obj)

        assert schema["type"] == "object"
        assert schema["properties"] == {}
        assert schema["required"] == []
        assert schema["additionalProperties"] is False

    def test_extract_controls_schema_flask(self):
        """Test controls schema extraction."""
        workflow_obj = Workflow("test-workflow", lambda: None)
        schema = _extract_controls_schema_flask(workflow_obj)

        assert schema["type"] == "object"
        assert schema["properties"] == {}
        assert schema["required"] == []
        assert schema["additionalProperties"] is False


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
