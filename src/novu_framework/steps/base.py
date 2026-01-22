from abc import ABC
from typing import Any, Awaitable, Callable, Dict, Optional


class BaseStep(ABC):
    """
    Abstract base class for all workflow steps.
    """

    step_type: str

    def __init__(
        self,
        step_id: str,
        resolver: Callable[..., Any] | Callable[..., Awaitable[Any]] | Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
    ):
        self.step_id = step_id
        self.resolver = resolver
        self.options = options or {}

    @property
    def skip(self) -> Optional[Callable[[], bool]]:
        return self.options.get("skip")

    @property
    def control_schema(self) -> Optional[Dict[str, Any]]:
        return self.options.get("control_schema")
