from dataclasses import replace
from app.domain.entities.product import Product
from app.domain.ports.product_repository_port import ProductRepositoryPort


class UpdateProductService:
    def __init__(self, repo: ProductRepositoryPort):
        self._repo = repo

    async def execute(self, pid: str, changes: dict) -> Product:
        current = await self._repo.find_by_id(pid)
        if not current:
            raise ValueError("Product not found")

        if (price := changes.get("price")) is not None and price < 0:
            raise ValueError("Price cannot be negative")

        clean = {k: v for k, v in changes.items() if v is not None}

        updated = replace(current, **clean)
        return await self._repo.update(updated)