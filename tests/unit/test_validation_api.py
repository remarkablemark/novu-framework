"""Test cases for validation API models."""

import pytest
from pydantic import ValidationError

from novu_framework.constants import (  # isort: skip
    FRAMEWORK_VERSION,
    SDK_VERSION,
    GetActionEnum,
)

from novu_framework.validation.api import (  # isort: skip
    CodeResponse,
    Discovered,
    DiscoveredWorkflows,
    DiscoverResponse,
    GetRequestQuery,
    HealthCheckResponse,
    JSONSchema,
    StepControls,
    StepOutputs,
    StepResults,
    TriggerPayload,
    WorkflowControls,
    WorkflowDetail,
    WorkflowPayload,
    WorkflowStep,
)


class TestGetRequestQuery:
    """Test cases for GetRequestQuery model."""

    def test_default_values(self):
        """Test default values for GetRequestQuery."""
        query = GetRequestQuery()
        assert query.action == GetActionEnum.HEALTH_CHECK
        assert query.workflow_id is None
        assert query.step_id is None

    def test_explicit_values(self):
        """Test explicit values for GetRequestQuery."""
        query = GetRequestQuery(
            action=GetActionEnum.DISCOVER, workflow_id="test-workflow", step_id="step-1"
        )
        assert query.action == GetActionEnum.DISCOVER
        assert query.workflow_id == "test-workflow"
        assert query.step_id == "step-1"

    def test_serialization(self):
        """Test model serialization."""
        query = GetRequestQuery(action=GetActionEnum.CODE)
        data = query.model_dump()
        assert data["action"] == "code"
        # None values are included by default in Pydantic v2
        assert data["workflow_id"] is None
        assert data["step_id"] is None


class TestJSONSchema:
    """Test cases for JSONSchema model."""

    def test_default_values(self):
        """Test default values for JSONSchema."""
        schema = JSONSchema(type="object")
        assert schema.type == "object"
        assert schema.properties == {}
        assert schema.required == []
        assert schema.additionalProperties is True

    def test_explicit_values(self):
        """Test explicit values for JSONSchema."""
        schema = JSONSchema(
            type="string",
            properties={"format": {"type": "email"}},
            required=["format"],
            additionalProperties=False,
        )
        assert schema.type == "string"
        assert schema.properties == {"format": {"type": "email"}}
        assert schema.required == ["format"]
        assert schema.additionalProperties is False


class TestStepControls:
    """Test cases for StepControls model."""

    def test_step_controls_creation(self):
        """Test StepControls creation."""
        json_schema = JSONSchema(type="object")
        controls = StepControls(schema=json_schema, unknownSchema={"custom": "value"})
        assert controls.json_schema == json_schema
        assert controls.unknownSchema == {"custom": "value"}

    def test_step_controls_defaults(self):
        """Test StepControls with defaults."""
        controls = StepControls(schema=JSONSchema(type="object"))
        assert controls.json_schema.type == "object"
        assert controls.unknownSchema == {}


class TestStepOutputs:
    """Test cases for StepOutputs model."""

    def test_step_outputs_creation(self):
        """Test StepOutputs creation."""
        json_schema = JSONSchema(type="object")
        outputs = StepOutputs(schema=json_schema, unknownSchema={"output": "data"})
        assert outputs.json_schema == json_schema
        assert outputs.unknownSchema == {"output": "data"}

    def test_step_outputs_defaults(self):
        """Test StepOutputs with defaults."""
        outputs = StepOutputs(schema=JSONSchema(type="object"))
        assert outputs.json_schema.type == "object"
        assert outputs.unknownSchema == {}


class TestStepResults:
    """Test cases for StepResults model."""

    def test_step_results_creation(self):
        """Test StepResults creation."""
        json_schema = JSONSchema(type="object")
        results = StepResults(schema=json_schema, unknownSchema={"result": "data"})
        assert results.json_schema == json_schema
        assert results.unknownSchema == {"result": "data"}

    def test_step_results_defaults(self):
        """Test StepResults with defaults."""
        results = StepResults(schema=JSONSchema(type="object"))
        assert results.json_schema.type == "object"
        assert results.unknownSchema == {}


