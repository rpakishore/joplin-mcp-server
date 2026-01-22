"""Error handling module for Joplin MCP Server."""


class JoplinMCPError(Exception):
    """Base exception for Joplin MCP Server errors.

    Attributes:
        message: User-friendly error message.
        detail: Original error information for debugging.
        category: Error type identifier.
    """

    category: str = "error"

    def __init__(self, message: str, detail: str | None = None) -> None:
        """Initialize the error.

        Args:
            message: User-friendly error message.
            detail: Original error information for debugging.
        """
        self.message = message
        self.detail = detail
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.detail:
            return f"{self.message} (detail: {self.detail})"
        return self.message


class AuthError(JoplinMCPError):
    """Authentication error - invalid or missing API token."""

    category: str = "auth_error"


class ConnectionError(JoplinMCPError):
    """Connection error - cannot connect to Joplin server."""

    category: str = "connection_error"


class NotFoundError(JoplinMCPError):
    """Not found error - requested resource does not exist."""

    category: str = "not_found"


class ValidationError(JoplinMCPError):
    """Validation error - invalid input parameters."""

    category: str = "validation_error"


class JoplinAPIError(JoplinMCPError):
    """Generic Joplin API error."""

    category: str = "joplin_error"
