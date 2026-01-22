import inspect
from typing import Any, Dict, List

from fastapi import APIRouter, FastAPI, HTTPException

from novu_framework.workflow import Workflow

from novu_framework.validation.api import (  # isort:skip
    Discovered,
    HealthCheckResponse,
    TriggerPayload,
)


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

    @router.get("", response_model=HealthCheckResponse)
    async def health_check() -> HealthCheckResponse:
        """
        Discovery endpoint for Novu Framework.
        """
        total_workflows = len(workflow_map)
        total_steps = 0

        for workflow in workflow_map.values():
            # Count steps by analyzing the handler function's source code
            try:
                source = inspect.getsource(workflow.handler)
                # Count step method calls (in_app, email, sms, push)
                step_count = (
                    source.count("await step.in_app")
                    + source.count("await step.email")
                    + source.count("await step.sms")
                    + source.count("await step.push")
                )
                total_steps += step_count
            except (OSError, TypeError):
                # If we can't get source code, skip step counting for this workflow
                pass

        return HealthCheckResponse(
            discovered=Discovered(
                workflows=total_workflows,
                steps=total_steps,
            ),
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
            result = await workflow.trigger(
                to=body.to, payload=body.payload, metadata=body.metadata
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(router)
