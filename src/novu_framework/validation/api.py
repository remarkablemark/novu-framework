from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ..constants import FRAMEWORK_VERSION, SDK_VERSION


class Discovered(BaseModel):
    """
    Information about discovered workflows and steps.
    """

    workflows: int = Field(..., description="Number of available workflows")
    steps: int = Field(..., description="Total number of steps across all workflows")


class HealthCheckResponse(BaseModel):
    """
    Response model for the root health check endpoint.
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
    discovered: Discovered = Field(..., description="Discovery information")

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
