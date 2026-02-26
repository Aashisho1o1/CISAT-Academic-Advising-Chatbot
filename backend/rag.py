"""
RAG pipeline — document loading, chunking, embedding, and retrieval.
Uses ChromaDB for local persistent vector storage and OpenAI text-embedding-3-small.
"""

import os
from pathlib import Path
from openai import OpenAI
import chromadb
from pypdf import PdfReader

KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"
CHROMA_DIR = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "cisat_knowledge"

_client: OpenAI | None = None
_chroma: chromadb.Collection | None = None


def get_openai_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


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


def load_documents() -> list[dict]:
    """Load .md, .txt, and .pdf files from the knowledge base directory."""
    docs = []
    if not KNOWLEDGE_BASE_DIR.exists():
        print(f"[RAG] knowledge_base/ directory not found at {KNOWLEDGE_BASE_DIR}")
        return docs

    for file_path in KNOWLEDGE_BASE_DIR.iterdir():
        if file_path.suffix in (".md", ".txt"):
            text = file_path.read_text(encoding="utf-8")
        elif file_path.suffix == ".pdf":
            reader = PdfReader(str(file_path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            continue
        docs.append({"filename": file_path.name, "text": text})
        print(f"[RAG] Loaded: {file_path.name} ({len(text)} chars)")

    return docs


def init_knowledge_base() -> None:
    """
    Load documents, chunk them, embed with OpenAI, and store in ChromaDB.
    Called once at app startup. Safe to call multiple times (re-embeds on each startup).
    """
    collection = get_collection()
    client = get_openai_client()
    docs = load_documents()

    if not docs:
        print("[RAG] No documents found — knowledge base is empty.")
        return

    # Clear existing entries and re-index (simple approach for prototype)
    existing = collection.count()
    if existing > 0:
        collection.delete(where={"source": {"$ne": "__none__"}})
        print(f"[RAG] Cleared {existing} existing chunks.")

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
        print("[RAG] Documents loaded but produced no chunks.")
        return

    print(f"[RAG] Embedding {len(all_chunks)} chunks...")
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
    print(f"[RAG] Indexed {len(all_chunks)} chunks from {len(docs)} documents.")


def retrieve(query: str, k: int = 5) -> list[str]:
    """
    Retrieve top-k most relevant chunks for the given query.
    Returns a list of chunk text strings.
    """
    collection = get_collection()
    if collection.count() == 0:
        return []

    client = get_openai_client()
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
