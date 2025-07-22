from app.domain.entities.product import Product
from app.domain.ports.product_repository_port import ProductRepositoryPort


class GetProductService:
    def __init__(self, repo: ProductRepositoryPort):
        self._repo = repo

    async def execute(self, pid: str) -> Product:
        prod = await self._repo.find_by_id(pid)
        if not prod:
            raise ValueError("Product not found")
        return prod
