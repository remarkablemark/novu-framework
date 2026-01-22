import pytest
from pydantic import BaseModel

from novu_framework.workflow import StepHandler


class EmailControls(BaseModel):
    subject: str = "New Comment"
    include_footer: bool = True


class SMSControls(BaseModel):
    message: str
    urgent: bool = False


def test_step_handler_email_with_pydantic_control_schema():
    """Test StepHandler email method with Pydantic model as controlSchema."""
    handler = StepHandler({"test": "data"})

    def resolver_with_controls(controls):
        return {
            "subject": controls.get("subject", "New Comment"),
            "body": "test body",
            "footer": "Thanks!" if controls.get("include_footer", False) else "",
        }

    # Mock the _execute_step method to capture the options
    original_execute = handler._execute_step
    captured_options = {}

    def mock_execute(step_class, step_id, resolver, **options):
        captured_options.update(options)
        return original_execute(step_class, step_id, resolver, **options)

    handler._execute_step = mock_execute

    handler.email(
        step_id="test-email",
        resolver=resolver_with_controls,
        controlSchema=EmailControls,
        controls={"subject": "Custom Subject", "include_footer": True},
    )

    assert "control_schema" in captured_options
    assert captured_options["control_schema"]["type"] == "object"
    assert "properties" in captured_options["control_schema"]
    assert "subject" in captured_options["control_schema"]["properties"]
    assert "include_footer" in captured_options["control_schema"]["properties"]


def test_step_handler_sms_with_pydantic_control_schema():
    """Test StepHandler sms method with Pydantic model as controlSchema."""
    handler = StepHandler({"test": "data"})

    def resolver_with_controls(controls):
        return {
            "text": controls.get("message", ""),
            "priority": "high" if controls.get("urgent", False) else "normal",
        }

    # Mock the _execute_step method to capture the options
    original_execute = handler._execute_step
    captured_options = {}

    def mock_execute(step_class, step_id, resolver, **options):
        captured_options.update(options)
        return original_execute(step_class, step_id, resolver, **options)

    handler._execute_step = mock_execute

    handler.sms(
        step_id="test-sms",
        resolver=resolver_with_controls,
        controlSchema=SMSControls,
        controls={"message": "Test message", "urgent": True},
    )

    assert "control_schema" in captured_options
    assert captured_options["control_schema"]["type"] == "object"
    assert "properties" in captured_options["control_schema"]
    assert "message" in captured_options["control_schema"]["properties"]
    assert "urgent" in captured_options["control_schema"]["properties"]


def test_step_handler_in_app_with_pydantic_control_schema():
    """Test StepHandler in_app method with Pydantic model as controlSchema."""
    handler = StepHandler({"test": "data"})

    def resolver_with_controls(controls):
        return {"body": f"Message: {controls.get('message', '')}"}

    # Mock the _execute_step method to capture the options
    original_execute = handler._execute_step
    captured_options = {}

    def mock_execute(step_class, step_id, resolver, **options):
        captured_options.update(options)
        return original_execute(step_class, step_id, resolver, **options)

    handler._execute_step = mock_execute

    handler.in_app(
        step_id="test-in-app",
        resolver=resolver_with_controls,
        controlSchema=SMSControls,  # Reuse SMSControls for testing
        controls={"message": "Test in-app message"},
    )

    assert "control_schema" in captured_options
    assert captured_options["control_schema"]["type"] == "object"


def test_step_handler_push_with_pydantic_control_schema():
    """Test StepHandler push method with Pydantic model as controlSchema."""
    handler = StepHandler({"test": "data"})

    def resolver_with_controls(controls):
        return {
            "title": controls.get("message", ""),
            "sound": "default" if not controls.get("urgent", False) else "alert",
        }

    # Mock the _execute_step method to capture the options
    original_execute = handler._execute_step
    captured_options = {}

    def mock_execute(step_class, step_id, resolver, **options):
        captured_options.update(options)
        return original_execute(step_class, step_id, resolver, **options)

    handler._execute_step = mock_execute

    handler.push(
        step_id="test-push",
        resolver=resolver_with_controls,
        controlSchema=SMSControls,  # Reuse SMSControls for testing
        controls={"message": "Test push message", "urgent": False},
    )

    assert "control_schema" in captured_options
    assert captured_options["control_schema"]["type"] == "object"


def test_convert_control_schema_with_dict():
    """Test _convert_control_schema with dict input (backward compatibility)."""
    handler = StepHandler({"test": "data"})

    dict_schema = {"type": "object", "properties": {"subject": {"type": "string"}}}
    result = handler._convert_control_schema(dict_schema)

    assert result == dict_schema


def test_convert_control_schema_with_pydantic():
    """Test _convert_control_schema with Pydantic model input."""
    handler = StepHandler({"test": "data"})

    result = handler._convert_control_schema(EmailControls)

    assert result["type"] == "object"
    assert "properties" in result
    assert "subject" in result["properties"]
    assert "include_footer" in result["properties"]
    assert result["properties"]["subject"]["type"] == "string"
    assert result["properties"]["include_footer"]["type"] == "boolean"


def test_convert_control_schema_with_invalid_type():
    """Test _convert_control_schema with invalid type raises ValueError."""
    handler = StepHandler({"test": "data"})

    with pytest.raises(
        ValueError, match="controlSchema must be a dict or Pydantic BaseModel class"
    ):
        handler._convert_control_schema("invalid_schema")


def test_control_schema_backward_compatibility():
    """Test that dict-based controlSchema still works (backward compatibility)."""
    handler = StepHandler({"test": "data"})

    def resolver_with_controls(controls):
        return {"subject": controls.get("subject", "default"), "body": "test body"}

    # Mock the _execute_step method to capture the options
    original_execute = handler._execute_step
    captured_options = {}

    def mock_execute(step_class, step_id, resolver, **options):
        captured_options.update(options)
        return original_execute(step_class, step_id, resolver, **options)

    handler._execute_step = mock_execute

    dict_schema = {
        "type": "object",
        "properties": {"subject": {"type": "string", "default": "New Comment"}},
    }

    handler.email(
        step_id="test-email",
        resolver=resolver_with_controls,
        controlSchema=dict_schema,
        controls={"subject": "Custom Subject"},
    )

    assert "control_schema" in captured_options
    assert captured_options["control_schema"] == dict_schema
