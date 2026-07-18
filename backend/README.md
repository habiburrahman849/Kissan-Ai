# Kissan AI MemoryAgent Backend

Website-first backend for the Kissan AI dual-brain assistant.

## Run locally

```powershell
cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

- Website: http://127.0.0.1:8000/chat.html
- API docs: http://127.0.0.1:8000/docs

## Current MVP

- Website chat endpoint: `POST /api/chat/message`
- Local farmer memory stored in SQLite
- Crop cycle start/harvest memory logic
- Document upload registry for future RAG indexing
- Qwen-compatible client with a mock Urdu response mode when credentials are not set
- Mem0 cloud memory search/save when `MEM0_API_KEY` is configured
- OpenWeatherMap-backed weather page when `OPENWEATHER_API_KEY` is configured

## Production swap-ins

- Replace local memory facade with hosted Mem0 in `app/memory/mem0_client.py`
- Replace seed retriever with LangChain + Qdrant/Chroma in `app/rag/retriever.py`
- Set Qwen credentials in `backend/.env`
