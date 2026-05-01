# 🔮 SmartLens — AI Wellness Dashboard

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.111+-green.svg)](https://fastapi.tiangolo.com/)
[![Redis 7](https://img.shields.io/badge/redis-7+-dc382d.svg)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker Compose](https://img.shields.io/badge/docker-compose-2496ED.svg)](https://docs.docker.com/compose/)

## 🚀 Quick Start

### Docker (Recommended)
```bash
git clone https://github.com/yourusername/smartlens.git
cd smartlens
cp .env.example .env
# Edit .env and add your OpenRouter API key from https://openrouter.ai/keys
docker compose up --build
```

Open **http://localhost** in your browser.

### Local Development
```bash
./setup.sh                    # One-time setup
redis-server &                # Terminal 1
./run.sh                       # Terminal 2 (backend)
brew services start nginx      # Terminal 3 (or skip if you have nginx running)
```

## ✨ Features

- 🍽️ **Food Analysis** - Upload images, get instant nutrition analysis (kcal, macros, ingredients)
- 🤖 **HK-Optimized AI** - 3 tested vision models working perfectly in Hong Kong
  - Meta Llama 4 Maverick (1.8s)
  - OpenAI GPT-4o Mini (1.8s)
  - Meta Llama 4 Scout (2.3s)
- 🔍 **Fake News Detection** - Classify headlines as real or misinformation
- 💤 **Sleep Analytics** - AI-powered sleep quality insights
- 👟 **Step Tracking** - Daily activity analysis with personalized recommendations
- 🔔 **Real-time Notifications** - Push alerts via Server-Sent Events (SSE)
- ⚡ **Redis Caching** - 6-hour cache for repeated analyses
- 🔐 **Rate Limiting** - Nginx protection against abuse

## 🏗️ Architecture

```
Browser → Nginx (Reverse Proxy) → FastAPI Backend → OpenRouter API
                ↓
           Redis Cache & Pub/Sub
```

- **Frontend**: Single-file HTML/CSS/JS (no build tools needed)
- **Backend**: FastAPI with async support
- **AI**: OpenRouter API (Llama, GPT-4o, Gemini, Qwen, etc.)
- **Cache**: Redis 7 with Pub/Sub
- **Proxy**: Nginx with rate limiting and SSL support

## 📂 Project Structure

```
smartlens/
├── docker-compose.yml          # Full stack orchestration
├── README.md                   # Setup and usage guide
├── ARCHITECTURE.md             # Technical deep-dive
├── CONTRIBUTING.md             # Contribution guidelines
├── LICENSE                     # MIT License
├── setup.sh                    # Initial setup script
├── run.sh                      # Local development runner
│
├── backend/                    # FastAPI application
│   ├── main.py                 # App entry point
│   ├── config.py               # Pydantic settings
│   ├── redis_client.py         # Redis pool & cache helpers
│   ├── openrouter_client.py    # OpenRouter API client
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend container
│   └── routers/                # API endpoint modules
│       ├── calories.py         # POST /api/calories/analyse
│       ├── news.py             # POST /api/news/analyse
│       ├── health.py           # POST /api/health/* endpoints
│       └── notifications.py    # GET /api/notifications/stream (SSE)
│
├── frontend/                   # HTML/CSS/JS UI
│   ├── SmartLens_HK_Final.html # 🔶 Main UI (HK-optimized)
│   ├── index.html              # Legacy Gemini-based UI
│   ├── script.py               # Model testing script
│   ├── script_1.py             # Nutrition test script
│   └── script_2.py             # HTML generation script
│
└── nginx/                      # Reverse proxy config
    ├── Dockerfile              # Nginx container
    └── nginx.conf              # Reverse proxy + SSL + rate limiting
```

## 🔌 API Endpoints

| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| `POST` | `/api/calories/analyse` | Analyse food image → nutrition | API Key |
| `POST` | `/api/news/analyse` | Classify headline as fake/real | API Key |
| `POST` | `/api/health/steps` | Get step count insight | API Key |
| `POST` | `/api/health/sleep` | Get sleep quality analysis | API Key |
| `GET` | `/api/notifications/stream` | SSE real-time notifications | None |
| `GET` | `/health` | Health check (pings Redis) | None |

### Example: Food Analysis
```bash
curl -X POST http://localhost/api/calories/analyse \
  -F "file=@pizza.jpg"
```

**Response:**
```json
{
  "meal_name": "🍕 Margherita Pizza",
  "kcal": 620,
  "carbs_g": 75,
  "protein_g": 22,
  "fat_g": 24,
  "fiber_g": 4,
  "sugar_g": 8,
  "ingredients": ["mozzarella", "tomato sauce", "dough", "basil"],
  "health_note": "High in refined carbs; moderate protein.",
  "portion_note": "2 medium slices (~300g)",
  "cached": false
}
```

## 🔑 Get an API Key

1. Visit [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign up with Google/GitHub
3. Copy your API key
4. Add to `.env`:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
   ```

Free tier includes:
- 10,000 requests/month
- Access to all models
- No credit card required initially

## 📊 Caching & Performance

All results are cached for fast repeat access:

| Type | TTL | Hit Speed |
|------|-----|-----------|
| Food image | 6 hours | ~100ms |
| News headline | 1 hour | ~100ms |
| Step insights | 10 min | ~100ms |
| Sleep analysis | 1 hour | ~100ms |

Cache miss with fallback models: < 3 seconds

## 🧪 Testing Vision Models

The project includes scripts to test vision models in your region:

```bash
cd frontend
python script.py      # Test all candidates
python script_1.py    # Detailed nutrition test
python script_2.py    # Generate optimized HTML
```

This ensures the models work reliably in Hong Kong (or your region).

## 📖 Documentation

- **[README.md](README.md)** - Setup instructions for Docker & local dev
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical deep-dive with diagrams
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute & development guide

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `502 Bad Gateway` | Check `OPENROUTER_API_KEY` in `.env` |
| `Redis connection error` | Wait 5s after `docker compose up` for Redis to start |
| Port 80 in use | Change to `"8080:80"` in `docker-compose.yml` |
| Blank UI | Hard refresh (Cmd+Shift+R) to clear cache |
| Rate limited | Wait 1 minute or use fallback model |

## 📈 Roadmap

- [ ] User authentication & profiles
- [ ] Dietary preference customization
- [ ] Integration with Apple Health / Google Fit
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Kubernetes deployment templates
- [ ] GitHub Actions CI/CD

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing procedures
- Pull request process

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- AI models via [OpenRouter](https://openrouter.ai/)
- Powered by Redis & Nginx
- Icons from Emoji & Unicode

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/smartlens/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/smartlens/discussions)
- **Twitter**: [@smartlens](https://twitter.com/smartlens)

---

**Made with 💜 for the AI Wellness community**

⭐ If you find this useful, please star the repository!
