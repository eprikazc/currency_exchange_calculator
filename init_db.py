from tortoise import Tortoise

from src.app import TORTOISE_ORM


async def init_db():
    await Tortoise.init(TORTOISE_ORM)
