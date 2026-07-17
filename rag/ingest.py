import os
os.environ["HF_HUB_OFFLINE"] = "1"

import chromadb
from sentence_transformers import SentenceTransformer

from config import KB_DIR, CHROMA_DIR, EMBEDDING_MODEL

COLLECTION_NAME = "crime_knowledge_base"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 120

_embedder = None


def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = text.strip()
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c.strip() for c in chunks if c.strip()]


def load_documents():
    documents = []
    for path in sorted(KB_DIR.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        for i, chunk in enumerate(chunk_text(raw)):
            documents.append({
                "id": f"{path.stem}-{i}",
                "text": chunk,
                "source": path.name,
            })
    return documents


def build_index():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Fresh build each time this is run - simplest way to keep the
    # index in sync with the knowledge base files during development.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    docs = load_documents()
    if not docs:
        print("No knowledge base documents found in rag/knowledge_base/.")
        return

    embedder = get_embedder()
    texts = [d["text"] for d in docs]
    embeddings = embedder.encode(texts, show_progress_bar=False).tolist()

    collection.add(
        ids=[d["id"] for d in docs],
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"source": d["source"]} for d in docs],
    )

    print(f"Indexed {len(docs)} chunks from {KB_DIR.name} into ChromaDB at {CHROMA_DIR}.")


if __name__ == "__main__":
    build_index()
