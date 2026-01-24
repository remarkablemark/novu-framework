"""
Flask integration for novu-framework.

This module provides Flask-specific workflow serving capabilities,
equivalent to the FastAPI integration but using Flask's ecosystem.
"""

from __future__ import annotations

from typing import List, Tuple

from flask import Blueprint, Flask, Response, jsonify, request
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

from novu_framework.workflow import Workflow

from novu_framework.validation.api import (  # isort:skip
    Discovered,
    HealthCheckResponse,
    TriggerPayload,
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
            clean_source = source

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
    async def health_check() -> Response:
        """
        Health check endpoint for Novu Framework.
        """
        total_workflows = len(workflow_map)
        total_steps = 0

        for workflow in workflow_map.values():
            # Count steps using AST analysis
            step_count = count_steps_in_workflow(workflow)
            total_steps += step_count

        response = HealthCheckResponse(
            discovered=Discovered(
                workflows=total_workflows,
                steps=total_steps,
            )
        )
        return jsonify(response.model_dump(by_alias=True))

    @blueprint.route("/workflows/<workflow_id>/execute", methods=["POST"])
    async def execute_workflow(workflow_id: str) -> Response:
        """
        Trigger a workflow execution.
        """
        if workflow_id not in workflow_map:
            raise NotFound(f"Workflow '{workflow_id}' not found")

        workflow = workflow_map[workflow_id]
        try:
            # Parse and validate request body
            data = request.get_json()
            if not data:
                raise BadRequest("Invalid JSON payload")

            payload = TriggerPayload(**data)
            result = await workflow.trigger(
                to=payload.to, payload=payload.payload, metadata=payload.metadata
            )
            return jsonify(result)
        except ValidationError as e:
            # Handle Pydantic validation errors
            error_details = e.errors()
            error_msg = "Validation error: " + "; ".join(
                [f"{err['loc'][-1]}: {err['msg']}" for err in error_details]
            )
            raise BadRequest(error_msg)
        except BadRequest:
            raise  # Re-raise BadRequest as-is
        except Exception as e:
            raise InternalServerError(str(e))

    # Register error handlers to match FastAPI error format
    @blueprint.errorhandler(NotFound)
    def handle_not_found(e: NotFound) -> Tuple[Response, int]:
        return jsonify({"detail": str(e)}), 404

    @blueprint.errorhandler(BadRequest)
    def handle_bad_request(e: BadRequest) -> Tuple[Response, int]:
        return jsonify({"detail": str(e)}), 400

    @blueprint.errorhandler(InternalServerError)
    def handle_internal_server_error(e: InternalServerError) -> Tuple[Response, int]:
        return jsonify({"detail": str(e)}), 500

    app.register_blueprint(blueprint)
