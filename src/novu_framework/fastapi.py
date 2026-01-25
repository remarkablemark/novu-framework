from typing import Any, Dict, List

from fastapi import APIRouter, FastAPI, HTTPException, Query

from novu_framework.workflow import Workflow

from novu_framework.error_handling import (  # isort:skip
    InternalError,
    NotFoundError,
    ValidationError,
    handle_error,
    validate_action,
    validate_workflow_id,
)

from novu_framework.validation.api import (  # isort:skip
    GetActionEnum,
    GetRequestQuery,
    TriggerPayload,
)

from novu_framework.common import (  # isort:skip
    handle_health_check,
    handle_discover,
    handle_code,
)

__all__ = ["serve"]


def serve(
    app: FastAPI, route: str = "/api/novu", workflows: List[Workflow] = []
) -> None:
    """
    Serve Novu workflows via FastAPI.
    """
    router = APIRouter(prefix=route, tags=["Novu"])
    workflow_map = {}
    for workflow_func in workflows:
        # Check if it's the wrapper or the object
        workflow = getattr(workflow_func, "_workflow", workflow_func)
        workflow_map[workflow.workflow_id] = workflow

    @router.get("", response_model_exclude_unset=True)
    async def handle_get_action(
        action: GetActionEnum = Query(
            default=GetActionEnum.HEALTH_CHECK, description="Action to perform"
        ),
        workflow_id: str = Query(
            default=None, description="Workflow ID (required for code action)"
        ),
        step_id: str = Query(
            default=None, description="Step ID (required for code action)"
        ),
    ) -> Dict[str, Any]:
        """
        Handle GET requests for workflow discovery, health checks, and code retrieval.
        """
        try:
            # Validate action
            validate_action(action.value)

            # Validate query parameters
            query = GetRequestQuery(
                action=action, workflow_id=workflow_id, step_id=step_id
            )

            if query.action == GetActionEnum.HEALTH_CHECK:
                return handle_health_check(workflow_map)
            elif query.action == GetActionEnum.DISCOVER:
                return handle_discover(workflow_map)
            elif query.action == GetActionEnum.CODE:
                if query.workflow_id:
                    validate_workflow_id(query.workflow_id, workflow_map)
                    return handle_code(workflow_map, query.workflow_id)
                else:
                    raise ValidationError("workflow_id is required for this action")
            else:
                raise ValidationError(f"Invalid action: {query.action}")
        except (ValidationError, NotFoundError, InternalError) as e:
            error_response = handle_error(e, f"GET /api/novu?action={action.value}")
            raise HTTPException(
                status_code=error_response["status_code"],
                detail=error_response["detail"],
            )
        except Exception as e:
            error_response = handle_error(e, f"GET /api/novu?action={action.value}")
            raise HTTPException(
                status_code=error_response["status_code"],
                detail=error_response["detail"],
            )

    @router.post("/workflows/{workflow_id}/execute")
    async def execute_workflow(
        workflow_id: str, body: TriggerPayload
    ) -> Dict[str, Any]:
        """
        Trigger a workflow execution.
        """
        if workflow_id not in workflow_map:
            raise HTTPException(
                status_code=404, detail=f"Workflow '{workflow_id}' not found"
            )

        workflow = workflow_map[workflow_id]
        try:
            result = workflow.trigger(
                to=body.to, payload=body.payload, metadata=body.metadata
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(router)
