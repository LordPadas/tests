from __future__ import annotations

import os
import json
import hashlib
from typing import List, Dict, Tuple
from pathlib import Path

import httpx
from sqlalchemy import create_engine, Column, String, Float, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from ..config import get_settings

settings = get_settings()

Base = declarative_base()

DOCUMENT_TABLE_NAME = "documents"


class Document(Base):
    __tablename__ = DOCUMENT_TABLE_NAME

    id = Column(String(64), primary_key=True)
    file_path = Column(String(512), nullable=False)
    file_name = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Float, nullable=False)
    embedding = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


def get_db_session():
    engine = create_engine(settings.DB_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def get_ollama_response(prompt: str, context: str = "") -> str:
    full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}\n\nAnswer:" if context else prompt

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{settings.OLLAMA_HOST}/api/generate",
                json={
                    "model": "phi",
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "num_gpu": 0,
                        "num_thread": 2,
                    }
                },
            )
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                return f"Error: Ollama returned {response.status_code}"
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"


def compute_embedding(text: str) -> List[float]:
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{settings.OLLAMA_HOST}/api/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": text,
                },
            )
            if response.status_code == 200:
                return response.json().get("embedding", [])
            return []
    except Exception:
        return []


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks


def index_document(file_path: str, content: str) -> List[Dict]:
    session = get_db_session()
    file_name = os.path.basename(file_path)
    doc_id = hashlib.sha256(f"{file_path}:{content[:100]}".encode()).hexdigest()[:16]

    existing = session.query(Document).filter(Document.file_path == file_path).first()
    if existing:
        session.query(Document).filter(Document.file_path == file_path).delete()
        session.commit()

    chunks = chunk_text(content)
    indexed_chunks = []

    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_{i}"
        emb = compute_embedding(chunk)

        doc = Document(
            id=chunk_id,
            file_path=file_path,
            file_name=file_name,
            content=content,
            chunk_text=chunk,
            chunk_index=i,
            embedding=json.dumps(emb) if emb else None,
        )
        session.add(doc)
        indexed_chunks.append({"id": chunk_id, "chunk": chunk, "index": i})

    session.commit()
    session.close()
    return indexed_chunks


def retrieve_relevant_chunks(query: str, top_k: int = 3) -> List[Dict]:
    session = get_db_session()
    query_emb = compute_embedding(query)

    if not query_emb:
        session.close()
        return []

    documents = session.query(Document).all()
    results = []

    for doc in documents:
        if not doc.embedding:
            continue
        try:
            doc_emb = json.loads(doc.embedding)
        except (json.JSONDecodeError, TypeError):
            continue

        sim = cosine_similarity(query_emb, doc_emb)
        results.append({
            "file_path": doc.file_path,
            "file_name": doc.file_name,
            "chunk_text": doc.chunk_text,
            "chunk_index": doc.chunk_index,
            "similarity": sim,
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    session.close()
    return results[:top_k]


def get_answer(query: str) -> Tuple[str, List[Dict]]:
    retrieved = retrieve_relevant_chunks(query, top_k=3)

    if retrieved:
        context = "\n\n".join(
            f"[{r['file_name']} (chunk {r['chunk_index']})]\n{r['chunk_text']}"
            for r in retrieved
        )
        answer = get_ollama_response(query, context)
    else:
        answer = get_ollama_response(query)
        context = ""

    sources = [
        {
            "path": r["file_path"],
            "name": r["file_name"],
            "section": f"Chunk {r['chunk_index']}",
            "confidence": round(r["similarity"], 2),
        }
        for r in retrieved
    ] if retrieved else [{"path": "", "name": "General", "section": None, "confidence": 0.5}]

    return answer, sources


def reindex_all(docs_dir: str = "/data/docs") -> Dict:
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        return {"indexed": 0, "errors": ["Directory not found"]}

    indexed = 0
    errors = []

    for file_path in docs_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in [".txt", ".md", ".pdf"]:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                if content:
                    index_document(str(file_path), content)
                    indexed += 1
            except Exception as e:
                errors.append(f"{file_path}: {str(e)}")

    return {"indexed": indexed, "errors": errors}
