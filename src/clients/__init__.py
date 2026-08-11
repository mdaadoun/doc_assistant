"""Infrastructure adapters: OpenAI, Gemini, Cohere, Qdrant external API clients."""

from clients.base_embedding import BaseEmbeddingAdapter
from clients.embedding import EmbeddingClientAdapter
from clients.gemini_embedding import GeminiEmbeddingAdapter
from clients.mock_embedding import MockEmbeddingAdapter
from clients.openai_embedding import OpenAIEmbeddingAdapter

__all__ = [
    "BaseEmbeddingAdapter",
    "OpenAIEmbeddingAdapter",
    "GeminiEmbeddingAdapter",
    "MockEmbeddingAdapter",
    "EmbeddingClientAdapter",
]
