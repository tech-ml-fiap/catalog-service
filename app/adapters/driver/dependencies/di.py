from functools import lru_cache
from app.adapters.driven.repositories.mongo_product_repository import MongoProductRepository
@lru_cache
def _singleton(): return MongoProductRepository()
def get_repo(): return _singleton()
