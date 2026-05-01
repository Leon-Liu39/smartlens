# 🔮 SmartLens — Full Stack AI Wellness Dashboard

AI-powered health & misinformation detection platform with real-time food calorie analysis.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla HTML/CSS/JS (single file, no build step) |
| Backend  | FastAPI (Python 3.11) |
| AI       | OpenRouter → Meta Llama 4 / GPT-4o / Qwen (HK-optimized) |
| Cache    | Redis 7 |
| Proxy    | Nginx 1.25 |
| Containers | Docker Compose |

---

## Quick Start (Docker)

### 1. Clone / unzip and enter folder
```bash
cd smartlens_bundle
```

### 2. Set your OpenRouter API key
```bash
cp .env.example .env
# Open .env in any editor and set:
# OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
```
Get a free key at https://openrouter.ai/keys

### 3. Build and run with Docker
```bash
docker compose up --build
```

Open **http://localhost** in your browser. The dashboard loads immediately.

---

## Quick Start (Local Development - No Docker)

### Prerequisites
- Python 3.11+
- Redis (install via `brew install redis` on macOS)
- Nginx (install via `brew install nginx` on macOS)

### 1. Set up environment
```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

### 2. Create virtual environment and install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 3. Start Redis (in a new terminal)
```bash
redis-server
```

### 4. Start FastAPI backend (in a new terminal)
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 5. Configure and start Nginx
```bash
# Create nginx config (see nginx section in this README)
# Then start nginx
nginx -g "daemon off;"
```

### 6. Access the dashboard
Open **http://localhost** in your browser.

---

## Architecture

```
Browser  ──── HTTP ────►  Nginx :80
                             │
              ┌──────────────┼──────────────────┐
              │ /            │ /api/*            │ /api/notifications/stream
              ▼              ▼                   ▼
         Static HTML    FastAPI :8000       SSE stream
         (frontend/)         │            (Redis pub/sub)
                             │
                    ┌────────┴─────────┐
                    │                  │
               OpenRouter          Redis :6379
            (Vision / Text)        (Cache + PubSub)
```

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/api/calories/analyse` | Upload food photo → kcal + macros |
| `POST` | `/api/news/analyse` | Classify headline as fake/real |
| `POST` | `/api/health/steps` | AI step count insight |
| `POST` | `/api/health/sleep` | AI sleep quality report |
| `GET`  | `/api/notifications/stream` | SSE real-time push stream |
| `GET`  | `/health` | Health check |

### Calorie Endpoint Example
```bash
curl -X POST http://localhost/api/calories/analyse \
  -F "file=@pizza.jpg"
```
```json
{
  "meal_name": "🍕 Margherita Pizza",
  "kcal": 620,
  "carbs_g": 75,
  "protein_g": 22,
  "fat_g": 24,
  "fiber_g": 4,
  "sugar_g": 8,
  "ingredients": ["mozzarella","tomato sauce","pizza dough","basil","olive oil"],
  "health_note": "High in refined carbs; moderate protein from cheese.",
  "portion_note": "2 medium slices (~300g)",
  "cached": false
}
```

---

## Redis Cache Keys

| Key | TTL |
|-----|-----|
| `smartlens:calories:<md5>` | 6 hours |
| `smartlens:news:<md5>` | 1 hour |
| `smartlens:steps:<n>:<goal>` | 10 minutes |
| `smartlens:sleep:<h>:<score>` | 1 hour |

---

## Folder Structure

```
smartlens_bundle/
├── docker-compose.yml       ← orchestrates all 3 services
├── .env.example             ← copy to .env and set API key
├── README.md
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf           ← reverse proxy + rate limiting + SSE config
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py              ← FastAPI app
│   ├── config.py            ← pydantic settings (reads .env)
│   ├── redis_client.py      ← async pool, cache helpers, pub/sub
│   ├── openrouter_client.py ← vision + text API calls
│   └── routers/
│       ├── calories.py      ← POST /calories/analyse
│       ├── news.py          ← POST /news/analyse
│       ├── health.py        ← POST /health/steps + /sleep
│       └── notifications.py ← GET /notifications/stream (SSE)
└── frontend/
    ├── SmartLens_HK_Final.html  ← HK-optimized UI with Llama 4 / GPT-4o / Qwen
    ├── index.html               ← Original Gemini-based UI (legacy)
    ├── script.py                ← Model testing script for HK region
    ├── script_1.py              ← Full nutrition test on working models
    └── script_2.py              ← HTML generation script
```

---

## Vision Models (HK-Optimized)

The **SmartLens_HK_Final.html** frontend uses three tested vision models optimized for the Hong Kong region:

| Model | Speed | Score | Status |
|-------|-------|-------|--------|
| `meta-llama/llama-4-maverick` | 🟢 1.8s | 10/10 | ✅ Primary |
| `openai/gpt-4o-mini` | 🟢 1.8s | 10/10 | ✅ Fallback 1 |
| `meta-llama/llama-4-scout` | 🟡 2.3s | 10/10 | ✅ Fallback 2 |

All models tested with comprehensive nutrition analysis and confirmed working in HK region with high accuracy.

The frontend automatically falls back to the next model if the primary is rate-limited.

---

| Problem | Fix |
|---------|-----|
| `502 Bad Gateway` | Check `OPENROUTER_API_KEY` in `.env` |
| `Redis connection error` | Wait 5 s after `docker compose up` for Redis to initialise |
| Blank UI | Open http://localhost (not a local file path) |
| Port 80 in use | Change `"80:80"` to `"8080:80"` in docker-compose.yml then visit http://localhost:8080 |

---

## Extending

- **Add a new AI agent**: Create `backend/routers/newfeature.py`, include in `main.py`
- **Change the vision model**: Edit `OPENROUTER_VISION_MODEL` in `.env`
- **Add HTTPS**: Add a Certbot service to `docker-compose.yml` and update `nginx.conf`
- **Scale backend**: Increase `replicas` in docker-compose.yml — Redis pub/sub ensures all instances share the notification stream
