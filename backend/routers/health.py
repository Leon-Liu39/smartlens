"""POST /health/steps and /health/sleep — AI wellness insights and watch data."""
import json
from datetime          import date, datetime
from typing            import Literal

from fastapi           import APIRouter, HTTPException
from pydantic          import BaseModel, Field, field_validator
from redis_client      import cache_get, cache_set, publish
from openrouter_client import text_analyse

router = APIRouter(prefix="/health", tags=["Health"])
WATCH_CHANNEL = "smartlens:notifications"

STEP_SYS = """You are a fitness coach AI. Given step-count data,
respond ONLY with JSON: {"insight": "<2 sentences>", "tip": "<action tip>", "badge": "<emoji + label>"}"""

SLEEP_SYS = """You are a sleep science expert. Given sleep data,
respond ONLY with JSON: {"insight": "<2 sentences>", "tip": "<1 actionable tip>", "quality": "poor|fair|good|excellent"}"""

class StepsRequest(BaseModel):
    steps:          int
    goal:           int = 10000
    active_minutes: int = 0

class SleepRequest(BaseModel):
    duration_hours: float
    deep_hours:     float = 0
    rem_hours:      float = 0
    score:          int   = 0

class WatchSteps(BaseModel):
    steps:          int = Field(..., ge=0, description="Daily step count from the watch")
    goal:           int = Field(10000, gt=0, description="Daily step goal")
    active_minutes: int = Field(0, ge=0, description="Active minutes recorded by the watch")
    distance_km:    float = Field(0, ge=0, description="Estimated walking/running distance")

class WatchSleep(BaseModel):
    duration_hours: float = Field(..., ge=0, le=24, description="Total sleep duration")
    deep_hours:     float = Field(0, ge=0, le=24, description="Deep sleep duration")
    rem_hours:      float = Field(0, ge=0, le=24, description="REM sleep duration")
    score:          int   = Field(0, ge=0, le=100, description="Watch sleep score")

class WatchReading(BaseModel):
    source:      str = Field("Demo Smartwatch", min_length=1)
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    day:         date = Field(default_factory=date.today)
    steps:       WatchSteps
    sleep:       WatchSleep
    mode:        Literal["demo", "imported"] = "imported"

    @field_validator("captured_at", mode="before")
    @classmethod
    def parse_captured_at(cls, value):
        if isinstance(value, str) and value.endswith("Z"):
            return value.replace("Z", "+00:00")
        return value

def _risk_flags(reading: WatchReading) -> list[dict]:
    flags = []
    step_ratio = reading.steps.steps / reading.steps.goal
    if step_ratio < 0.4:
        flags.append({
            "level": "notice",
            "message": "Step count is far below today's goal. Consider a short walk if you feel well.",
        })
    if reading.sleep.duration_hours < 6:
        flags.append({
            "level": "warning",
            "message": "Sleep duration is low. Prioritise rest and avoid intense exercise today.",
        })
    if reading.sleep.score and reading.sleep.score < 60:
        flags.append({
            "level": "notice",
            "message": "Watch sleep score is below the healthy range. Keep caffeine and screens low tonight.",
        })
    return flags

def _demo_watch_reading() -> WatchReading:
    """Local demo connector until real Apple Health/Fitbit OAuth is wired in."""
    today = date.today()
    seed = int(today.strftime("%j"))
    steps = 6200 + (seed % 5) * 740
    active_minutes = 32 + (seed % 4) * 7
    sleep_duration = round(6.4 + (seed % 3) * 0.35, 1)
    deep = round(1.1 + (seed % 2) * 0.2, 1)
    rem = round(1.4 + (seed % 3) * 0.15, 1)
    score = min(92, int(68 + (sleep_duration - 6) * 7 + deep * 4))
    return WatchReading(
        source="Demo Smartwatch",
        day=today,
        steps=WatchSteps(
            steps=steps,
            goal=10000,
            active_minutes=active_minutes,
            distance_km=round(steps * 0.00072, 2),
        ),
        sleep=WatchSleep(
            duration_hours=sleep_duration,
            deep_hours=deep,
            rem_hours=rem,
            score=score,
        ),
        mode="demo",
    )

def _reading_response(reading: WatchReading) -> dict:
    data = reading.model_dump(mode="json")
    data["risk_flags"] = _risk_flags(reading)
    return data

@router.post("/steps")
async def steps_insight(req: StepsRequest):
    key = f"smartlens:steps:{req.steps}:{req.goal}"
    cached = await cache_get(key)
    if cached:
        return cached
    try:
        raw = await text_analyse(STEP_SYS,
            f"Steps: {req.steps}/{req.goal}, Active minutes: {req.active_minutes}")
        result = json.loads(raw.replace("```json","").replace("```","").strip())
    except Exception as e:
        raise HTTPException(502, str(e))
    await cache_set(key, result, 600)
    return result

@router.post("/sleep")
async def sleep_insight(req: SleepRequest):
    key = f"smartlens:sleep:{req.duration_hours}:{req.score}"
    cached = await cache_get(key)
    if cached:
        return cached
    try:
        raw = await text_analyse(SLEEP_SYS,
            f"Duration: {req.duration_hours}h, Deep: {req.deep_hours}h, "
            f"REM: {req.rem_hours}h, Score: {req.score}")
        result = json.loads(raw.replace("```json","").replace("```","").strip())
    except Exception as e:
        raise HTTPException(502, str(e))
    await cache_set(key, result, 3600)
    return result

@router.get("/watch/latest")
async def latest_watch_reading():
    """Read the latest available watch sample.

    In production this is the adapter boundary for Apple Health, Fitbit, Garmin,
    or Health Connect. The demo keeps the UI usable without external accounts.
    """
    key = f"smartlens:watch:latest:{date.today().isoformat()}"
    cached = await cache_get(key)
    if cached:
        return cached

    result = _reading_response(_demo_watch_reading())
    await cache_set(key, result, 600)
    return result

@router.post("/watch/import")
async def import_watch_reading(reading: WatchReading):
    """Accept normalized watch data exported from a wearable integration."""
    result = _reading_response(reading)
    await cache_set("smartlens:watch:last_import", result, 3600)
    if result["risk_flags"]:
        await publish(WATCH_CHANNEL, {
            "type": "health_watch_alert",
            "title": "Watch health check",
            "message": result["risk_flags"][0]["message"],
            "source": reading.source,
        })
    return result
