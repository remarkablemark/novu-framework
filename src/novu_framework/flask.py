"""
Flask integration for novu-framework.

This module provides Flask-specific workflow serving capabilities,
equivalent to the FastAPI integration but using Flask's ecosystem.
"""

from __future__ import annotations

import ast
import inspect
import textwrap
from typing import Any, Dict, List, Optional, Tuple

from flask import Blueprint, Flask, Response, jsonify, request
from pydantic import ValidationError as PydanticValidationError

from novu_framework.workflow import Workflow

from novu_framework.error_handling import (  # isort:skip
    InternalError,
    NotFoundError,
    ValidationError,
    handle_error,
    validate_action,
)

from novu_framework.validation.api import (  # isort:skip
    DiscoveredWorkflows,
    DiscoverResponse,
    GetActionEnum,
    GetRequestQuery,
    HealthCheckResponse,
    TriggerPayload,
    CodeResponse,
)

__all__ = ["serve"]


def count_steps_in_workflow(workflow: Workflow) -> int:
    """Count steps by analyzing the handler function with AST."""
    try:
        import ast
        import inspect
        import textwrap

        source = inspect.getsource(workflow.handler)

        # Remove decorator if present - find the function definition
        lines = source.split("\n")
        func_start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("def "):
                func_start = i
                break

        # Get the function lines and dedent them
        func_lines = lines[func_start:]
        if func_lines:
            clean_source = textwrap.dedent("\n".join(func_lines))
        else:
            clean_source = source  # pragma: no cover

        tree = ast.parse(clean_source)

        step_count = 0
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "step"
                and node.func.attr in {"in_app", "email", "sms", "push"}
            ):
                step_count += 1

        return step_count
    except (OSError, TypeError, SyntaxError):
        return 0


def serve(app: Flask, route: str = "/api/novu", workflows: List[Workflow] = []) -> None:
    """
    Serve Novu workflows via Flask.
    """

    blueprint = Blueprint("novu", route, url_prefix=route)
    workflow_map = {}
    for workflow_func in workflows:
        # Check if it's the wrapper or the object
        workflow = getattr(workflow_func, "_workflow", workflow_func)
        workflow_map[workflow.workflow_id] = workflow

    @blueprint.route("", methods=["GET"])
    def handle_get_action() -> Response | Tuple[Response, int]:
        """
        Handle GET requests for workflow discovery, health checks, and code retrieval.
        """
        try:
            # Parse query parameters
            action_param = request.args.get("action", "health-check")
            workflow_id = request.args.get("workflow_id")
            step_id = request.args.get("step_id")

            # Validate action
            validate_action(action_param)

            # Validate query parameters
            query = GetRequestQuery(
                action=GetActionEnum(action_param),
                workflow_id=workflow_id,
                step_id=step_id,
            )

            if query.action == GetActionEnum.HEALTH_CHECK:
                response_data = _handle_health_check_flask(workflow_map)
            elif query.action == GetActionEnum.DISCOVER:
                response_data = _handle_discover_flask(workflow_map)
            elif query.action == GetActionEnum.CODE:
                try:
                    response_data = _handle_code_flask(workflow_map, query.workflow_id)
                except (ValidationError, NotFoundError, InternalError) as e:
                    error_response = handle_error(
                        e, f"GET /api/novu?action={action_param}"
                    )
                    response = jsonify(error_response)
                    return response, error_response["status_code"]
            else:
                raise ValidationError(f"Invalid action: {query.action}")

            response = jsonify(response_data)
            return response
        except (ValidationError, NotFoundError, InternalError) as e:
            error_response = handle_error(e, f"GET /api/novu?action={action_param}")
            response = jsonify(error_response)
            return response, error_response["status_code"]
        except ValueError as e:
            error_response = handle_error(e, f"GET /api/novu?action={action_param}")
            response = jsonify(error_response)
            return response, error_response["status_code"]
        except Exception as e:
            error_response = handle_error(e, f"GET /api/novu?action={action_param}")
            response = jsonify(error_response)
            return response, error_response["status_code"]

    @blueprint.route("/workflows/<workflow_id>/execute", methods=["POST"])
    def execute_workflow(workflow_id: str) -> Response | Tuple[Response, int]:
        """
        Trigger a workflow execution.
        """
        if workflow_id not in workflow_map:
            response = jsonify({"detail": f"Workflow '{workflow_id}' not found"})
            return response, 404

        workflow = workflow_map[workflow_id]
        try:
            # Parse and validate request body
            data = request.get_json()
            if not data:
                response = jsonify({"detail": "Invalid JSON payload"})
                return response, 400

            payload = TriggerPayload(**data)
            result = workflow.trigger(
                to=payload.to, payload=payload.payload, metadata=payload.metadata
            )
            response = jsonify(result)
            return response
        except (ValidationError, PydanticValidationError) as e:
            # Handle Pydantic validation errors
            if isinstance(e, PydanticValidationError):
                error_details = e.errors()
                error_msg = "Validation error: " + "; ".join(
                    [f"{err['loc'][-1]}: {err['msg']}" for err in error_details]
                )
            else:
                error_msg = f"Validation error: {str(e)}"
            response = jsonify({"detail": error_msg})
            return response, 400
        except Exception as e:
            # Check if it's a JSON parsing error
            if "400 Bad Request" in str(e) or "Not a JSON" in str(e):
                response = jsonify({"detail": "Invalid JSON"})
                return response, 400
            response = jsonify({"detail": str(e)})
            return response, 500

    # Register error handlers to match FastAPI error format
    @blueprint.errorhandler(404)
    def handle_not_found(e: Exception) -> Tuple[Response, int]:
        response = jsonify({"detail": str(e)})
        return response, 404

    @blueprint.errorhandler(400)
    def handle_bad_request(e: Exception) -> Tuple[Response, int]:
        response = jsonify({"detail": str(e)})
        return response, 400

    @blueprint.errorhandler(500)
    def handle_internal_server_error(e: Exception) -> Tuple[Response, int]:
        response = jsonify({"detail": str(e)})
        return response, 500

    @blueprint.errorhandler(Exception)
    def handle_generic_error(e: Exception) -> Tuple[Response, int]:
        response = jsonify({"detail": str(e)})
        return response, 500

    app.register_blueprint(blueprint)


