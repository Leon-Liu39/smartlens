# All 6 score 10/10! 
# Best by speed: llama-4-maverick (1.8s) & gpt-4o-mini (1.8s)
# Since user wanted Gemini-style fast model, use:
#   Primary   : meta-llama/llama-4-maverick  (fastest, 10/10, free-tier eligible)
#   Fallback 1: openai/gpt-4o-mini           (1.8s, 10/10, cheapest OpenAI)
#   Fallback 2: meta-llama/llama-4-scout     (2.3s, 10/10)

# Now rebuild the HTML with these 3 models
content = Path('output/SmartLens_Final_Gemini.html').read_text(encoding='utf-8')

OLD_MODELS = '''  const MODELS = [
    "google/gemini-2.0-flash-001",  // ✅ Gemini 2.0 Flash via OpenRouter
  ];'''

NEW_MODELS = '''  // All 3 tested & confirmed working in HK region (scored 10/10)
  const MODELS = [
    "meta-llama/llama-4-maverick",   // 🏆 Primary  — 1.8s, 10/10, HK ✅
    "openai/gpt-4o-mini",            // ✅ Fallback1 — 1.8s, 10/10, HK ✅
    "meta-llama/llama-4-scout",      // ✅ Fallback2 — 2.3s, 10/10, HK ✅
  ];'''

content = content.replace(OLD_MODELS, NEW_MODELS)

# Update scan message
OLD_SCAN = '        $("scanMsg").textContent = "Asking Gemini 2.0 Flash…";'
NEW_SCAN = '''        const modelLabel = {
          "meta-llama/llama-4-maverick" : "Llama 4 Maverick",
          "openai/gpt-4o-mini"          : "GPT-4o Mini",
          "meta-llama/llama-4-scout"    : "Llama 4 Scout",
        }[model] || model;
        $("scanMsg").textContent = `Asking ${modelLabel}…`;'''
content = content.replace(OLD_SCAN, NEW_SCAN)

# Update error message
OLD_ERR = '"Gemini 2.0 Flash rate limit hit. Please wait 1 minute and try again."'
NEW_ERR = '"All models rate-limited. Please wait 1 minute and try again."'
content = content.replace(OLD_ERR, NEW_ERR)

# Final checks
checks = [
    ("New key present",              KEY in content),
    ("No gemini model",              "gemini" not in content),
    ("llama-4-maverick primary",     "llama-4-maverick" in content),
    ("gpt-4o-mini fallback",         "gpt-4o-mini" in content),
    ("llama-4-scout fallback",       "llama-4-scout" in content),
    ("model label map",              "modelLabel" in content),
    ("max_tokens present",           "max_tokens" in content),
    ("Robust JSON parse",            "lastIndexOf" in content),
    ("calError div",                 'id="calError"' in content),
    ("analyseBtn",                   'id="analyseBtn"' in content),
    ("Phone UI",                     'class="phone"' in content),
    ("Notifications",                "const Notifications" in content),
    ("Steps module",                 "const Steps" in content),
    ("FakeNews module",              "const FakeNews" in content),
]

all_ok = True
for name, ok in checks:
    print(f"  {'✅' if ok else '❌'}  {name}")
    if not ok: all_ok = False

print(f"\n{'✅ ALL GOOD' if all_ok else '❌ ISSUES'}  |  {len(content)//1024} KB")

out = Path('output/SmartLens_HK_Final.html')
out.write_text(content, encoding='utf-8')
print(f"Saved → {out.name}")
