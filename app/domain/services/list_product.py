from typing import List, Optional

from app.domain.entities.product import Product
from app.domain.ports.product_repository_port import ProductRepositoryPort


class ListProductsService:
    def __init__(self, repo: ProductRepositoryPort):
        self._repo = repo

    async def execute(
        self, *, active: bool | None = None, category: Optional[str] = None
    ) -> List[Product]:
        return await self._repo.find_all(cat=category, active=active)
