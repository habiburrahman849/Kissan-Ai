# Kissan AI - Project Structure

## Directory Layout

```
kissan-ai/
├── .amazonq/rules/memory-bank/     # Amazon Q memory bank docs
├── backend/                        # Python FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/             # FastAPI route handlers
│   │   │   │   ├── chat.py         # POST /api/chat/message
│   │   │   │   ├── crops.py        # Crop cycle CRUD
│   │   │   │   ├── documents.py    # Document upload registry
│   │   │   │   ├── farmers.py      # Farmer profile CRUD
│   │   │   │   ├── health.py       # GET /health
│   │   │   │   └── weather.py      # Weather data endpoint
│   │   │   └── schemas/            # Pydantic request/response models
│   │   │       ├── chat.py
│   │   │       ├── crop.py
│   │   │       └── farmer.py
│   │   ├── core/
│   │   │   └── memory_agent.py     # Central orchestrator (dual-brain logic)
│   │   ├── db/
│   │   │   ├── models.py           # SQLAlchemy ORM models
│   │   │   └── session.py          # DB engine + session factory
│   │   ├── llm/
│   │   │   └── qwen_client.py      # Qwen LLM client (OpenAI-compatible)
│   │   ├── memory/
│   │   │   ├── mem0_client.py      # Mem0 cloud memory facade
│   │   │   └── memory_extractor.py # Extract crop/date facts from chat
│   │   ├── rag/
│   │   │   └── retriever.py        # Document retrieval (seed impl)
│   │   ├── services/
│   │   │   └── weather_service.py  # OpenWeatherMap HTTP client
│   │   ├── utils/                  # Shared utilities (currently empty)
│   │   ├── config.py               # Pydantic Settings + lru_cache
│   │   └── main.py                 # FastAPI app factory + static files
│   ├── data/
│   │   ├── raw_pdfs/               # Pakistan agri PDFs (source documents)
│   │   ├── processed_docs/         # Post-processing output
│   │   └── vector_index/           # Vector embeddings store
│   ├── tests/
│   │   └── test_system_prompt.py
│   ├── .env.example
│   ├── kissan_ai.db                # SQLite database file
│   └── requirements.txt
├── chat.html                       # Frontend pages (served as static files)
├── weather.html
├── profile.html
├── settings.html
├── login.html
├── help.html
├── index.html
├── shared.css                      # Global stylesheet
└── shared.js                       # Shared JS utilities (auth, API calls)
```

## Core Components and Relationships

### Request Flow
```
Browser → FastAPI (main.py) → Route Handler → MemoryAgent (core)
                                                    ├── Mem0Client (memory search)
                                                    ├── Retriever (RAG docs)
                                                    ├── WeatherService (context)
                                                    └── QwenClient (LLM response)
                                                    └── MemoryExtractor (save facts)
```

### Data Layer
- SQLAlchemy ORM models in `db/models.py` (Farmer, CropCycle, Document)
- SQLite for local dev; URL-resolved via `config.py` for absolute paths
- Session dependency injected into routes via `db/session.py`

### Configuration
- Single `Settings` class in `config.py` using `pydantic-settings`
- All secrets via `.env` file; graceful fallback when keys are absent
- `get_settings()` cached with `@lru_cache`

### Frontend Integration
- FastAPI serves the frontend HTML files as `StaticFiles` from `backend/../`
- `shared.js` provides common auth state, API base URL, and fetch helpers used across all pages

## Architectural Patterns
- Feature-sliced backend: `api/`, `core/`, `db/`, `llm/`, `memory/`, `rag/`, `services/`
- Facade pattern: `mem0_client.py` and `retriever.py` are swappable production stubs
- Dependency injection: DB sessions and settings passed via FastAPI `Depends()`
- Graceful degradation: mock responses when external API keys are missing
