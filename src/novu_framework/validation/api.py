from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ..constants import GetActionEnum  # Re-export for convenience
from ..constants import FRAMEWORK_VERSION, SDK_VERSION

__all__ = [
    "GetActionEnum",
    "GetRequestQuery",
    "DiscoverResponse",
    "DiscoveredWorkflows",
    "CodeResponse",
    "HealthCheckResponse",
    "TriggerPayload",
]


class GetRequestQuery(BaseModel):
    """Query parameters for GET requests."""

    action: GetActionEnum = Field(
        default=GetActionEnum.HEALTH_CHECK, description="Action to perform"
    )
    workflow_id: Optional[str] = Field(
        default=None, description="Workflow ID (required for code action)"
    )
    step_id: Optional[str] = Field(
        default=None, description="Step ID (required for code action)"
    )


class JSONSchema(BaseModel):
    """JSON Schema definition for validation."""

    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)
    additionalProperties: bool = True


class StepControls(BaseModel):
    json_schema: JSONSchema = Field(
        serialization_alias="schema", validation_alias="schema"
    )
    unknownSchema: Dict[str, Any] = Field(default_factory=dict)


class StepOutputs(BaseModel):
    json_schema: JSONSchema = Field(
        serialization_alias="schema", validation_alias="schema"
    )
    unknownSchema: Dict[str, Any] = Field(default_factory=dict)


class StepResults(BaseModel):
    json_schema: JSONSchema = Field(
        serialization_alias="schema", validation_alias="schema"
    )
    unknownSchema: Dict[str, Any] = Field(default_factory=dict)


class WorkflowStep(BaseModel):
    step_id: str = Field(description="Step identifier", serialization_alias="stepId")
    type: str = Field(description="Step type (in_app, chat, email, sms, push)")
    controls: StepControls = Field(description="Step input controls and validation")
    outputs: StepOutputs = Field(description="Step output schema")
    results: Optional[StepResults] = Field(
        default=None, description="Step results schema"
    )
    code: str = Field(description="Step implementation code")
    options: Dict[str, Any] = Field(default_factory=dict, description="Step options")
    providers: List[str] = Field(
        default_factory=list, description="Available providers"
    )


class WorkflowPayload(BaseModel):
    json_schema: JSONSchema = Field(
        serialization_alias="schema", validation_alias="schema"
    )
    unknownSchema: Dict[str, Any] = Field(default_factory=dict)


class WorkflowControls(BaseModel):
    json_schema: JSONSchema = Field(
        serialization_alias="schema", validation_alias="schema"
    )
    unknownSchema: Dict[str, Any] = Field(default_factory=dict)


class WorkflowDetail(BaseModel):
    workflow_id: str = Field(
        description="Workflow identifier", serialization_alias="workflowId"
    )
    severity: str = Field(default="none", description="Workflow severity level")
    steps: List[WorkflowStep] = Field(description="List of workflow steps")
    code: str = Field(description="Workflow implementation code")
    payload: WorkflowPayload = Field(description="Workflow payload schema")
    controls: WorkflowControls = Field(description="Workflow controls schema")
    tags: List[str] = Field(default_factory=list, description="Workflow tags")
    preferences: Dict[str, Any] = Field(
        default_factory=dict, description="Workflow preferences"
    )


class DiscoverResponse(BaseModel):
    workflows: List[WorkflowDetail] = Field(description="List of discovered workflows")


class DiscoveredWorkflows(BaseModel):
    workflows: int = Field(description="Number of discovered workflows")
    steps: int = Field(description="Total number of steps across all workflows")


class CodeResponse(BaseModel):
    code: str = Field(description="Workflow implementation code")


class Discovered(BaseModel):
    """
    Information about discovered workflows and steps.
    """

    workflows: int = Field(..., description="Number of available workflows")
    steps: int = Field(..., description="Total number of steps across all workflows")


class HealthCheckResponse(BaseModel):
    """
    Response model for the health check action.
    """

    status: str = Field(default="ok", description="Health check status")
    sdk_version: str = Field(
        default=SDK_VERSION,
        description="Python SDK version",
        serialization_alias="sdkVersion",
    )
    framework_version: str = Field(
        default=FRAMEWORK_VERSION,
        description="Novu Framework version",
        serialization_alias="frameworkVersion",
    )
    discovered: DiscoveredWorkflows = Field(description="Workflow discovery metrics")

    model_config = {"populate_by_name": True}


class TriggerPayload(BaseModel):
    """
    Request model for triggering a workflow.
    """

    to: str | Dict[str, Any] = Field(..., description="Target recipient")
    payload: Dict[str, Any] = Field(..., description="Workflow payload data")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )
