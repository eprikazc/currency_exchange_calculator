import os

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from src.routers.currencies import router as currencies_router
from src.routers.prices import router as prices_routes

app = FastAPI()


app.include_router(currencies_router, prefix="/currencies", tags=["currencies"])
app.include_router(prices_routes, prefix="/prices", tags=["prices"])


TORTOISE_ORM = {
    "connections": {"default": os.environ["DB_URL"]},
    "apps": {
        "models": {
            "models": ["src.models_tortoise", "aerich.models"],
            "default_connection": "default",
        },
    },
}


register_tortoise(
    app,
    config=TORTOISE_ORM,
    add_exception_handlers=True,
)
