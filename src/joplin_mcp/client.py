"""Joppy client wrapper for Joplin MCP Server."""

from dataclasses import asdict
from typing import Any

from joppy.client_api import ClientApi
from joppy.data_types import NotebookData, NoteData, TagData
from requests.exceptions import ConnectionError as RequestsConnectionError

from joplin_mcp.config import Config, get_config
from joplin_mcp.errors import (
    AuthError,
    ConnectionError,
    JoplinAPIError,
    NotFoundError,
)


def _dataclass_to_dict(obj: Any) -> dict[str, Any]:
    """Convert a joppy dataclass to a dictionary, handling datetime conversion."""
    if hasattr(obj, "__dataclass_fields__"):
        result: dict[str, Any] = {}
        for key, value in asdict(obj).items():
            if value is not None:
                result[key] = value
        return result
    # If not a dataclass, assume it's already a dict
    if isinstance(obj, dict):
        return obj
    raise TypeError(f"Expected dataclass or dict, got {type(obj)}")


class JoplinClient:
    """Wrapper around joppy ClientApi with error translation.

    This class provides a unified interface to the Joplin API and translates
    joppy exceptions to our custom error types.
    """

    def __init__(self, config: Config) -> None:
        """Initialize the client with configuration.

        Args:
            config: Configuration object with API token and connection settings.
        """
        self._config = config
        self._client: ClientApi | None = None

    def _get_client(self) -> ClientApi:
        """Get or create the joppy ClientApi instance.

        Returns:
            Configured ClientApi instance.
        """
        if self._client is None:
            url = f"http://{self._config.host}:{self._config.port}"
            self._client = ClientApi(token=self._config.api_token, url=url)
        return self._client

    def _handle_error(self, e: Exception, context: str = "") -> None:
        """Translate joppy exceptions to our custom error types.

        Args:
            e: The exception to translate.
            context: Additional context for error message.

        Raises:
            ConnectionError: If connection to Joplin failed.
            AuthError: If authentication failed.
            NotFoundError: If resource was not found.
            JoplinAPIError: For other API errors.
        """
        error_str = str(e).lower()
        detail = str(e)

        if isinstance(e, RequestsConnectionError) or "connection refused" in error_str:
            raise ConnectionError(
                f"Cannot connect to Joplin at {self._config.host}:{self._config.port}. "
                "Is Joplin running with the Web Clipper service enabled?",
                detail=detail,
            )

        if "401" in error_str or "403" in error_str or "unauthorized" in error_str:
            raise AuthError(
                "Authentication failed. Check your JOPLIN_API_TOKEN.",
                detail=detail,
            )

        if "404" in error_str or "not found" in error_str:
            raise NotFoundError(
                f"Resource not found{': ' + context if context else ''}",
                detail=detail,
            )

        raise JoplinAPIError(
            f"Joplin API error{': ' + context if context else ''}",
            detail=detail,
        )

    # Note operations
    def get_note(self, note_id: str, fields: list[str] | None = None) -> dict[str, Any]:
        """Get a note by ID.

        Args:
            note_id: The note ID.
            fields: Optional list of fields to retrieve.

        Returns:
            Note data as dictionary.
        """
        try:
            client = self._get_client()
            kwargs: dict[str, Any] = {"id_": note_id}
            if fields:
                kwargs["fields"] = ",".join(fields)
            note: NoteData = client.get_note(**kwargs)
            return _dataclass_to_dict(note)
        except Exception as e:
            self._handle_error(e, f"note {note_id}")
            raise  # Never reached, but keeps type checker happy

    def search_notes(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        """Search for notes.

        Args:
            query: Search query string.
            **kwargs: Additional search parameters.

        Returns:
            List of matching notes.
        """
        try:
            client = self._get_client()
            result = client.search(query=query, **kwargs)
            return [_dataclass_to_dict(item) for item in result.items]
        except Exception as e:
            self._handle_error(e, f"search '{query}'")
            raise

    def create_note(self, **kwargs: Any) -> dict[str, Any]:
        """Create a new note.

        Args:
            **kwargs: Note properties (title, body, parent_id, etc.).

        Returns:
            Created note data with ID.
        """
        try:
            client = self._get_client()
            note_id = client.add_note(**kwargs)
            # Fetch the created note to return full data
            return self.get_note(note_id)
        except Exception as e:
            self._handle_error(e, "create note")
            raise

    def update_note(self, note_id: str, **kwargs: Any) -> None:
        """Update an existing note.

        Args:
            note_id: The note ID to update.
            **kwargs: Fields to update.
        """
        try:
            client = self._get_client()
            client.modify_note(id_=note_id, **kwargs)
        except Exception as e:
            self._handle_error(e, f"update note {note_id}")
            raise

    def get_note_tags(self, note_id: str) -> list[dict[str, Any]]:
        """Get tags attached to a note.

        Args:
            note_id: The note ID.

        Returns:
            List of tags attached to the note.
        """
        try:
            client = self._get_client()
            result = client.get_tags(note_id=note_id)
            return [_dataclass_to_dict(tag) for tag in result.items]
        except Exception as e:
            self._handle_error(e, f"get tags for note {note_id}")
            raise

    def get_note_resources(self, note_id: str) -> list[dict[str, Any]]:
        """Get resources (attachments) for a note.

        Args:
            note_id: The note ID.

        Returns:
            List of resources attached to the note.
        """
        try:
            client = self._get_client()
            result = client.get_resources(note_id=note_id)
            return [_dataclass_to_dict(res) for res in result.items]
        except Exception as e:
            self._handle_error(e, f"get resources for note {note_id}")
            raise

    # Notebook operations
    def get_notebooks(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Get all notebooks.

        Args:
            **kwargs: Additional parameters.

        Returns:
            List of notebooks.
        """
        try:
            client = self._get_client()
            result = client.get_notebooks(**kwargs)
            return [_dataclass_to_dict(nb) for nb in result.items]
        except Exception as e:
            self._handle_error(e, "get notebooks")
            raise

    def get_notebook(self, notebook_id: str) -> dict[str, Any]:
        """Get a notebook by ID.

        Args:
            notebook_id: The notebook ID.

        Returns:
            Notebook data.
        """
        try:
            client = self._get_client()
            notebook: NotebookData = client.get_notebook(id_=notebook_id)
            return _dataclass_to_dict(notebook)
        except Exception as e:
            self._handle_error(e, f"notebook {notebook_id}")
            raise

    def create_notebook(self, **kwargs: Any) -> dict[str, Any]:
        """Create a new notebook.

        Args:
            **kwargs: Notebook properties (title, parent_id).

        Returns:
            Created notebook data.
        """
        try:
            client = self._get_client()
            notebook_id = client.add_notebook(**kwargs)
            return self.get_notebook(notebook_id)
        except Exception as e:
            self._handle_error(e, "create notebook")
            raise

    def update_notebook(self, notebook_id: str, **kwargs: Any) -> None:
        """Update an existing notebook.

        Args:
            notebook_id: The notebook ID to update.
            **kwargs: Fields to update.
        """
        try:
            client = self._get_client()
            client.modify_notebook(id_=notebook_id, **kwargs)
        except Exception as e:
            self._handle_error(e, f"update notebook {notebook_id}")
            raise

    # Tag operations
    def get_tags(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Get all tags.

        Args:
            **kwargs: Additional parameters.

        Returns:
            List of tags.
        """
        try:
            client = self._get_client()
            result = client.get_tags(**kwargs)
            return [_dataclass_to_dict(tag) for tag in result.items]
        except Exception as e:
            self._handle_error(e, "get tags")
            raise

    def get_tag(self, tag_id: str) -> dict[str, Any]:
        """Get a tag by ID.

        Args:
            tag_id: The tag ID.

        Returns:
            Tag data.
        """
        try:
            client = self._get_client()
            tag: TagData = client.get_tag(id_=tag_id)
            return _dataclass_to_dict(tag)
        except Exception as e:
            self._handle_error(e, f"tag {tag_id}")
            raise

    def create_tag(self, title: str) -> dict[str, Any]:
        """Create a new tag.

        Args:
            title: Tag title.

        Returns:
            Created tag data.
        """
        try:
            client = self._get_client()
            tag_id = client.add_tag(title=title)
            return self.get_tag(tag_id)
        except Exception as e:
            self._handle_error(e, f"create tag '{title}'")
            raise

    def add_tag_to_note(self, tag_id: str, note_id: str) -> None:
        """Add a tag to a note.

        Args:
            tag_id: The tag ID.
            note_id: The note ID.
        """
        try:
            client = self._get_client()
            client.add_tag_to_note(tag_id=tag_id, note_id=note_id)
        except Exception as e:
            self._handle_error(e, f"add tag {tag_id} to note {note_id}")
            raise

    def remove_tag_from_note(self, tag_id: str, note_id: str) -> None:
        """Remove a tag from a note.

        Args:
            tag_id: The tag ID.
            note_id: The note ID.
        """
        try:
            client = self._get_client()
            # delete_tag with note_id parameter removes the tag from the note
            client.delete_tag(id_=tag_id, note_id=note_id)
        except Exception as e:
            self._handle_error(e, f"remove tag {tag_id} from note {note_id}")
            raise


_client: JoplinClient | None = None


def get_client() -> JoplinClient:
    """Get the singleton JoplinClient instance.

    Returns:
        Configured JoplinClient instance.
    """
    global _client
    if _client is None:
        config = get_config()
        _client = JoplinClient(config)
    return _client
