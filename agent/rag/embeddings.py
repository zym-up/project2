"""Embedding model — defaults to DeepSeek API, configurable."""
import json
import os
from langchain_openai import OpenAIEmbeddings


def create_embeddings(config_path: str = "config.json") -> OpenAIEmbeddings:
    """Create embedding model instance.

    Priority: env vars > config.json > defaults
    """
    base_url = os.getenv("EMBEDDING_BASE_URL", "")
    api_key = os.getenv("EMBEDDING_API_KEY", "")
    model = os.getenv("EMBEDDING_MODEL", "")

    if not base_url:
        try:
            with open(config_path, encoding="utf-8") as f:
                cfg = json.load(f)
            emb_cfg = cfg.get("embedding", {})
            base_url = base_url or emb_cfg.get("base_url", "")
            api_key = api_key or emb_cfg.get("api_key", "")
            model = model or emb_cfg.get("model", "text-embedding-3-small")
        except (FileNotFoundError, KeyError):
            pass

    if not api_key:
        api_key = os.getenv("DEEPSEEK_API_KEY", "")

    return OpenAIEmbeddings(
        base_url=base_url,
        api_key=api_key,
        model=model,
    )
