"""LangGraph workflow nodes.

Nodes:
- understand_intent: RAG retrieval + intent parsing
- plan_analysis: LLM generates analysis plan
- execute_step: Execute current step via Tool Calling
- interpret_result: LLM interprets execution results
- decide_next: Deterministic next-action logic
- generate_conclusion: Generate comprehensive conclusion
"""
import json
import logging
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

from graph.state import AnalysisState
from graph.tools import create_analysis_tools
from engine.data_loader import get_data_info
from engine.config import load_config, AppConfig

logger = logging.getLogger(__name__)


def _get_llm(config: AppConfig) -> ChatOpenAI:
    return ChatOpenAI(
        base_url=config.llm.base_url,
        api_key=config.llm.api_key,
        model=config.llm.model,
        temperature=config.llm.temperature,
        max_tokens=config.llm.max_tokens,
        max_retries=3,
        timeout=60,
    )


def _get_rag_context(query: str) -> str:
    """Get RAG context, returns empty string on failure (graceful degradation)."""
    try:
        from agent.rag.retriever import get_retriever
        retriever = get_retriever()
        docs = retriever.invoke(query)
        if docs:
            return "\n\n".join([f"Domain knowledge:\n{d.page_content}" for d in docs[:3]])
    except Exception as e:
        logger.warning("RAG unavailable: %s", e)
    return ""


# === Node functions ===

async def understand_intent(state: AnalysisState, config: RunnableConfig) -> dict:
    """Node 1: Intent understanding + RAG knowledge injection."""
    user_input = state["user_input"]
    rag_context = _get_rag_context(user_input)

    df = state.get("df")
    df_info = {}
    if df is not None:
        df_info = get_data_info(df)

    logger.info("understand_intent: rag=%d chars, columns=%d",
                len(rag_context), len(df_info.get("columns", [])))

    return {"rag_context": rag_context, "df_info": df_info}


async def plan_analysis(state: AnalysisState, config: RunnableConfig) -> dict:
    """Node 2: LLM generates analysis plan."""
    app_config = load_config("config.json")
    llm = _get_llm(app_config)
    tools = create_analysis_tools()

    tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in tools])
    system_prompt = f"""You are an automotive R&D data analysis expert.

Available tools:
{tool_descriptions}

Dataset info:
- Rows: {state['df_info'].get('row_count', 'N/A')}
- Columns: {state['df_info'].get('col_count', 'N/A')}
- Column names: {state['df_info'].get('columns', [])}
- Numeric: {state['df_info'].get('numeric_columns', [])}
- Categorical: {state['df_info'].get('categorical_columns', [])}

{state.get('rag_context', '')}

Generate a step-by-step analysis plan. Return STRICT JSON (no markdown):
{{"plan": [{{"id": 1, "type": "clean|eda|feature|model", "description": "step description in Chinese", "params": {{}}, "status": "pending"}}]}}
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"User request: {state['user_input']}\nGenerate analysis plan."),
    ]

    try:
        response = await llm.ainvoke(messages)
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("\n", 1)[0]
            if raw.startswith("json"):
                raw = raw[4:].strip()
        plan_data = json.loads(raw)
        plan = plan_data.get("plan", [])
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("LLM JSON parse failed: %s", e)
        plan = [
            {"id": 1, "type": "eda", "description": "Descriptive statistics", "params": {}, "status": "pending"},
            {"id": 2, "type": "eda", "description": "Correlation analysis", "params": {"method": "pearson"}, "status": "pending"},
        ]

    return {"plan": plan, "current_step_index": 0, "next_action": "execute", "error_message": ""}


async def execute_step(state: AnalysisState, config: RunnableConfig) -> dict:
    """Node 3: Execute current analysis step."""
    idx = state["current_step_index"]
    plan = state["plan"]

    if idx >= len(plan):
        return {"next_action": "done"}

    step = plan[idx]
    step["status"] = "running"

    app_config = load_config("config.json")
    llm = _get_llm(app_config)
    tools = create_analysis_tools()
    llm_with_tools = llm.bind_tools(tools)

    prompt = f"""Execute this analysis step:
- Type: {step['type']}
- Description: {step['description']}
- Parameters: {step.get('params', {})}

Previous results:
{state.get('context_summary', 'None')}

Select and call the appropriate tool to execute this step."""

    try:
        response = await llm_with_tools.ainvoke([HumanMessage(content=prompt)])
        tool_results = []

        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                tool = next((t for t in tools if t.name == tc["name"]), None)
                if tool:
                    tool_args = dict(tc["args"])
                    df = state.get("df")
                    if df is not None:
                        tool_args["df"] = df
                    result = tool.func(**tool_args)
                    tool_results.append({"tool": tc["name"], "result": result})

        result_entry = {
            "step_id": step["id"],
            "type": step["type"],
            "description": step["description"],
            "status": "done",
            "metrics": {},
            "text": json.dumps(tool_results, ensure_ascii=False, default=str),
            "charts": [],
        }

        results = list(state.get("results", []))
        results.append(result_entry)

        return {
            "results": results,
            "current_step_index": idx + 1,
            "next_action": "decide",
            "error_message": "",
        }

    except Exception as e:
        logger.exception("execute_step failed: step_id=%d", step["id"])
        return {
            "next_action": "replan" if idx < 2 else "done",
            "error_message": f"Step {step['id']} failed: {e}",
        }


async def interpret_result(state: AnalysisState, config: RunnableConfig) -> dict:
    """Node 4: LLM interprets execution result."""
    app_config = load_config("config.json")
    llm = _get_llm(app_config)
    results = state.get("results", [])

    if not results:
        return {"context_summary": "No results yet.", "next_action": "done"}

    latest = results[-1]
    prompt = f"""Interpret this analysis result for automotive R&D engineers:
Step type: {latest['type']}
Step description: {latest['description']}
Result: {latest.get('text', 'No data')}

Explain in plain Chinese what this means. Keep it under 300 characters."""

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    interpretation = response.content

    prev = state.get("context_summary", "")
    new_summary = f"{prev}\nStep {latest['step_id']}: {latest['description']} | Interpretation: {interpretation}"

    return {"context_summary": new_summary, "next_action": "decide"}


def decide_next(state: AnalysisState) -> Literal["execute", "generate_conclusion"]:
    """Node 5: Deterministic next-action logic (no LLM)."""
    idx = state["current_step_index"]
    plan = state["plan"]

    if idx >= len(plan):
        return "generate_conclusion"

    return "execute"


async def generate_conclusion(state: AnalysisState, config: RunnableConfig) -> dict:
    """Node 6: Generate comprehensive conclusion."""
    app_config = load_config("config.json")
    llm = _get_llm(app_config)

    summary = state.get("context_summary", "")
    prompt = f"""Based on all analysis results, generate a comprehensive conclusion:

Analysis summary:
{summary}

Original request: {state['user_input']}

Output structure:
1. Key findings (3-5 items)
2. Engineering recommendations
3. Notes and caveats
"""

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return {"conclusion": response.content, "next_action": "done"}
