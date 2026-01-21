from typing import Any, Awaitable, Callable, Dict, Optional, Union

from .base import BaseStep


class EmailStep(BaseStep):
    """
    Email notification step.
    """

    step_type = "EMAIL"

    def __init__(
        self,
        step_id: str,
        resolver: Union[Callable[..., Any], Callable[..., Awaitable[Any]]],
        options: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(step_id, resolver, options)
