"""Unit tests for Flask GET action handlers."""

from unittest.mock import Mock, patch

from flask import Flask

from novu_framework.flask import _handle_health_check_flask, serve
from novu_framework.workflow import Workflow


class TestFlaskHealthCheck:
    """Test Flask health check GET action."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True

        # Create mock workflow
        self.mock_workflow = Mock(spec=Workflow)
        self.mock_workflow.workflow_id = "test-workflow"
        self.mock_workflow.handler = lambda: "test code"

        # Serve the workflow
        serve(self.app, workflows=[self.mock_workflow])

    def test_health_check_endpoint_success(self):
        """Test health check endpoint returns proper response."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=health-check")

            assert response.status_code == 200
            data = response.get_json()

            assert data["status"] == "ok"
            assert "sdkVersion" in data
            assert "frameworkVersion" in data
            assert "discovered" in data
            assert data["discovered"]["workflows"] == 1
            assert data["discovered"]["steps"] >= 0

    def test_health_check_default_action(self):
        """Test health check is the default action."""
        with self.app.test_client() as client:
            response = client.get("/api/novu")

            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "ok"

    @patch("novu_framework.flask.count_steps_in_workflow")
    def test_health_check_with_workflow_steps(self, mock_count_steps):
        """Test health check counts workflow steps correctly."""
        mock_count_steps.return_value = 3

        with self.app.test_client() as client:
            response = client.get("/api/novu?action=health-check")

            assert response.status_code == 200
            data = response.get_json()
            assert data["discovered"]["workflows"] == 1
            assert data["discovered"]["steps"] == 3
            mock_count_steps.assert_called_once_with(self.mock_workflow)

    def test_health_check_empty_workflows(self):
        """Test health check with no workflows."""
        empty_app = Flask(__name__)
        empty_app.config["TESTING"] = True
        serve(empty_app, workflows=[])

        with empty_app.test_client() as client:
            response = client.get("/api/novu?action=health-check")

            assert response.status_code == 200
            data = response.get_json()
            assert data["discovered"]["workflows"] == 0
            assert data["discovered"]["steps"] == 0

    def test_handle_health_check_function(self):
        """Test the _handle_health_check_flask function directly."""
        workflow_map = {"test-workflow": self.mock_workflow}

        with patch("novu_framework.flask.count_steps_in_workflow", return_value=2):
            response_data = _handle_health_check_flask(workflow_map)

            assert isinstance(response_data, dict)
            assert response_data["status"] == "ok"
            assert response_data["discovered"]["workflows"] == 1
            assert response_data["discovered"]["steps"] == 2

    def test_health_check_response_format(self):
        """Test health check response matches expected format."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=health-check")
            data = response.get_json()

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

    def test_health_check_invalid_action_parameter(self):
        """Test health check with invalid action parameter."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=invalid-action")

            assert response.status_code == 400
            data = response.get_json()
            assert "detail" in data

    def test_health_check_performance_timing(self):
        """Test health check response is fast (<100ms)."""
        import time

        with self.app.test_client() as client:
            start_time = time.time()
            response = client.get("/api/novu?action=health-check")
            end_time = time.time()

            response_time_ms = (end_time - start_time) * 1000

            assert response.status_code == 200
            assert response_time_ms < 100

    def test_health_check_content_type(self):
        """Test health check returns proper content type."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=health-check")

            assert response.status_code == 200
            assert response.content_type == "application/json"

    def test_health_check_error_handling(self):
        """Test health check handles errors gracefully."""
        with patch(
            "novu_framework.flask.count_steps_in_workflow",
            side_effect=Exception("Test error"),
        ):
            with self.app.test_client() as client:
                response = client.get("/api/novu?action=health-check")

                assert response.status_code == 500
                data = response.get_json()
                assert "detail" in data
