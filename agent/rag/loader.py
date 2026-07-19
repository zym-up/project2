"""Document loader — load docs from knowledge/ directory."""
from pathlib import Path
from langchain_core.documents import Document


def load_documents(knowledge_dir: str = "knowledge") -> list[Document]:
    """Load all documents from knowledge directory.

    Supported: .txt, .md, .yaml, .yml
    """
    docs = []
    root = Path(knowledge_dir)
    if not root.exists():
        return docs

    for filepath in root.rglob("*"):
        if filepath.is_file():
            suffix = filepath.suffix.lower()
            if suffix in (".txt", ".md", ".yaml", ".yml"):
                try:
                    content = filepath.read_text(encoding="utf-8")
                    docs.append(Document(
                        page_content=content,
                        metadata={"source": str(filepath), "type": suffix.lstrip(".")},
                    ))
                except Exception:
                    pass

    return docs
