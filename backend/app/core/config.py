from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RAG API"

    # OpenAI Settings
    OPENAI_API_KEY: str | None = None

    # Anthropic Settings
    ANTHROPIC_API_KEY: str

    # VoyageAI Settings
    VOYAGE_API_KEY: str

    # Vector Store Settings
    VECTOR_STORE_PATH: str = "vector_store"

    # Chroma Settings
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 9000

    # Phoenix Settings
    PHOENIX_API_KEY: str

    class Config:
        env_file = "../.env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()