from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass

import numpy as np
from sqlalchemy.orm import Session

INDEX_DIR = pathlib.Path(__file__).parent.parent.parent.parent / "data" / "vector_index"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@dataclass
class RetrievedDoc:
    title: str
    source: str | None
    snippet: str


class AgricultureRetriever:
    def __init__(self) -> None:
        self._index = None
        self._chunks: list[dict] = []
        self._model = None
        self._load()

    def _load(self) -> None:
        index_path = INDEX_DIR / "index.faiss"
        chunks_path = INDEX_DIR / "chunks.json"
        if not index_path.exists() or not chunks_path.exists():
            return
        try:
            import faiss
            from sentence_transformers import SentenceTransformer

            self._index = faiss.read_index(str(index_path))
            with open(chunks_path, encoding="utf-8") as f:
                self._chunks = json.load(f)
            self._model = SentenceTransformer(MODEL_NAME)
            print(f"RAG: loaded {self._index.ntotal} vectors from {INDEX_DIR}")
        except Exception as e:
            print(f"RAG: failed to load index — {e}")

    def search(self, db: Session, query: str, memory: dict, limit: int = 3) -> list[RetrievedDoc]:
        if self._index is None or self._model is None:
            return [
                RetrievedDoc(
                    title="General Crop Advisory",
                    source="development seed knowledge",
                    snippet="Run `python ingest.py` in the backend folder to build the RAG index from PDFs.",
                )
            ]

        vec = self._model.encode([query], convert_to_numpy=True).astype(np.float32)
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
