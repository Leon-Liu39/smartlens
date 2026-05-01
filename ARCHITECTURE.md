# SmartLens Architecture & Design

## System Overview

SmartLens is a full-stack AI wellness dashboard that combines:
- **Real-time food analysis** using vision AI models
- **Fake news detection** using language models
- **Health insights** with personalized recommendations
- **Push notifications** via Server-Sent Events (SSE)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                         │
│              (SmartLens_HK_Final.html)                      │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/HTTPS
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                    │
│              Port 80 (or 8080 if local dev)                │
│                  ├── / → Static Files                      │
│                  ├── /api/* → Backend :8001                │
│                  └── /api/notifications/stream → SSE       │
└────────────────────┬────────────────────────────────────────┘
                     │ TCP
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                FastAPI Backend (main.py)                    │
│                    Port 8001                               │
│     ┌─────────────────────────────────────────────┐        │
│     │  /api/calories/analyse     (POST)          │        │
│     │  /api/news/analyse         (POST)          │        │
│     │  /api/health/steps         (POST)          │        │
│     │  /api/health/sleep         (POST)          │        │
│     │  /api/notifications/stream (GET, SSE)      │        │
│     │  /health                   (GET)           │        │
│     └─────────────────────────────────────────────┘        │
│                      │                                      │
│         ┌────────────┴────────────────┐                    │
│         ▼                             ▼                     │
│   OpenRouter API              Redis (Cache & PubSub)       │
│   (Vision + Text models)      Port 6379                    │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (HTML/CSS/JS)

**File**: `frontend/SmartLens_HK_Final.html`

**Features**:
- Single-file, no build process required
- Responsive dashboard layout
- Real-time SSE notifications
- Image upload for food analysis
- Cache management for offline viewing

**Vision Models** (with fallbacks):
1. Meta Llama 4 Maverick (1.8s, primary)
2. OpenAI GPT-4o Mini (1.8s, fallback 1)
3. Meta Llama 4 Scout (2.3s, fallback 2)

All tested and optimized for Hong Kong region.

### Backend (FastAPI)

**File**: `backend/main.py`

**Routers**:

#### 1. Calories Router (`routers/calories.py`)
- **POST** `/api/calories/analyse`
- Accepts image upload
- Returns: meal name, kcal, macros (carbs/protein/fat/fiber/sugar)
- Caches results for 6 hours
- Fallback models if primary rate-limited

#### 2. News Router (`routers/news.py`)
- **POST** `/api/news/analyse`
- Text input: headline to check
- Returns: fake/real classification with confidence
- Uses text model from config
- Cache: 1 hour TTL

#### 3. Health Router (`routers/health.py`)
- **POST** `/api/health/steps`
  - Input: daily steps count
  - Returns: personalized insight
  - Cache: 10 minutes
  
- **POST** `/api/health/sleep`
  - Input: hours slept, quality score
  - Returns: sleep analysis with recommendations
  - Cache: 1 hour

#### 4. Notifications Router (`routers/notifications.py`)
- **GET** `/api/notifications/stream`
- Server-Sent Events (SSE) stream
- Real-time push notifications
- Redis Pub/Sub backend
- No caching (real-time only)

### Config & Settings

**File**: `backend/config.py`

Loads from `.env`:
- `OPENROUTER_API_KEY` - API authentication
- `OPENROUTER_VISION_MODEL` - Primary vision model
- `OPENROUTER_FALLBACK_MODEL` - Fallback vision model
- `OPENROUTER_TEXT_MODEL` - Text classification model
- `APP_NAME` - Application name (default: SmartLens)
- `DAILY_CALORIE_GOAL` - Daily target (default: 2000)
- `LOG_LEVEL` - Logging verbosity (default: info)

### Redis Client

**File**: `backend/redis_client.py`

**Responsibilities**:
- Connection pooling (async)
- Cache operations (get/set/delete)
- Pub/Sub for notifications
- Cache invalidation helpers

**Cache Strategy**:
```python
Key format: "smartlens:<type>:<hash>"
Examples:
  - smartlens:calories:a1b2c3d4  (TTL: 6h)
  - smartlens:news:x9y8z7w6      (TTL: 1h)
  - smartlens:steps:8000:2000    (TTL: 10m)
```

### OpenRouter Client

**File**: `backend/openrouter_client.py`

**Functions**:
- `analyse_food_image()` - Vision API for calorie analysis
- `classify_news()` - Text API for fake news detection
- `get_health_insight()` - Text API for personalized advice

**Error Handling**:
- Automatic retry with fallback models
- Rate limit handling (429 → sleep & retry)
- Timeout handling (30s)
- Graceful degradation

## Data Flow

### Food Image Analysis

```
1. User uploads image via frontend
2. Frontend shows "Analyzing..." spinner
3. POST /api/calories/analyse with FormData
4. Backend checks Redis cache by MD5(image)
5. If cached → return cached result (6h TTL)
6. If not cached:
   a. Try primary vision model
   b. Parse JSON response
   c. Validate nutrition fields
   d. Cache result in Redis
   e. Return to frontend
7. If rate limited → auto-retry with fallback model
```

### News Classification

```
1. User enters headline
2. POST /api/news/analyse with JSON
3. Backend checks Redis cache by MD5(text)
4. If cached → return cached result (1h TTL)
5. If not cached:
   a. Call OpenRouter text API
   b. Parse classification + confidence
   c. Cache result
   d. Return to frontend
```

### Notifications (SSE)

```
1. Frontend connects: EventSource("/api/notifications/stream")
2. Backend creates SSE connection
3. Subscribe to Redis pub/sub channel
4. When notification published:
   a. Format JSON: {type, data}
   b. Send to client via SSE
5. Frontend receives and displays notification
6. Auto-reconnect on disconnect (5s delay)
```

## Environment Variables

```env
# Required
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx

# Optional (with defaults)
OPENROUTER_VISION_MODEL=meta-llama/llama-4-maverick
OPENROUTER_FALLBACK_MODEL=openai/gpt-4o-mini
OPENROUTER_TEXT_MODEL=google/gemini-2.0-flash-001
APP_NAME=SmartLens
DAILY_CALORIE_GOAL=2000
LOG_LEVEL=info
REDIS_URL=redis://localhost:6379  (in production, can be overridden)
```

## Testing Vision Models

See `frontend/script.py`, `script_1.py`, `script_2.py` for:
- Model compatibility testing
- Performance benchmarking (latency)
- Accuracy scoring
- Regional availability verification

**Last tested**: April 30, 2026
**Region**: Hong Kong
**Result**: 6 models confirmed working (10/10 score)

## Caching Strategy

| Resource | TTL | Key Format | Invalidation |
|----------|-----|-----------|--------------|
| Food images | 6h | `smartlens:calories:<md5>` | Manual or TTL |
| News analysis | 1h | `smartlens:news:<md5>` | Manual or TTL |
| Step insights | 10m | `smartlens:steps:<count>:<goal>` | Manual or TTL |
| Sleep analysis | 1h | `smartlens:sleep:<hours>:<score>` | Manual or TTL |

**Rationale**:
- Food images: longest TTL (same meal doesn't change)
- News: medium TTL (stories evolve)
- Steps/Sleep: short TTL (daily changes)

## Rate Limiting (Nginx)

```
api_general: 30 req/minute per IP
api_upload: 10 req/minute per IP
max_connections: 3 per IP
```

Prevents abuse and ensures fair usage.

## Deployment Options

### Option 1: Docker (Recommended)
```bash
docker compose up --build
```
- All services in containers
- No local dependencies needed
- Production-ready networking

### Option 2: Local Development
```bash
./setup.sh        # One-time setup
redis-server &    # Terminal 1
./run.sh          # Terminal 2
nginx -g "daemon off;" # Terminal 3 (if using local nginx)
```
- Faster iteration
- Better debugging
- Requires local Redis/Nginx

### Option 3: Cloud Deployment
- Kubernetes YAML templates available in `k8s/` (future)
- Environment-specific configs for staging/production
- CI/CD integration via GitHub Actions

## Performance Metrics

**Target Response Times**:
- Food analysis: < 3s (with fallback)
- News classification: < 2s
- Health insights: < 1s
- SSE notification push: < 500ms

**Caching Impact**:
- Cache hit: < 100ms
- Cache miss: < 3s (with fallback)
- Hit rate: ~60% (estimated)

## Security

**Implemented**:
- API key stored in `.env` (never committed)
- HTTPS ready (Nginx SSL config available)
- CORS headers (frontend-only access)
- Input validation on all endpoints
- Rate limiting per IP
- Image upload validation (size, format)

**Future**:
- JWT authentication
- Database encryption
- DDoS protection
- Web Application Firewall (WAF)

## Monitoring & Logging

**Logs**:
- FastAPI logs: stdout/stderr
- Nginx logs: `/var/log/nginx/`
- Redis logs: stdout (if running foreground)

**Health Check**:
- GET `/health` → pings Redis, returns status

## Future Roadmap

- [ ] User authentication & profiles
- [ ] Dietary preference customization
- [ ] Integration with fitness trackers
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Kubernetes deployment
- [ ] Advanced analytics dashboard
- [ ] Social features (meal sharing)

---

For more details, see README.md and CONTRIBUTING.md
