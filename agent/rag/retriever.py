"""RAG retriever — singleton, LangChain Retriever interface."""
import logging
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document

from agent.rag.embeddings import create_embeddings
from agent.rag.store import load_vector_store

logger = logging.getLogger(__name__)

_retriever_instance = None


def get_retriever(
    persist_dir: str = "chroma_db",
    k: int = 3,
) -> BaseRetriever:
    """Get RAG retriever singleton.

    Args:
        persist_dir: Chroma persist directory
        k: Number of chunks to retrieve

    Returns:
        LangChain Retriever instance
    """
    global _retriever_instance

    if _retriever_instance is not None:
        return _retriever_instance

    try:
        embeddings = create_embeddings()
        vector_store = load_vector_store(embeddings, persist_dir=persist_dir)
        _retriever_instance = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )
        logger.info("RAG retriever initialized, k=%d", k)
    except Exception as e:
        logger.warning("RAG init failed: %s. Using fallback.", e)
        _retriever_instance = _FallbackRetriever()

    return _retriever_instance


class _FallbackRetriever(BaseRetriever):
    """Fallback retriever when RAG is unavailable (returns empty results)."""

    def _get_relevant_documents(self, query: str) -> list[Document]:
        return []
