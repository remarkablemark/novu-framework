"""Integration tests for Flask code endpoint."""

from flask import Flask

from novu_framework.flask import serve
from novu_framework.workflow import Workflow


class TestFlaskCodeIntegration:
    """Integration tests for Flask code endpoint."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True

        # Create test workflow
        def test_handler(payload, step_handler):
            step_handler.email("send-welcome", lambda: {"subject": "Welcome!"})
            step_handler.in_app("show-notification", lambda: {"body": "Welcome!"})
            return "completed"

        self.workflow = Workflow("test-workflow", test_handler)
        serve(self.app, workflows=[self.workflow])

    def test_code_endpoint_success(self):
        """Test code endpoint returns workflow code."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=code&workflow_id=test-workflow")

            assert response.status_code == 200
            data = response.get_json()

            assert "code" in data
            assert "def test_handler(payload, step_handler):" in data["code"]
            assert 'step_handler.email("send-welcome"' in data["code"]
            assert 'step_handler.in_app("show-notification"' in data["code"]
            assert 'return "completed"' in data["code"]

    def test_code_endpoint_missing_workflow_id(self):
        """Test code endpoint with missing workflow_id parameter."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=code")

            assert response.status_code == 400
            data = response.get_json()
            assert "workflow_id is required for this action" in data["detail"]

    def test_code_endpoint_invalid_workflow_id(self):
        """Test code endpoint with invalid workflow_id."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=code&workflow_id=non-existent")

            assert response.status_code == 404
            data = response.get_json()
            assert "Workflow 'non-existent' not found" in data["detail"]

    def test_code_endpoint_response_format(self):
        """Test code endpoint response matches expected format."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=code&workflow_id=test-workflow")

            assert response.status_code == 200
            data = response.get_json()

            # Check response structure
            assert isinstance(data, dict)
            assert "code" in data
            assert isinstance(data["code"], str)
            assert len(data["code"]) > 0

    def test_code_endpoint_with_complex_workflow(self):
        """Test code endpoint with complex workflow."""

        def complex_handler(payload, step_handler):
            # Multiple steps
            step_handler.email("send-welcome", lambda: {"subject": "Welcome!"})
            step_handler.sms("send-sms", lambda: {"message": "SMS message"})
            step_handler.in_app("show-notification", lambda: {"body": "Notification"})
            step_handler.push(
                "send-push", lambda: {"title": "Push", "body": "Push message"}
            )

            # Conditional logic
            if payload.get("send_email", True):
                step_handler.email(
                    "conditional-email", lambda: {"subject": "Conditional"}
                )

            return "complex_completed"

        complex_workflow = Workflow("complex-workflow", complex_handler)
        complex_app = Flask(__name__)
        complex_app.config["TESTING"] = True
        serve(complex_app, workflows=[complex_workflow])

        with complex_app.test_client() as client:
            response = client.get("/api/novu?action=code&workflow_id=complex-workflow")

            assert response.status_code == 200
            data = response.get_json()
            assert "code" in data
            assert "def complex_handler(payload, step_handler):" in data["code"]
            assert 'step_handler.email("send-welcome"' in data["code"]
            assert 'step_handler.sms("send-sms"' in data["code"]
            assert 'step_handler.in_app("show-notification"' in data["code"]
            assert "step_handler.push(" in data["code"] and "send-push" in data["code"]
            assert 'if payload.get("send_email", True):' in data["code"]

    def test_code_endpoint_with_decorated_workflow(self):
        """Test code endpoint with decorated workflow."""

        def workflow_decorator(func):
            def wrapper(payload, step_handler):
                step_handler.email(
                    "decorator-email", lambda: {"subject": "From decorator"}
                )
                return func(payload, step_handler)

            return wrapper

        @workflow_decorator
        def decorated_handler(payload, step_handler):
            step_handler.email("handler-email", lambda: {"subject": "From handler"})
            return "decorated_completed"

        decorated_workflow = Workflow("decorated-workflow", decorated_handler)
        decorated_app = Flask(__name__)
        decorated_app.config["TESTING"] = True
        serve(decorated_app, workflows=[decorated_workflow])

        with decorated_app.test_client() as client:
            response = client.get(
                "/api/novu?action=code&workflow_id=decorated-workflow"
            )

            assert response.status_code == 200
            data = response.get_json()
            assert "code" in data
            # inspect.getsource returns the wrapper function, not the decorator
            assert "def wrapper(payload, step_handler):" in data["code"]
            assert (
                "step_handler.email(" in data["code"]
                and "decorator-email" in data["code"]
            )

    def test_code_endpoint_with_multiple_workflows(self):
        """Test code endpoint with multiple registered workflows."""

        def handler2(payload, step_handler):
            step_handler.sms("send-sms-2", lambda: {"message": "SMS from handler 2"})
            return "handler2_completed"

        workflow2 = Workflow("workflow-2", handler2)
        multi_app = Flask(__name__)
        multi_app.config["TESTING"] = True
        serve(multi_app, workflows=[self.workflow, workflow2])

        with multi_app.test_client() as client:
            # Test first workflow
            response1 = client.get("/api/novu?action=code&workflow_id=test-workflow")
            assert response1.status_code == 200
            data1 = response1.get_json()
            assert "def test_handler(payload, step_handler):" in data1["code"]

            # Test second workflow
            response2 = client.get("/api/novu?action=code&workflow_id=workflow-2")
            assert response2.status_code == 200
            data2 = response2.get_json()
            assert "def handler2(payload, step_handler):" in data2["code"]
            assert 'step_handler.sms("send-sms-2"' in data2["code"]

    def test_code_endpoint_with_empty_workflows(self):
        """Test code endpoint with no registered workflows."""
        empty_app = Flask(__name__)
        empty_app.config["TESTING"] = True
        serve(empty_app, workflows=[])

        with empty_app.test_client() as client:
            response = client.get("/api/novu?action=code&workflow_id=test-workflow")

            assert response.status_code == 404
            data = response.get_json()
            assert "Workflow 'test-workflow' not found" in data["detail"]

    def test_code_endpoint_with_different_routes(self):
        """Test code endpoint with custom route prefix."""
        custom_app = Flask(__name__)
        custom_app.config["TESTING"] = True
        serve(custom_app, route="/custom/novu", workflows=[self.workflow])

        with custom_app.test_client() as client:
            response = client.get("/custom/novu?action=code&workflow_id=test-workflow")

            assert response.status_code == 200
            data = response.get_json()
            assert "code" in data
            assert "def test_handler(payload, step_handler):" in data["code"]

    def test_code_endpoint_concurrent_requests(self):
        """Test code endpoint with concurrent requests."""
        import threading

        results = []

        def make_request():
            with self.app.test_client() as client:
                response = client.get("/api/novu?action=code&workflow_id=test-workflow")
                results.append(
                    {"status": response.status_code, "data": response.get_json()}
                )

        # Make 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed with consistent data
        assert len(results) == 10
        for result in results:
            assert result["status"] == 200
            assert "code" in result["data"]
            assert "def test_handler(payload, step_handler):" in result["data"]["code"]

    def test_code_endpoint_response_consistency(self):
        """Test code endpoint returns consistent responses."""
        responses = []

        for _ in range(5):
            with self.app.test_client() as client:
                response = client.get("/api/novu?action=code&workflow_id=test-workflow")
                responses.append(response.get_json())

        # All responses should be identical
        first_response = responses[0]
        for response in responses[1:]:
            assert response == first_response

    def test_code_endpoint_with_special_characters_in_workflow_id(self):
        """Test code endpoint with special characters in workflow_id."""
        with self.app.test_client() as client:
            response = client.get(
                "/api/novu?action=code&workflow_id=test-workflow%20with%20spaces"
            )

            assert response.status_code == 404
            data = response.get_json()
            assert "Workflow 'test-workflow with spaces' not found" in data["detail"]

    def test_code_endpoint_with_unicode_workflow_id(self):
        """Test code endpoint with unicode characters in workflow_id."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=code&workflow_id=test-workflow-🚀")

            assert response.status_code == 404
            data = response.get_json()
            assert "Workflow 'test-workflow-🚀' not found" in data["detail"]

    def test_code_endpoint_with_very_long_workflow_id(self):
        """Test code endpoint with very long workflow_id."""
        long_id = "a" * 1000
        with self.app.test_client() as client:
            response = client.get(f"/api/novu?action=code&workflow_id={long_id}")

            assert response.status_code == 404
            data = response.get_json()
            assert f"Workflow '{long_id}' not found" in data["detail"]

    def test_code_endpoint_with_query_parameter_variations(self):
        """Test code endpoint with different query parameter formats."""
        with self.app.test_client() as client:
            # Test with different parameter order
            response1 = client.get("/api/novu?workflow_id=test-workflow&action=code")
            assert response1.status_code == 200
            assert "code" in response1.get_json()

            # Test with URL-encoded parameters
            response2 = client.get("/api/novu?action=code&workflow_id=test-workflow")
            assert response2.status_code == 200
            assert "code" in response2.get_json()

            # Both responses should be identical
            assert response1.get_json() == response2.get_json()

    def test_code_endpoint_content_type(self):
        """Test code endpoint returns correct content type."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=code&workflow_id=test-workflow")

            assert response.status_code == 200
            assert response.headers["content-type"] == "application/json"

    def test_code_endpoint_response_size(self):
        """Test code endpoint response size is reasonable."""
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=code&workflow_id=test-workflow")

            assert response.status_code == 200
            data = response.get_json()

            # Response should contain the actual code, not be empty or too small
            assert len(data["code"]) > 50  # At least some meaningful code
            assert len(data["code"]) < 10000  # Not excessively large

    def test_code_endpoint_blueprint_registration(self):
        """Test code endpoint works with blueprint registration."""
        # Check that blueprint is registered
        blueprint_names = [bp.name for bp in self.app.blueprints.values()]
        assert "novu" in blueprint_names

        # Check that code endpoint is accessible
        with self.app.test_client() as client:
            response = client.get("/api/novu?action=code&workflow_id=test-workflow")
            assert response.status_code == 200
            assert "code" in response.get_json()

    def test_code_endpoint_application_context(self):
        """Test code endpoint works within Flask application context."""
        with self.app.app_context():
            with self.app.test_request_context():
                # Test that the blueprint is properly registered
                rules = list(self.app.url_map.iter_rules())
                code_rule = None
                for rule in rules:
                    if "/api/novu" in rule.rule:
                        code_rule = rule
                        break

                assert code_rule is not None
                assert code_rule.endpoint == "novu.handle_get_action"
