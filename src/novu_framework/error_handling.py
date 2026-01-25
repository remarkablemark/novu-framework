"""Centralized error handling for Novu framework."""

import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException

logger = logging.getLogger(__name__)


class NovuError(Exception):
    """Base exception for Novu framework errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(NovuError):
    """Validation error for request parameters."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, 400, details)


class NotFoundError(NovuError):
    """Resource not found error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, 404, details)


class InternalError(NovuError):
    """Internal server error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, 500, details)


def handle_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """
    Handle errors consistently across frameworks.

    Args:
        error: The exception that occurred
        context: Additional context for logging

    Returns:
        Error response dictionary
    """
    # Log the error
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)

    # Handle different error types
    if isinstance(error, NovuError):
        return {
            "detail": error.message,
            "status_code": error.status_code,
            "type": error.__class__.__name__,
            **error.details,
        }
    elif isinstance(error, HTTPException):
        return {
            "detail": error.detail,
            "status_code": error.status_code,
            "type": "HTTPException",
        }
    elif isinstance(error, ValueError):
        return {"detail": str(error), "status_code": 400, "type": "ValueError"}
    else:
        return {
            "detail": "Internal server error",
            "status_code": 500,
            "type": "InternalServerError",
        }


def validate_workflow_id(workflow_id: str, workflow_map: Dict[str, Any]) -> None:
    """
    Validate workflow ID exists in workflow map.

    Args:
        workflow_id: Workflow ID to validate
        workflow_map: Dictionary of available workflows

    Raises:
        ValidationError: If workflow_id is missing
        NotFoundError: If workflow_id is not found
    """
    if not workflow_id:
        raise ValidationError("workflow_id is required for this action")

    if workflow_id not in workflow_map:
        raise NotFoundError(f"Workflow '{workflow_id}' not found")


def validate_action(action: str) -> None:
    """
    Validate action parameter.

    Args:
        action: Action to validate

    Raises:
        ValidationError: If action is invalid
    """
    valid_actions = ["health-check", "discover", "code"]

    if action not in valid_actions:
        raise ValidationError(
            f"Invalid action: {action}. Valid actions: {', '.join(valid_actions)}"
        )
