from __future__ import annotations

from dataclasses import replace
from unittest.mock import AsyncMock
import pytest

from app.domain.entities.product import Product
from app.shared.enums.category import Category
from app.domain.services.create_product import CreateProductService


@pytest.fixture
def sample_product() -> Product:
    return Product(
        name="Burger",
        description="Cheese Burger",
        price=12.5,
        category=Category.LUNCH,
        stock=10,
        id=None,
    )


@pytest.mark.asyncio
async def test_execute_success(sample_product):
    mock_repo = AsyncMock()

    created_prod = replace(sample_product, id="new-id")
    mock_repo.create.return_value = created_prod

    service = CreateProductService(mock_repo)
    result = await service.execute(sample_product)

    mock_repo.create.assert_awaited_once_with(sample_product)
    assert result.id == "new-id" and result.price == sample_product.price


@pytest.mark.asyncio
async def test_execute_negative_price_raises(sample_product):
    product_neg = replace(sample_product, price=-1)
    mock_repo = AsyncMock()
    service = CreateProductService(mock_repo)

    with pytest.raises(ValueError, match="Price cannot be negative"):
        await service.execute(product_neg)

    mock_repo.create.assert_not_called()
