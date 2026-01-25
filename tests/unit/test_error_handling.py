import pytest
from fastapi import HTTPException

from novu_framework.error_handling import (  # isort: skip
    InternalError,
    NotFoundError,
    ValidationError,
    handle_error,
    validate_action,
    validate_workflow_id,
)


class TestErrorHandlingCoverage:
    """Test cases for error handling edge cases to achieve 100% coverage."""

    def test_internal_error_with_details(self):
        """Test InternalError with details parameter."""
        details = {"error_code": "INTERNAL_ERROR", "context": "test"}
        error = InternalError("Internal error occurred", details=details)

        assert error.message == "Internal error occurred"
        assert error.status_code == 500
        assert error.details == details

    def test_handle_error_with_http_exception(self):
        """Test handle_error with HTTPException."""
        http_error = HTTPException(status_code=400, detail="Bad request")

        result = handle_error(http_error, "test context")

        assert result["detail"] == "Bad request"
        assert result["status_code"] == 400
        assert result["type"] == "HTTPException"

    def test_validate_workflow_id_missing_id(self):
        """Test validate_workflow_id with missing workflow_id."""
        with pytest.raises(ValidationError) as exc_info:
            validate_workflow_id("", {})

        assert "workflow_id is required" in str(exc_info.value)

    def test_validate_workflow_id_not_found(self):
        """Test validate_workflow_id with non-existent workflow."""
        with pytest.raises(NotFoundError) as exc_info:
            validate_workflow_id("nonexistent", {})

        assert "not found" in str(exc_info.value)

    def test_validate_action_invalid_action(self):
        """Test validate_action with invalid action."""
        with pytest.raises(ValidationError) as exc_info:
            validate_action("invalid-action")

        assert "Invalid action" in str(exc_info.value)
        assert "invalid-action" in str(exc_info.value)

    def test_handle_error_with_value_error(self):
        """Test handle_error with ValueError."""
        value_error = ValueError("Invalid value provided")

        result = handle_error(value_error, "test context")

        assert result["detail"] == "Invalid value provided"
        assert result["status_code"] == 400
        assert result["type"] == "ValueError"
