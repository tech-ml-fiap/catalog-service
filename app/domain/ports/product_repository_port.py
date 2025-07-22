from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.product import Product

class ProductRepositoryPort(ABC):
    @abstractmethod
    async def create(self, product: Product) -> Product:
        """Cria um novo product no repositório e retorna com ID populado."""
        pass

    @abstractmethod
    async def find_by_id(self, product_id: str) -> Optional[Product]:
        """Retorna um Product (ou None se não encontrado)."""
        pass

    @abstractmethod
    async def find_all(self, cat: str | None = None, active: bool | None = None) -> List[Product]:
        """Lista todos os products."""
        pass

    @abstractmethod
    async def update(self, product: Product) -> Product:
        """Atualiza um product existente."""
        pass

    @abstractmethod
    async def delete(self, product_id: str) -> None:
        """Remove o product pelo ID."""
        pass

    @abstractmethod
    async def reserve_stock(self, product_id: str, qty: int) -> None:
        """Remove o product pelo ID."""
        pass

