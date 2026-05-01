# ⚡ SmartLens Quick Reference Guide

**For developers jumping in to SmartLens**

---

## 🚀 30-Second Setup

### Docker (Recommended)
```bash
git clone https://github.com/yourusername/smartlens.git
cd smartlens
cp .env.example .env
# Add API key to .env
docker compose up --build
# Open http://localhost
```

### Local Development
```bash
git clone https://github.com/yourusername/smartlens.git
cd smartlens
./setup.sh                    # One-time
redis-server &                # Terminal 1
./run.sh                      # Terminal 2 (backend)
# Open http://localhost
```

---

## 📁 Where Are Things?

| What | Where |
|------|-------|
| Main API | `backend/main.py` |
| Frontend UI | `frontend/SmartLens_HK_Final.html` |
| Food Analysis | `backend/routers/calories.py` |
| News Detection | `backend/routers/news.py` |
| Health Insights | `backend/routers/health.py` |
| Notifications | `backend/routers/notifications.py` |
| Config/Settings | `backend/config.py` |
| Redis Cache | `backend/redis_client.py` |
| API Integration | `backend/openrouter_client.py` |
| Nginx Config | `nginx/nginx.conf` |
| Environment Template | `.env.example` |
| Compose Setup | `docker-compose.yml` |

---

## 🔧 Common Tasks

### Add a New API Endpoint
```python
# 1. Create backend/routers/newfeature.py
from fastapi import APIRouter
router = APIRouter(prefix="/api/newfeature", tags=["newfeature"])

@router.post("/endpoint")
async def my_endpoint(data: SomeModel):
    return {"result": "value"}

# 2. Include in backend/main.py
app.include_router(newfeature_router)
```

### Change Vision Model
```bash
# Edit .env
OPENROUTER_VISION_MODEL=openai/gpt-4o  # Change primary model
```

### Add Redis Caching
```python
# In your endpoint:
from redis_client import get_redis

@router.post("/endpoint")
async def my_endpoint(data: SomeModel):
    r = await get_redis()
    
    # Try cache first
    cached = await r.get(f"key:{data.id}")
    if cached:
        return json.loads(cached)
    
    # Compute result
    result = {...}
    
    # Store in cache (1 hour TTL)
    await r.setex(f"key:{data.id}", 3600, json.dumps(result))
    
    return result
```

### Update Frontend
```bash
# Edit frontend/SmartLens_HK_Final.html
# Make changes to HTML/CSS/JS
# Refresh browser with Cmd+Shift+R (clear cache)
# No rebuild needed!
```

### Run Backend Tests
```bash
cd backend
pytest tests/  # (Add tests as needed)
```

### Check Nginx Config
```bash
nginx -t  # Test syntax
nginx -s reload  # Reload without restart
```

### View Logs
```bash
# Docker
docker compose logs backend  # Backend logs
docker compose logs redis    # Redis logs

# Local
# Backend: stdout of uvicorn process
# Redis: stdout of redis-server
# Nginx: /opt/homebrew/var/log/nginx/
```

---

## 🐛 Debugging

### Backend Won't Start
```bash
# Check if port 8001 is in use
lsof -i :8001

# Check Redis is running
redis-cli ping  # Should return PONG

# Check API key
grep OPENROUTER_API_KEY .env  # Should not be empty
```

### Frontend Blank/Black
```bash
# Clear cache
# Cmd+Shift+R (Chrome/Firefox on macOS)
# Shift+Cmd+Delete (Safari)

# Check console for errors
# Open DevTools (F12 or Cmd+Option+I)
# Look for red errors in Console tab
```

### API Returns 502
```bash
# Backend is not running or crashed
# Check docker compose logs
docker compose logs backend

# Or check uvicorn stdout
```

### Rate Limited
```bash
# Wait 1 minute (rate limit TTL)
# Or edit nginx.conf to increase limits
# Change: limit_req_zone ... rate=30r/m;
```

---

## 📊 API Usage Examples

### Food Analysis
```javascript
// Frontend
const formData = new FormData();
formData.append('file', imageFile);
const res = await fetch('/api/calories/analyse', {
  method: 'POST',
  body: formData
});
const data = await res.json();
console.log(data.meal_name, data.kcal);
```

### News Classification
```javascript
const res = await fetch('/api/news/analyse', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ headline: "Breaking news..." })
});
const { fake_score, verdict } = await res.json();
```

### Real-time Notifications
```javascript
// Already in frontend, but for reference:
const es = new EventSource('/api/notifications/stream');
es.onmessage = (e) => {
  const { type, data } = JSON.parse(e.data);
  console.log(`Got notification: ${data.title}`);
};
```

---

## 🔑 Environment Variables

