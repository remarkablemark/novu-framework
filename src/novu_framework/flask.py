from typing import List, Tuple

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
    GetActionEnum,
    GetRequestQuery,
    TriggerPayload,
)

from novu_framework.common import (  # isort:skip
    handle_health_check as handle_health_check_flask,
    handle_discover as handle_discover_flask,
    handle_code as handle_code_flask,
)

__all__ = ["serve"]


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
                response_data = handle_health_check_flask(workflow_map)
            elif query.action == GetActionEnum.DISCOVER:
                response_data = handle_discover_flask(workflow_map)
            elif query.action == GetActionEnum.CODE:
                try:
                    if not query.workflow_id:
                        raise ValidationError("workflow_id is required for this action")
                    response_data = handle_code_flask(workflow_map, query.workflow_id)
                except (ValidationError, NotFoundError, InternalError) as e:
                    error_response = handle_error(
                        e, f"GET /api/novu?action={action_param}"
                    )
                    response = jsonify(error_response)
                    return response, error_response["status_code"]
            else:  # pragma: no cover
                raise ValidationError(f"Invalid action: {query.action}")

            response = jsonify(response_data)
            return response
        except (ValidationError, NotFoundError, InternalError) as e:
            error_response = handle_error(e, f"GET /api/novu?action={action_param}")
            response = jsonify(error_response)
            return response, error_response["status_code"]
        except ValueError as e:  # pragma: no cover
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
            else:  # pragma: no cover
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
    def handle_not_found(e: Exception) -> Tuple[Response, int]:  # pragma: no cover
        response = jsonify({"detail": str(e)})
        return response, 404

    @blueprint.errorhandler(400)
    def handle_bad_request(e: Exception) -> Tuple[Response, int]:  # pragma: no cover
        response = jsonify({"detail": str(e)})
        return response, 400

    @blueprint.errorhandler(500)
    def handle_internal_server_error(
        e: Exception,
    ) -> Tuple[Response, int]:  # pragma: no cover
        response = jsonify({"detail": str(e)})
        return response, 500

    @blueprint.errorhandler(Exception)
    def handle_generic_error(e: Exception) -> Tuple[Response, int]:  # pragma: no cover
        response = jsonify({"detail": str(e)})
        return response, 500

    app.register_blueprint(blueprint)
