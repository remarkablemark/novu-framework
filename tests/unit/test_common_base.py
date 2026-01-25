"""Base test class for shared workflow functionality tests."""

from unittest.mock import patch

import pytest

from novu_framework import workflow
from novu_framework.error_handling import NotFoundError, ValidationError
from novu_framework.workflow import Workflow, workflow_registry

from novu_framework.common import (  # isort: skip
    extract_controls_schema,
    extract_payload_schema,
    extract_workflow_details,
    extract_workflow_steps,
    handle_code,
    handle_discover,
    handle_health_check,
    count_steps_in_workflow,
)


class BaseTestWorkflowFunctionality:
    """Base test class for shared workflow functionality."""

    def test_count_steps_in_workflow_simple(self):
        """Test counting steps in a simple workflow."""
        workflow_registry.clear()

        @workflow(self.get_workflow_name("test-workflow"))
        def test_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            step.sms("step-2", lambda: {"message": "SMS"})
            return {"status": "completed"}

        count = count_steps_in_workflow(test_workflow._workflow)
        assert count == 2

    def test_count_steps_in_workflow_all_step_types(self):
        """Test counting all supported step types."""
        workflow_registry.clear()

        @workflow(self.get_workflow_name("all-steps-workflow"))
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

        @workflow(self.get_workflow_name("no-steps-workflow"))
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

    def test_handle_health_check_empty(self):
        """Test health check with no workflows."""
        result = handle_health_check({})

        assert result["status"] == "ok"
        assert result["discovered"]["workflows"] == 0
        assert result["discovered"]["steps"] == 0

    def test_handle_health_check_with_workflows(self):
        """Test health check with workflows."""
        workflow_registry.clear()

        @workflow(self.get_workflow_name("health-check-workflow"))
        def health_check_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            step.sms("step-2", lambda: {"text": "SMS"})
            return {"status": "completed"}

        workflow_map = {
            self.get_workflow_name(
                "health-check-workflow"
            ): health_check_workflow._workflow
        }
        result = handle_health_check(workflow_map)

        assert result["status"] == "ok"
        assert result["discovered"]["workflows"] == 1
        assert result["discovered"]["steps"] == 2

    def test_handle_health_check_mixed_workflows(self):
        """Test health check with mixed workflows (some with steps, some without)."""
        workflow_registry.clear()

        @workflow(self.get_workflow_name("with-steps"))
        def with_steps_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        @workflow(self.get_workflow_name("without-steps"))
        def without_steps_workflow(payload):
            return {"status": "completed"}

        workflow_map = {
            self.get_workflow_name("with-steps"): with_steps_workflow._workflow,
            self.get_workflow_name("without-steps"): without_steps_workflow._workflow,
        }
        result = handle_health_check(workflow_map)

        assert result["status"] == "ok"
        assert result["discovered"]["workflows"] == 2
        assert result["discovered"]["steps"] == 1

    def test_handle_discover_empty(self):
        """Test discover with no workflows."""
        result = handle_discover({})
        assert result["workflows"] == []

    def test_handle_discover_with_workflow(self):
        """Test discover with a workflow."""
        workflow_registry.clear()

        @workflow(self.get_workflow_name("discover-workflow"))
        def discover_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        workflow_map = {
            self.get_workflow_name("discover-workflow"): discover_workflow._workflow
        }
        result = handle_discover(workflow_map)

        assert len(result["workflows"]) == 1
        workflow_detail = result["workflows"][0]
        assert workflow_detail["workflowId"] == self.get_workflow_name(
            "discover-workflow"
        )
        assert workflow_detail["severity"] == "none"
        assert len(workflow_detail["steps"]) == 1
        assert workflow_detail["steps"][0]["stepId"] == "step-1"
        assert workflow_detail["steps"][0]["type"] == "email"

    def test_handle_discover_multiple_workflows(self):
        """Test discover with multiple workflows."""
        workflow_registry.clear()

        @workflow(self.get_workflow_name("workflow-1"))
        def workflow_1(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        @workflow(self.get_workflow_name("workflow-2"))
        def workflow_2(payload, step):
            step.sms("step-1", lambda: {"text": "SMS"})
            return {"status": "completed"}

        workflow_map = {
            self.get_workflow_name("workflow-1"): workflow_1._workflow,
            self.get_workflow_name("workflow-2"): workflow_2._workflow,
        }
        result = handle_discover(workflow_map)

        assert len(result["workflows"]) == 2

        # Check first workflow
        wf1 = next(
            w
            for w in result["workflows"]
            if w["workflowId"] == self.get_workflow_name("workflow-1")
        )
        assert len(wf1["steps"]) == 1
        assert wf1["steps"][0]["type"] == "email"

        # Check second workflow
        wf2 = next(
            w
            for w in result["workflows"]
            if w["workflowId"] == self.get_workflow_name("workflow-2")
        )
        assert len(wf2["steps"]) == 1
        assert wf2["steps"][0]["type"] == "sms"

    def test_extract_workflow_details_basic(self):
        """Test basic workflow details extraction."""

        @workflow(self.get_workflow_name("detail-workflow"))
        def detail_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        details = extract_workflow_details(
            self.get_workflow_name("detail-workflow"), detail_workflow._workflow
        )

        assert details["workflow_id"] == self.get_workflow_name("detail-workflow")
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

        @workflow(self.get_workflow_name("attributed-workflow"))
        def attributed_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        # Add custom attributes to the workflow object
        attributed_workflow._workflow.tags = ["test", "email"]
        attributed_workflow._workflow.preferences = {"priority": "high"}

        details = extract_workflow_details(
            self.get_workflow_name("attributed-workflow"), attributed_workflow._workflow
        )

        assert details["tags"] == ["test", "email"]
        assert details["preferences"] == {"priority": "high"}

    def test_extract_workflow_details_source_exception(self):
        """Test workflow details extraction when source cannot be retrieved."""
        workflow_obj = Workflow("test-workflow", lambda: None)

        with patch("inspect.getsource", side_effect=OSError("Cannot read source")):
            details = extract_workflow_details("test-workflow", workflow_obj)

            assert details["workflow_id"] == "test-workflow"
            assert (
                details["code"]
                == "# Workflow test-workflow\ndef handler(payload):\n    pass"
            )

    def test_extract_workflow_steps_all_types(self):
        """Test extracting steps with all supported types."""

        @workflow(self.get_workflow_name("all-types-workflow"))
        def all_types_workflow(payload, step):
            step.in_app("step-1", lambda: {"message": "In app"})
            step.email("step-2", lambda: {"message": "Email"})
            step.sms("step-3", lambda: {"message": "SMS"})
            step.push("step-4", lambda: {"message": "Push"})
            step.chat("step-5", lambda: {"message": "Chat"})
            return {"status": "completed"}

        steps = extract_workflow_steps(all_types_workflow._workflow)

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

        @workflow(self.get_workflow_name("no-steps-workflow"))
        def no_steps_workflow(payload, step):
            return {"status": "completed"}

        steps = extract_workflow_steps(no_steps_workflow._workflow)
        assert steps == []

    def test_extract_workflow_steps_source_exception(self):
        """Test extracting steps when source cannot be retrieved."""
        workflow_obj = Workflow("test-workflow", lambda: None)

        with patch("inspect.getsource", side_effect=OSError("Cannot read source")):
            steps = extract_workflow_steps(workflow_obj)
            assert steps == []

    def test_extract_workflow_steps_syntax_error(self):
        """Test extracting steps when source has syntax error."""
        workflow_obj = Workflow("test-workflow", lambda: None)

        with patch("inspect.getsource", return_value="invalid syntax"):
            steps = extract_workflow_steps(workflow_obj)
            assert steps == []

    def test_extract_payload_schema(self):
        """Test payload schema extraction."""
        workflow_obj = Workflow("test-workflow", lambda: None)
        schema = extract_payload_schema(workflow_obj)

        assert schema["type"] == "object"
        assert schema["properties"] == {}
        assert schema["required"] == []
        assert schema["additionalProperties"] is False

    def test_extract_controls_schema(self):
        """Test controls schema extraction."""
        workflow_obj = Workflow("test-workflow", lambda: None)
        schema = extract_controls_schema(workflow_obj)

        assert schema["type"] == "object"
        assert schema["properties"] == {}
        assert schema["required"] == []
        assert schema["additionalProperties"] is False

    def test_handle_code_success(self):
        """Test successful code retrieval."""

        @workflow(self.get_workflow_name("code-workflow"))
        def code_workflow(payload, step):
            step.email("step-1", lambda: {"message": "Hello"})
            return {"status": "completed"}

        workflow_map = {
            self.get_workflow_name("code-workflow"): code_workflow._workflow
        }
        result = handle_code(workflow_map, self.get_workflow_name("code-workflow"))

        assert "code" in result
        assert "def code_workflow" in result["code"]

    def test_handle_code_missing_workflow_id(self):
        """Test code action with missing workflow_id."""
        workflow_id = self.get_missing_workflow_id()
        with pytest.raises(ValidationError) as exc_info:
            handle_code({}, workflow_id)

        assert "workflow_id is required" in str(exc_info.value)

    def test_handle_code_workflow_not_found(self):
        """Test code action with non-existent workflow."""
        with pytest.raises(NotFoundError) as exc_info:
            handle_code({}, "nonexistent-workflow")

        assert "not found" in str(exc_info.value)

    def test_handle_code_source_exception(self):
        """Test code retrieval when source cannot be extracted."""
        workflow_obj = Workflow("test-workflow", lambda: None)
        workflow_map = {"test-workflow": workflow_obj}

        with patch("inspect.getsource", side_effect=OSError("Cannot read source")):
            result = handle_code(workflow_map, "test-workflow")

            assert (
                result["code"]
                == "# Workflow test-workflow\ndef handler(payload):\n    pass"
            )

    def get_workflow_name(self, base_name):
        """Override this method to customize workflow naming for each framework."""
        return base_name

    def get_missing_workflow_id(self):
        """Override this method to customize missing workflow ID for each framework."""
        return ""
