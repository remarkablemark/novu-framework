from novu_framework.steps.base import BaseStep


class StepImplementation(BaseStep):
    """Test implementation of BaseStep for coverage."""

    step_type = "TEST"


def test_base_step_initialization():
    """Test BaseStep initialization with all parameters."""

    def resolver():
        return {"test": "result"}

    options = {
        "skip": lambda: False,
        "control_schema": {"type": "object"},
        "custom_option": "value",
    }

    step = StepImplementation("test-step", resolver, options)

    assert step.step_id == "test-step"
    assert step.resolver == resolver
    assert step.options == options
    assert step.step_type == "TEST"


def test_base_step_initialization_minimal():
    """Test BaseStep initialization with minimal parameters."""

    def resolver():
        return {"test": "result"}

    step = StepImplementation("minimal-step", resolver)

    assert step.step_id == "minimal-step"
    assert step.resolver == resolver
    assert step.options == {}


def test_base_step_skip_property():
    """Test skip property returns skip function from options."""

    def skip_func():
        return True

    step = StepImplementation("skip-step", lambda: {}, {"skip": skip_func})

    assert step.skip == skip_func


def test_base_step_skip_property_none():
    """Test skip property returns None when not in options."""
    step = StepImplementation("no-skip-step", lambda: {})

    assert step.skip is None


def test_base_step_control_schema_property():
    """Test control_schema property returns schema from options."""
    schema = {"type": "object", "properties": {"test": {"type": "string"}}}

    step = StepImplementation("schema-step", lambda: {}, {"control_schema": schema})

    assert step.control_schema == schema


def test_base_step_control_schema_property_none():
    """Test control_schema property returns None when not in options."""
    step = StepImplementation("no-schema-step", lambda: {})

    assert step.control_schema is None
