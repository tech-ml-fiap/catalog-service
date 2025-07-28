from collections import defaultdict
from dataclasses import asdict

from fastapi import status
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.adapters.driver.dependencies.di import get_repo
from app.domain.entities.product import Product
from app.domain.services.create_product import CreateProductService
from app.domain.services.delete_product import DeleteProductService
from app.domain.services.get_product import GetProductService
from app.domain.services.list_product import ListProductsService
from app.domain.services.reserve_stock import ReserveStockService
from app.domain.services.update_product import UpdateProductService
from app.shared.enums.category import Category
from app.shared.exceptions.inventory import OutOfStockException

router = APIRouter(prefix="/products", tags=["products"])


class ProductIn(BaseModel):
    name: str
    description: str | None
    price: float
    category: Category
    stock: int = 0

class ProductPatchIn(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    category: Category | None = None
    stock: int | None = Field(default=None, ge=0)
    active: bool | None = None

class ReserveBody(BaseModel):
    qty: int = Field(gt=0, description="Quantidade a reservar")

class ProductOut(ProductIn):
    id: str


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductIn, repo=Depends(get_repo)):
    service = CreateProductService(repo)
    entity = Product(**body.model_dump())
    created = await service.execute(entity)
    return ProductOut(**asdict(created))


@router.get("/", response_model=list[ProductOut])
async def list_products(
    category: Category | None = Query(
        default=None,
        description="Filtra por categoria; omita para todas",
    ),
    active: bool | None = Query(
        default=None,
        description="true = ativos, false = inativos, omitido = todos",
    ),
    repo=Depends(get_repo),
):
    service = ListProductsService(repo)
    prods = await service.execute(category=category, active=active)
    return [ProductOut(**asdict(p)) for p in prods]


@router.patch("/{pid}", response_model=ProductOut)
async def patch_product(pid: str, body: ProductPatchIn, repo=Depends(get_repo)):
    service = UpdateProductService(repo)
    updated = await service.execute(pid, body.model_dump(exclude_unset=True))
    return ProductOut(**asdict(updated))


@router.delete("/{pid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(pid: str, repo=Depends(get_repo)):
    service = DeleteProductService(repo)
    try:
        await service.execute(pid)
    except ValueError as e:
        # produto não existe ou já está inativo
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{pid}", response_model=ProductOut, status_code=status.HTTP_200_OK)
async def get_product(pid: str, repo=Depends(get_repo)):
    service = GetProductService(repo)
    try:
        prod = await service.execute(pid)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ProductOut(**asdict(prod))

@router.post("/{pid}/reserve", status_code=status.HTTP_204_NO_CONTENT)
async def reserve_stock(pid: str, body: ReserveBody, repo=Depends(get_repo)):
    service = ReserveStockService(repo)
    try:
        await service.execute(pid, body.qty)
    except OutOfStockException as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{pid}/activate", response_model=ProductOut, status_code=status.HTTP_200_OK)
async def activate_product(pid: str, repo=Depends(get_repo)):
    service = UpdateProductService(repo)
    try:
        updated = await service.execute(pid, {"active": True})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ProductOut(**asdict(updated))


class CategoryBreakdown(BaseModel):
    count: int
    stock: int
    active: int
    inactive: int
    valuation: float  # soma de price * stock

class ProductsSummaryOut(BaseModel):
    total_products: int
    active_products: int
    inactive_products: int
    total_stock: int
    total_valuation: float
    by_category: dict[Category, CategoryBreakdown]


@router.get(
    "/summary",
    response_model=ProductsSummaryOut,
    summary="Resumo de inventário",
    description="Estatísticas gerais e por categoria (quantidade, estoque, ativos/inativos e valuation).",
)
async def summarize_products(repo=Depends(get_repo)):
    prods = await ListProductsService(repo).execute(category=None, active=None)

    total_products = len(prods)
    active_products = sum(1 for p in prods if getattr(p, "active", True))
    inactive_products = total_products - active_products
    total_stock = sum(int(p.stock or 0) for p in prods)
    total_valuation = float(sum((p.price or 0.0) * (p.stock or 0) for p in prods))

    cat_map: dict[Category, dict[str, float | int]] = defaultdict(
        lambda: {"count": 0, "stock": 0, "active": 0, "inactive": 0, "valuation": 0.0}
    )

    for p in prods:
        c = p.category
        cat_map[c]["count"] += 1
        cat_map[c]["stock"] += int(p.stock or 0)
        if getattr(p, "active", True):
            cat_map[c]["active"] += 1
        else:
            cat_map[c]["inactive"] += 1
        cat_map[c]["valuation"] += float((p.price or 0.0) * (p.stock or 0))

    by_category: dict[Category, CategoryBreakdown] = {
        c: CategoryBreakdown(
            count=int(v["count"]),
            stock=int(v["stock"]),
            active=int(v["active"]),
            inactive=int(v["inactive"]),
            valuation=float(v["valuation"]),
        )
        for c, v in cat_map.items()
    }

    return ProductsSummaryOut(
        total_products=total_products,
        active_products=active_products,
        inactive_products=inactive_products,
        total_stock=total_stock,
        total_valuation=total_valuation,
        by_category=by_category,
    )