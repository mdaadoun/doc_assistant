"""Domain models for differential update tracking and file state manifest."""

from datetime import datetime, timezone

from pydantic import Field

from models.base import BaseDomainModel
from models.chunk import ChunkDocument


class FileState(BaseDomainModel):
    """Immutable state snapshot for an ingested document file."""

    file_path: str = Field(..., description="Normalized document file path")
    content_hash: str = Field(..., description="SHA-256 hash of file contents")
    file_size_bytes: int = Field(..., ge=0, description="File size in bytes")
    last_modified: float = Field(
        ..., ge=0.0, description="Modification epoch timestamp"
    )
    processed_at: str = Field(
        ..., description="ISO 8601 timestamp string when file was processed"
    )
    chunk_ids: list[str] = Field(
        default_factory=list, description="IDs of generated chunks"
    )


class StateManifest(BaseDomainModel):
    """Manifest repository persisting file states for differential comparison."""

    version: str = Field(default="1.0.0", description="Manifest schema version")
    last_synced_at: str | None = Field(
        default=None, description="ISO 8601 timestamp of last sync"
    )
    files: dict[str, FileState] = Field(
        default_factory=dict, description="Map of path to FileState"
    )


class DifferentialDelta(BaseDomainModel):
    """Categorized file changes detected between current disk state and state manifest."""

    new_files: list[str] = Field(
        default_factory=list, description="Newly detected file paths"
    )
    changed_files: list[str] = Field(
        default_factory=list, description="Modified file paths"
    )
    deleted_files: list[str] = Field(
        default_factory=list, description="Deleted file paths"
    )
    unchanged_files: list[str] = Field(
        default_factory=list, description="Unmodified file paths"
    )

    @property
    def has_changes(self) -> bool:
        """Return True if any new, changed, or deleted files are detected."""
        return bool(self.new_files or self.changed_files or self.deleted_files)

    @property
    def files_to_process(self) -> list[str]:
        """Return combined list of new and changed file paths requiring ingestion."""
        return self.new_files + self.changed_files


class DifferentialResult(BaseDomainModel):
    """Output payload of differential ingestion execution."""

    delta: DifferentialDelta = Field(..., description="Categorized diff delta payload")
    chunks: list[ChunkDocument] = Field(
        default_factory=list, description="Chunks generated from processing"
    )
    processed_count: int = Field(
        default=0, ge=0, description="Number of files parsed and chunked"
    )


def current_iso_timestamp() -> str:
    """Return current UTC timestamp formatted as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()