def _handle_health_check_flask(workflow_map: Dict[str, Any]) -> Dict[str, Any]:
    """Handle health check action for Flask."""
    total_workflows = len(workflow_map)
    total_steps = 0

    for workflow in workflow_map.values():
        # Count steps using AST analysis
        step_count = count_steps_in_workflow(workflow)
        total_steps += step_count

    response = HealthCheckResponse(
        discovered=DiscoveredWorkflows(workflows=total_workflows, steps=total_steps),
    )
    return response.model_dump(by_alias=True)


def _handle_discover_flask(workflow_map: Dict[str, Any]) -> Dict[str, Any]:
    """Handle discover action for Flask."""
    workflows = []

    for workflow_id, workflow in workflow_map.items():
        # Extract workflow details
        workflow_detail = _extract_workflow_details_flask(workflow_id, workflow)
        workflows.append(workflow_detail)

    response = DiscoverResponse(workflows=workflows)  # type: ignore[arg-type]
    return response.model_dump(by_alias=True)


def _handle_code_flask(
    workflow_map: Dict[str, Any], workflow_id: Optional[str]
) -> Dict[str, Any]:
    """Handle code action for Flask."""

    if not workflow_id:
        raise ValidationError("workflow_id is required for this action")

    if workflow_id not in workflow_map:
        raise NotFoundError(f"Workflow '{workflow_id}' not found")

    workflow = workflow_map[workflow_id]
    try:
        code = inspect.getsource(workflow.handler)
    except (OSError, TypeError):
        # Fallback when source cannot be extracted
        code = f"# Workflow {workflow_id}\ndef handler(payload):\n    pass"

    response = CodeResponse(code=code)
    return response.model_dump(by_alias=True)


def _extract_workflow_details_flask(workflow_id: str, workflow: Any) -> Dict[str, Any]:
    """Extract detailed information from a workflow for discover response."""

    # Get workflow source code
    try:
        workflow_code = inspect.getsource(workflow.handler)
    except (OSError, TypeError):
        workflow_code = f"# Workflow {workflow_id}\ndef handler(payload):\n    pass"

    # Extract step details using AST analysis
    steps = _extract_workflow_steps_flask(workflow)

    # Create workflow detail matching Novu cloud format
    workflow_detail = {
        "workflow_id": workflow_id,
        "severity": "none",
        "steps": steps,
        "code": workflow_code,
        "payload": {
            "schema": _extract_payload_schema_flask(workflow),
            "unknownSchema": {},
        },
        "controls": {
            "schema": _extract_controls_schema_flask(workflow),
            "unknownSchema": {},
        },
        "tags": getattr(workflow, "tags", []),
        "preferences": getattr(workflow, "preferences", {}),
    }

    return workflow_detail


def _extract_workflow_steps_flask(workflow: Any) -> List[Any]:
    """Extract step details from workflow using AST analysis."""
    import inspect

    try:
        source = inspect.getsource(workflow.handler)

        # Remove decorator if present - find the function definition
        lines = source.split("\n")
        func_start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("def "):
                func_start = i
                break

        # Get the function lines and dedent them
        func_lines = lines[func_start:]
        if func_lines:
            clean_source = textwrap.dedent("\n".join(func_lines))
        else:
            clean_source = source  # pragma: no cover

        tree = ast.parse(clean_source)

        steps = []
        step_counter = 0

        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "step"
                and node.func.attr in {"in_app", "email", "sms", "push", "chat"}
            ):
                step_counter += 1
                step_id = f"step-{step_counter}"
                step_type = node.func.attr

                # Extract step code (simplified)
                step_code = f"step.{step_type}('{step_id}', () => {{}}"

                # Create step detail
                step_detail = {
                    "step_id": step_id,
                    "type": step_type,
                    "controls": {
                        "schema": {
                            "type": "object",
                            "properties": {},
                            "required": [],
                            "additionalProperties": False,
                        },
                        "unknownSchema": {},
                    },
                    "outputs": {
                        "schema": {
                            "type": "object",
                            "properties": {},
                            "required": [],
                            "additionalProperties": False,
                        },
                        "unknownSchema": {},
                    },
                    "results": {
                        "schema": {
                            "type": "object",
                            "properties": {},
                            "required": [],
                            "additionalProperties": False,
                        },
                        "unknownSchema": {},
                    },
                    "code": step_code,
                    "options": {},
                    "providers": [step_type],
                }
                steps.append(step_detail)

        return steps
    except (OSError, TypeError, SyntaxError):
        return []


def _extract_payload_schema_flask(workflow: Any) -> Dict[str, Any]:
    """Extract payload schema from workflow."""
    # Default payload schema - can be enhanced to analyze workflow parameters
    return {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }


def _extract_controls_schema_flask(workflow: Any) -> Dict[str, Any]:
    """Extract controls schema from workflow."""
    # Default controls schema - can be enhanced to analyze workflow controls
    return {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }
