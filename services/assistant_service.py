
from services import gemini_service

SYSTEM_INSTRUCTION = (
    "You are an AI assistant for a city police department's crime "
    "analytics platform. Answer the officer's question using ONLY the "
    "provided context excerpts. If the context does not contain enough "
    "information to answer confidently, say so explicitly rather than "
    "guessing. Cite which source document each key point comes from. "
    "Keep answers focused and under 180 words."
)


def answer_question(question: str, top_k: int = 4) -> dict:
    from rag.retriever import retrieve

    hits = retrieve(question, top_k=top_k)

    if not hits:
        return {
            "answer": "No relevant documents were found in the knowledge base for this question.",
            "sources": [],
        }

    context_block = "\n\n".join(
        f"[Source: {h['source']}]\n{h['text']}" for h in hits
    )

    if not gemini_service.is_configured():
        preview = hits[0]["text"][:300]
        return {
            "answer": (
                "Gemini API key not configured, so here is the most relevant "
                f"retrieved excerpt instead:\n\n{preview}..."
            ),
            "sources": [h["source"] for h in hits],
        }

    prompt = (
        f"Context excerpts:\n{context_block}\n\n"
        f"Officer's question: {question}\n\n"
        "Answer grounded strictly in the context above."
    )

    try:
        answer = gemini_service.generate(prompt, system_instruction=SYSTEM_INSTRUCTION)
    except Exception as exc:
        answer = f"Gemini call failed ({exc}). Top retrieved excerpt:\n\n{hits[0]['text'][:300]}..."

    return {
        "answer": answer,
        "sources": sorted({h["source"] for h in hits}),
        "retrieved_chunks": hits,
    }
