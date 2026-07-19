"""Initialize RAG knowledge base — one-shot script.

Usage: python scripts/init_rag.py [--knowledge-dir knowledge] [--persist-dir chroma_db]
"""
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.rag.loader import load_documents
from agent.rag.splitter import split_documents
from agent.rag.embeddings import create_embeddings
from agent.rag.store import create_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Initialize RAG knowledge base")
    parser.add_argument("--knowledge-dir", default="knowledge", help="Knowledge directory")
    parser.add_argument("--persist-dir", default="chroma_db", help="Chroma persist directory")
    parser.add_argument("--chunk-size", type=int, default=800, help="Chunk size")
    parser.add_argument("--chunk-overlap", type=int, default=100, help="Chunk overlap")
    args = parser.parse_args()

    logger.info("Loading documents from %s...", args.knowledge_dir)
    docs = load_documents(args.knowledge_dir)
    logger.info("Loaded %d documents", len(docs))

    if not docs:
        logger.warning("No documents found in %s!", args.knowledge_dir)
        return

    logger.info("Splitting (chunk_size=%d)...", args.chunk_size)
    chunks = split_documents(docs, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    logger.info("Created %d chunks", len(chunks))

    logger.info("Initializing embeddings...")
    embeddings = create_embeddings()

    logger.info("Creating vector store at %s...", args.persist_dir)
    create_vector_store(chunks, embeddings, persist_dir=args.persist_dir)
    logger.info("RAG initialization complete!")


if __name__ == "__main__":
    main()
