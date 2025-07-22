from dataclasses import asdict
from typing import List, Optional

from bson.decimal128 import Decimal128
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from os import getenv
from app.domain.entities.product import Product
from app.domain.ports.product_repository_port import ProductRepositoryPort
from app.shared.exceptions.inventory import OutOfStockException

_cli = AsyncIOMotorClient(getenv("MONGO_URI"))
_col = _cli["catalog_db"]["products"]

class MongoProductRepository(ProductRepositoryPort):
    async def create(self, p: Product) -> Product:
        doc = asdict(p).copy()
        doc.pop("id", None)

        db_doc = doc | {"active": True}
        res = await _col.insert_one(db_doc)

        return Product(**doc, id=str(res.inserted_id))

    async def find_by_id(self, product_id: str) -> Optional[Product]:
        doc = await _col.find_one({"_id": ObjectId(product_id)})
        return self._doc_to_entity(doc) if doc else None

    async def find_all(
        self,
        cat: str | None = None,
        active: bool | None = None,
    ) -> List[Product]:
        query = {}
        if cat:
            query["category"] = cat
        if active is not None:
            query["active"] = active

        cursor = _col.find(query)
        return [self._doc_to_entity(d) async for d in cursor]

    async def update(self, p: Product) -> Product:
        if not p.id:
            raise ValueError("Product id required")
        data = asdict(p).copy()
        pid = data.pop("id")
        data.pop("active", None)
        await _col.update_one({"_id": ObjectId(pid)}, {"$set": data})
        return await self.find_by_id(pid)

    async def delete(self, pid: str) -> None:
        await _col.update_one(
            {"_id": ObjectId(pid)}, {"$set": {"active": False}}
        )

    async def reserve_stock(self, pid: str, qty: int) -> None:
        res = await _col.update_one(
            {"_id": ObjectId(pid), "active": True, "stock": {"$gte": qty}},
            {"$inc": {"stock": -qty}},
        )
        if res.modified_count == 0:
            raise OutOfStockException("Not enough stock or product inactive")

    @staticmethod
    def _doc_to_entity(d: dict) -> Product:
        d = d.copy()
        d["id"] = str(d.pop("_id"))
        d.pop("active", None)

        price = d.get("price")
        if isinstance(price, Decimal128):
            d["price"] = float(price.to_decimal())
        return Product(**d)