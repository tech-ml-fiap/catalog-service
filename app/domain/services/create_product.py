from app.domain.entities.product import Product
from app.domain.ports.product_repository_port import ProductRepositoryPort


class CreateProductService:

    def __init__(self, repo: ProductRepositoryPort):
        self._repo = repo

    async def execute(self, product: Product) -> Product:
        if product.price < 0:
            raise ValueError("Price cannot be negative")
        return await self._repo.create(product)
