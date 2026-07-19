"""LangGraph AnalysisState 定义."""
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
import pandas as pd


class StepResult(TypedDict, total=False):
    step_id: int
    type: str
    description: str
    status: str
    metrics: dict
    text: str
    charts: list[str]


class AnalysisStep(TypedDict, total=False):
    id: int
    type: str
    description: str
    params: dict
    status: str


class AnalysisState(TypedDict, total=False):
    user_input: str
    project_id: str
    df: Optional[pd.DataFrame]
    rag_context: str
    df_info: dict
    plan: list[AnalysisStep]
    current_step_index: int
    results: Annotated[list[StepResult], add_messages]
    context_summary: str
    next_action: str
    error_message: str
    conclusion: str
