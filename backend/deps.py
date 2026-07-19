"""FastAPI shared dependencies."""
import logging
from pathlib import Path

from engine.project_manager import ProjectManager
from graph.workflow import create_production_workflow, create_dev_workflow

logger = logging.getLogger(__name__)

pm = ProjectManager(projects_dir="projects")

_workflow = None


def get_workflow():
    """Get compiled Graph workflow.

    Production: SQLite checkpointing. Dev fallback: in-memory.
    """
    global _workflow
    if _workflow is None:
        try:
            _workflow = create_production_workflow("checkpoints.db")
            logger.info("Workflow: SQLite checkpointer")
        except Exception as e:
            logger.warning("SQLite unavailable (%s), using memory", e)
            _workflow = create_dev_workflow()
    return _workflow


def load_chart_html(project_id: str, chart_name: str) -> str:
    """Load chart HTML from disk."""
    chart_path = Path("projects") / project_id / "charts" / f"{chart_name}.html"
    if chart_path.exists():
        return chart_path.read_text(encoding="utf-8")
    return ""
