from typing import Any, Awaitable, Callable, Dict, Optional

from .base import BaseStep


class PushStep(BaseStep):
    """
    Push notification step.
    """

    step_type = "PUSH"

    def __init__(
        self,
        step_id: str,
        resolver: Callable[..., Any] | Callable[..., Awaitable[Any]],
        options: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(step_id, resolver, options)
