from app.domain.ports.product_repository_port import ProductRepositoryPort

class ReserveStockService:
    def __init__(self, repo: ProductRepositoryPort):
        self._repo = repo

    async def execute(self, pid: str, qty: int) -> None:
        if qty <= 0:
            raise ValueError("qty must be positive")
        await self._repo.reserve_stock(pid, qty)
