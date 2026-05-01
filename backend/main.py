"""
SmartLens — FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi            import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config             import settings
from redis_client       import get_redis
from routers.calories      import router as cal_router
from routers.news          import router as news_router
from routers.health        import router as health_router
from routers.notifications import router as notif_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up Redis connection pool on startup
    await get_redis()
    print(f"[SmartLens] Redis connected | Model: {settings.openrouter_vision_model}")
    yield

app = FastAPI(
    title="SmartLens API",
    version="2.0.0",
    description="AI Wellness + Fake News detection backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Nginx is the public boundary; restrict if needed
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────
app.include_router(cal_router)
app.include_router(news_router)
app.include_router(health_router)
app.include_router(notif_router)

@app.get("/health", tags=["System"])
async def health_check():
    r = await get_redis()
    await r.ping()
    return {"status": "ok", "service": settings.app_name}
