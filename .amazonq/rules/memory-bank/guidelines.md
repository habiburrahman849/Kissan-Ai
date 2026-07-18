# Kissan AI - Development Guidelines

## Code Quality Standards

### Python Style
- Use `from __future__ import annotations` at the top of files that use modern type hints
- Use `str | None` union syntax (Python 3.10+), not `Optional[str]`
- Use `list[dict]` and `dict[str, list]` lowercase generics, not `List[Dict]`
- Keep imports grouped: stdlib → third-party → local (`app.*`)
- No inline comments; let code be self-explanatory through naming

### JavaScript Style
- Mix of `var` (legacy IIFE blocks) and `const`/`let` (modern async functions) — prefer `const`/`let` for new code
- Section headers as `// ===== SECTION NAME =====` comments to organize large files
- IIFEs `(function() { ... })()` for encapsulating stateful UI modules (drag, swipe)
- `async/await` with `try/catch` for all API calls; never use raw `.then()` chains

---

## Structural Conventions

### Backend Architecture
- Feature-sliced layout: `api/routes/`, `api/schemas/`, `core/`, `db/`, `llm/`, `memory/`, `rag/`, `services/`
- Each route file owns one resource (farmers, crops, chat, weather, documents, health)
- Pydantic schemas in `api/schemas/` separate from ORM models in `db/models.py`
- All external service clients are classes instantiated with `get_settings()` in `__init__`

### FastAPI Patterns
```python
# App factory in main.py — routers registered with /api prefix
app.include_router(chat.router, prefix="/api")

# Startup hook for DB init
@app.on_event("startup")
def on_startup() -> None:
    init_db()

# Catch-all page serving with path traversal protection
@app.get("/{page_name:path}")
def serve_page(page_name: str):
    requested = (frontend_path / page_name).resolve()
    if frontend_path in requested.parents and requested.is_file():
        return FileResponse(requested)
```

### SQLAlchemy ORM Patterns
```python
# All models inherit from Base (imported from app.db.session)
class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)  # no timezone

# Relationships declared bidirectionally
crop_cycles = relationship("CropCycle", back_populates="farmer")
farmer = relationship("Farmer", back_populates="crop_cycles")

# Nullable columns declared explicitly
district = Column(String(120), nullable=True)
```

### Settings Pattern
```python
# Single Settings class with pydantic-settings
class Settings(BaseSettings):
    qwen_api_key: str | None = None  # None = feature disabled

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

## Graceful Degradation Pattern
Every external integration must have a fallback. This is a core project convention:

```python
# Service class pattern: try real API, fall back silently
async def get_weather(self, city: str = "Mardan,PK") -> dict:
    if not self.settings.openweather_api_key:
        return self._fallback(city)
    try:
        ...  # real API call
    except Exception:
        return self._fallback(city)

# LLM client: try Qwen, fall back to mock
async def generate_urdu_answer(self, ...) -> tuple[str, str]:
    if self.settings.qwen_api_base and self.settings.qwen_api_key:
        try:
            return await self._call_remote_qwen(...), "qwen"
        except Exception:
            return self._development_answer(...), "mock"
    return self._development_answer(...), "mock"
```

---

## Async HTTP Client Pattern
Use `httpx.AsyncClient` as a context manager with explicit timeout:

```python
async with httpx.AsyncClient(timeout=60) as client:
    response = await client.post(url, headers=..., json=...)
    response.raise_for_status()
    data = response.json()
```

---

## Frontend API Call Pattern
All frontend API calls follow this structure in `shared.js`:

```javascript
async function fetchSomething() {
  try {
    const response = await fetch('/api/endpoint?param=value');
    if (!response.ok) throw new Error('Failed to fetch');
    const data = await response.json();
    updateUI(data);
  } catch (error) {
    console.error('Error:', error);
    showToast('Error message', 'error');
  }
}
```

- Always use `showToast(message, 'success'|'error')` for user feedback
- Farmer ID is hardcoded as `1` for MVP: `farmer_id=1`
- API base is `/api/` (relative, served by FastAPI)

---

## Naming Conventions

### Python
- Classes: `PascalCase` — `QwenClient`, `WeatherService`, `MemoryAgent`
- Functions/methods: `snake_case` — `get_weather`, `generate_urdu_answer`
- Private methods: leading underscore — `_call_remote_qwen`, `_fallback`, `_shape`
- Constants: `UPPER_SNAKE_CASE` — `KISSAN_AI_SYSTEM_PROMPT`
- DB columns: `snake_case` strings — `"farmer_id"`, `"crop_cycles"`

### JavaScript
- Functions: `camelCase` — `fetchFarmerProfile`, `updateWeatherUI`, `sendChatMessage`
- DOM element IDs: `camelCase` — `chatArea`, `voiceRecordingBar`, `sidebarOverlay`
- State objects: plain objects — `var voiceState = { isRecording: false, ... }`

---

## Data Shape Conventions

### API Response Shapes
Weather response always includes: `location`, `temperature`, `condition`, `icon`, `humidity`, `wind_kmh`, `rain_mm`, `pressure`, `forecast[]`, `advisories[]`

Advisory objects always have: `type`, `title`, `text`, `tone` (values: `"blue"`, `"orange"`, `"green"`)

### ORM Defaults
- Dates stored as `String(40)` for flexibility (e.g., `sowing_date`, `event_date`)
- `created_at` always uses `default=datetime.utcnow` (no timezone)
- Status fields use `String(40)` with string values like `"active"`, `"uploaded"`

---

## Localization Patterns
- Default language: Urdu (`"ur"`)
- Supported: `"ur"` (Urdu script), `"hinglish"` (Roman Urdu), `"en"` (English)
- Language detection via `detect_language()` in `qwen_client.py` — checks Urdu Unicode block `\u0600`–`\u06FF`
- All mock/fallback responses provided in all 3 languages
- Local units in responses: acres, kanal, maund; local varieties: CP-77400, NIAB-878, Super Basmati

---

## Production Swap Points
These are explicitly designed as stubs — replace for production:

| File | Current | Production Swap |
|---|---|---|
| `app/memory/mem0_client.py` | Local SQLite facade | Hosted Mem0 |
| `app/rag/retriever.py` | Seed retriever | LangChain + Qdrant/Chroma |
| `app/llm/qwen_client.py` | Mock Urdu responses | Live Qwen API |
| `backend/kissan_ai.db` | SQLite | PostgreSQL via `DATABASE_URL` |

---

## Security Notes
- Path traversal protection on static file serving: always check `frontend_path in requested.parents`
- Never recommend banned pesticides (enforced in system prompt)
- CORS currently set to `allow_origins=["*"]` — restrict in production
- API keys loaded from `.env` only, never hardcoded; use `.env.example` as template
