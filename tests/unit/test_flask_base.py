"""Flask-specific base test class."""

from tests.unit.test_common_base import BaseTestWorkflowFunctionality


class FlaskBaseTest(BaseTestWorkflowFunctionality):
    """Base test class for Flask-specific tests."""

    def get_workflow_name(self, base_name):
        """Return workflow name for Flask tests."""
        return f"{base_name}-flask"

    def get_missing_workflow_id(self):
        """Return missing workflow ID for Flask tests."""
        return None
