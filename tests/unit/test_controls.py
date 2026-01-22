import pytest

from novu_framework.workflow import StepHandler


def test_step_handler_resolver_with_controls():
    """Test StepHandler resolver with controls argument."""
    handler = StepHandler({"test": "data"})

    def resolver_with_controls(controls):
        return {"subject": controls.get("subject", "default"), "body": "test body"}

    result = handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="controls-step",
        resolver=resolver_with_controls,
        controls={"subject": "Custom Subject"},
    )

    assert result == {"subject": "Custom Subject", "body": "test body"}
    assert handler.step_results["controls-step"] == {
        "subject": "Custom Subject",
        "body": "test body",
    }


def test_step_handler_resolver_with_controls_default():
    """Test StepHandler resolver with controls using default values."""
    handler = StepHandler({"test": "data"})

    def resolver_with_controls(controls):
        return {"subject": controls.get("subject", "default"), "body": "test body"}

    result = handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="controls-default-step",
        resolver=resolver_with_controls,
        controls={},  # Empty controls
    )

    assert result == {"subject": "default", "body": "test body"}
    assert handler.step_results["controls-default-step"] == {
        "subject": "default",
        "body": "test body",
    }


def test_step_handler_resolver_fallback_no_controls():
    """Test StepHandler resolver fallback when function doesn't accept controls."""
    handler = StepHandler({"test": "data"})

    def resolver_no_args():
        return {"fixed": "result"}

    result = handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="no-controls-step",
        resolver=resolver_no_args,
        controls={"subject": "Custom Subject"},
    )

    assert result == {"fixed": "result"}
    assert handler.step_results["no-controls-step"] == {"fixed": "result"}


def test_step_handler_resolver_fallback_payload():
    """Test StepHandler resolver fallback to payload argument when function signature is incompatible."""
    handler = StepHandler({"test": "data"})

    def resolver_no_args():
        return {"fixed": "result"}

    result = handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="no-args-step",
        resolver=resolver_no_args,
        controls={"subject": "Custom Subject"},  # This will trigger fallback to no args
    )

    assert result == {"fixed": "result"}
    assert handler.step_results["no-args-step"] == {"fixed": "result"}


@pytest.mark.asyncio
async def test_step_handler_resolver_async_with_controls():
    """Test StepHandler with async resolver that accepts controls."""
    handler = StepHandler({"test": "data"})

    async def async_resolver_with_controls(controls):
        return {"subject": controls.get("subject", "default"), "async": True}

    result = handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="async-controls-step",
        resolver=async_resolver_with_controls,
        controls={"subject": "Async Subject"},
    )

    # In sync version, async resolvers are returned as coroutine objects
    import inspect

    assert inspect.iscoroutine(result)

    # Verify the coroutine works by awaiting it
    awaited_result = await result
    assert awaited_result == {"subject": "Async Subject", "async": True}
    assert handler.step_results["async-controls-step"] == result
