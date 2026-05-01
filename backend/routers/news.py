"""POST /news/analyse — Fake-news classifier via OpenRouter text model."""
import hashlib, json
from fastapi          import APIRouter, HTTPException
from pydantic         import BaseModel
from redis_client     import cache_get, cache_set, publish
from openrouter_client import text_analyse

router   = APIRouter(prefix="/news", tags=["FakeNews"])
CACHE_TTL = 3600   # 1 h

SYSTEM = """You are an expert fact-checker and misinformation analyst.
Given a news headline and its source, evaluate how likely it is to be
fake or misleading. Respond ONLY with valid JSON — no markdown, no prose:
{
  "headline":   "<original headline>",
  "source":     "<source>",
  "confidence": <integer 0-100 — probability it is FAKE>,
  "verdict":    "fake" | "real" | "uncertain",
  "reasoning":  "<one concise sentence explaining your verdict>"
}"""

class NewsRequest(BaseModel):
    headline: str
    source:   str = "unknown"

@router.post("/analyse")
async def analyse_news(req: NewsRequest):
    key = f"smartlens:news:{hashlib.md5((req.headline+req.source).encode()).hexdigest()}"

    cached = await cache_get(key)
    if cached:
        return cached

    try:
        raw = await text_analyse(SYSTEM, f"Headline: {req.headline}\nSource: {req.source}")
        result = json.loads(raw.replace("```json","").replace("```","").strip())
    except Exception as e:
        raise HTTPException(502, f"AI error: {e}")

    await cache_set(key, result, CACHE_TTL)

    if result.get("verdict") == "fake":
        await publish("smartlens:notifications", {
            "type": "notification",
            "data": {
                "icon":     "🔍",
                "app":      "FakeGuard",
                "title":    "⚠️ Misinformation Detected",
                "message":  req.headline[:60],
                "tag":      "fake-news",
                "tag_text": f"{result.get('confidence',0)}% Fake",
                "bg_color": "rgba(251,113,133,.15)",
            }
        })

    return result
