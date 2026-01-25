"""Unit tests for code action handlers."""

from unittest.mock import Mock, patch

import pytest

from novu_framework.common import handle_code
from novu_framework.common import handle_code as handle_code_flask
from novu_framework.error_handling import NotFoundError, ValidationError
from novu_framework.validation.api import CodeResponse
from novu_framework.workflow import Workflow


class TestCodeAction:
    """Test code action handlers."""

    def setup_method(self):
        """Set up test fixtures."""

        # Create real workflow instead of mock
        def test_handler(payload):
            return "test result"

        self.workflow = Workflow("test-workflow", test_handler)
        self.workflow_map = {"test-workflow": self.workflow}

    def test_handle_code_function_success(self):
        """Test handle_code function with valid workflow."""
        workflow_id = "test-workflow"

        response_data = handle_code(self.workflow_map, workflow_id)

        assert isinstance(response_data, dict)
        assert "code" in response_data
        assert "def test_handler(payload):" in response_data["code"]

    def test_handle_code_function_missing_workflow_id(self):
        """Test handle_code function with missing workflow_id."""
        with pytest.raises(ValidationError) as exc_info:
            handle_code(self.workflow_map, "")

        assert "workflow_id is required for this action" in str(exc_info.value)

    def test_handle_code_function_workflow_not_found(self):
        """Test handle_code function with non-existent workflow."""
        with pytest.raises(NotFoundError) as exc_info:
            handle_code(self.workflow_map, "non-existent")

        assert "Workflow 'non-existent' not found" in str(exc_info.value)

    def test_handle_code_function_empty_workflow_map(self):
        """Test handle_code function with empty workflow map."""
        empty_map = {}

        with pytest.raises(NotFoundError) as exc_info:
            handle_code(empty_map, "test-workflow")

        assert "Workflow 'test-workflow' not found" in str(exc_info.value)

    def test_handle_code_function_response_format(self):
        """Test handle_code function returns proper response format."""
        workflow_id = "test-workflow"

        response_data = handle_code(self.workflow_map, workflow_id)

        # Check response structure
        assert isinstance(response_data, dict)
        assert "code" in response_data
        assert isinstance(response_data["code"], str)

        # Verify it matches CodeResponse model format
        response = CodeResponse(code=response_data["code"])
        assert response.code == response_data["code"]

    def test_handle_code_flask_function_success(self):
        """Test handle_code_flask function with valid workflow."""
        workflow_id = "test-workflow"

        response_data = handle_code_flask(self.workflow_map, workflow_id)

        assert isinstance(response_data, dict)
        assert "code" in response_data
        assert "def test_handler(payload):" in response_data["code"]

    def test_handle_code_flask_function_missing_workflow_id(self):
        """Test handle_code_flask function with missing workflow_id."""
        with pytest.raises(ValidationError) as exc_info:
            handle_code_flask(self.workflow_map, "")

        assert "workflow_id is required for this action" in str(exc_info.value)

    def test_handle_code_flask_function_workflow_not_found(self):
        """Test handle_code_flask function with non-existent workflow."""
        with pytest.raises(NotFoundError) as exc_info:
            handle_code_flask(self.workflow_map, "non-existent")

        assert "Workflow 'non-existent' not found" in str(exc_info.value)

    def test_handle_code_flask_function_empty_workflow_map(self):
        """Test handle_code_flask function with empty workflow map."""
        empty_map = {}

        with pytest.raises(NotFoundError) as exc_info:
            handle_code_flask(empty_map, "test-workflow")

        assert "Workflow 'test-workflow' not found" in str(exc_info.value)

    def test_handle_code_flask_function_response_format(self):
        """Test handle_code_flask function returns proper response format."""
        workflow_id = "test-workflow"

        response_data = handle_code_flask(self.workflow_map, workflow_id)

        # Check response structure
        assert isinstance(response_data, dict)
        assert "code" in response_data
        assert isinstance(response_data["code"], str)

        # Verify it matches CodeResponse model format
        response = CodeResponse(code=response_data["code"])
        assert response.code == response_data["code"]

    @patch("novu_framework.common.inspect.getsource")
    def test_handle_code_function_source_extraction_error(self, mock_getsource):
        """Test handle_code function handles source extraction errors."""
        mock_getsource.side_effect = OSError("Cannot get source")

        workflow_id = "test-workflow"

        response_data = handle_code(self.workflow_map, workflow_id)

        # Should still return response even with source extraction error
        assert isinstance(response_data, dict)
        assert "code" in response_data
        # When source extraction fails, it should return fallback code
        assert "# Workflow test-workflow" in response_data["code"]

    @patch("novu_framework.common.inspect.getsource")
    def test_handle_code_flask_function_source_extraction_error(self, mock_getsource):
        """Test handle_code_flask function handles source extraction errors."""
        mock_getsource.side_effect = OSError("Cannot get source")

        workflow_id = "test-workflow"

        response_data = handle_code_flask(self.workflow_map, workflow_id)

        # Should still return response even with source extraction error
        assert isinstance(response_data, dict)
        assert "code" in response_data
        # When source extraction fails, it should return fallback code
        assert "# Workflow test-workflow" in response_data["code"]

    def test_handle_code_function_with_complex_workflow(self):
        """Test handle_code function with complex workflow handler."""

        def complex_handler(payload, step_handler):
            step_handler.email("send-welcome", lambda: {"subject": "Welcome!"})
            step_handler.in_app("show-notification", lambda: {"body": "Welcome!"})
            step_handler.sms("send-sms", lambda: {"message": "SMS message"})
            return "completed"

        complex_workflow = Mock(spec=Workflow)
        complex_workflow.workflow_id = "complex-workflow"
        complex_workflow.handler = complex_handler

        workflow_map = {"complex-workflow": complex_workflow}

        response_data = handle_code(workflow_map, "complex-workflow")

        assert isinstance(response_data, dict)
        assert "code" in response_data
        assert "def complex_handler(payload, step_handler):" in response_data["code"]

    def test_handle_code_flask_function_with_complex_workflow(self):
        """Test handle_code_flask function with complex workflow handler."""

        def complex_handler(payload, step_handler):
            step_handler.email("send-welcome", lambda: {"subject": "Welcome!"})
            step_handler.in_app("show-notification", lambda: {"body": "Welcome!"})
            step_handler.sms("send-sms", lambda: {"message": "SMS message"})
            return "completed"

        complex_workflow = Mock(spec=Workflow)
        complex_workflow.workflow_id = "complex-workflow"
        complex_workflow.handler = complex_handler

        workflow_map = {"complex-workflow": complex_workflow}

        response_data = handle_code_flask(workflow_map, "complex-workflow")

        assert isinstance(response_data, dict)
        assert "code" in response_data
        assert "def complex_handler(payload, step_handler):" in response_data["code"]

    def test_handle_code_function_with_decorator_workflow(self):
        """Test handle_code function with decorated workflow handler."""

        @workflow_decorator
        def decorated_handler(payload, step_handler):
            step_handler.email("send-welcome", lambda: {"subject": "Welcome!"})
            return "completed"

        decorated_workflow = Mock(spec=Workflow)
        decorated_workflow.workflow_id = "decorated-workflow"
        decorated_workflow.handler = decorated_handler

        workflow_map = {"decorated-workflow": decorated_workflow}

        response_data = handle_code(workflow_map, "decorated-workflow")

        assert isinstance(response_data, dict)
        assert "code" in response_data
        assert "@workflow_decorator" in response_data["code"]

    def test_handle_code_flask_function_with_decorator_workflow(self):
        """Test handle_code_flask function with decorated workflow handler."""

        @workflow_decorator
        def decorated_handler(payload, step_handler):
            step_handler.email("send-welcome", lambda: {"subject": "Welcome!"})
            return "completed"

        decorated_workflow = Mock(spec=Workflow)
        decorated_workflow.workflow_id = "decorated-workflow"
        decorated_workflow.handler = decorated_handler

        workflow_map = {"decorated-workflow": decorated_workflow}

        response_data = handle_code_flask(workflow_map, "decorated-workflow")

        assert isinstance(response_data, dict)
        assert "code" in response_data
        assert "@workflow_decorator" in response_data["code"]

    def test_handle_code_function_multiple_workflows(self):
        """Test handle_code function with multiple workflows."""

        def handler2(payload):
            return "result2"

        workflow2 = Workflow("workflow-2", handler2)

        workflow_map = {"test-workflow": self.workflow, "workflow-2": workflow2}

        # Test first workflow
        response_data1 = handle_code(workflow_map, "test-workflow")
        assert "def test_handler(payload):" in response_data1["code"]

        # Test second workflow
        response_data2 = handle_code(workflow_map, "workflow-2")
        assert "def handler2(payload):" in response_data2["code"]

    def test_handle_code_flask_function_multiple_workflows(self):
        """Test handle_code_flask function with multiple workflows."""

        def handler2(payload):
            return "result2"

        workflow2 = Workflow("workflow-2", handler2)

        workflow_map = {"test-workflow": self.workflow, "workflow-2": workflow2}

        # Test first workflow
        response_data1 = handle_code_flask(workflow_map, "test-workflow")
        assert "def test_handler(payload):" in response_data1["code"]

        # Test second workflow
        response_data2 = handle_code_flask(workflow_map, "workflow-2")
        assert "def handler2(payload):" in response_data2["code"]

    def test_handle_code_function_code_response_serialization(self):
        """Test handle_code function properly serializes CodeResponse."""
        workflow_id = "test-workflow"

        response_data = handle_code(self.workflow_map, workflow_id)

        # Verify it can be used to create a CodeResponse
        code_response = CodeResponse(**response_data)
        assert code_response.code == response_data["code"]
        assert code_response.model_dump(by_alias=True) == response_data

    def test_handle_code_flask_function_code_response_serialization(self):
        """Test handle_code_flask function properly serializes CodeResponse."""
        workflow_id = "test-workflow"

        response_data = handle_code_flask(self.workflow_map, workflow_id)

        # Verify it can be used to create a CodeResponse
        code_response = CodeResponse(**response_data)
        assert code_response.code == response_data["code"]
        assert code_response.model_dump(by_alias=True) == response_data


# Mock decorator for testing
def workflow_decorator(func):
    return func
