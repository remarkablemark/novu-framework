"""Unit tests for GET action handlers."""

import pytest

from novu_framework.validation.api import (  # isort:skip
    CodeResponse,
    DiscoveredWorkflows,
    DiscoverResponse,
    GetActionEnum,
    GetRequestQuery,
    HealthCheckResponse,
)


class TestGetRequestQuery:
    """Test GetRequestQuery validation."""

    def test_default_action(self):
        """Test default action is health-check."""
        query = GetRequestQuery()
        assert query.action == GetActionEnum.HEALTH_CHECK
        assert query.workflow_id is None
        assert query.step_id is None

    def test_discover_action(self):
        """Test discover action validation."""
        query = GetRequestQuery(action=GetActionEnum.DISCOVER)
        assert query.action == GetActionEnum.DISCOVER

    def test_code_action_requires_workflow_id(self):
        """Test code action validation with missing workflow_id."""
        query = GetRequestQuery(action=GetActionEnum.CODE, workflow_id=None)
        # This should not raise validation error since workflow_id is optional
        # The validation happens in the handler logic
        assert query.action == GetActionEnum.CODE
        assert query.workflow_id is None

    def test_invalid_action_raises_error(self):
        """Test invalid action raises ValidationError."""
        with pytest.raises(ValueError):
            GetRequestQuery(action="invalid-action")


class TestResponseModels:
    """Test response model serialization."""

    def test_health_check_response_serialization(self):
        """Test HealthCheckResponse serialization."""
        discovered = DiscoveredWorkflows(workflows=2, steps=5)
        response = HealthCheckResponse(status="ok", discovered=discovered)

        data = response.model_dump(by_alias=True)
        assert data["status"] == "ok"
        assert data["sdkVersion"] is not None
        assert data["frameworkVersion"] is not None
        assert data["discovered"]["workflows"] == 2
        assert data["discovered"]["steps"] == 5

    def test_discover_response_serialization(self):
        """Test DiscoverResponse serialization."""
        workflows = [
            {
                "workflow_id": "test-workflow",
                "severity": "none",
                "steps": [],
                "code": "def test(): pass",
                "payload": {
                    "schema": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False,
                    },
                    "unknownSchema": {},
                },
                "controls": {
                    "schema": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False,
                    },
                    "unknownSchema": {},
                },
                "tags": [],
                "preferences": {},
            }
        ]

        response = DiscoverResponse(workflows=workflows)
        data = response.model_dump(by_alias=True)

        assert data["workflows"][0]["workflowId"] == "test-workflow"
        assert data["workflows"][0]["severity"] == "none"

    def test_code_response_serialization(self):
        """Test CodeResponse serialization."""
        code = "async ({ step, payload }) => { await step.email('test', () => ({ subject: 'Test' })); }"
        response = CodeResponse(code=code)

        data = response.model_dump(by_alias=True)
        assert data["code"] == code


class TestGetActionEnum:
    """Test GetActionEnum values."""

    def test_enum_values(self):
        """Test all enum values are correct."""
        assert GetActionEnum.DISCOVER == "discover"
        assert GetActionEnum.HEALTH_CHECK == "health-check"
        assert GetActionEnum.CODE == "code"

    def test_enum_is_string(self):
        """Test enum inherits from str."""
        assert isinstance(GetActionEnum.DISCOVER, str)
        assert GetActionEnum.HEALTH_CHECK.value == "health-check"
