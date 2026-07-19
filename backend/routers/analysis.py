"""Analysis routes — LangGraph StateGraph-driven streaming API."""
import json
import logging

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.runnables import RunnableConfig

from backend.models.schemas import AnalysisRunRequest
from backend.deps import pm, get_workflow

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def _sanitize(obj):
    """Recursively replace NaN/Infinity with None."""
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    return obj


def _load_df(project_id: str) -> pd.DataFrame:
    """Load and merge project data."""
    project = pm.load_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="项目不存在")
    data_files = pm.list_data_files(project_id)
    if not data_files:
        raise HTTPException(status_code=400, detail="项目没有数据文件")
    return pm.merge_selected_data(project_id, data_files)


@router.post("/run/stream")
async def run_analysis_stream(req: AnalysisRunRequest):
    """Streaming analysis — LangGraph drives all nodes automatically.

    SSE event types:
    - llm_token: LLM streaming token
    - tool_start / tool_end: Tool call lifecycle
    - chain_end: Node completed with state update
    - done: Workflow complete
    - error: Error message
    """
    try:
        df = _load_df(req.project_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据加载失败: {e}")

    workflow = get_workflow()
    config: RunnableConfig = {"configurable": {"thread_id": req.project_id}}

    initial_state = {
        "user_input": req.user_input,
        "project_id": req.project_id,
        "df": df,
        "plan": [],
        "current_step_index": 0,
        "results": [],
        "context_summary": "",
        "next_action": "execute",
        "error_message": "",
        "rag_context": "",
        "conclusion": "",
    }

    async def event_gen():
        try:
            async for event in workflow.astream_events(initial_state, config=config, version="v2"):
                event_type = event.get("event", "")

                if event_type == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk", {})
                    if hasattr(chunk, "content") and chunk.content:
                        yield f"data: {json.dumps({'type': 'llm_token', 'content': chunk.content}, ensure_ascii=False)}\n\n"

                elif event_type == "on_tool_start":
                    yield f"data: {json.dumps({'type': 'tool_start', 'tool': event.get('name', 'unknown')}, ensure_ascii=False)}\n\n"

                elif event_type == "on_tool_end":
                    output = _sanitize(event.get("data", {}).get("output", {}))
                    yield f"data: {json.dumps({'type': 'tool_end', 'tool': event.get('name', 'unknown'), 'output': output}, ensure_ascii=False)}\n\n"

                elif event_type == "on_chain_end":
                    name = event.get("name", "")
                    output = event.get("data", {}).get("output", {})
                    if isinstance(output, dict):
                        yield f"data: {json.dumps({'type': 'chain_end', 'node': name, 'state_update': _sanitize(output)}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logger.exception("Graph execution error")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
