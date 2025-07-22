from __future__ import annotations

import importlib
from dataclasses import replace
from typing import Any

import pytest
from bson import ObjectId
from fastapi import HTTPException

ROUTER_PATH = "app.adapters.driver.controllers.product_router"
router_mod = importlib.import_module(ROUTER_PATH)

ProductIn = router_mod.ProductIn
Product = router_mod.Product
Category = router_mod.Category
OutOfStockException = router_mod.OutOfStockException

SAMPLE_ENTITY = Product(
    id=str(ObjectId()),
    name="Burger",
    description="Cheese Burger",
    price=12.5,
    category=Category.LUNCH,
    stock=10,
)

class _SvcStub:
    def __init__(self, _repo, *, result: Any = None, exc: Exception | None = None):
        self._result = result
        self._exc = exc

    async def execute(self, *args, **kwargs):
        if self._exc:
            raise self._exc
        return self._result


def _patch_service(monkeypatch, cls_name: str, *, result=None, exc=None):
    monkeypatch.setattr(
        router_mod,
        cls_name,
        lambda repo: _SvcStub(repo, result=result, exc=exc),
    )


@pytest.mark.asyncio
async def test_create_product_success(monkeypatch):
    _patch_service(monkeypatch, "CreateProductService", result=SAMPLE_ENTITY)

    body = ProductIn.model_validate(
        {
            "name": "Burger",
            "description": "Cheese Burger",
            "price": 12.5,
            "category": "Lanche",
            "stock": 10,
        }
    )
    result = await router_mod.create_product(body, repo="fake_repo")

    assert result.id == SAMPLE_ENTITY.id and result.name == "Burger"


@pytest.mark.asyncio
async def test_list_products_filtered(monkeypatch):
    _patch_service(monkeypatch, "ListProductsService", result=[SAMPLE_ENTITY])

    prods = await router_mod.list_products(
        category=Category.LUNCH, active=True, repo="fake_repo"
    )

    assert len(prods) == 1 and prods[0].name == "Burger"


@pytest.mark.asyncio
async def test_patch_product_success(monkeypatch):
    updated = replace(SAMPLE_ENTITY, price=15.0)
    _patch_service(monkeypatch, "UpdateProductService", result=updated)

    body = router_mod.ProductPatchIn(price=15.0)
    resp = await router_mod.patch_product(SAMPLE_ENTITY.id, body, repo="fake_repo")

    assert resp.price == 15.0


@pytest.mark.asyncio
async def test_delete_product_success(monkeypatch):
    _patch_service(monkeypatch, "DeleteProductService", result=None)

    resp = await router_mod.delete_product(SAMPLE_ENTITY.id, repo="fake_repo")
    assert resp is None


@pytest.mark.asyncio
async def test_delete_product_not_found(monkeypatch):
    _patch_service(monkeypatch, "DeleteProductService", exc=ValueError("not found"))

    with pytest.raises(HTTPException) as exc:
        await router_mod.delete_product(SAMPLE_ENTITY.id, repo="fake_repo")

    assert exc.value.status_code == 404 and exc.value.detail == "not found"


@pytest.mark.asyncio
async def test_reserve_stock_success(monkeypatch):
    _patch_service(monkeypatch, "ReserveStockService", result=None)

    body = router_mod.ReserveBody(qty=2)
    resp = await router_mod.reserve_stock(SAMPLE_ENTITY.id, body, repo="fake_repo")

    assert resp is None


@pytest.mark.asyncio
async def test_reserve_stock_conflict(monkeypatch):
    _patch_service(
        monkeypatch,
        "ReserveStockService",
        exc=OutOfStockException("Not enough stock"),
    )

    body = router_mod.ReserveBody(qty=999)
    with pytest.raises(HTTPException) as exc:
        await router_mod.reserve_stock(SAMPLE_ENTITY.id, body, repo="fake_repo")

    assert exc.value.status_code == 409 and exc.value.detail == "Not enough stock"