```env
# Required
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx

# Models (optional, have defaults)
OPENROUTER_VISION_MODEL=meta-llama/llama-4-maverick
OPENROUTER_FALLBACK_MODEL=openai/gpt-4o-mini
OPENROUTER_TEXT_MODEL=google/gemini-2.0-flash-001

# App (optional)
APP_NAME=SmartLens
DAILY_CALORIE_GOAL=2000
LOG_LEVEL=info
REDIS_URL=redis://localhost:6379
```

---

## 📚 Key Files to Know

### Core Backend
- **main.py** (100 lines) - FastAPI app, imports routers, sets up middleware
- **config.py** (30 lines) - Reads .env into Python settings
- **redis_client.py** (100 lines) - Redis connection pool + cache helpers
- **openrouter_client.py** (150 lines) - API calls with fallback + retry logic

### Routers (Each ~100 lines)
- **calories.py** - Image upload → nutrition analysis
- **news.py** - Text → fake news classification
- **health.py** - Steps/sleep → AI insights
- **notifications.py** - SSE stream with Redis pub/sub

### Frontend
- **SmartLens_HK_Final.html** (1155 lines) - Complete UI + JS logic

---

## 🎯 Development Workflow

### 1. Pick a Task
```
[] Fix bug in food analysis
[] Add sleep recommendations
[] Improve error messages
[] Add new AI model
```

### 2. Create a Branch
```bash
git checkout -b feature/amazing-feature
```

### 3. Make Changes
- Backend: Edit Python files
- Frontend: Edit HTML/CSS/JS
- Config: Update .env.example

### 4. Test Locally
```bash
./run.sh                    # Start backend
# Test in browser / curl
```

### 5. Commit & Push
```bash
git add .
git commit -m "[area] Description of change

- Specific change
- Another change
- Fixes #123"
git push origin feature/amazing-feature
```

### 6. Create Pull Request
- Clear description
- Reference issues
- Mention breaking changes

---

## ⚡ Performance Tuning

### Redis Cache Hit Rate
Monitor in logs. Target > 60%.
If low: increase TTL values

### Backend Response Time
Check logs. Target < 3s even with fallback.
If slow: check OpenRouter API status

### Nginx Rate Limits
Current: 30 req/min general, 10 req/min uploads
Edit `nginx/nginx.conf` to adjust

### Database Queries
Currently no database, uses Redis only.
Scales to millions of requests.

---

## 🔐 Security Checklist

- ✅ Never commit `.env` (in .gitignore)
- ✅ API keys in environment variables only
- ✅ Rate limiting enabled (Nginx)
- ✅ CORS headers configured
- ✅ Input validation on all endpoints
- ✅ Error messages don't leak sensitive info
- ⚠️ TODO: Add authentication for user profiles

---

## 📖 Learn More

- **[README.md](README.md)** - Setup & features
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical details & diagrams
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Dev guidelines
- **[FILE_TREE.txt](FILE_TREE.txt)** - Visual file structure

---

## 🆘 Getting Help

1. Check **Troubleshooting** section in README.md
2. Search existing **GitHub Issues**
3. Read **CONTRIBUTING.md** for dev setup help
4. Create a **GitHub Discussion** for questions
5. Check backend logs: `docker compose logs backend`

---

## 🚀 Deploy to Production

### Using Docker Compose
```bash
# Build and start
docker compose up --build -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

### Add HTTPS
```bash
# Certbot is ready in nginx/nginx.conf
# Uncomment SSL section and install certificates
sudo certbot certonly --standalone -d yourdomain.com
```

### Scale Backend
```yaml
# In docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3  # Run 3 instances
    # Load balancer (Nginx) will distribute requests
```

---

## 📊 Useful Commands

```bash
# Python
python -m venv .venv              # Create venv
source .venv/bin/activate         # Activate
pip install -r backend/requirements.txt  # Install deps

# Docker
docker compose up                 # Start
docker compose down               # Stop
docker compose logs -f            # Stream logs
docker compose ps                 # Status

# Redis
redis-cli PING                    # Test connection
redis-cli FLUSHALL                # Clear cache
redis-cli MONITOR                 # Watch all commands

# Nginx
nginx -t                          # Test config
nginx -s reload                   # Reload
nginx -s stop                     # Stop

# Git
git status                        # Check changes
git diff                          # See changes
git log --oneline -5              # Last 5 commits
```

---

## 💡 Quick Wins (Easy Contributions)

1. **Improve error messages** - Make them more user-friendly
2. **Add model comparison table** - Document pros/cons
3. **Create tutorial blog post** - Help new users
4. **Add dark mode toggle** - Let users choose
5. **Optimize image upload** - Reduce file size before upload
6. **Add unit tests** - Test individual functions
7. **Create API docs** - Auto-generate from code
8. **Add analytics** - Track popular foods/news

---

**Happy coding! 🎉**

Have questions? Check the documentation or create a GitHub Discussion.
Found a bug? Create an Issue with reproduction steps.
Have an idea? Create a Discussion to get feedback!
