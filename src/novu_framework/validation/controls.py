from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ControlSchema(BaseModel):
    """
    Schema for non-technical configuration modifications.
    """

    schema_id: str = Field(..., description="Unique schema identifier")
    workflow_id: str = Field(..., description="Parent workflow identifier")
    step_id: Optional[str] = Field(
        None, description="Parent step identifier (workflow-level if None)"
    )
    schema_dict: Dict[str, Any] = Field(..., description="Pydantic schema definition")
    description: str = Field(..., description="Human-readable schema description")

    model_config = {"extra": "forbid"}
