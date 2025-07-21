from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from pydantic_settings import BaseSettings

from .models import LegislationDocument, LegislationFragment

class MongoDBConfig(BaseSettings):
    MONGODB_URL: str = "mongodb://admin:password123@localhost:27117"
    MONGODB_DB_NAME: str = "legislation_db"

    class Config:
        env_file = ".env"

async def init_mongodb():
    config = MongoDBConfig()

    # Create Motor client
    client = AsyncIOMotorClient(config.MONGODB_URL)
    db = client[config.MONGODB_DB_NAME]

    # Initialize beanie with the MongoDB client
    await init_beanie(
        database=db,
        document_models=[
            LegislationDocument,
            LegislationFragment
        ],
        allow_index_dropping=True
    )

    return client

async def close_mongodb_connection(client: AsyncIOMotorClient):
    client.close()