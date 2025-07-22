from dataclasses import dataclass
from typing import Optional
from app.shared.enums.category import Category

@dataclass(frozen=True, slots=True)
class Product:
    name: str
    description: str
    price: float
    category: Category
    stock: int = 0
    id: Optional[str] = None
