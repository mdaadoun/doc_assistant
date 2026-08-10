"""Base domain model definition using Pydantic V2 immutable configuration."""

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T", bound="BaseDomainModel")


class BaseDomainModel(BaseModel):
    """Base domain model enforcing immutability and strict schema validation."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=False,
    )

    def to_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Convert model instance to dictionary payload."""
        return self.model_dump(**kwargs)

    def to_json(self, **kwargs: Any) -> str:
        """Serialize model instance to JSON string."""
        return self.model_dump_json(**kwargs)

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """Instantiate model from dictionary payload."""
        return cls.model_validate(data)
