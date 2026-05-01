"""POST /health/steps  and  /health/sleep — AI wellness insights."""
import json
from fastapi           import APIRouter, HTTPException
from pydantic          import BaseModel
from redis_client      import cache_get, cache_set, publish
from openrouter_client import text_analyse

router = APIRouter(prefix="/health", tags=["Health"])

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
