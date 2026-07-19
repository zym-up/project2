"""Chroma vector store management."""
from langchain_chroma import Chroma
from langchain_core.documents import Document


def create_vector_store(
    docs: list[Document],
    embeddings,
    persist_dir: str = "chroma_db",
) -> Chroma:
    """Create and persist vector store."""
    return Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_dir,
    )


def load_vector_store(
    embeddings,
    persist_dir: str = "chroma_db",
) -> Chroma:
    """Load existing vector store."""
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
    )