class TestWorkflowStep:
    """Test cases for WorkflowStep model."""

    def test_workflow_step_creation(self):
        """Test WorkflowStep creation with all fields."""
        controls = StepControls(schema=JSONSchema(type="object"))
        outputs = StepOutputs(schema=JSONSchema(type="object"))
        results = StepResults(schema=JSONSchema(type="object"))

        step = WorkflowStep(
            step_id="step-1",
            type="email",
            controls=controls,
            outputs=outputs,
            results=results,
            code="step.email('step-1', () => {})",
            options={"async": True},
            providers=["email", "sendgrid"],
        )

        assert step.step_id == "step-1"
        assert step.type == "email"
        assert step.controls == controls
        assert step.outputs == outputs
        assert step.results == results
        assert step.code == "step.email('step-1', () => {})"
        assert step.options == {"async": True}
        assert step.providers == ["email", "sendgrid"]

    def test_workflow_step_defaults(self):
        """Test WorkflowStep with default values."""
        step = WorkflowStep(
            step_id="step-1",
            type="in_app",
            controls=StepControls(schema=JSONSchema(type="object")),
            outputs=StepOutputs(schema=JSONSchema(type="object")),
            code="step.in_app('step-1', () => {})",
        )

        assert step.results is None
        assert step.options == {}
        assert step.providers == []

    def test_workflow_step_serialization_alias(self):
        """Test serialization aliases."""
        step = WorkflowStep(
            step_id="step-1",
            type="email",
            controls=StepControls(schema=JSONSchema(type="object")),
            outputs=StepOutputs(schema=JSONSchema(type="object")),
            code="step.email('step-1', () => {})",
        )

        data = step.model_dump(by_alias=True)
        assert data["stepId"] == "step-1"
        assert "step_id" not in data


class TestWorkflowPayload:
    """Test cases for WorkflowPayload model."""

    def test_workflow_payload_creation(self):
        """Test WorkflowPayload creation."""
        json_schema = JSONSchema(type="object", properties={"name": {"type": "string"}})
        payload = WorkflowPayload(schema=json_schema, unknownSchema={"custom": "value"})

        assert payload.json_schema == json_schema
        assert payload.unknownSchema == {"custom": "value"}

    def test_workflow_payload_defaults(self):
        """Test WorkflowPayload with defaults."""
        payload = WorkflowPayload(schema=JSONSchema(type="object"))
        assert payload.json_schema.type == "object"
        assert payload.unknownSchema == {}


class TestWorkflowControls:
    """Test cases for WorkflowControls model."""

    def test_workflow_controls_creation(self):
        """Test WorkflowControls creation."""
        json_schema = JSONSchema(type="object")
        controls = WorkflowControls(
            schema=json_schema, unknownSchema={"control": "data"}
        )

        assert controls.json_schema == json_schema
        assert controls.unknownSchema == {"control": "data"}

    def test_workflow_controls_defaults(self):
        """Test WorkflowControls with defaults."""
        controls = WorkflowControls(schema=JSONSchema(type="object"))
        assert controls.json_schema.type == "object"
        assert controls.unknownSchema == {}


class TestWorkflowDetail:
    """Test cases for WorkflowDetail model."""

    def test_workflow_detail_creation(self):
        """Test WorkflowDetail creation with all fields."""
        controls = StepControls(schema=JSONSchema(type="object"))
        outputs = StepOutputs(schema=JSONSchema(type="object"))
        step = WorkflowStep(
            step_id="step-1",
            type="email",
            controls=controls,
            outputs=outputs,
            code="step.email('step-1', () => {})",
        )

        detail = WorkflowDetail(
            workflow_id="test-workflow",
            severity="high",
            steps=[step],
            code="def handler(payload, step):\n    pass",
            payload=WorkflowPayload(schema=JSONSchema(type="object")),
            controls=WorkflowControls(schema=JSONSchema(type="object")),
            tags=["test", "email"],
            preferences={"priority": "high"},
        )

        assert detail.workflow_id == "test-workflow"
        assert detail.severity == "high"
        assert detail.steps == [step]
        assert detail.code == "def handler(payload, step):\n    pass"
        assert detail.tags == ["test", "email"]
        assert detail.preferences == {"priority": "high"}

    def test_workflow_detail_defaults(self):
        """Test WorkflowDetail with default values."""
        detail = WorkflowDetail(
            workflow_id="test-workflow",
            steps=[],
            code="def handler(payload, step):\n    pass",
            payload=WorkflowPayload(schema=JSONSchema(type="object")),
            controls=WorkflowControls(schema=JSONSchema(type="object")),
        )

        assert detail.severity == "none"
        assert detail.tags == []
        assert detail.preferences == {}

    def test_workflow_detail_serialization_alias(self):
        """Test serialization aliases."""
        detail = WorkflowDetail(
            workflow_id="test-workflow",
            steps=[],
            code="def handler(payload, step):\n    pass",
            payload=WorkflowPayload(schema=JSONSchema(type="object")),
            controls=WorkflowControls(schema=JSONSchema(type="object")),
        )

        data = detail.model_dump(by_alias=True)
        assert data["workflowId"] == "test-workflow"
        assert "workflow_id" not in data


