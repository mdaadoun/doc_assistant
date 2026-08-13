"""Grounded LLM generation service enforcing context-only grounding and zero temperature."""

import time
from collections.abc import AsyncGenerator, Sequence
from typing import Any

import structlog
from openai import AsyncOpenAI

from core.config import get_settings
from core.exceptions import ConfigurationError, GenerationError
from generation.finops import FinOpsCollector
from models.chat import FinOpsMetadata

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a precise corporate assistant for Helvetia Consulting.
Your task is to answer the user's question STRICTLY using the context blocks provided below.

STRICT RULES:
1. Base your answer ONLY on clear facts directly mentioned in the Context. Do NOT use outside knowledge or assumptions.
2. If the answer cannot be fully derived from the provided Context, state clearly: "I cannot answer this question based on the available documentation."
3. For EVERY factual claim in your response, append an inline citation referencing the source file and page using this exact format: [Doc: <file_name> | Page: <page_number>].
"""

NO_CONTEXT_REFUSAL = "I cannot answer this question based on the available documentation."


class GroundedGenerator:
    """Grounded LLM generation service for contextual question answering."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        client: AsyncOpenAI | None = None,
        finops_collector: FinOpsCollector | None = None,
    ) -> None:
        """Initialize GroundedGenerator with credentials or custom AsyncOpenAI client."""
        settings = get_settings()
        key = api_key if api_key is not None else settings.openai_api_key

        if client is not None:
            self.client = client
        elif key and key.strip():
            self.client = AsyncOpenAI(api_key=key.strip())
        else:
            raise ConfigurationError(
                "OpenAI API key is required for GroundedGenerator",
                code="CONFIG_ERROR",
                details={"provider": "openai"},
            )

        self.model = model or settings.default_model
        self.temperature = temperature if temperature is not None else settings.temperature
        self.finops_collector = finops_collector or FinOpsCollector(default_model=self.model)

    def _format_context(self, contexts: Sequence[dict[str, Any] | Any]) -> str:
        """Format context objects or dictionaries into structured prompt blocks."""
        blocks: list[str] = []
        for ctx in contexts:
            if isinstance(ctx, dict):
                file_name = str(ctx.get("file_name") or ctx.get("source_file") or "Unknown")
                page_number = ctx.get("page_number") if ctx.get("page_number") is not None else ctx.get("page", 1)
                text = str(ctx.get("text") or ctx.get("content") or ctx.get("excerpt") or "")
            else:
                file_name = str(getattr(ctx, "file_name", getattr(ctx, "source_file", "Unknown")))
                page_number = getattr(ctx, "page_number", getattr(ctx, "page", 1))
                text = str(getattr(ctx, "text", getattr(ctx, "content", getattr(ctx, "excerpt", ""))))

            block = (
                f"Source File: {file_name}\n"
                f"Page Number: {page_number}\n"
                f"Content: {text}\n"
                "---"
            )
            blocks.append(block)
        return "\n".join(blocks)

    async def generate_stream(
        self, query: str, contexts: Sequence[dict[str, Any] | Any]
    ) -> AsyncGenerator[str, None]:
        """Stream grounded LLM response tokens based strictly on provided context."""
        if not contexts:
            yield NO_CONTEXT_REFUSAL
            return

        context_str = self._format_context(contexts)
        prompt = f"CONTEXT INFORMATION:\n{context_str}\n\nUSER QUESTION: {query}"

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
        except Exception as err:
            logger.error("Grounded LLM streaming generation failed", error=str(err))
            raise GenerationError(
                f"LLM streaming generation failed: {err}",
                details={"query": query, "model": self.model},
            ) from err

    async def generate(
        self, query: str, contexts: Sequence[dict[str, Any] | Any]
    ) -> str:
        """Generate complete grounded response string non-streamingly."""
        tokens: list[str] = []
        async for token in self.generate_stream(query, contexts):
            tokens.append(token)
        return "".join(tokens)

    async def generate_with_finops(
        self, query: str, contexts: Sequence[dict[str, Any] | Any]
    ) -> tuple[str, FinOpsMetadata]:
        """Generate grounded response non-streamingly and collect FinOps telemetry."""
        start_time = time.perf_counter()
        if not contexts:
            elapsed = time.perf_counter() - start_time
            finops = self.finops_collector.collect(
                prompt_text="",
                completion_text="",
                execution_time_seconds=elapsed,
                model=self.model,
                prompt_tokens=0,
                completion_tokens=0,
            )
            return NO_CONTEXT_REFUSAL, finops

        context_str = self._format_context(contexts)
        prompt = f"CONTEXT INFORMATION:\n{context_str}\n\nUSER QUESTION: {query}"
        full_prompt = f"{SYSTEM_PROMPT}\n{prompt}"

        answer = await self.generate(query, contexts)
        elapsed = time.perf_counter() - start_time

        finops = self.finops_collector.collect(
            prompt_text=full_prompt,
            completion_text=answer,
            execution_time_seconds=elapsed,
            model=self.model,
        )
        return answer, finops

