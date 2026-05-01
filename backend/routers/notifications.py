"""GET /notifications/stream — SSE stream backed by Redis pub/sub."""
import asyncio, json
from fastapi           import APIRouter
from fastapi.responses import StreamingResponse
from redis_client      import subscribe

router  = APIRouter(prefix="/notifications", tags=["Notifications"])
CHANNEL = "smartlens:notifications"

@router.get("/stream")
async def sse_stream():
    async def event_generator():
        # Heartbeat to keep connection alive through proxies
        yield "event: connected\ndata: {}\n\n"
        async for raw in subscribe(CHANNEL):
            try:
                payload = json.loads(raw)
                yield f"data: {json.dumps(payload)}\n\n"
            except Exception:
                continue
            await asyncio.sleep(0)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":  "no-cache",
            "X-Accel-Buffering": "no",
            "Connection":     "keep-alive",
        }
    )