class TestDiscoverResponse:
    """Test cases for DiscoverResponse model."""

    def test_discover_response_creation(self):
        """Test DiscoverResponse creation."""
        controls = StepControls(schema=JSONSchema(type="object"))
        outputs = StepOutputs(schema=JSONSchema(type="object"))
        step = WorkflowStep(
            step_id="step-1",
            type="email",
            controls=controls,
            outputs=outputs,
            code="step.email('step-1', () => {})",
        )

        detail = WorkflowDetail(
            workflow_id="test-workflow",
            steps=[step],
            code="def handler(payload, step):\n    pass",
            payload=WorkflowPayload(schema=JSONSchema(type="object")),
            controls=WorkflowControls(schema=JSONSchema(type="object")),
        )

        response = DiscoverResponse(workflows=[detail])
        assert response.workflows == [detail]

    def test_discover_response_empty(self):
        """Test DiscoverResponse with empty workflows."""
        response = DiscoverResponse(workflows=[])
        assert response.workflows == []


class TestDiscoveredWorkflows:
    """Test cases for DiscoveredWorkflows model."""

    def test_discovered_workflows_creation(self):
        """Test DiscoveredWorkflows creation."""
        discovered = DiscoveredWorkflows(workflows=5, steps=10)
        assert discovered.workflows == 5
        assert discovered.steps == 10


class TestCodeResponse:
    """Test cases for CodeResponse model."""

    def test_code_response_creation(self):
        """Test CodeResponse creation."""
        code = "def handler(payload, step):\n    pass"
        response = CodeResponse(code=code)
        assert response.code == code


class TestDiscovered:
    """Test cases for Discovered model."""

    def test_discovered_creation(self):
        """Test Discovered creation."""
        discovered = Discovered(workflows=3, steps=7)
        assert discovered.workflows == 3
        assert discovered.steps == 7

    def test_discovered_required_fields(self):
        """Test that Discovered requires all fields."""
        with pytest.raises(ValidationError):
            Discovered()  # Missing required fields


class TestHealthCheckResponse:
    """Test cases for HealthCheckResponse model."""

    def test_health_check_response_defaults(self):
        """Test HealthCheckResponse with default values."""
        discovered = DiscoveredWorkflows(workflows=1, steps=2)
        response = HealthCheckResponse(discovered=discovered)

        assert response.status == "ok"
        assert response.sdk_version == SDK_VERSION
        assert response.framework_version == FRAMEWORK_VERSION
        assert response.discovered == discovered

    def test_health_check_response_explicit_values(self):
        """Test HealthCheckResponse with explicit values."""
        discovered = DiscoveredWorkflows(workflows=5, steps=10)
        response = HealthCheckResponse(
            status="warning",
            sdk_version="1.0.0",
            framework_version="2024-01-01",
            discovered=discovered,
        )

        assert response.status == "warning"
        assert response.sdk_version == "1.0.0"
        assert response.framework_version == "2024-01-01"
        assert response.discovered == discovered

    def test_health_check_response_serialization_alias(self):
        """Test serialization aliases."""
        discovered = DiscoveredWorkflows(workflows=1, steps=2)
        response = HealthCheckResponse(discovered=discovered)

        data = response.model_dump(by_alias=True)
        assert data["sdkVersion"] == SDK_VERSION
        assert data["frameworkVersion"] == FRAMEWORK_VERSION
        assert "sdk_version" not in data
        assert "framework_version" not in data


class TestTriggerPayload:
    """Test cases for TriggerPayload model."""

    def test_trigger_payload_string_recipient(self):
        """Test TriggerPayload with string recipient."""
        payload = TriggerPayload(
            to="user@example.com",
            payload={"message": "Hello"},
            metadata={"source": "web"},
        )

        assert payload.to == "user@example.com"
        assert payload.payload == {"message": "Hello"}
        assert payload.metadata == {"source": "web"}

    def test_trigger_payload_dict_recipient(self):
        """Test TriggerPayload with dict recipient."""
        recipient = {"email": "user@example.com", "name": "John"}
        payload = TriggerPayload(to=recipient, payload={"message": "Hello"})

        assert payload.to == recipient
        assert payload.payload == {"message": "Hello"}
        assert payload.metadata is None

    def test_trigger_payload_required_fields(self):
        """Test that TriggerPayload requires to and payload fields."""
        with pytest.raises(ValidationError):
            TriggerPayload(to="user@example.com")  # Missing payload

        with pytest.raises(ValidationError):
            TriggerPayload(payload={"message": "Hello"})  # Missing to

    def test_trigger_payload_optional_metadata(self):
        """Test TriggerPayload without metadata."""
        payload = TriggerPayload(to="user@example.com", payload={"message": "Hello"})

        assert payload.metadata is None
