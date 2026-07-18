# Kissan AI - Technology Stack

## Backend

### Language & Runtime
- Python 3.10+ (uses `str | None` union syntax)

### Framework
- FastAPI - async web framework, auto-generates OpenAPI docs at `/docs`
- Uvicorn - ASGI server (`uvicorn[standard]`)

### Database
- SQLAlchemy - ORM for model definitions and queries
- SQLite (local dev) - file: `backend/kissan_ai.db`
- Production swap: any SQLAlchemy-compatible DB via `DATABASE_URL` env var

### Configuration
- `pydantic-settings` - typed settings from `.env` file
- `functools.lru_cache` - singleton settings instance

### HTTP Client
- `httpx` - async HTTP client for external API calls (Mem0, OpenWeatherMap)

### LLM Integration
- Qwen (qwen-plus) via Alibaba DashScope - OpenAI-compatible API
- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Falls back to mock Urdu responses when `QWEN_API_KEY` is not set

### Memory
- Mem0 cloud API (`https://api.mem0.ai`) - semantic memory search and save
- Falls back to local SQLite memory when `MEM0_API_KEY` is not set

### File Handling
- `python-multipart` - multipart form data for document uploads

## Frontend

### Languages
- Vanilla HTML5, CSS3, JavaScript (ES6+)
- No build step, no framework - plain static files

### Pages
- `index.html`, `chat.html`, `weather.html`, `profile.html`, `settings.html`, `login.html`, `help.html`
- `shared.css` - global styles
- `shared.js` - shared auth state, API helpers, navigation utilities

### Serving
- FastAPI `StaticFiles` mounts the frontend directory at root
- No separate frontend server needed

## External Services

| Service | Purpose | Env Var | Fallback |
|---|---|---|---|
| Alibaba DashScope (Qwen) | LLM inference | `QWEN_API_KEY` | Mock Urdu response |
| Mem0 | Cloud memory | `MEM0_API_KEY` | Local SQLite memory |
| OpenWeatherMap | Weather data | `OPENWEATHER_API_KEY` | No weather context |
| Qdrant/Chroma (future) | Vector DB | `VECTOR_DB_URL` | Seed retriever |

## Development Commands

```powershell
# Setup
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Copy and fill in secrets
copy .env.example .env

# Run dev server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Access points
# App:      http://127.0.0.1:8000/chat.html
# API docs: http://127.0.0.1:8000/docs
```

## Key Dependencies (requirements.txt)
```
fastapi
uvicorn[standard]
pydantic-settings
sqlalchemy
python-multipart
httpx
```

## Data Files
- `backend/data/raw_pdfs/` - Pakistan agricultural PDFs (crop calendars, census, land stats)
- `backend/data/processed_docs/` - Chunked/processed document output
- `backend/data/vector_index/` - Persisted vector embeddings
