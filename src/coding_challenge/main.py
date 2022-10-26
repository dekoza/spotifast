from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from . import settings
from .endpoints import router

app = FastAPI(title="Example project - Artist updater")

app.include_router(router)

register_tortoise(
    app,
    db_url=settings.DATABASE_URL,
    modules={"models": ["coding_challenge.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
