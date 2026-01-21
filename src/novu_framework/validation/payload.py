from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Payload(BaseModel):
    """
    Data structure passed to workflow triggers, validated against schema.
    """

    workflow_id: str = Field(..., description="Target workflow identifier")
    recipient: str = Field(..., description="Target recipient identifier")
    data: Dict[str, Any] = Field(
        ..., description="Payload data matching workflow schema"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional payload metadata"
    )

    model_config = {"extra": "forbid"}
