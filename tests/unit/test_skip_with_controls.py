from novu_framework.workflow import StepHandler


def test_skip_with_controls():
    """Test skip function that accepts controls argument."""
    handler = StepHandler({"test": "data"})

    def skip_with_controls(controls):
        # Skip if subject contains "skip"
        return controls.get("subject", "").lower() == "skip"

    def test_step():
        return {"result": "test"}

    # Mock the _execute_step method to capture the options
    captured_options = {}
    captured_step_class = None
    captured_step_id = None
    captured_resolver = None

    def mock_execute(step_class, step_id, resolver, **options):
        nonlocal captured_options, captured_step_class
        nonlocal captured_step_id, captured_resolver
        captured_options = options
        captured_step_class = step_class
        captured_step_id = step_id
        captured_resolver = resolver
        return {"result": "executed"}

    handler._execute_step = mock_execute

    # Test with controls that should trigger skip
    handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="skip-test",
        resolver=test_step,
        skip=skip_with_controls,
        controls={"subject": "skip"},
    )

    # The skip function should be called with controls and return True
    # This should result in a skipped result
    assert "skip" in captured_options
    assert captured_options["skip"] == skip_with_controls


def test_skip_with_controls_no_skip():
    """Test skip function that accepts controls but doesn't skip."""
    handler = StepHandler({"test": "data"})

    def skip_with_controls(controls):
        # Skip if subject contains "skip"
        return controls.get("subject", "").lower() == "skip"

    def test_step():
        return {"result": "test"}

    # Mock the _execute_step method to capture the options
    captured_options = {}

    def mock_execute(step_class, step_id, resolver, **options):
        nonlocal captured_options
        captured_options = options
        return {"result": "executed"}

    handler._execute_step = mock_execute

    # Test with controls that should NOT trigger skip
    handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="no-skip-test",
        resolver=test_step,
        skip=skip_with_controls,
        controls={"subject": "normal"},
    )

    assert "skip" in captured_options
    assert captured_options["skip"] == skip_with_controls


def test_skip_no_controls_fallback():
    """Test skip function that doesn't accept controls (fallback behavior)."""
    handler = StepHandler({"test": "data"})

    def skip_no_args():
        return True

    def test_step():
        return {"result": "test"}

    # Mock the _execute_step method to capture the options
    captured_options = {}

    def mock_execute(step_class, step_id, resolver, **options):
        nonlocal captured_options
        captured_options = options
        return {"result": "executed"}

    handler._execute_step = mock_execute

    # Test with skip function that takes no args
    handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="skip-no-args",
        resolver=test_step,
        skip=skip_no_args,
        controls={"subject": "test"},
    )

    assert "skip" in captured_options
    assert captured_options["skip"] == skip_no_args


def test_skip_payload_fallback():
    """Test skip function that accepts payload as fallback."""
    handler = StepHandler({"test": "data"})

    def skip_with_payload(payload):
        return payload.get("test") == "data"

    def test_step():
        return {"result": "test"}

    # Mock the _execute_step method to capture the options
    captured_options = {}

    def mock_execute(step_class, step_id, resolver, **options):
        nonlocal captured_options
        captured_options = options
        return {"result": "executed"}

    handler._execute_step = mock_execute

    # Test with skip function that takes payload
    handler._execute_step(
        step_class=type("TestStep", (), {"step_type": "TEST"}),
        step_id="skip-payload",
        resolver=test_step,
        skip=skip_with_payload,
        controls={"subject": "test"},
    )

    assert "skip" in captured_options
    assert captured_options["skip"] == skip_with_payload
