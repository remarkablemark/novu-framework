import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Type, Union

from pydantic import BaseModel

from novu_framework.steps.email import EmailStep
from novu_framework.steps.in_app import InAppStep
from novu_framework.steps.push import PushStep
from novu_framework.steps.sms import SmsStep


class StepHandler:
    """
    Handles the execution of workflow steps.
    """

    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload
        self.step_results: Dict[str, Any] = {}

    async def _execute_step(
        self,
        step_class: Type[Any],
        step_id: str,
        resolver: Callable[..., Any],
        **options: Any,
    ) -> Dict[str, Any]:
        """
        Generic method to execute a step.
        """
        # T019: Implement step skip logic
        skip = options.get("skip")
        if skip and callable(skip):
            should_skip = skip()
            if inspect.isawaitable(should_skip):
                should_skip = await should_skip
            if should_skip:
                skipped_result: Dict[str, Any] = {"skipped": True}
                self.step_results[step_id] = skipped_result
                return skipped_result

        # Execute resolver
        # The resolver can be an async function or a sync function returning a dict
        if inspect.iscoroutinefunction(resolver) or inspect.isawaitable(resolver):
            # This check is slightly loose, normally we check if the result of calling
            # it is awaitable. But here we haven't called it yet.
            pass

        result: Any = resolver
        if callable(resolver):
            # Check if resolver takes args (like inputs or controls)- simplified for now
            # For this MVP, assume resolver takes no args or we need to pass something?
            # Quickstart: async () => ({..}) implies no args or maybe execution context?
            # We will call it with no args for now as per quickstart examples
            try:
                result = resolver()
            except TypeError:
                # Fallback if it expects arguments (future proofing)
                result = resolver(self.payload)

        if inspect.isawaitable(result):
            result = await result

        # Store result
        self.step_results[step_id] = result
        return result  # type: ignore[no-any-return]

    async def in_app(
        self,
        step_id: str,
        resolver: Callable[..., Any],
        **options: Any,
    ) -> Dict[str, Any]:
        return await self._execute_step(InAppStep, step_id, resolver, **options)

    async def email(
        self,
        step_id: str,
        resolver: Callable[..., Any],
        **options: Any,
    ) -> Dict[str, Any]:
        return await self._execute_step(EmailStep, step_id, resolver, **options)

    async def sms(
        self,
        step_id: str,
        resolver: Callable[..., Any],
        **options: Any,
    ) -> Dict[str, Any]:
        return await self._execute_step(SmsStep, step_id, resolver, **options)

    async def push(
        self,
        step_id: str,
        resolver: Callable[..., Any],
        **options: Any,
    ) -> Dict[str, Any]:
        return await self._execute_step(
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
        to: Union[str, Dict[str, Any]],
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Trigger the workflow execution.
        """
        # Validated payload creation (T010 implementation will expand this)
        validated_payload: Union[Dict[str, Any], BaseModel] = payload
        if self.payload_schema:
            try:
                validated_payload = self.payload_schema(**payload)
            except Exception as e:
                # Wrap validation errors? For now let Pydantic error bubble up or handle
                # gracefully
                raise e

        # Initialize StepHandler
        step_handler = StepHandler(payload)

        # Execute the handler with the step handler
        # T018: Update Workflow execution engine
        await self.handler(validated_payload, step_handler)

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
        async def wrapper(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover
            return await func(*args, **kwargs)

        # Attach workflow instance to wrapper for easy access
        setattr(wrapper, "workflow_id", workflow_id)
        setattr(wrapper, "trigger", workflow.trigger)
        setattr(wrapper, "_workflow", workflow)

        return wrapper

    return decorator
