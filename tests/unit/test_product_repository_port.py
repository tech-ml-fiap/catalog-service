from __future__ import annotations

from dataclasses import replace, asdict
from types import SimpleNamespace
import pytest

from app.domain.entities.product import Product
from app.shared.enums.category import Category
from app.domain.ports.product_repository_port import ProductRepositoryPort


@pytest.fixture
def sample_product() -> Product:
    return Product(
        name="Burger",
        description="Cheese Burger",
        price=12.5,
        category=Category.LUNCH,
        stock=10,
        id="abc",
    )


class DummyRepo(ProductRepositoryPort):
    def __init__(self, prod: Product):
        self._prod = prod
        self.calls = SimpleNamespace(created=None, updated=None, deleted=None, reserved=None)

    async def create(self, product: Product) -> Product:
        self.calls.created = product
        return replace(product, id="new-id")

    async def find_by_id(self, product_id: str):
        return self._prod if product_id == self._prod.id else None

    async def find_all(self, cat=None, active=None):
        return [self._prod]

    async def update(self, product: Product):
        self.calls.updated = product
        return product

    async def delete(self, product_id: str):
        self.calls.deleted = product_id

    async def reserve_stock(self, product_id: str, qty: int):
        self.calls.reserved = (product_id, qty)


def test_cannot_instantiate_port_directly():
    with pytest.raises(TypeError):
        ProductRepositoryPort()


@pytest.mark.asyncio
async def test_dummy_repo_implements_all_methods(sample_product):
    repo = DummyRepo(sample_product)

    created = await repo.create(sample_product)
    assert created.id == "new-id" and repo.calls.created is sample_product

    assert await repo.find_by_id("abc") == sample_product
    assert await repo.find_by_id("xyz") is None

    all_items = await repo.find_all()
    assert len(all_items) == 1 and asdict(all_items[0]) == asdict(sample_product)

    updated_prod = replace(sample_product, price=15.0)
    updated = await repo.update(updated_prod)
    assert updated.price == 15.0 and repo.calls.updated is updated_prod

    await repo.delete("abc")
    assert repo.calls.deleted == "abc"

    await repo.reserve_stock("abc", 2)
    assert repo.calls.reserved == ("abc", 2)
