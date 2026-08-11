"""Differential update tracker for detecting new, modified, and deleted corpus files."""

import hashlib
from collections.abc import Sequence
from pathlib import Path

from core.exceptions import IngestionError
from models.differential import (
    DifferentialDelta,
    FileState,
    StateManifest,
    current_iso_timestamp,
)


class DifferentialTracker:
    """Tracks document file states to compute differential ingestion deltas."""

    def __init__(self, manifest_path: str | Path | None = None) -> None:
        """Initialize tracker with optional manifest persistence path."""
        self.manifest_path = Path(manifest_path).resolve() if manifest_path else None
        self._manifest = (
            self.load_manifest(self.manifest_path)
            if self.manifest_path and self.manifest_path.exists()
            else StateManifest()
        )

    @property
    def manifest(self) -> StateManifest:
        """Return current state manifest."""
        return self._manifest

    @staticmethod
    def compute_file_hash(file_path: str | Path, chunk_size: int = 65536) -> str:
        """Compute SHA-256 hash of target file using chunked binary reading."""
        path = Path(file_path).resolve()
        if not path.is_file():
            raise IngestionError(
                f"Cannot hash non-file target: {path}",
                code="FILE_NOT_FOUND",
                details={"file_path": str(path)},
            )
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _resolve_target_files(
        self, target_paths: Sequence[str | Path] | str | Path
    ) -> list[Path]:
        """Resolve inputs into list of valid existing file paths."""
        targets: list[Path] = []
        raw_list = (
            [target_paths]
            if isinstance(target_paths, str | Path)
            else list(target_paths)
        )
        for raw in raw_list:
            p = Path(raw).resolve()
            if p.is_dir():
                targets.extend([item for item in p.rglob("*") if item.is_file()])
            elif p.is_file():
                targets.append(p)
        return sorted(list(set(targets)))

    def scan(
        self, target_paths: Sequence[str | Path] | str | Path
    ) -> DifferentialDelta:
        """Scan filesystem targets against manifest to detect file status deltas."""
        target_files = self._resolve_target_files(target_paths)
        current_map = {str(p): p for p in target_files}

        new_files: list[str] = []
        changed_files: list[str] = []
        unchanged_files: list[str] = []

        for path_str, path_obj in current_map.items():
            current_hash = self.compute_file_hash(path_obj)
            if path_str not in self._manifest.files:
                new_files.append(path_str)
            else:
                tracked = self._manifest.files[path_str]
                if current_hash != tracked.content_hash:
                    changed_files.append(path_str)
                else:
                    unchanged_files.append(path_str)

        deleted_files: list[str] = [
            tracked_path
            for tracked_path in self._manifest.files
            if tracked_path not in current_map and not Path(tracked_path).exists()
        ]

        return DifferentialDelta(
            new_files=sorted(new_files),
            changed_files=sorted(changed_files),
            deleted_files=sorted(deleted_files),
            unchanged_files=sorted(unchanged_files),
        )

    def update_file_state(
        self, file_path: str | Path, chunk_ids: list[str] | None = None
    ) -> FileState:
        """Record or update FileState entry in memory manifest."""
        path = Path(file_path).resolve()
        norm_path = str(path)
        stat = path.stat()
        content_hash = self.compute_file_hash(path)
        state = FileState(
            file_path=norm_path,
            content_hash=content_hash,
            file_size_bytes=stat.st_size,
            last_modified=stat.st_mtime,
            processed_at=current_iso_timestamp(),
            chunk_ids=chunk_ids or [],
        )
        updated_files = dict(self._manifest.files)
        updated_files[norm_path] = state
        self._manifest = self._manifest.model_copy(
            update={"files": updated_files, "last_synced_at": current_iso_timestamp()}
        )
        return state

    def remove_file_state(self, file_path: str | Path) -> FileState | None:
        """Remove file state from manifest if tracked."""
        norm_path = str(Path(file_path).resolve())
        if norm_path not in self._manifest.files:
            return None
        updated_files = dict(self._manifest.files)
        removed = updated_files.pop(norm_path)
        self._manifest = self._manifest.model_copy(
            update={"files": updated_files, "last_synced_at": current_iso_timestamp()}
        )
        return removed

    def sync_delta(self, delta: DifferentialDelta) -> None:
        """Purge deleted files from manifest state."""
        for deleted_path in delta.deleted_files:
            self.remove_file_state(deleted_path)

    def load_manifest(self, path: str | Path) -> StateManifest:
        """Load manifest from JSON file path."""
        p = Path(path).resolve()
        if not p.exists():
            raise IngestionError(
                f"Manifest file not found: {p}",
                code="MANIFEST_NOT_FOUND",
                details={"manifest_path": str(p)},
            )
        try:
            return StateManifest.model_validate_json(p.read_text(encoding="utf-8"))
        except Exception as err:
            raise IngestionError(
                f"Failed to parse manifest JSON: {err}",
                code="INVALID_MANIFEST",
                details={"manifest_path": str(p), "error": str(err)},
            ) from err

    def save_manifest(self, path: str | Path | None = None) -> Path:
        """Persist current manifest state to JSON file."""
        target_path = Path(path).resolve() if path else self.manifest_path
        if not target_path:
            raise IngestionError(
                "No manifest path specified for save",
                code="MISSING_MANIFEST_PATH",
            )
        target_path.parent.mkdir(parents=True, exist_ok=True)
        self._manifest = self._manifest.model_copy(
            update={"last_synced_at": current_iso_timestamp()}
        )
        target_path.write_text(
            self._manifest.model_dump_json(indent=2), encoding="utf-8"
        )
        return target_path
