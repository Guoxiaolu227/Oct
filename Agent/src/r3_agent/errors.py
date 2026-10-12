class R3AgentError(Exception):
    """Base error for expected agent failures."""


class ConfigError(R3AgentError):
    """Raised when configuration or artifacts are invalid."""


class InputError(R3AgentError):
    """Raised when a manuscript cannot be safely loaded."""


class InputTooLargeError(InputError):
    """Raised instead of truncating an oversized manuscript."""


class ProviderError(R3AgentError):
    """Raised when a model request cannot be completed."""


class RequestBudgetExceededError(R3AgentError):
    """Raised before a review can exceed its configured request budget."""

    error_code = "request_budget_exceeded"


class ResponseError(R3AgentError):
    """Raised when a model response violates its contract."""
