from __future__ import annotations

from dataclasses import asdict
from typing import Any, List

import pytest
from unittest.mock import AsyncMock, MagicMock

from bson import ObjectId
from bson.decimal128 import Decimal128

from app.domain.entities.product import Product
from app.shared.exceptions.inventory import OutOfStockException
from app.adapters.driven.repositories.mongo_product_repository import (
    MongoProductRepository,
)


class _FakeResult:
    def __init__(self, inserted_id=None, modified_count=None):
        self.inserted_id = inserted_id
        self.modified_count = modified_count


class _FakeCursor:
    def __init__(self, docs: List[dict]):
        self._docs = docs

    def __aiter__(self):
        async def _gen():
            for d in self._docs:
                yield d
        return _gen()


@pytest.fixture
def sample_product() -> Product:
    return Product(
        name="Burger",
        description="Cheese Burger",
        price=12.5,
        category="BURGER",
        stock=10,
        id=None,
    )

@pytest.fixture
def mock_col(monkeypatch) -> MagicMock:
    mock_col = MagicMock()
    mock_col.insert_one = AsyncMock()
    mock_col.find_one = AsyncMock()
    mock_col.update_one = AsyncMock()
    mock_col.find = MagicMock()
    monkeypatch.setattr(
        "app.adapters.driven.repositories.mongo_product_repository._col", mock_col
    )
    return mock_col


@pytest.fixture
def repo(mock_col) -> MongoProductRepository:
    return MongoProductRepository()


@pytest.mark.asyncio
async def test_create_inserts_doc_and_returns_entity(repo, mock_col, sample_product):
    inserted_id = ObjectId()
    mock_col.insert_one.return_value = _FakeResult(inserted_id=inserted_id)

    prod = await repo.create(sample_product)

    mock_col.insert_one.assert_awaited_once()
    sent_doc = mock_col.insert_one.call_args.args[0]
    assert sent_doc["name"] == "Burger"
    assert sent_doc["active"] is True
    assert prod.id == str(inserted_id)
    assert not hasattr(prod, "active")


@pytest.mark.asyncio
async def test_find_by_id_maps_doc_to_entity(repo, mock_col, sample_product):
    oid = ObjectId()
    db_doc = asdict(sample_product) | {"_id": oid, "active": True}
    mock_col.find_one.return_value = db_doc

    prod = await repo.find_by_id(str(oid))

    mock_col.find_one.assert_awaited_with({"_id": oid})
    assert isinstance(prod, Product)
    assert prod.id == str(oid)
    assert prod.name == sample_product.name


@pytest.mark.asyncio
async def test_find_by_id_not_found_returns_none(repo, mock_col):
    oid = ObjectId()
    mock_col.find_one.return_value = None

    prod = await repo.find_by_id(str(oid))

    mock_col.find_one.assert_awaited_with({"_id": oid})
    assert prod is None


@pytest.mark.asyncio
async def test_find_all_with_filters(repo, mock_col, sample_product):
    db_doc = asdict(sample_product) | {"_id": ObjectId(), "active": True}
    mock_col.find.return_value = _FakeCursor([db_doc])

    results = await repo.find_all(cat="BURGER", active=True)

    mock_col.find.assert_called_once_with({"category": "BURGER", "active": True})
    assert len(results) == 1 and results[0].name == "Burger"


@pytest.mark.asyncio
async def test_find_all_no_filters_returns_all(repo, mock_col, sample_product):
    docs = [
        asdict(sample_product) | {"_id": ObjectId(), "active": True},
        asdict(sample_product) | {"_id": ObjectId(), "active": False},
    ]
    mock_col.find.return_value = _FakeCursor(docs)

    results = await repo.find_all()

    mock_col.find.assert_called_once_with({})
    assert len(results) == 2


@pytest.mark.asyncio
async def test_update_success(repo, mock_col, sample_product):
    pid = str(ObjectId())
    mock_col.update_one.return_value = _FakeResult()
    mock_col.find_one.return_value = asdict(sample_product) | {"_id": ObjectId(pid)}

    data = asdict(sample_product).copy()
    data["id"] = pid
    updated = await repo.update(Product(**data))

    sent = mock_col.update_one.call_args.args[1]["$set"]
    assert "active" not in sent
    assert updated.id == pid


@pytest.mark.asyncio
async def test_update_missing_id_raises(repo):
    with pytest.raises(ValueError):
        await repo.update(Product(name="x", description="y", price=1, category="z", stock=1))


@pytest.mark.asyncio
async def test_delete_sets_active_false(repo, mock_col):
    pid = str(ObjectId())
    await repo.delete(pid)
    mock_col.update_one.assert_awaited_with(
        {"_id": ObjectId(pid)}, {"$set": {"active": False}}
    )


@pytest.mark.asyncio
async def test_reserve_stock_success(repo, mock_col):
    pid = str(ObjectId())
    mock_col.update_one.return_value = _FakeResult(modified_count=1)

    await repo.reserve_stock(pid, 2)

    mock_col.update_one.assert_awaited_with(
        {"_id": ObjectId(pid), "active": True, "stock": {"$gte": 2}},
        {"$inc": {"stock": -2}},
    )


@pytest.mark.asyncio
async def test_reserve_stock_out_of_stock_raises(repo, mock_col):
    pid = str(ObjectId())
    mock_col.update_one.return_value = _FakeResult(modified_count=0)

    with pytest.raises(OutOfStockException):
        await repo.reserve_stock(pid, 99)


def test_doc_to_entity_converts_decimal128():
    price_dec = Decimal128("12.50")
    raw = {
        "_id": ObjectId(),
        "name": "Pizza",
        "description": "Mussarela",
        "price": price_dec,
        "category": "PIZZA",
        "stock": 5,
        "active": True,
    }
    prod = MongoProductRepository._doc_to_entity(raw)
    assert isinstance(prod.price, float) and prod.price == 12.5
    assert prod.id
