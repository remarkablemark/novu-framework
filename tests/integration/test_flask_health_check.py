"""Integration tests for Flask health check GET action."""

from unittest.mock import Mock, patch

from flask import Flask

from novu_framework.flask import serve
from novu_framework.workflow import Workflow


class TestFlaskHealthCheckIntegration:
    """Integration tests for Flask health check endpoint."""

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

    def test_health_check_full_request_cycle(self):
        """Test complete request/response cycle for health check."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=health-check")

            assert response.status_code == 200
            data = response.get_json()

            # Verify response structure
            assert data["status"] == "ok"
            assert "sdkVersion" in data
            assert "frameworkVersion" in data
            assert "discovered" in data
            assert "workflows" in data["discovered"]
            assert "steps" in data["discovered"]

            # Verify data types
            assert isinstance(data["discovered"]["workflows"], int)
            assert isinstance(data["discovered"]["steps"], int)
            assert data["discovered"]["workflows"] >= 0
            assert data["discovered"]["steps"] >= 0

    def test_health_check_with_multiple_workflows(self):
        """Test health check with multiple registered workflows."""
        # Create additional workflows
        workflow2 = Mock(spec=Workflow)
        workflow2.workflow_id = "workflow-2"
        workflow2.handler = lambda: "test code 2"

        workflow3 = Mock(spec=Workflow)
        workflow3.workflow_id = "workflow-3"
        workflow3.handler = lambda: "test code 3"

        # Create new app with multiple workflows
        multi_app = Flask(__name__)
        multi_app.config["TESTING"] = True
        serve(multi_app, workflows=[self.mock_workflow, workflow2, workflow3])

        with multi_app.test_client() as client:
            response = client.get("/api/novu?action=health-check")

            assert response.status_code == 200
            data = response.get_json()
            assert data["discovered"]["workflows"] == 3
            assert data["discovered"]["steps"] >= 0

    @patch("novu_framework.common.count_steps_in_workflow")
    def test_health_check_step_counting(self, mock_count_steps):
        """Test health check accurately counts workflow steps."""
        mock_count_steps.return_value = 5

        with self.app.test_client() as client:
            response = client.get("/api/novu?action=health-check")

            assert response.status_code == 200
            data = response.get_json()
            assert data["discovered"]["workflows"] == 1
            assert data["discovered"]["steps"] == 5
            mock_count_steps.assert_called_once_with(self.mock_workflow)

    def test_health_check_default_action(self):
        """Test health check works with default action (no query parameter)."""
        with self.app.test_client() as client:
            response = client.get("/api/novu")

            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "ok"
            assert "discovered" in data

    def test_health_check_case_sensitivity(self):
        """Test health check action is case sensitive."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=HEALTH-CHECK")

            assert response.status_code == 400
            data = response.get_json()
            assert "detail" in data

    def test_health_check_response_headers(self):
        """Test health check response includes proper headers."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=health-check")

            assert response.status_code == 200
            assert response.content_type == "application/json"

    def test_health_check_concurrent_requests(self):
        """Test health check handles concurrent requests."""
        import threading

        results = []

        def make_request():
            with self.app.test_client() as client:
                response = client.get("/api/novu?action=health-check")
                results.append(response.status_code)

        # Make 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed
        assert len(results) == 10
        assert all(status == 200 for status in results)

    def test_health_check_with_empty_workflows(self):
        """Test health check with no registered workflows."""
        empty_app = Flask(__name__)
        empty_app.config["TESTING"] = True
        serve(empty_app, workflows=[])

        with empty_app.test_client() as client:
            response = client.get("/api/novu?action=health-check")

            assert response.status_code == 200
            data = response.get_json()
            assert data["discovered"]["workflows"] == 0
            assert data["discovered"]["steps"] == 0

    def test_health_check_response_consistency(self):
        """Test health check returns consistent responses."""
        # Make multiple requests and verify consistency
        responses = []
        for _ in range(5):
            with self.app.test_client() as client:
                response = client.get("/api/novu?action=health-check")
                responses.append(response.get_json())

        # All responses should be identical
        first_response = responses[0]
        for response in responses[1:]:
            assert response == first_response

    @patch("novu_framework.common.count_steps_in_workflow")
    def test_health_check_error_handling(self, mock_count_steps):
        """Test health check handles errors gracefully."""
        mock_count_steps.side_effect = Exception("Test error")

        with self.app.test_client() as client:
            response = client.get("/api/novu?action=health-check")

            # Should return 500 when error occurs
            assert response.status_code == 500
            data = response.get_json()
            assert "detail" in data

    def test_health_check_with_complex_workflow(self):
        """Test health check with complex workflow handler."""

        # Create a workflow with a complex handler
        def complex_handler(payload, step):
            # Simulate a complex workflow with multiple steps
            step.email("test", lambda: {"subject": "Test"})
            step.in_app("notify", lambda: {"body": "Notification"})
            step.chat("message", lambda: {"text": "Hello"})
            return "completed"

        complex_workflow = Mock(spec=Workflow)
        complex_workflow.workflow_id = "complex-workflow"
        complex_workflow.handler = complex_handler

        complex_app = Flask(__name__)
        complex_app.config["TESTING"] = True
        serve(complex_app, workflows=[complex_workflow])

        with complex_app.test_client() as client:
            response = client.get("/api/novu?action=health-check")

            assert response.status_code == 200
            data = response.get_json()
            assert data["discovered"]["workflows"] == 1
            # Should count at least 2 steps in the complex workflow
            assert data["discovered"]["steps"] >= 2

    def test_health_check_application_context(self):
        """Test health check works within Flask application context."""
        with self.app.app_context():
            with self.app.test_request_context():
                # Test that the blueprint is properly registered
                rules = list(self.app.url_map.iter_rules())
                health_check_rule = None
                for rule in rules:
                    if "/api/novu" in rule.rule:
                        health_check_rule = rule
                        break

                assert health_check_rule is not None
                assert health_check_rule.endpoint == "novu.handle_get_action"

    def test_health_check_blueprint_registration(self):
        """Test that the blueprint is properly registered with Flask."""
        # Check that blueprint is registered
        blueprint_names = [bp.name for bp in self.app.blueprints.values()]
        assert "novu" in blueprint_names

        # Check that routes are registered
        rules = list(self.app.url_map.iter_rules())
        api_routes = [rule for rule in rules if "/api/novu" in rule.rule]
        assert len(api_routes) > 0

    def test_health_check_different_routes(self):
        """Test health check with different route prefixes."""
        custom_app = Flask(__name__)
        custom_app.config["TESTING"] = True
        serve(custom_app, route="/custom/novu", workflows=[self.mock_workflow])

        with custom_app.test_client() as client:
            response = client.get("/custom/novu?action=health-check")

            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "ok"
            assert "discovered" in data
