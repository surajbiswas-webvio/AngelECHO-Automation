class AutomationFrameworkError(Exception):
    """Base exception for framework-level failures."""


class ElementStateError(AutomationFrameworkError):
    """Raised when an element does not reach the expected state."""


class TestDataError(AutomationFrameworkError):
    """Raised when required test data is missing or invalid."""

