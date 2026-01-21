from typing import Any, Dict

from pydantic import BaseModel

from novu_framework.workflow import workflow, workflow_registry


class AutoPayload(BaseModel):
    message: str


def test_workflow_decorator_auto_extract_payload_param():
    """Test workflow decorator automatically extracts schema from payload parameter."""
    workflow_registry.clear()

    @workflow("auto-payload-workflow")
    async def auto_workflow(payload: AutoPayload, step):
        return {"processed": True}

    workflow_obj = workflow_registry.get("auto-payload-workflow")
    assert workflow_obj is not None
    assert workflow_obj.payload_schema == AutoPayload


def test_workflow_decorator_auto_extract_first_param():
    """Test workflow decorator extracts schema from first BaseModel parameter."""
    workflow_registry.clear()

    @workflow("auto-first-workflow")
    async def auto_first_workflow(data: AutoPayload, step):
        return {"processed": True}

    workflow_obj = workflow_registry.get("auto-first-workflow")
    assert workflow_obj is not None
    assert workflow_obj.payload_schema == AutoPayload


def test_workflow_decorator_auto_extract_no_basemodel():
    """Test workflow decorator when no BaseModel parameter is found."""
    workflow_registry.clear()

    @workflow("auto-no-basemodel-workflow")
    async def auto_no_basemodel_workflow(payload: Dict[str, Any], step):
        return {"processed": True}

    workflow_obj = workflow_registry.get("auto-no-basemodel-workflow")
    assert workflow_obj is not None
    assert workflow_obj.payload_schema is None
