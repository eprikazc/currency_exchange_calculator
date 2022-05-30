import os

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from src.routers.pairs import router as pairs_router

app = FastAPI()


app.include_router(pairs_router, prefix="/pairs", tags=["pairs"])


TORTOISE_ORM = {
    "connections": {"default": os.environ["DB_URL"]},
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


register_tortoise(
    app,
    config=TORTOISE_ORM,
    add_exception_handlers=True,
)
