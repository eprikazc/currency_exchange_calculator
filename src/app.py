from fastapi import FastAPI

from src.routers.currencies import router as currencies_router
from src.routers.prices import router as prices_routes

app = FastAPI()


app.include_router(currencies_router, prefix="/currencies", tags=["currencies"])
app.include_router(prices_routes, prefix="/prices", tags=["prices"])
