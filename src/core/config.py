"""Type-safe configuration via pydantic-settings BaseSettings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server
    environment: str = Field(default="development")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    log_level: str = Field(default="INFO")

    # LLM Provider
    openai_api_key: str = Field(default="")

    # Qdrant Vector Store
    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333)
    qdrant_collection: str = Field(default="helvetia_docs")

    # Retrieval
    default_top_k: int = Field(default=5)
    confidence_threshold: float = Field(default=0.35)
    default_chunk_size: int = Field(default=512)
    default_overlap_ratio: float = Field(default=0.10)

    # Model
    default_model: str = Field(default="gpt-4o-mini")
    embedding_model: str = Field(default="text-embedding-3-small")
    temperature: float = Field(default=0.0)
    max_tokens: int = Field(default=2048)

    # Cohere Reranker (fallback)
    cohere_api_key: str = Field(default="")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    """Singleton settings accessor."""
    return Settings()
