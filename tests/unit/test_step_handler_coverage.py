import pytest

from novu_framework.workflow import StepHandler


@pytest.mark.asyncio
async def test_step_handler_resolver_sync_function():
    """Test StepHandler with synchronous resolver function."""
    handler = StepHandler({"test": "data"})

    def sync_resolver():
        return {"sync": "result"}

    result = await handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="sync-step",
        resolver=sync_resolver,
    )

    assert result == {"sync": "result"}
    assert handler.step_results["sync-step"] == {"sync": "result"}


@pytest.mark.asyncio
async def test_step_handler_resolver_async_function():
    """Test StepHandler with asynchronous resolver function."""
    handler = StepHandler({"test": "data"})

    async def async_resolver():
        return {"async": "result"}

    result = await handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="async-step",
        resolver=async_resolver,
    )

    assert result == {"async": "result"}
    assert handler.step_results["async-step"] == {"async": "result"}


@pytest.mark.asyncio
async def test_step_handler_resolver_non_callable():
    """Test StepHandler with non-callable resolver (direct value)."""
    handler = StepHandler({"test": "data"})

    result = await handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="value-step",
        resolver={"direct": "value"},
    )

    assert result == {"direct": "value"}
    assert handler.step_results["value-step"] == {"direct": "value"}
