# Kissan AI Backend

FastAPI service for the MemoryAgent demo. Frontend files live in repo `static/` and are served by `app.main`.

## Local run

```bash
# from backend/
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # then fill keys
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Site: http://127.0.0.1:8000/
- Chat: http://127.0.0.1:8000/chat.html
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/health

`FRONTEND_DIR` defaults to `../static` (relative to `backend/`).

## Production (Render)

Use the **root** `Dockerfile` + `render.yaml`. Render sets `PORT`; uvicorn binds to `0.0.0.0:$PORT`.

Auth: guest mode + email/password (Clerk removed).
Weather: OpenWeatherMap when `OPENWEATHER_API_KEY` is set.
LLM: Qwen when `QWEN_API_KEY` is set; otherwise offline fallback.
