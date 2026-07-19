"""LangGraph StateGraph workflow builder."""
import logging

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

from graph.state import AnalysisState
from graph.nodes import (
    understand_intent,
    plan_analysis,
    execute_step,
    interpret_result,
    decide_next,
    generate_conclusion,
)

logger = logging.getLogger(__name__)


def build_workflow(checkpointer=None):
    """Build analysis workflow StateGraph.

    Graph:
    START -> understand_intent -> plan_analysis -> execute_step -> interpret_result
                ^                                                    |
                |                      ┌─────────────────────────────┘
                |                      v
                └─────────────── decide_next ---> generate_conclusion -> END
    """
    workflow = StateGraph(AnalysisState)

    workflow.add_node("understand_intent", understand_intent)
    workflow.add_node("plan_analysis", plan_analysis)
    workflow.add_node("execute_step", execute_step)
    workflow.add_node("interpret_result", interpret_result)
    workflow.add_node("generate_conclusion", generate_conclusion)

    workflow.add_edge(START, "understand_intent")
    workflow.add_edge("understand_intent", "plan_analysis")
    workflow.add_edge("plan_analysis", "execute_step")
    workflow.add_edge("execute_step", "interpret_result")

    workflow.add_conditional_edges(
        "interpret_result",
        decide_next,
        {
            "execute": "execute_step",
            "generate_conclusion": "generate_conclusion",
        },
    )

    workflow.add_edge("generate_conclusion", END)

    if checkpointer is None:
        checkpointer = MemorySaver()

    return workflow.compile(checkpointer=checkpointer)


def create_production_workflow(db_path: str = "checkpoints.db"):
    """Create production workflow with SQLite state persistence."""
    try:
        checkpointer = SqliteSaver.from_conn_string(db_path)
        logger.info("Using SQLite checkpointer: %s", db_path)
    except Exception as e:
        logger.warning("SQLite unavailable (%s), using memory checkpointer", e)
        checkpointer = MemorySaver()

    return build_workflow(checkpointer=checkpointer)


def create_dev_workflow():
    """Create dev workflow with in-memory state."""
    return build_workflow(checkpointer=MemorySaver())
