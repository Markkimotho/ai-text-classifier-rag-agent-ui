import os
import re
from pathlib import Path
from typing import Optional

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory store: list of (chunk_text, embedding_vector)
_store: list[tuple[str, list[float]]] = []
_documents: list[str] = []

# Lazy-loaded embedding model and FAISS index
_model = None
_index = None
_index_to_chunk: list[str] = []


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _embed(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return model.encode(texts, show_progress_bar=False).tolist()


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return [c for c in chunks if c.strip()]


def _extract_text_from_file(filepath: Path, content_type: str) -> str:
    if content_type == "application/pdf" or filepath.suffix.lower() == ".pdf":
        import fitz  # PyMuPDF
        doc = fitz.open(str(filepath))
        return "\n".join(page.get_text() for page in doc)
    else:
        return filepath.read_text(errors="replace")


def ingest_file(filepath: Path, content_type: str) -> int:
    global _index, _index_to_chunk

    text = _extract_text_from_file(filepath, content_type)
    chunks = _chunk_text(text)

    if not chunks:
        return 0

    embeddings = _embed(chunks)

    import numpy as np
    import faiss

    vectors = np.array(embeddings, dtype="float32")
    dim = vectors.shape[1]

    if _index is None:
        _index = faiss.IndexFlatL2(dim)

    _index.add(vectors)
    _index_to_chunk.extend(chunks)

    filename = filepath.name
    if filename not in _documents:
        _documents.append(filename)

    return len(chunks)


def retrieve(question: str, top_k: int = 3) -> list[str]:
    global _index, _index_to_chunk

    if _index is None or _index.ntotal == 0:
        return []

    import numpy as np

    q_vec = np.array(_embed([question]), dtype="float32")
    k = min(top_k, _index.ntotal)
    _, indices = _index.search(q_vec, k)

    return [_index_to_chunk[i] for i in indices[0] if i != -1]


def generate_answer(question: str, chunks: list[str]) -> str:
    if not chunks:
        return "I could not find relevant information in the uploaded documents."

    context = "\n\n".join(f"[Source {i+1}]: {chunk}" for i, chunk in enumerate(chunks))
    prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer based on the context above:"

    try:
        from gpt4all import GPT4All
        model_name = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
        model_path = Path.home() / ".cache" / "gpt4all"
        if (model_path / model_name).exists():
            gpt = GPT4All(model_name, model_path=str(model_path), verbose=False)
            with gpt.chat_session():
                return gpt.generate(prompt, max_tokens=256)
    except Exception:
        pass

    # Deterministic template fallback (for CI / offline environments)
    first_chunk = chunks[0][:300].strip()
    sentences = re.split(r"(?<=[.!?])\s+", first_chunk)
    summary = " ".join(sentences[:3]) if sentences else first_chunk
    return f"Based on the uploaded documents: {summary}"


def list_documents() -> list[str]:
    return list(_documents)


def reset_store():
    global _index, _index_to_chunk, _documents
    _index = None
    _index_to_chunk = []
    _documents = []
