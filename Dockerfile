# Multi-stage non-root Dockerfile (<250 MB target)
FROM python:3.11-slim AS builder

WORKDIR /build
RUN pip install --no-cache-dir poetry==1.8.2
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

FROM python:3.11-slim AS runtime

RUN groupadd -g 10001 appgroup \
    && useradd -u 10001 -g appgroup -s /bin/false appuser

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src/ ./src/
COPY data/ ./data/

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
