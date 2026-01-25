"""Unit tests for discover action handlers."""

from unittest.mock import Mock, patch

import pytest

from novu_framework.validation.api import DiscoverResponse
from novu_framework.workflow import Workflow

from novu_framework.fastapi import (  # isort:skip
    _extract_workflow_details,
    _extract_workflow_steps,
    _handle_discover,
)


class TestDiscoverAction:
    """Test discover action handlers and utilities."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_workflow = Mock(spec=Workflow)
        self.mock_workflow.workflow_id = "test-workflow"
        self.mock_workflow.handler = lambda payload: "test result"

    @pytest.mark.asyncio
    async def test_handle_discover_function(self):
        """Test the _handle_discover function directly."""
        workflow_map = {"test-workflow": self.mock_workflow}

        response_data = await _handle_discover(workflow_map)

        assert isinstance(response_data, dict)
        assert "workflows" in response_data
        assert len(response_data["workflows"]) == 1
        workflow = response_data["workflows"][0]
        assert workflow["workflowId"] == "test-workflow"
        assert "steps" in workflow
        assert "code" in workflow
        assert "payload" in workflow
        assert "controls" in workflow

    def test_extract_workflow_details(self):
        """Test _extract_workflow_details function."""
        workflow_detail = _extract_workflow_details("test-workflow", self.mock_workflow)

        assert workflow_detail["workflow_id"] == "test-workflow"
        assert workflow_detail["severity"] == "none"
        assert isinstance(workflow_detail["steps"], list)
        assert "code" in workflow_detail
        assert "payload" in workflow_detail
        assert "controls" in workflow_detail
        assert workflow_detail["tags"] == []
        assert workflow_detail["preferences"] == {}

    def test_extract_workflow_details_with_tags_and_preferences(self):
        """Test _extract_workflow_details with custom tags and preferences."""
        # Create workflow with custom attributes
        custom_workflow = Mock(spec=Workflow)
        custom_workflow.workflow_id = "custom-workflow"
        custom_workflow.handler = lambda payload: "test"
        custom_workflow.tags = ["test", "demo"]
        custom_workflow.preferences = {"priority": "high", "timeout": 30}

        workflow_detail = _extract_workflow_details("custom-workflow", custom_workflow)

        assert workflow_detail["tags"] == ["test", "demo"]
        assert workflow_detail["preferences"] == {"priority": "high", "timeout": 30}

    def test_extract_workflow_steps_empty(self):
        """Test _extract_workflow_steps with workflow that has no steps."""

        def empty_workflow(payload):
            return "no steps"

        empty_mock = Mock(spec=Workflow)
        empty_mock.handler = empty_workflow

        steps = _extract_workflow_steps(empty_mock)

        assert steps == []

    def test_extract_workflow_steps_with_steps(self):
        """Test _extract_workflow_steps with workflow that has steps."""

        def workflow_with_steps(payload, step):
            step.email("send-email", lambda: {"subject": "Test"})
            step.in_app("show-notification", lambda: {"body": "Notification"})
            step.sms("send-sms", lambda: {"message": "SMS message"})
            return "completed"

        steps_workflow = Mock(spec=Workflow)
        steps_workflow.handler = workflow_with_steps

        steps = _extract_workflow_steps(steps_workflow)

        assert len(steps) == 3
        assert steps[0]["step_id"] == "step-1"
        assert steps[0]["type"] == "email"
        assert steps[1]["step_id"] == "step-2"
        assert steps[1]["type"] == "in_app"
        assert steps[2]["step_id"] == "step-3"
        assert steps[2]["type"] == "sms"

    def test_extract_workflow_steps_structure(self):
        """Test _extract_workflow_steps returns proper step structure."""

        def simple_workflow(payload):
            step.email("test-email", lambda: {"subject": "Test"})
            return "done"

        simple_mock = Mock(spec=Workflow)
        simple_mock.handler = simple_workflow

        steps = _extract_workflow_steps(simple_mock)

        assert len(steps) == 1
        step = steps[0]

        # Check required fields
        required_fields = [
            "step_id",
            "type",
            "controls",
            "outputs",
            "results",
            "code",
            "options",
            "providers",
        ]
        for field in required_fields:
            assert field in step

        # Check field types
        assert isinstance(step["step_id"], str)
        assert isinstance(step["type"], str)
        assert isinstance(step["controls"], dict)
        assert isinstance(step["outputs"], dict)
        assert isinstance(step["results"], dict)
        assert isinstance(step["code"], str)
        assert isinstance(step["options"], dict)
        assert isinstance(step["providers"], list)

        # Check step type is valid
        assert step["type"] in {"email", "in_app", "sms", "push", "chat"}

    def test_extract_workflow_steps_error_handling(self):
        """Test _extract_workflow_steps handles errors gracefully."""

        # Create a workflow that will cause an error during AST parsing
        def error_workflow(payload, step):
            # This will cause a syntax error when parsed
            step.email("test", lambda: {"subject": "Test"})
            return "done"

        error_mock = Mock(spec=Workflow)
        error_mock.handler = error_workflow

        # Mock inspect.getsource to raise an exception
        with patch(
            "novu_framework.fastapi.inspect.getsource",
            side_effect=OSError("Cannot get source"),
        ):
            steps = _extract_workflow_steps(error_mock)
            assert steps == []

    def test_extract_workflow_steps_invalid_step_type(self):
        """Test _extract_workflow_steps ignores invalid step types."""

        def invalid_workflow(payload, step):
            step.email("valid-email", lambda: {"subject": "Valid"})
            step.invalid_type("invalid-step", lambda: {"data": "Invalid"})
            step.in_app("valid-in-app", lambda: {"body": "Valid"})
            return "done"

        invalid_mock = Mock(spec=Workflow)
        invalid_mock.handler = invalid_workflow

        steps = _extract_workflow_steps(invalid_mock)

        # Should only extract valid step types
        assert len(steps) == 2
        assert steps[0]["type"] == "email"
        assert steps[1]["type"] == "in_app"

    def test_discover_response_serialization(self):
        """Test DiscoverResponse serialization with extracted workflow details."""
        workflow_detail = _extract_workflow_details("test-workflow", self.mock_workflow)

        response = DiscoverResponse(workflows=[workflow_detail])
        data = response.model_dump(by_alias=True)

        assert "workflows" in data
        assert len(data["workflows"]) == 1
        workflow = data["workflows"][0]
        assert workflow["workflowId"] == "test-workflow"
        assert "steps" in workflow
        assert "code" in workflow
        assert "payload" in workflow
        assert "controls" in workflow

    def test_discover_response_empty_workflows(self):
        """Test DiscoverResponse with no workflows."""
        response = DiscoverResponse(workflows=[])
        data = response.model_dump(by_alias=True)

        assert data["workflows"] == []

    def test_discover_response_multiple_workflows(self):
        """Test DiscoverResponse with multiple workflows."""
        workflow1 = Mock(spec=Workflow)
        workflow1.workflow_id = "workflow-1"
        workflow1.handler = lambda p: "result1"

        workflow2 = Mock(spec=Workflow)
        workflow2.workflow_id = "workflow-2"
        workflow2.handler = lambda p: "result2"

        detail1 = _extract_workflow_details("workflow-1", workflow1)
        detail2 = _extract_workflow_details("workflow-2", workflow2)

        response = DiscoverResponse(workflows=[detail1, detail2])
        data = response.model_dump(by_alias=True)

        assert len(data["workflows"]) == 2
        assert data["workflows"][0]["workflowId"] == "workflow-1"
        assert data["workflows"][1]["workflowId"] == "workflow-2"

    def test_payload_schema_extraction(self):
        """Test payload schema extraction."""
        from novu_framework.fastapi import _extract_payload_schema

        schema = _extract_payload_schema(self.mock_workflow)

        assert isinstance(schema, dict)
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert "additionalProperties" in schema
        assert schema["additionalProperties"] is False

    def test_controls_schema_extraction(self):
        """Test controls schema extraction."""
        from novu_framework.fastapi import _extract_controls_schema

        schema = _extract_controls_schema(self.mock_workflow)

        assert isinstance(schema, dict)
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert "additionalProperties" in schema
        assert schema["additionalProperties"] is False
