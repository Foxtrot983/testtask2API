from fastapi import FastAPI
from contextlib import asynccontextmanager

from .components.routes import router
from .components.crud import check_and_prepare_db
from .components.database import Base
from .components.scheduler import scheduler

@asynccontextmanager
async def check_add_items(app: FastAPI):
    check_and_prepare_db()
    scheduler.start()
    yield
    pass

app = FastAPI(lifespan=check_add_items)
app.include_router(router)