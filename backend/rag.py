"""
RAG pipeline — document loading, chunking, embedding, and retrieval.
Uses ChromaDB for local persistent vector storage and OpenAI text-embedding-3-small.
"""

import hashlib
import json
import logging
from pathlib import Path

import chromadb
from pypdf import PdfReader

from openai_client import get_client

logger = logging.getLogger("advising_rag")

KNOWLEDGE_BASE_DIR = (Path(__file__).parent / "knowledge_base").resolve()
CHROMA_DIR = Path(__file__).parent / "chroma_db"
HASH_CACHE_PATH = Path(__file__).parent / "chroma_db" / "_doc_hashes.json"
COLLECTION_NAME = "cisat_knowledge"

_chroma: chromadb.Collection | None = None


def get_collection() -> chromadb.Collection:
    global _chroma
    if _chroma is None:
        db = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _chroma = db.get_or_create_collection(COLLECTION_NAME)
    return _chroma


def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return [c.strip() for c in chunks if c.strip()]


def _safe_resolve(file_path: Path) -> Path | None:
    """Resolve symlinks and verify the file is inside KNOWLEDGE_BASE_DIR."""
    resolved = file_path.resolve()
    if not str(resolved).startswith(str(KNOWLEDGE_BASE_DIR)):
        logger.warning("Path traversal blocked: %s resolves outside knowledge_base/", file_path.name)
        return None
    return resolved


def load_documents() -> list[dict]:
    """Load .md, .txt, and .pdf files from the knowledge base directory."""
    docs = []
    if not KNOWLEDGE_BASE_DIR.exists():
        logger.warning("knowledge_base/ directory not found at %s", KNOWLEDGE_BASE_DIR)
        return docs

    for file_path in KNOWLEDGE_BASE_DIR.iterdir():
        safe_path = _safe_resolve(file_path)
        if safe_path is None:
            continue

        if safe_path.suffix in (".md", ".txt"):
            text = safe_path.read_text(encoding="utf-8")
        elif safe_path.suffix == ".pdf":
            reader = PdfReader(str(safe_path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            continue
        docs.append({"filename": safe_path.name, "text": text})
        logger.info("Loaded: %s (%d chars)", safe_path.name, len(text))

    return docs


def _compute_doc_hashes(docs: list[dict]) -> dict[str, str]:
    """Return a mapping of filename → SHA-256 hash of content."""
    return {
        doc["filename"]: hashlib.sha256(doc["text"].encode("utf-8")).hexdigest()
        for doc in docs
    }


def _load_cached_hashes() -> dict[str, str]:
    """Load previously saved doc hashes from disk."""
    if HASH_CACHE_PATH.exists():
        try:
            return json.loads(HASH_CACHE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cached_hashes(hashes: dict[str, str]) -> None:
    """Persist doc hashes to disk."""
    HASH_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    HASH_CACHE_PATH.write_text(json.dumps(hashes), encoding="utf-8")


def init_knowledge_base() -> None:
    """
    Load documents, chunk them, embed with OpenAI, and store in ChromaDB.
    Only re-indexes when document content has changed (hash-based check).
    """
    collection = get_collection()
    client = get_client()
    docs = load_documents()

    if not docs:
        logger.info("No documents found — knowledge base is empty.")
        return

    current_hashes = _compute_doc_hashes(docs)
    cached_hashes = _load_cached_hashes()

    if current_hashes == cached_hashes and collection.count() > 0:
        logger.info("Knowledge base unchanged — skipping re-index (%d chunks cached).", collection.count())
        return

    logger.info("Knowledge base changed — re-indexing...")

    # Clear existing entries and re-index
    existing = collection.count()
    if existing > 0:
        collection.delete(where={"source": {"$ne": "__none__"}})
        logger.info("Cleared %d existing chunks.", existing)

    all_chunks = []
    all_ids = []
    all_metadatas = []

    for doc in docs:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"{doc['filename']}__chunk_{i}")
            all_metadatas.append({"source": doc["filename"], "chunk_index": i})

    if not all_chunks:
        logger.info("Documents loaded but produced no chunks.")
        return

    logger.info("Embedding %d chunks...", len(all_chunks))
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=all_chunks,
    )
    embeddings = [item.embedding for item in response.data]

    collection.add(
        ids=all_ids,
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=all_metadatas,
    )
    _save_cached_hashes(current_hashes)
    logger.info("Indexed %d chunks from %d documents.", len(all_chunks), len(docs))


def retrieve(query: str, k: int = 5) -> list[str]:
    """
    Retrieve top-k most relevant chunks for the given query.
    Returns a list of chunk text strings.
    """
    collection = get_collection()
    if collection.count() == 0:
        return []

    client = get_client()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query],
    )
    query_embedding = response.data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, collection.count()),
        include=["documents"],
    )
    return results["documents"][0] if results["documents"] else []
