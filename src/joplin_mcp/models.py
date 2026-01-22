"""Pydantic models for Joplin MCP Server."""

from datetime import datetime

from pydantic import BaseModel, Field


# Tag models
class TagRef(BaseModel):
    """Lightweight tag reference for embedding in Note responses."""

    id: str
    title: str


class Tag(BaseModel):
    """Full tag model."""

    id: str
    title: str
    created_time: datetime
    updated_time: datetime


class TagCreate(BaseModel):
    """Model for creating a new tag."""

    title: str


# Note models
class NoteSnippet(BaseModel):
    """Note with truncated body for search results."""

    id: str
    title: str
    notebook_id: str = Field(alias="parent_id")
    created_time: datetime
    updated_time: datetime
    is_todo: bool
    todo_completed: bool
    snippet: str = Field(description="First 500 characters of the note body")

    model_config = {"populate_by_name": True}


class Note(BaseModel):
    """Full note model with complete body and tags."""

    id: str
    title: str
    body: str
    notebook_id: str = Field(alias="parent_id")
    created_time: datetime
    updated_time: datetime
    is_todo: bool
    todo_completed: bool
    tags: list[TagRef] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class NoteCreate(BaseModel):
    """Model for creating a new note."""

    title: str
    body: str
    notebook_id: str | None = Field(default=None, alias="parent_id")
    is_todo: bool = False
    tags: list[str] | None = Field(default=None, description="List of tag IDs to attach")

    model_config = {"populate_by_name": True}


class NoteUpdate(BaseModel):
    """Model for updating a note. None means 'don't change'."""

    title: str | None = None
    body: str | None = None
    notebook_id: str | None = Field(default=None, alias="parent_id")
    is_todo: bool | None = None
    todo_completed: bool | None = None

    model_config = {"populate_by_name": True}


# Notebook models
class Notebook(BaseModel):
    """Notebook model."""

    id: str
    title: str
    parent_id: str | None = None
    created_time: datetime
    updated_time: datetime


class NotebookTreeNode(BaseModel):
    """Notebook tree node for hierarchical view."""

    id: str
    title: str
    children: list["NotebookTreeNode"] = Field(default_factory=list)


class NotebookCreate(BaseModel):
    """Model for creating a new notebook."""

    title: str
    parent_id: str | None = None


class NotebookUpdate(BaseModel):
    """Model for updating a notebook. None means 'don't change'."""

    title: str | None = None
    parent_id: str | None = None


# Resource models
class Resource(BaseModel):
    """Resource (attachment) model."""

    id: str
    title: str
    filename: str
    mime: str
    size: int
    created_time: datetime
    updated_time: datetime


# Error response
class ErrorResponse(BaseModel):
    """Error response model."""

    category: str
    message: str
    detail: str | None = None
