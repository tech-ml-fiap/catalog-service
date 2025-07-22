from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.adapters.driver.controllers.product_router import router
from app.db_init import ensure_indexes

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_indexes()
    yield

app = FastAPI(title="Catalog Service", lifespan=lifespan)
app.include_router(router)