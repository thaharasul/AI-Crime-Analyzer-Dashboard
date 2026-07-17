import os
os.environ["HF_HUB_OFFLINE"] = "1"

import chromadb
from sentence_transformers import SentenceTransformer

import chromadb

from config import CHROMA_DIR
from rag.ingest import COLLECTION_NAME, get_embedder

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        try:
            _collection = _client.get_collection(COLLECTION_NAME)
        except Exception as exc:
            raise RuntimeError(
                "RAG index not found. Run `python -m rag.ingest` first."
            ) from exc
    return _collection


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    collection = _get_collection()
    embedder = get_embedder()
    query_embedding = embedder.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )

    hits = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for text, meta, distance in zip(documents, metadatas, distances):
        hits.append({
            "text": text,
            "source": meta.get("source", "unknown"),
            "relevance": round(1 - distance, 4),
        })
    return hits
