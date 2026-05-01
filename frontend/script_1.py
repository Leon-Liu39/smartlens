# 6 models work in HK! Now do FULL nutrition test on all 6 to pick the best

PROMPT_FULL = """You are a nutritionist AI. Analyse this food image carefully.
Return ONLY raw JSON, no markdown, no explanation:
{"meal_name":"emoji + dish name","kcal":500,"carbs_g":60,"protein_g":30,"fat_g":20,"fiber_g":5,"sugar_g":8,"ingredients":["a","b","c","d","e"],"health_note":"one sentence","portion_note":"e.g. 300g"}"""

WORKING = [
    "meta-llama/llama-4-scout",
    "meta-llama/llama-4-maverick",
    "mistralai/pixtral-large-2411",
    "qwen/qwen2.5-vl-72b-instruct",
    "openai/gpt-4o-mini",
    "openai/gpt-4o",
]

results = []
print("Full nutrition test on all 6 working models...\n")

for model in WORKING:
    t0 = time.time()
    try:
        with httpx.Client(timeout=30) as c:
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
                        {"type": "text", "text": PROMPT_FULL},
                    ]}],
                    "temperature": 0.1,
                    "max_tokens": 1024,
                }
            )
        elapsed = round(time.time() - t0, 1)
        d = r.json()

        if r.status_code == 200 and "choices" in d:
            raw    = (d["choices"][0]["message"]["content"] or "").strip()
            finish = d["choices"][0].get("finish_reason","?")
            err    = d["choices"][0].get("error")
            if err or not raw or "{" not in raw:
                print(f"  ⚠️  {model:<42} → bad response  ({elapsed}s)")
                results.append({"model":model,"score":0,"time":elapsed})
                continue
            clean = raw.replace("```json","").replace("```","").strip()
            s = clean.find("{"); e = clean.rfind("}")+1
            meal  = json.loads(clean[s:e])
            kcal  = meal.get("kcal",0)
            prot  = meal.get("protein_g",0)
            carb  = meal.get("carbs_g",0)
            fat   = meal.get("fat_g",0)
            score = sum([kcal>0, prot>0, carb>0, fat>0,
                         bool(meal.get("fiber_g")), bool(meal.get("sugar_g")),
                         bool(meal.get("ingredients")), bool(meal.get("health_note")),
                         bool(meal.get("portion_note")), finish=="stop"])
            print(f"  ✅  {model:<42}  {kcal}kcal P:{prot}g C:{carb}g F:{fat}g  {elapsed}s  score:{score}/10")
            results.append({"model":model,"score":score,"time":elapsed,"meal":meal})
        else:
            err = d.get("error",{}).get("message","")[:60]
            print(f"  ❌  {model:<42} → {err}")
            results.append({"model":model,"score":0,"time":0})
    except Exception as ex:
        print(f"  💥  {model:<42} → {ex}")
        results.append({"model":model,"score":0,"time":0})
    time.sleep(0.5)

# Rank
print("\n\n── RANKING ──────────────────────────────────────────")
for r in sorted(results, key=lambda x: (-x["score"], x["time"])):
    print(f"  score {r['score']}/10  {r['time']}s  {r['model']}")
