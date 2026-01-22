import pytest

from novu_framework.workflow import StepHandler


@pytest.mark.asyncio
async def test_step_handler_email_with_control_schema():
    """Test StepHandler email method with controlSchema parameter."""
    handler = StepHandler({"test": "data"})

    def resolver_with_controls(controls):
        return {"subject": controls.get("subject", "default"), "body": "test body"}

    # Mock the _execute_step method to capture the options
    original_execute = handler._execute_step
    captured_options = {}

    async def mock_execute(step_class, step_id, resolver, **options):
        captured_options.update(options)
        # Call the original to maintain behavior
        return await original_execute(step_class, step_id, resolver, **options)

    handler._execute_step = mock_execute

    control_schema = {
        "type": "object",
        "properties": {"subject": {"type": "string", "default": "New Comment"}},
    }

    await handler.email(
        step_id="test-email",
        resolver=resolver_with_controls,
        controlSchema=control_schema,
        controls={"subject": "Custom Subject"},
    )

    assert "control_schema" in captured_options
    assert captured_options["control_schema"] == control_schema
    assert captured_options["controls"] == {"subject": "Custom Subject"}


@pytest.mark.asyncio
async def test_step_handler_in_app_with_control_schema():
    """Test StepHandler in_app method with controlSchema parameter."""
    handler = StepHandler({"test": "data"})

    def resolver_with_controls(controls):
        return {"body": controls.get("message", "default message")}

    # Mock the _execute_step method to capture the options
    original_execute = handler._execute_step
    captured_options = {}

    async def mock_execute(step_class, step_id, resolver, **options):
        captured_options.update(options)
        return await original_execute(step_class, step_id, resolver, **options)

    handler._execute_step = mock_execute

    control_schema = {"type": "object", "properties": {"message": {"type": "string"}}}

    await handler.in_app(
        step_id="test-in-app",
        resolver=resolver_with_controls,
        controlSchema=control_schema,
    )

    assert "control_schema" in captured_options
    assert captured_options["control_schema"] == control_schema


@pytest.mark.asyncio
async def test_step_handler_sms_with_control_schema():
    """Test StepHandler sms method with controlSchema parameter."""
    handler = StepHandler({"test": "data"})

    def resolver_with_controls(controls):
        return {"text": controls.get("message", "default SMS")}

    # Mock the _execute_step method to capture the options
    original_execute = handler._execute_step
    captured_options = {}

    async def mock_execute(step_class, step_id, resolver, **options):
        captured_options.update(options)
        return await original_execute(step_class, step_id, resolver, **options)

    handler._execute_step = mock_execute

    control_schema = {"type": "object", "properties": {"message": {"type": "string"}}}

    await handler.sms(
        step_id="test-sms",
        resolver=resolver_with_controls,
        controlSchema=control_schema,
    )

    assert "control_schema" in captured_options
    assert captured_options["control_schema"] == control_schema


@pytest.mark.asyncio
async def test_step_handler_push_with_control_schema():
    """Test StepHandler push method with controlSchema parameter."""
    handler = StepHandler({"test": "data"})

    def resolver_with_controls(controls):
        return {"title": controls.get("title", "default title")}

    # Mock the _execute_step method to capture the options
    original_execute = handler._execute_step
    captured_options = {}

    async def mock_execute(step_class, step_id, resolver, **options):
        captured_options.update(options)
        return await original_execute(step_class, step_id, resolver, **options)

    handler._execute_step = mock_execute

    control_schema = {"type": "object", "properties": {"title": {"type": "string"}}}

    await handler.push(
        step_id="test-push",
        resolver=resolver_with_controls,
        controlSchema=control_schema,
    )

    assert "control_schema" in captured_options
    assert captured_options["control_schema"] == control_schema


@pytest.mark.asyncio
async def test_step_methods_without_control_schema():
    """Test step methods work without controlSchema parameter (backward compatibility)."""
    handler = StepHandler({"test": "data"})

    def resolver_no_controls():
        return {"fixed": "result"}

    # Mock the _execute_step method to capture the options
    original_execute = handler._execute_step
    captured_options = {}

    async def mock_execute(step_class, step_id, resolver, **options):
        captured_options.update(options)
        return await original_execute(step_class, step_id, resolver, **options)

    handler._execute_step = mock_execute

    await handler.email("test-email", resolver_no_controls)

    assert "control_schema" not in captured_options
