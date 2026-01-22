from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from ..constants import FRAMEWORK_VERSION, SDK_VERSION


class WorkflowResponse(BaseModel):
    """
    Response model for workflow discovery.
    """

    workflow_id: str = Field(
        ...,
        description="Unique identifier for the workflow",
        serialization_alias="workflowId",
    )
    name: str = Field(..., description="Human-readable workflow name")
    steps: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of workflow steps"
    )
    payload_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON schema for payload validation",
        serialization_alias="payloadSchema",
    )

    model_config = {"populate_by_name": True}


class HealthCheckResponse(BaseModel):
    """
    Response model for the root discovery endpoint.
    """

    workflows: List[WorkflowResponse] = Field(
        ..., description="List of available workflows"
    )
    framework_version: str = Field(
        FRAMEWORK_VERSION,
        description="Version of the Novu Framework",
        serialization_alias="frameworkVersion",
    )
    sdk_version: str = Field(
        SDK_VERSION, description="Version of the SDK", serialization_alias="sdkVersion"
    )

    model_config = {"populate_by_name": True}


class TriggerPayload(BaseModel):
    """
    Request model for triggering a workflow.
    """

    to: Union[str, Dict[str, Any]] = Field(..., description="Target recipient")
    payload: Dict[str, Any] = Field(..., description="Workflow payload data")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )
