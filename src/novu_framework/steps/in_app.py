from typing import Any, Awaitable, Callable, Dict, Optional, Union

from .base import BaseStep


class InAppStep(BaseStep):
    """
    In-App notification step.
    """

    step_type = "IN_APP"

    def __init__(
        self,
        step_id: str,
        resolver: Union[
            Callable[..., Any], Callable[..., Awaitable[Any]], Dict[str, Any]
        ],
        options: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(step_id, resolver, options)
