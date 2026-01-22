import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import BaseModel

from novu_framework.steps.email import EmailStep
from novu_framework.steps.in_app import InAppStep
from novu_framework.steps.push import PushStep
from novu_framework.steps.sms import SmsStep


class StepHandler:
    """
    Handles the execution of workflow steps.
    """

    def __init__(self, payload: Dict[str, Any], workflow: Optional["Workflow"] = None):
        self.payload = payload
        self.step_results: Dict[str, Any] = {}
        self.workflow = workflow
        self.executed_steps: List[str] = []

    def _execute_step(
        self,
        step_class: Type[Any],
        step_id: str,
        resolver: Callable[..., Any] | Dict[str, Any],
        **options: Any,
    ) -> Dict[str, Any]:
        """
        Generic method to execute a step.
        """
        # T019: Implement step skip logic
        skip = options.get("skip")
        if skip and callable(skip):
            should_skip = skip()
            # For sync version, we don't support async skip functions
            if should_skip:
                skipped_result: Dict[str, Any] = {"skipped": True}
                self.step_results[step_id] = skipped_result
                return skipped_result

        # Execute resolver
        # The resolver can be a sync function returning a dict, or a dict directly
        result: Any
        if isinstance(resolver, dict):
            # Direct dict argument, use as-is
            result = resolver
        else:
            # Handle callable resolver (sync only)
            # Get controls from options, default to empty dict if not provided
            controls = options.get("controls", {})

            result = resolver
            if callable(resolver):
                # Check if resolver takes args (controls, inputs, or payload)
                # If controls are provided and non-empty, try to call with controls first
                if controls:
                    try:
                        result = resolver(controls)
                    except TypeError:
                        try:
                            # Fallback to no args (previous behavior)
                            result = resolver()
                        except TypeError:
                            # Final fallback to payload
                            result = resolver(self.payload)
                else:
                    # No controls provided, use original behavior
                    try:
                        result = resolver()
                    except TypeError:
                        # Fallback to payload
                        result = resolver(self.payload)

        # For sync version, we don't support async resolvers
        # Store result and track step
        self.step_results[step_id] = result
        self.executed_steps.append(step_id)

        # Update workflow steps if workflow reference is available
        if self.workflow and step_id not in [
            step.get("step_id") for step in self.workflow.steps
        ]:
            self.workflow.steps.append(
                {"step_id": step_id, "type": step_class.__name__}
            )

        return result  # type: ignore[no-any-return]

    def _convert_control_schema(
        self, control_schema: Dict[str, Any] | Type[BaseModel]
    ) -> Dict[str, Any]:
        """
        Convert control schema from Pydantic model to JSON Schema if needed.
        """
        if isinstance(control_schema, dict):
            # Already a JSON schema dict, return as-is
            return control_schema
        elif inspect.isclass(control_schema) and issubclass(control_schema, BaseModel):
            # Convert Pydantic model to JSON schema
            return control_schema.model_json_schema()
        else:
            raise ValueError(
                f"controlSchema must be a dict or Pydantic BaseModel class, got {type(control_schema)}"
            )

    def in_app(
        self,
        step_id: str,
        resolver: Callable[..., Any] | Dict[str, Any],
        controlSchema: Optional[Dict[str, Any] | Type[BaseModel]] = None,
        **options: Any,
    ) -> Dict[str, Any]:
        if controlSchema is not None:
            options["control_schema"] = self._convert_control_schema(controlSchema)
        return self._execute_step(InAppStep, step_id, resolver, **options)

    def email(
        self,
        step_id: str,
        resolver: Callable[..., Any] | Dict[str, Any],
        controlSchema: Optional[Dict[str, Any] | Type[BaseModel]] = None,
        **options: Any,
    ) -> Dict[str, Any]:
        if controlSchema is not None:
            options["control_schema"] = self._convert_control_schema(controlSchema)
        return self._execute_step(EmailStep, step_id, resolver, **options)

    def sms(
        self,
        step_id: str,
        resolver: Callable[..., Any] | Dict[str, Any],
        controlSchema: Optional[Dict[str, Any] | Type[BaseModel]] = None,
        **options: Any,
    ) -> Dict[str, Any]:
        if controlSchema is not None:
            options["control_schema"] = self._convert_control_schema(controlSchema)
        return self._execute_step(SmsStep, step_id, resolver, **options)

    def push(
        self,
        step_id: str,
        resolver: Callable[..., Any] | Dict[str, Any],
        controlSchema: Optional[Dict[str, Any] | Type[BaseModel]] = None,
        **options: Any,
    ) -> Dict[str, Any]:
        if controlSchema is not None:
            options["control_schema"] = self._convert_control_schema(controlSchema)
        return self._execute_step(
            PushStep, step_id, resolver, **options
        )  # pragma: no cover


