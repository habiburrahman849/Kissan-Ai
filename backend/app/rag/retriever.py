from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass

from sqlalchemy.orm import Session

# backend/data/vector_index (same place ingest.py writes)
INDEX_DIR = pathlib.Path(__file__).resolve().parents[2] / "data" / "vector_index"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@dataclass
class RetrievedDoc:
    title: str
    source: str | None
    snippet: str


class AgricultureRetriever:
    """Lazy FAISS + SentenceTransformer loader so /api/health stays fast on Render."""

    def __init__(self) -> None:
        self._index = None
        self._chunks: list[dict] = []
        self._model = None
        self._last_loaded_time = 0.0
        self._load_failed = False

    def _load(self) -> None:
        if self._load_failed and self._index is not None:
            return

        index_path = INDEX_DIR / "index.faiss"
        chunks_path = INDEX_DIR / "chunks.json"
        if not index_path.exists() or not chunks_path.exists():
            print(f"RAG: index not found at {INDEX_DIR} — run: python ingest.py")
            self._load_failed = True
            return
        try:
            import faiss
            from sentence_transformers import SentenceTransformer

            self._index = faiss.read_index(str(index_path))
            with open(chunks_path, encoding="utf-8") as f:
                self._chunks = json.load(f)
            # Heavy: downloads model on first use if not cached in the image
            self._model = SentenceTransformer(MODEL_NAME)
            self._last_loaded_time = index_path.stat().st_mtime
            self._load_failed = False
            print(f"RAG: loaded {self._index.ntotal} vectors from {INDEX_DIR}")
        except Exception as e:
            print(f"RAG: failed to load index — {e}")
            self._index = None
            self._model = None
            self._load_failed = True

    def search(self, db: Session, query: str, memory: dict, limit: int = 3) -> list[RetrievedDoc]:
        index_path = INDEX_DIR / "index.faiss"

        # Auto-reload if file is modified or if not loaded yet
        if index_path.exists():
            mtime = index_path.stat().st_mtime
            if self._index is None or self._model is None or mtime > self._last_loaded_time:
                print("RAG: Index modified or not loaded yet. Reloading index...")
                self._load()

        if self._index is None or self._model is None:
            return [
                RetrievedDoc(
                    title="General Crop Advisory",
                    source="seed knowledge",
                    snippet=(
                        "Local PDF index is not built yet or model is unavailable on this host. "
                        "Meanwhile: use recommended fertilizer schedules for Kharif/Rabi crops, "
                        "avoid spraying before rain, and consult a local extension officer for pesticide rates."
                    ),
                )
            ]

        import numpy as np

        # Boost query with farmer context for better locality
        boosted = query
        if memory.get("current_crop"):
            boosted += f" {memory['current_crop']}"
        if memory.get("district"):
            boosted += f" {memory['district']}"

        vec = self._model.encode([boosted], convert_to_numpy=True).astype(np.float32)
        _, indices = self._index.search(vec, limit)

        results: list[RetrievedDoc] = []
        for idx in indices[0]:
            if idx < 0 or idx >= len(self._chunks):
                continue
            chunk = self._chunks[idx]
            results.append(
                RetrievedDoc(
                    title=chunk["source"],
                    source=chunk["source"],
                    snippet=chunk["text"][:500],
                )
            )
        return results
