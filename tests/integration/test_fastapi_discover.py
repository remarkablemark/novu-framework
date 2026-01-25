"""Integration tests for FastAPI discover GET action."""

from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from novu_framework.fastapi import serve
from novu_framework.workflow import Workflow


class TestFastAPIDiscoverIntegration:
    """Integration tests for FastAPI discover endpoint."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = FastAPI()
        self.client = TestClient(self.app)

        # Create mock workflow
        self.mock_workflow = Mock(spec=Workflow)
        self.mock_workflow.workflow_id = "test-workflow"
        self.mock_workflow.handler = lambda payload: "test result"

        # Serve the workflow
        serve(self.app, workflows=[self.mock_workflow])

    def test_discover_endpoint_success(self):
        """Test discover endpoint returns proper workflow discovery information."""
        response = self.client.get("/api/novu?action=discover")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "workflows" in data
        assert len(data["workflows"]) == 1
        workflow = data["workflows"][0]

        # Verify required workflow fields
        required_fields = [
            "workflowId",
            "severity",
            "steps",
            "code",
            "payload",
            "controls",
            "tags",
            "preferences",
        ]
        for field in required_fields:
            assert field in workflow, f"Missing required field: {field}"

        # Verify workflow ID
        assert workflow["workflowId"] == "test-workflow"
        assert workflow["severity"] == "none"
        assert isinstance(workflow["steps"], list)
        assert isinstance(workflow["tags"], list)
        assert isinstance(workflow["preferences"], dict)

    def test_discover_with_multiple_workflows(self):
        """Test discover endpoint with multiple registered workflows."""
        # Create additional workflows
        workflow2 = Mock(spec=Workflow)
        workflow2.workflow_id = "workflow-2"
        workflow2.handler = lambda payload: "result2"

        workflow3 = Mock(spec=Workflow)
        workflow3.workflow_id = "workflow-3"
        workflow3.handler = lambda payload: "result3"

        # Create new app with multiple workflows
        multi_app = FastAPI()
        multi_client = TestClient(multi_app)
        serve(multi_app, workflows=[self.mock_workflow, workflow2, workflow3])

        response = multi_client.get("/api/novu?action=discover")

        assert response.status_code == 200
        data = response.json()
        assert len(data["workflows"]) == 3

        # Verify all workflows are present
        workflow_ids = [w["workflowId"] for w in data["workflows"]]
        assert "test-workflow" in workflow_ids
        assert "workflow-2" in workflow_ids
        assert "workflow-3" in workflow_ids

    def test_discover_with_complex_workflow(self):
        """Test discover endpoint with complex workflow containing multiple steps."""

        def complex_handler(payload, step):
            step.email("send-welcome", lambda: {"subject": "Welcome!"})
            step.in_app("show-notification", lambda: {"body": "Welcome notification"})
            step.sms("send-sms", lambda: {"message": "SMS message"})
            step.push("send-push", lambda: {"title": "Push notification"})
            return "completed"

        complex_workflow = Mock(spec=Workflow)
        complex_workflow.workflow_id = "complex-workflow"
        complex_workflow.handler = complex_handler

        complex_app = FastAPI()
        complex_client = TestClient(complex_app)
        serve(complex_app, workflows=[complex_workflow])

        response = complex_client.get("/api/novu?action=discover")

        assert response.status_code == 200
        data = response.json()
        assert len(data["workflows"]) == 1

        workflow = data["workflows"][0]
        assert workflow["workflowId"] == "complex-workflow"
        assert len(workflow["steps"]) == 4

        # Verify step details
        step_types = [step["type"] for step in workflow["steps"]]
        assert "email" in step_types
        assert "in_app" in step_types
        assert "sms" in step_types
        assert "push" in step_types

    def test_discover_workflow_code_extraction(self):
        """Test discover endpoint properly extracts workflow code."""

        def test_handler(payload, step):
            """Test workflow handler function."""
            step.email("test-step", lambda: {"subject": "Test"})
            return "test result"

        code_workflow = Mock(spec=Workflow)
        code_workflow.workflow_id = "code-test-workflow"
        code_workflow.handler = test_handler

        code_app = FastAPI()
        code_client = TestClient(code_app)
        serve(code_app, workflows=[code_workflow])

        response = code_client.get("/api/novu?action=discover")

        assert response.status_code == 200
        data = response.json()
        workflow = data["workflows"][0]

        # Verify code is extracted
        assert "code" in workflow
        assert isinstance(workflow["code"], str)
        assert "def test_handler(payload, step):" in workflow["code"]
        assert 'step.email("test-step"' in workflow["code"]

    def test_discover_workflow_with_tags_and_preferences(self):
        """Test discover endpoint with workflow having custom tags and preferences."""
        tagged_workflow = Mock(spec=Workflow)
        tagged_workflow.workflow_id = "tagged-workflow"
        tagged_workflow.handler = lambda payload: "tagged result"
        tagged_workflow.tags = ["test", "demo", "production"]
        tagged_workflow.preferences = {"priority": "high", "timeout": 30, "retries": 3}

        tagged_app = FastAPI()
        tagged_client = TestClient(tagged_app)
        serve(tagged_app, workflows=[tagged_workflow])

        response = tagged_client.get("/api/novu?action=discover")

        assert response.status_code == 200
        data = response.json()
        workflow = data["workflows"][0]

        assert workflow["tags"] == ["test", "demo", "production"]
        assert workflow["preferences"] == {
            "priority": "high",
            "timeout": 30,
            "retries": 3,
        }

    def test_discover_empty_workflows(self):
        """Test discover endpoint with no registered workflows."""
        empty_app = FastAPI()
        empty_client = TestClient(empty_app)
        serve(empty_app, workflows=[])

        response = empty_client.get("/api/novu?action=discover")

        assert response.status_code == 200
        data = response.json()
        assert data["workflows"] == []

    def test_discover_response_format_matches_novu_cloud(self):
        """Test discover response format matches Novu cloud format exactly."""
        response = self.client.get("/api/novu?action=discover")

        assert response.status_code == 200
        data = response.json()

        # Verify top-level structure
        assert isinstance(data, dict)
        assert "workflows" in data
        assert isinstance(data["workflows"], list)

        if data["workflows"]:
            workflow = data["workflows"][0]

            # Verify workflow structure matches Novu cloud format
            assert isinstance(workflow, dict)

            # Check required fields with correct naming (camelCase for API)
            api_required_fields = [
                "workflowId",
                "severity",
                "steps",
                "code",
                "payload",
                "controls",
                "tags",
                "preferences",
            ]
            for field in api_required_fields:
                assert field in workflow, f"Missing API field: {field}"

            # Check payload structure
            payload = workflow["payload"]
            assert "schema" in payload
            assert "unknownSchema" in payload
            assert isinstance(payload["schema"], dict)
            assert payload["schema"]["type"] == "object"

            # Check controls structure
            controls = workflow["controls"]
            assert "schema" in controls
            assert "unknownSchema" in controls
            assert isinstance(controls["schema"], dict)
            assert controls["schema"]["type"] == "object"

    def test_discover_step_structure_validation(self):
        """Test discover endpoint returns properly structured step information."""

        def step_workflow(payload):
            step.email("email-step", lambda: {"subject": "Test Email"})
            return "done"

        step_test_workflow = Mock(spec=Workflow)
        step_test_workflow.workflow_id = "step-test-workflow"
        step_test_workflow.handler = step_workflow

        step_app = FastAPI()
        step_client = TestClient(step_app)
        serve(step_app, workflows=[step_test_workflow])

        response = step_client.get("/api/novu?action=discover")

        assert response.status_code == 200
        data = response.json()
        workflow = data["workflows"][0]

        if workflow["steps"]:
            step = workflow["steps"][0]

            # Verify step structure
            step_required_fields = [
                "stepId",
                "type",
                "controls",
                "outputs",
                "results",
                "code",
                "options",
                "providers",
            ]
            for field in step_required_fields:
                assert field in step, f"Missing step field: {field}"

            # Verify step type is valid
            assert step["type"] in {"email", "in_app", "sms", "push", "chat"}
            assert step["stepId"].startswith("step-")
            assert isinstance(step["providers"], list)
            assert step["type"] in step["providers"]

    def test_discover_concurrent_requests(self):
        """Test discover endpoint handles concurrent requests."""
        import threading

        results = []

        def make_request():
            response = self.client.get("/api/novu?action=discover")
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

    def test_discover_response_consistency(self):
        """Test discover endpoint returns consistent responses."""
        # Make multiple requests and verify consistency
        responses = []
        for _ in range(5):
            response = self.client.get("/api/novu?action=discover")
            responses.append(response.json())

        # All responses should be identical
        first_response = responses[0]
        for response in responses[1:]:
            assert response == first_response

    def test_discover_error_handling(self):
        """Test discover endpoint handles errors gracefully."""
        # Test with invalid action parameter
        response = self.client.get("/api/novu?action=invalid-action")

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_discase_sensitivity(self):
        """Test discover action is case sensitive."""
        response = self.client.get("/api/novu?action=DISCOVER")

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_discover_response_headers(self):
        """Test discover endpoint includes proper headers."""
        response = self.client.get("/api/novu?action=discover")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    @patch("novu_framework.fastapi.inspect.getsource")
    def test_discover_source_extraction_error(self, mock_getsource):
        """Test discover endpoint handles source extraction errors."""
        mock_getsource.side_effect = OSError("Cannot get source")

        response = self.client.get("/api/novu?action=discover")

        # Should still return 200 with fallback code
        assert response.status_code == 200
        data = response.json()
        assert len(data["workflows"]) == 1
        workflow = data["workflows"][0]
        assert workflow["workflowId"] == "test-workflow"
        assert "# Workflow test-workflow" in workflow["code"]
