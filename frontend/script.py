import httpx, json, base64, time
from pathlib import Path

KEY = "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"

data_url = "data:image/jpeg;base64," + base64.b64encode(
    Path("output/test_food.jpg").read_bytes()
).decode()

PROMPT = """You are a nutritionist AI. Analyse this food image.
Return ONLY raw JSON, no markdown:
{"meal_name":"emoji + dish","kcal":500,"carbs_g":60,"protein_g":30,"fat_g":20,"fiber_g":5,"sugar_g":8,"ingredients":["a","b","c"],"health_note":"one sentence","portion_note":"300g"}"""

# Test all vision-capable models that may work in HK region
candidates = [
    # Gemini variants
    "google/gemini-2.0-flash-lite-001",
    "google/gemini-flash-1.5",
    "google/gemini-flash-1.5-8b",
    "google/gemini-pro-vision",
    # Meta Llama vision (uses US infra, available globally via OR)
    "meta-llama/llama-4-scout",
    "meta-llama/llama-4-maverick",
    # Mistral vision
    "mistralai/pixtral-12b",
    "mistralai/pixtral-large-2411",
    # Qwen vision (Chinese model — good for HK)
    "qwen/qwen2.5-vl-72b-instruct",
    "qwen/qwen2.5-vl-7b-instruct",
    "qwen/qvq-72b-preview",
    # OpenAI
    "openai/gpt-4o-mini",
    "openai/gpt-4o",
]

print(f"Testing {len(candidates)} vision models for HK region...\n")
working = []

for model in candidates:
    try:
        with httpx.Client(timeout=20) as c:
            r = c.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://smartlens.app",
                    "X-Title": "SmartLens",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text", "text": "What food is this? 5 words max."},
                    ]}],
                    "temperature": 0.1,
                    "max_tokens": 20,
                }
            )
        d = r.json()
        if r.status_code == 200 and "choices" in d:
            err = d["choices"][0].get("error")
            raw = (d["choices"][0]["message"]["content"] or "").strip()
            if err:
                code = err.get("code","?")
                msg  = err.get("message","")[:55]
                print(f"  ⚠️  {model:<45} → choice error {code}: {msg}")
            elif raw:
                print(f"  ✅  {model:<45} → '{raw[:40]}'")
                working.append(model)
            else:
                print(f"  ⚠️  {model:<45} → empty response")
        else:
            err = d.get("error",{}).get("message","")[:65]
            print(f"  ❌  {model:<45} → {r.status_code}: {err}")
    except Exception as ex:
        print(f"  💥  {model:<45} → {str(ex)[:55]}")
    time.sleep(0.4)

print(f"\n✅ Working in your region: {len(working)}")
for m in working:
    print(f"   {m}")
