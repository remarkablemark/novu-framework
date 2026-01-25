"""FastAPI-specific base test class."""

from tests.unit.test_common_base import BaseTestWorkflowFunctionality


class FastAPIBaseTest(BaseTestWorkflowFunctionality):
    """Base test class for FastAPI-specific tests."""

    def get_workflow_name(self, base_name):
        """Return workflow name for FastAPI tests."""
        return base_name

    def get_missing_workflow_id(self):
        """Return missing workflow ID for FastAPI tests."""
        return ""
