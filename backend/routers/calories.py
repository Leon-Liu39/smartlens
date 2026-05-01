"""
POST /calories/analyse
  — Accepts a food photo, calls OpenRouter Vision, caches in Redis.
"""
import hashlib, io
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
from redis_client    import cache_get, cache_set, publish
from openrouter_client import vision_analyse

router = APIRouter(prefix="/calories", tags=["Calories"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/heic"}
MAX_BYTES     = 12 * 1024 * 1024   # 12 MB
CACHE_TTL     = 6 * 3600           # 6 hours

def _resize_if_needed(data: bytes, mime: str) -> tuple[bytes, str]:
    """Resize images >1 MP to keep API latency low; keep quality."""
    try:
        img = Image.open(io.BytesIO(data))
        w, h = img.size
        if w * h > 1_000_000:
            img.thumbnail((1024, 1024), Image.LANCZOS)
            buf = io.BytesIO()
            fmt = "JPEG" if "jpeg" in mime else "PNG"
            img.save(buf, format=fmt, quality=88)
            return buf.getvalue(), f"image/{fmt.lower()}"
    except Exception:
        pass
    return data, mime

@router.post("/analyse")
async def analyse_food(file: UploadFile = File(...)):
    # Validate
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}")

    raw = await file.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, "File too large (max 12 MB)")

    # Resize & cache key
    image_bytes, mime = _resize_if_needed(raw, file.content_type)
    digest = hashlib.md5(image_bytes).hexdigest()
    cache_key = f"smartlens:calories:{digest}"

    # Cache hit
    cached = await cache_get(cache_key)
    if cached:
        cached["cached"] = True
        return cached

    # Call OpenRouter Vision
    try:
        result = await vision_analyse(image_bytes, mime)
    except Exception as e:
        raise HTTPException(502, f"Vision API error: {e}")

    # Validate required fields
    required = ["meal_name", "kcal", "carbs_g", "protein_g", "fat_g"]
    for f in required:
        if f not in result:
            raise HTTPException(502, f"Incomplete AI response (missing {f})")

    result["cached"] = False

    # Store in Redis
    await cache_set(cache_key, result, CACHE_TTL)

    # Push notification to SSE channel
    await publish("smartlens:notifications", {
        "type": "notification",
        "data": {
            "icon":      "🍽️",
            "app":       "NutriAI",
            "title":     f"{result['meal_name']} analysed",
            "message":   f"{result['kcal']} kcal · P:{result.get('protein_g',0)}g "
                         f"C:{result.get('carbs_g',0)}g F:{result.get('fat_g',0)}g",
            "tag":       "calories",
            "tag_text":  f"+{result['kcal']} kcal",
            "bg_color":  "rgba(251,191,36,.15)",
        }
    })

    return result
