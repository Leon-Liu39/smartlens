"""
OpenRouter API client — handles both text and vision requests.
Automatically retries with a fallback model on 4xx errors.
"""
import json, base64, httpx
from config import settings

OR_BASE    = "https://openrouter.ai/api/v1/chat/completions"
OR_HEADERS = {
    "Authorization": f"Bearer {settings.openrouter_api_key}",
    "HTTP-Referer":  "https://smartlens-dashboard.app",
    "X-Title":       "SmartLens Dashboard",
    "Content-Type":  "application/json",
}

async def _post(payload: dict, timeout: int = 45) -> dict:
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(OR_BASE, headers=OR_HEADERS, json=payload)
        if not r.is_success:
            err = r.json().get("error", {}).get("message", r.text)
            raise RuntimeError(f"OpenRouter {r.status_code}: {err}")
        return r.json()

def _extract_text(response: dict) -> str:
    return response["choices"][0]["message"]["content"].strip()

# ── Vision call (food photo → JSON) ──────────────────────────────────
async def vision_analyse(image_bytes: bytes, mime_type: str) -> dict:
    b64 = base64.b64encode(image_bytes).decode()
    data_url = f"data:{mime_type};base64,{b64}"

    prompt = """You are a professional nutritionist AI.
Analyse this food photo carefully.
Respond with ONLY a valid JSON object — no markdown fences, no extra text.

Required format:
{
  "meal_name": "dish name with 1 leading emoji",
  "kcal": <integer — total estimated calories>,
  "carbs_g": <integer>,
  "protein_g": <integer>,
  "fat_g": <integer>,
  "fiber_g": <integer>,
  "sugar_g": <integer>,
  "ingredients": ["up to 6 key ingredients"],
  "health_note": "one sentence nutritional quality assessment",
  "portion_note": "brief description of estimated portion size"
}
Base all estimates on portion sizes clearly visible in the photo."""

    body = {
        "model": settings.openrouter_vision_model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text",      "text": prompt},
            ]
        }],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 600,
    }

    try:
        resp = await _post(body)
    except RuntimeError:
        # Retry with fallback model
        body["model"] = settings.openrouter_fallback_model
        resp = await _post(body)

    raw = _extract_text(resp)
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)

# ── Text call (fake news / health insights) ───────────────────────────
async def text_analyse(system_prompt: str, user_prompt: str) -> str:
    body = {
        "model": settings.openrouter_text_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 300,
    }
    resp = await _post(body)
    return _extract_text(resp)
