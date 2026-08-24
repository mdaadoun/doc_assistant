"""Application main entrypoint for Doc Assistant API."""

import uvicorn

from api.app import app, create_app

__all__ = ["app", "create_app"]

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000)
