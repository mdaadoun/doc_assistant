"""Unit tests for BaseDomainModel schema definition and behavior."""

import pytest
from pydantic import ValidationError

from models.base import BaseDomainModel


class DummyDomainModel(BaseDomainModel):
    """Concrete subclass for domain model testing."""

    id: str
    count: int


def test_base_domain_model_config() -> None:
    """Verify BaseDomainModel enforces frozen and forbid extra configuration."""
    assert BaseDomainModel.model_config.get("frozen") is True
    assert BaseDomainModel.model_config.get("extra") == "forbid"
    assert BaseDomainModel.model_config.get("use_enum_values") is True


def test_domain_model_instantiation() -> None:
    """Verify concrete domain model initializes correctly with valid attributes."""
    model = DummyDomainModel(id="doc-123", count=5)
    assert model.id == "doc-123"
    assert model.count == 5


def test_domain_model_immutability() -> None:
    """Verify domain model instances are frozen and reject mutation."""
    model = DummyDomainModel(id="doc-123", count=5)
    with pytest.raises(ValidationError):
        model.id = "doc-456"


def test_domain_model_forbid_extra() -> None:
    """Verify domain model rejects undeclared extra attributes."""
    with pytest.raises(ValidationError):
        DummyDomainModel(id="doc-123", count=5, invalid_param="unknown")  # type: ignore[call-arg]


def test_domain_model_to_dict() -> None:
    """Verify to_dict returns dictionary payload matching model fields."""
    model = DummyDomainModel(id="doc-123", count=5)
    payload = model.to_dict()
    assert payload == {"id": "doc-123", "count": 5}


def test_domain_model_to_json() -> None:
    """Verify to_json returns serialized JSON string representation."""
    model = DummyDomainModel(id="doc-123", count=5)
    json_str = model.to_json()
    assert '"id":"doc-123"' in json_str or '"id": "doc-123"' in json_str
    assert '"count":5' in json_str or '"count": 5' in json_str


def test_domain_model_from_dict() -> None:
    """Verify from_dict instantiates model from dictionary payload."""
    data = {"id": "doc-789", "count": 10}
    model = DummyDomainModel.from_dict(data)
    assert isinstance(model, DummyDomainModel)
    assert model.id == "doc-789"
    assert model.count == 10
