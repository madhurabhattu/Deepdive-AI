"""RAG Pipeline Utility.

Coordinates query embedding, document search, prompt generation,
and LLM completion streaming for the grounded Q&A experience.
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from typing import TYPE_CHECKING, Any

from utils.ai_client import stream_chat
from utils.embedding_service import get_embeddings

if TYPE_CHECKING:
    from utils.vector_store import FAISSVectorStore

logger = logging.getLogger(__name__)


def stream_rag_answer(
    question: str,
    vector_store: FAISSVectorStore,
    embedding_model: str,
    llm_model: str,
    provider: str,
    byok_key: str | None = None,
    k: int = 4,
) -> Generator[dict[str, Any], None, None]:
    """Retrieves context from the vector store and streams an LLM response.

    Args:
        question: User query.
        vector_store: Initialized vector store containing indexed chunks.
        embedding_model: Embedding model name.
        llm_model: Local LLM model name.
        provider: AI provider.
        byok_key: API Key for BYOK mode.
        k: Top-k chunks to retrieve.

    Yields:
        Dictionaries of type:
          - {'type': 'token', 'content': str} for each text chunk.
          - {'type': 'sources', 'content': list[dict[str, Any]]} for the sources.
    """
    # 1. Embed user query
    try:
        query_embeddings = get_embeddings([question], model_name=embedding_model)
        query_emb = query_embeddings[0]
    except Exception as exc:
        logger.error("Failed to generate query embedding: %s", exc)
        yield {
            "type": "token",
            "content": f"⚠️ Failed to process query embeddings: {exc}",
        }
        yield {"type": "sources", "content": []}
        return

    # 2. Retrieve top-k chunks
    retrieved_results = vector_store.search(query_emb, k=k)
    if not retrieved_results:
        yield {
            "type": "token",
            "content": "I could not find that information in the uploaded document.",
        }
        yield {"type": "sources", "content": []}
        return

    retrieved_chunks = [chunk for chunk, _ in retrieved_results]

    # 3. Format context
    context_parts = []
    for chunk in retrieved_chunks:
        part = (
            f"Source: {chunk.metadata['filename']} "
            f"(Page {chunk.metadata['page_number']})\n"
            f"Content: {chunk.text}"
        )
        context_parts.append(part)
    context_str = "\n\n---\n\n".join(context_parts)

    # 4. Prompt template (grounded Q&A rules)
    prompt = f"""You are answering strictly using the provided document context.

If the answer is not present in the document, say:
"I could not find that information in the uploaded document."

Context:
{context_str}

Question:
{question}"""

    system_instruction = (
        "You are answering strictly using the provided document context. "
        "If the answer is not present in the document, say: "
        "'I could not find that information in the uploaded document.'"
    )

    # 5. Call LLM stream_chat
    try:
        token_generator = stream_chat(
            prompt=prompt,
            system_instruction=system_instruction,
            provider=provider,
            byok_key=byok_key,
            ollama_model=llm_model,
        )
        for token in token_generator:
            yield {"type": "token", "content": token}
    except Exception as exc:
        logger.error("RAG streaming generation failed: %s", exc)
        yield {
            "type": "token",
            "content": f"\n\n⚠️ Error during LLM generation: {exc}",
        }

    # 6. Yield sources at the end
    sources = []
    for chunk, score in retrieved_results:
        sources.append(
            {
                "filename": chunk.metadata["filename"],
                "page_number": chunk.metadata["page_number"],
                "chunk_id": chunk.metadata["chunk_id"],
                "text": chunk.text,
                "score": float(score),
            }
        )
    yield {"type": "sources", "content": sources}
