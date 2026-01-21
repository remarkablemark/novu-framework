from typing import Any, Dict, List

from fastapi import APIRouter, FastAPI, HTTPException

from novu_framework import __version__
from novu_framework.workflow import Workflow

from novu_framework.validation.api import (  # isort:skip
    DiscoveryResponse,
    TriggerPayload,
    WorkflowResponse,
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

    @router.get("", response_model=DiscoveryResponse)
    async def discovery() -> DiscoveryResponse:
        """
        Discovery endpoint for Novu Framework.
        """
        discovered_workflows = []
        for workflow in workflow_map.values():
            # Note: Step discovery requires executing the workflow or analyzing code.
            # For this MVP, we are not executing the workflow for discovery to avoid
            # side effects or payload requirements. Steps list will be empty for now.
            # A future improvement could be a "dry run" mode with mock payloads.

            payload_schema: Dict[str, Any] = {}
            if workflow.payload_schema:
                try:
                    payload_schema = workflow.payload_schema.model_json_schema()
                except AttributeError:
                    # Fallback if not a Pydantic V2 model or similar issue
                    payload_schema = {}

            discovered_workflows.append(
                WorkflowResponse(
                    workflow_id=workflow.workflow_id,
                    name=workflow.name,
                    payload_schema=payload_schema,
                    steps=[],
                )
            )

        return DiscoveryResponse(
            workflows=discovered_workflows,
            framework_version=__version__,
            sdk_version="0.0.0",  # Placeholder
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
