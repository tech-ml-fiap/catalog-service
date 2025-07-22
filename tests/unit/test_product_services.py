from __future__ import annotations

from dataclasses import replace
from unittest.mock import AsyncMock
import pytest
from bson import ObjectId

from app.domain.entities.product import Product
from app.shared.enums.category import Category

# imports dos serviços
DeleteProductService = __import__("app.domain.services.delete_product", fromlist=["DeleteProductService"]).DeleteProductService
GetProductService    = __import__("app.domain.services.get_product",   fromlist=["GetProductService"]).GetProductService
ListProductsService  = __import__("app.domain.services.list_product",  fromlist=["ListProductsService"]).ListProductsService
ReserveStockService  = __import__("app.domain.services.reserve_stock", fromlist=["ReserveStockService"]).ReserveStockService
UpdateProductService = __import__("app.domain.services.update_product",fromlist=["UpdateProductService"]).UpdateProductService


@pytest.fixture
def sample_product() -> Product:
    return Product(
        name="Burger",
        description="Cheese Burger",
        price=12.5,
        category=Category.LUNCH,
        stock=10,
        id=str(ObjectId()),
    )


def _mock_repo(**methods):
    repo = AsyncMock()
    for name, value in methods.items():
        m = AsyncMock()
        if isinstance(value, Exception):
            m.side_effect = value
        else:
            m.return_value = value
        setattr(repo, name, m)
    return repo


@pytest.mark.asyncio
async def test_delete_product_success(sample_product):
    repo = _mock_repo(find_by_id=sample_product, delete=None)
    await DeleteProductService(repo).execute(sample_product.id)
    repo.delete.assert_awaited_once_with(sample_product.id)


@pytest.mark.asyncio
async def test_delete_product_not_found(sample_product):
    repo = _mock_repo(find_by_id=None)
    with pytest.raises(ValueError):
        await DeleteProductService(repo).execute("x")


@pytest.mark.asyncio
async def test_delete_product_zero_stock(sample_product):
    repo = _mock_repo(find_by_id=replace(sample_product, stock=0))
    with pytest.raises(ValueError):
        await DeleteProductService(repo).execute(sample_product.id)


@pytest.mark.asyncio
async def test_get_product_success(sample_product):
    repo = _mock_repo(find_by_id=sample_product)
    assert await GetProductService(repo).execute(sample_product.id) == sample_product


@pytest.mark.asyncio
async def test_get_product_not_found():
    repo = _mock_repo(find_by_id=None)
    with pytest.raises(ValueError):
        await GetProductService(repo).execute("x")


@pytest.mark.asyncio
async def test_list_products(sample_product):
    repo = _mock_repo(find_all=[sample_product])
    service = ListProductsService(repo)
    prods = await service.execute(active=True, category="BURGER")
    repo.find_all.assert_awaited_once_with(cat="BURGER", active=True)
    assert prods == [sample_product]


@pytest.mark.asyncio
async def test_reserve_stock_success():
    repo = _mock_repo(reserve_stock=None)
    await ReserveStockService(repo).execute("pid", 2)
    repo.reserve_stock.assert_awaited_once_with("pid", 2)


@pytest.mark.asyncio
@pytest.mark.parametrize("q", [0, -3])
async def test_reserve_stock_invalid_qty(q):
    repo = _mock_repo()
    with pytest.raises(ValueError):
        await ReserveStockService(repo).execute("pid", q)
    repo.reserve_stock.assert_not_called()


@pytest.mark.asyncio
async def test_update_product_success(sample_product):
    repo = _mock_repo(
        find_by_id=sample_product,
        update=replace(sample_product, price=15.0)
    )
    service = UpdateProductService(repo)
    result = await service.execute(sample_product.id, {"price": 15.0, "description": None})
    repo.update.assert_awaited()
    assert result.price == 15.0 and result.description == sample_product.description


@pytest.mark.asyncio
async def test_update_product_not_found():
    repo = _mock_repo(find_by_id=None)
    with pytest.raises(ValueError):
        await UpdateProductService(repo).execute("pid", {})


@pytest.mark.asyncio
async def test_update_product_negative_price(sample_product):
    repo = _mock_repo(find_by_id=sample_product)
    with pytest.raises(ValueError):
        await UpdateProductService(repo).execute(sample_product.id, {"price": -1})
