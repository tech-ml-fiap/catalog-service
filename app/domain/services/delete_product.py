from app.domain.ports.product_repository_port import ProductRepositoryPort


class DeleteProductService:
    def __init__(self, repo: ProductRepositoryPort):
        self._repo = repo

    async def execute(self, pid: str) -> None:
        prod = await self._repo.find_by_id(pid)
        if not prod or prod.stock <= 0:
            raise ValueError("Product not found or already inactive")
        await self._repo.delete(pid)
