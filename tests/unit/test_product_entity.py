from dataclasses import asdict
import pytest

from app.domain.entities.product import Product
from app.shared.enums.category import Category


def _make() -> Product:
    return Product(
        name="Burger",
        description="Cheese Burger",
        price=12.5,
        category=Category.LUNCH,
    )


def test_creation_defaults_and_asdict():
    p = _make()
    assert p.stock == 0 and p.id is None
    d = asdict(p)
    assert d["name"] == "Burger" and d["stock"] == 0 and d["id"] is None


def test_equality_and_hash():
    p1, p2 = _make(), _make()
    assert p1 == p2
    assert len({p1, p2}) == 1


def test_immutable_fields():
    p = _make()
    with pytest.raises(AttributeError):
        p.price = 99.9

