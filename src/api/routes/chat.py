"""POST /api/v1/chat endpoint with Server-Sent Events (SSE) streaming."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.dependencies import get_chat_service, verify_api_key
from api.services.chat_service import ChatService
from models.chat import ChatRequest

router = APIRouter(
    prefix="/api/v1",
    tags=["Chat"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "/chat",
    response_class=StreamingResponse,
    summary="Execute grounded chat prompt with SSE streaming response",
)
async def chat_endpoint(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    """Stream conversation answer deltas, metadata, and citations via SSE."""
    stream_gen = chat_service.stream_chat(request)
    return StreamingResponse(
        stream_gen,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
