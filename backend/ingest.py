"""
Run once (or whenever PDFs change):
    python ingest.py
Produces:
    data/vector_index/index.faiss
    data/vector_index/chunks.json
"""
from __future__ import annotations

import json
import pathlib

import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

RAW_DIR = pathlib.Path("data/raw_pdfs")
OUT_DIR = pathlib.Path("data/vector_index")
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def _extract_text(pdf_path: pathlib.Path) -> str:
    try:
        reader = PdfReader(str(pdf_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        print(f"  skip {pdf_path.name}: {e}")
        return ""


def _chunk(text: str, source: str) -> list[dict]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i : i + CHUNK_SIZE]
        chunks.append({"text": " ".join(chunk_words), "source": source})
        i += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_chunks: list[dict] = []
    pdf_files = [p for p in RAW_DIR.iterdir() if p.suffix.lower() == ".pdf"]
    print(f"Found {len(pdf_files)} PDFs")

    for pdf in pdf_files:
        print(f"  processing {pdf.name}")
        text = _extract_text(pdf)
        if text.strip():
            all_chunks.extend(_chunk(text, pdf.name))

    print(f"Total chunks: {len(all_chunks)}")

    model = SentenceTransformer(MODEL_NAME)
    texts = [c["text"] for c in all_chunks]
    print("Embedding chunks (this may take a few minutes)...")
    embeddings = model.encode(texts, batch_size=64, show_progress_bar=True, convert_to_numpy=True)
    embeddings = embeddings.astype(np.float32)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, str(OUT_DIR / "index.faiss"))
    with open(OUT_DIR / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False)

    print(f"Saved index ({index.ntotal} vectors) and chunks to {OUT_DIR}")


if __name__ == "__main__":
    main()
