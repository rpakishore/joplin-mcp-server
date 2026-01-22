"""Configuration module for Joplin MCP Server."""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for Joplin MCP Server.

    Attributes:
        api_token: Joplin API token for authentication.
        host: Joplin server host.
        port: Joplin server port.
    """

    api_token: str
    host: str = "localhost"
    port: int = 41184


_config: Config | None = None


def get_config() -> Config:
    """Get the configuration from environment variables.

    Returns:
        Config object with settings loaded from environment.

    Raises:
        ValueError: If JOPLIN_API_TOKEN is not set.
    """
    global _config

    if _config is not None:
        return _config

    api_token = os.environ.get("JOPLIN_API_TOKEN")
    if not api_token:
        raise ValueError(
            "JOPLIN_API_TOKEN environment variable is required. "
            "Get your token from Joplin: Tools > Options > Web Clipper"
        )

    host = os.environ.get("JOPLIN_HOST", "localhost")
    port_str = os.environ.get("JOPLIN_PORT", "41184")

    try:
        port = int(port_str)
    except ValueError:
        raise ValueError(f"JOPLIN_PORT must be a valid integer, got: {port_str}")

    _config = Config(api_token=api_token, host=host, port=port)
    return _config
