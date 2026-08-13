"""Type-safe configuration loading via Pydantic BaseSettings."""

from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # Server settings
    environment: str = Field(default="development", description="Execution mode")
    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=8000, description="Server port")
    log_level: str = Field(default="INFO", description="Logger verbosity level")

    # API keys
    openai_api_key: str = Field(default="", description="OpenAI API key")
    cohere_api_key: str = Field(default="", description="Cohere API key")
    gemini_api_key: str = Field(default="", description="Gemini API key")

    # Qdrant Vector Store
    qdrant_host: str = Field(default="localhost", description="Qdrant host")
    qdrant_port: int = Field(default=6333, description="Qdrant gRPC/HTTP port")
    qdrant_collection: str = Field(
        default="helvetia_docs", description="Target collection name"
    )

    # Retrieval parameters
    default_top_k: int = Field(default=5, description="Default retrieval top k")
    confidence_threshold: float = Field(
        default=0.35, description="Min similarity score threshold"
    )
    default_chunk_size: int = Field(default=512, description="Token size per chunk")
    default_overlap_ratio: float = Field(
        default=0.10, description="Overlap ratio between adjacent chunks"
    )

    # Reranker parameters
    reranker_provider: str = Field(
        default="flashrank", description="Default reranker engine provider"
    )
    reranker_model: str = Field(
        default="ms-marco-MiniLM-L-6-v2", description="Cross-encoder model"
    )
    reranker_candidate_k: int = Field(
        default=30, description="Top candidate count passed to reranker"
    )
    reranker_top_k: int = Field(
        default=5, description="Top reranked count returned by adapter"
    )

    # LLM & Embedding models
    default_model: str = Field(
        default="gpt-4o-mini", description="Default generation LLM model"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small", description="Default embedding model"
    )
    temperature: float = Field(default=0.0, description="Sampling temperature")
    max_tokens: int = Field(default=2048, description="Max response token limit")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    def __init__(self, _env_file: str | None = None, **values: Any) -> None:
        """Initialize settings with optional env file override."""
        if _env_file is not None:
            values["_env_file"] = _env_file
        super().__init__(**values)

    def is_production(self) -> bool:
        """Return True if running in production environment."""
        return self.environment.lower() == "production"

    def is_openai_configured(self) -> bool:
        """Check if OpenAI API key is set."""
        return bool(self.openai_api_key and self.openai_api_key.strip())

    def is_cohere_configured(self) -> bool:
        """Check if Cohere API key is set."""
        return bool(self.cohere_api_key and self.cohere_api_key.strip())

    def is_gemini_configured(self) -> bool:
        """Check if Gemini API key is set."""
        return bool(self.gemini_api_key and self.gemini_api_key.strip())

    def get_api_key_status(self) -> dict[str, bool]:
        """Return validation map of required external API key credentials."""
        return {
            "openai": self.is_openai_configured(),
            "cohere": self.is_cohere_configured(),
            "gemini": self.is_gemini_configured(),
        }


@lru_cache
def get_settings() -> Settings:
    """Return cached singleton instance of Settings."""
    return Settings()


def clear_settings_cache() -> None:
    """Reset cached Settings singleton (useful for testing override cases)."""
    get_settings.cache_clear()
