from __future__ import annotations

import asyncio
from dataclasses import replace
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock

import pytest
from pytest_bdd import scenario, given, when, then, parsers

from app.domain.entities.product import Product
from app.domain.services.create_product import CreateProductService
from app.shared.enums.category import Category

FEATURE_FILE = Path(__file__).parents[1] / "features" / "create_product.feature"


@scenario(str(FEATURE_FILE), "Create product successfully")
def test_create_product_successfully():
    pass


@scenario(str(FEATURE_FILE), "Negative price raises")
def test_negative_price_raises():
    pass


# ---------------- Fixtures ----------------
@pytest.fixture
def context() -> Dict[str, Any]:
    return {"result": None, "error": None, "product": None}


@pytest.fixture
def repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(repo: AsyncMock) -> CreateProductService:
    return CreateProductService(repo)


# ---------------- GIVEN ----------------
@given("a sample product")
def given_sample_product(context):
    context["product"] = Product(
        name="Burger",
        description="Cheese Burger",
        price=12.5,
        category=Category.LUNCH,
        stock=10,
        id=None,
    )


@given(parsers.parse('the repository will return the product with id "{new_id}"'))
def given_repo_return(context, repo: AsyncMock, new_id: str):
    repo.create.return_value = replace(context["product"], id=new_id)


@given(parsers.parse("a sample product with price {price:g}"))
def given_sample_product_with_price(context, price: float):
    context["product"] = Product(
        name="Burger",
        description="Cheese Burger",
        price=price,
        category=Category.LUNCH,
        stock=10,
        id=None,
    )


# ---------------- WHEN ----------------
@when("I execute create_product")
def when_execute_create_product(context, service: CreateProductService):
    try:
        context["result"] = asyncio.run(service.execute(context["product"]))
    except Exception as e:  # noqa: BLE001
        context["error"] = e


# ---------------- THEN ----------------
@then(parsers.parse('the result id should be "{expected_id}"'))
def then_result_id(context, expected_id: str):
    assert context["result"] is not None, "result não foi definido"
    assert context["result"].id == expected_id


@then(parsers.parse("the result price should be {expected_price:g}"))
def then_result_price(context, expected_price: float):
    assert context["result"] is not None, "result não foi definido"
    assert context["result"].price == expected_price


@then("the repository create must be awaited once")
def then_repo_called_once(repo: AsyncMock, context):
    repo.create.assert_awaited_once_with(context["product"])


@then("the repository create must not be called")
def then_repo_not_called(repo: AsyncMock):
    repo.create.assert_not_called()


@then(parsers.parse('a ValueError should be raised with message "{msg}"'))
def then_error_message(context, msg: str):
    err = context["error"]
    assert isinstance(err, ValueError), f"Nenhum ValueError capturado. Recebido: {err!r}"
    assert msg in str(err)
