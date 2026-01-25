"""
Common functions shared between FastAPI and Flask integrations.

This module contains framework-agnostic business logic for workflow analysis,
step extraction, and response generation.
"""

import ast
import inspect
import textwrap
from typing import Any, Dict, List

from novu_framework.error_handling import NotFoundError, ValidationError
from novu_framework.workflow import Workflow

from novu_framework.validation.api import (  # isort: skip
    CodeResponse,
    DiscoveredWorkflows,
    DiscoverResponse,
    HealthCheckResponse,
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


def handle_health_check(workflow_map: Dict[str, Workflow]) -> Dict[str, Any]:
    """Handle health check action."""
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


def handle_discover(workflow_map: Dict[str, Workflow]) -> Dict[str, Any]:
    """Handle discover action with detailed workflow information."""
    workflows = []

    for workflow_id, workflow in workflow_map.items():
        # Extract workflow details
        workflow_detail = extract_workflow_details(workflow_id, workflow)
        workflows.append(workflow_detail)

    response = DiscoverResponse(workflows=workflows)  # type: ignore[arg-type]
    return response.model_dump(by_alias=True)


def handle_code(workflow_map: Dict[str, Workflow], workflow_id: str) -> Dict[str, Any]:
    """Handle code action."""
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


def extract_workflow_details(workflow_id: str, workflow: Workflow) -> Dict[str, Any]:
    """Extract detailed information from a workflow for discover response."""
    # Get workflow source code
    try:
        workflow_code = inspect.getsource(workflow.handler)
    except (OSError, TypeError):
        workflow_code = f"# Workflow {workflow_id}\ndef handler(payload):\n    pass"

    # Extract step details using AST analysis
    steps = extract_workflow_steps(workflow)

    # Create workflow detail matching Novu cloud format
    workflow_detail = {
        "workflow_id": workflow_id,
        "severity": "none",
        "steps": steps,
        "code": workflow_code,
        "payload": {"schema": extract_payload_schema(workflow), "unknownSchema": {}},
        "controls": {"schema": extract_controls_schema(workflow), "unknownSchema": {}},
        "tags": getattr(workflow, "tags", []),
        "preferences": getattr(workflow, "preferences", {}),
    }

    return workflow_detail


def extract_workflow_steps(workflow: Workflow) -> List[Dict[str, Any]]:
    """Extract step details from workflow using AST analysis."""
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
                step_code = f"step.{step_type}('{step_id}', () => {{}})"

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


def extract_payload_schema(workflow: Workflow) -> Dict[str, Any]:
    """Extract payload schema from workflow."""
    # Default payload schema - can be enhanced to analyze workflow parameters
    return {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }


def extract_controls_schema(workflow: Workflow) -> Dict[str, Any]:
    """Extract controls schema from workflow."""
    # Default controls schema - can be enhanced to analyze workflow controls
    return {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }
