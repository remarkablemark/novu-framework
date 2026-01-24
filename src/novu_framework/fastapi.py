import ast
import inspect
import textwrap
from typing import Any, Dict, List

from fastapi import APIRouter, FastAPI, HTTPException

from novu_framework.workflow import Workflow

from novu_framework.validation.api import (  # isort:skip
    Discovered,
    HealthCheckResponse,
    TriggerPayload,
)


def count_steps_in_workflow(workflow: Workflow) -> int:
    """Count steps by analyzing the handler function with AST."""
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
        Health check endpoint for Novu Framework.
        """
        total_workflows = len(workflow_map)
        total_steps = 0

        for workflow in workflow_map.values():
            # Count steps using AST analysis
            step_count = count_steps_in_workflow(workflow)
            total_steps += step_count

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