class Workflow:
    """
    Represents a notification workflow with steps, payload schema, and execution logic.
    """

    def __init__(
        self,
        workflow_id: str,
        handler: Callable[..., Any],
        payload_schema: Optional[Type[BaseModel]] = None,
        name: Optional[str] = None,
    ):
        self.workflow_id = workflow_id
        self.handler = handler
        self.payload_schema = payload_schema
        self.name = name or workflow_id
        self.steps: List[Any] = []

    async def trigger(
        self,
        to: str | Dict[str, Any],
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Trigger the workflow execution.
        """
        # Validated payload creation (T010 implementation will expand this)
        validated_payload: Dict[str, Any] | BaseModel = payload
        if self.payload_schema:
            try:
                validated_payload = self.payload_schema(**payload)
            except Exception as e:
                # Wrap validation errors? For now let Pydantic error bubble up or handle
                # gracefully
                raise e

        # Initialize StepHandler with workflow reference
        step_handler = StepHandler(payload, workflow=self)

        # Execute the handler with the step handler
        # T018: Update Workflow execution engine
        result = self.handler(validated_payload, step_handler)
        # Handle async handlers if they still exist
        if inspect.isawaitable(result):
            await result

        # Return the collected results
        return {
            "workflow_id": self.workflow_id,
            "status": "completed",
            "step_results": step_handler.step_results,
            "payload": payload,
        }


class WorkflowRegistry:
    """
    Registry for managing registered workflows.
    """

    def __init__(self) -> None:
        self.workflows: Dict[str, Workflow] = {}

    def register(self, workflow: Workflow) -> None:
        """
        Register a workflow in the registry.
        """
        if workflow.workflow_id in self.workflows:
            raise ValueError(
                f"Workflow with ID '{workflow.workflow_id}' already exists"
            )
        self.workflows[workflow.workflow_id] = workflow

    def get(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by ID.
        """
        return self.workflows.get(workflow_id)

    def clear(self) -> None:
        """
        Clear all registered workflows.
        """
        self.workflows.clear()


# Global registry instance
workflow_registry = WorkflowRegistry()


def workflow(
    workflow_id: str,
    payload_schema: Optional[Type[BaseModel]] = None,
    name: Optional[str] = None,
) -> Callable[..., Any]:
    """
    Decorator to register a notification workflow.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        nonlocal payload_schema, name

        # Automatically extract payload schema from type hints if not provided
        if payload_schema is None:
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                # Check for parameter named 'payload' or simply the first parameter that
                # is a BaseModel
                if (
                    param_name == "payload"
                    and inspect.isclass(param.annotation)
                    and issubclass(param.annotation, BaseModel)
                ):
                    payload_schema = param.annotation
                    break

            # Fallback: check first argument if not named payload (optional, but good
            # for flexibility)
            if payload_schema is None:
                for param_name, param in sig.parameters.items():
                    if inspect.isclass(param.annotation) and issubclass(
                        param.annotation, BaseModel
                    ):
                        payload_schema = param.annotation
                        break

        workflow = Workflow(
            workflow_id=workflow_id,
            handler=func,
            payload_schema=payload_schema,
            name=name or workflow_id,
        )
        workflow_registry.register(workflow)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover
            return func(*args, **kwargs)

        # Attach workflow instance to wrapper for easy access
        setattr(wrapper, "workflow_id", workflow_id)
        setattr(wrapper, "trigger", workflow.trigger)
        setattr(wrapper, "_workflow", workflow)

        return wrapper

    return decorator
