class NovuError(Exception):
    """Base exception for all Novu Framework errors."""

    pass


class WorkflowError(NovuError):
    """Raised when there is an error in the workflow definition or execution."""

    pass


class StepError(NovuError):
    """Raised when there is an error in a workflow step."""

    pass


class ValidationError(NovuError):
    """Raised when there is a validation error in payload or controls."""

    pass
