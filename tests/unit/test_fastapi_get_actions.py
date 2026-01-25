"""Unit tests for FastAPI GET action handlers."""

from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from novu_framework.fastapi import _handle_health_check, serve
from novu_framework.workflow import Workflow


class TestFastAPIHealthCheck:
    """Test FastAPI health check GET action."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = FastAPI()
        self.client = TestClient(self.app)

        # Create mock workflow
        self.mock_workflow = Mock(spec=Workflow)
        self.mock_workflow.workflow_id = "test-workflow"
        self.mock_workflow.handler = lambda: "test code"

        # Serve the workflow
        serve(self.app, workflows=[self.mock_workflow])

    def test_health_check_endpoint_success(self):
        """Test health check endpoint returns proper response."""
        response = self.client.get("/api/novu?action=health-check")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "sdkVersion" in data
        assert "frameworkVersion" in data
        assert "discovered" in data
        assert data["discovered"]["workflows"] == 1
        assert data["discovered"]["steps"] >= 0

    def test_health_check_default_action(self):
        """Test health check is the default action."""
        response = self.client.get("/api/novu")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @patch("novu_framework.fastapi.count_steps_in_workflow")
    def test_health_check_with_workflow_steps(self, mock_count_steps):
        """Test health check counts workflow steps correctly."""
        mock_count_steps.return_value = 3

        response = self.client.get("/api/novu?action=health-check")

        assert response.status_code == 200
        data = response.json()
        assert data["discovered"]["workflows"] == 1
        assert data["discovered"]["steps"] == 3
        mock_count_steps.assert_called_once_with(self.mock_workflow)

    def test_health_check_empty_workflows(self):
        """Test health check with no workflows."""
        empty_app = FastAPI()
        empty_client = TestClient(empty_app)
        serve(empty_app, workflows=[])

        response = empty_client.get("/api/novu?action=health-check")

        assert response.status_code == 200
        data = response.json()
        assert data["discovered"]["workflows"] == 0
        assert data["discovered"]["steps"] == 0

    @pytest.mark.asyncio
    async def test_handle_health_check_function(self):
        """Test the _handle_health_check function directly."""
        workflow_map = {"test-workflow": self.mock_workflow}

        with patch("novu_framework.fastapi.count_steps_in_workflow", return_value=2):
            response = await _handle_health_check(workflow_map)

            assert isinstance(response, dict)
            assert response["status"] == "ok"
            assert response["discovered"]["workflows"] == 1
            assert response["discovered"]["steps"] == 2

    def test_health_check_response_format(self):
        """Test health check response matches expected format."""
        response = self.client.get("/api/novu?action=health-check")
        data = response.json()

        # Verify required fields
        required_fields = ["status", "sdkVersion", "frameworkVersion", "discovered"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Verify discovered fields
        discovered_fields = ["workflows", "steps"]
        for field in discovered_fields:
            assert field in data["discovered"], f"Missing discovered field: {field}"

        # Verify data types
        assert isinstance(data["status"], str)
        assert isinstance(data["discovered"]["workflows"], int)
        assert isinstance(data["discovered"]["steps"], int)

    def test_health_check_performance_timing(self):
        """Test health check response is fast (<100ms)."""
        import time

        start_time = time.time()
        response = self.client.get("/api/novu?action=health-check")
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert response_time_ms < 100
