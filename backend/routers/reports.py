"""Report generation routes."""
import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, FileResponse

from backend.models.schemas import GenerateReportRequest, ConcludeRequest
from backend.deps import pm, get_workflow
from engine.reporter import generate_html_report, build_section

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/report", tags=["report"])


@router.post("/generate")
async def generate_report(req: GenerateReportRequest):
    project = pm.load_project(req.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="项目不存在")

    state = project.get("state", {})
    rounds = state.get("rounds", [])
    sections = []

    for round_data in rounds:
        for step in round_data.get("steps", []):
            if step.get("status") == "done":
                sections.append(build_section(
                    title=step.get("description", "分析步骤"),
                    text=step.get("text", ""),
                ))

    html = generate_html_report(
        title=req.title,
        sections=sections,
        conclusion=project.get("conclusion", ""),
        data_source=project.get("meta", {}).get("data_file", ""),
        rows=0,
        cols=0,
    )

    report_path = pm.save_report(req.project_id, html)
    return {"report_path": report_path, "status": "ok"}


@router.post("/conclude/stream")
async def conclude_stream(req: ConcludeRequest):
    workflow = get_workflow()

    async def event_gen():
        try:
            async for event in workflow.astream_events(
                {"user_input": req.user_notes or "Generate conclusion"},
                config={"configurable": {"thread_id": req.project_id}},
                version="v2",
            ):
                event_type = event.get("event", "")
                if event_type == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk", {})
                    if hasattr(chunk, "content") and chunk.content:
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk.content}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@router.get("/download/{project_id}")
async def download_latest(project_id: str):
    reports = pm.list_reports(project_id)
    if not reports:
        raise HTTPException(status_code=404, detail="无报告")
    latest = sorted(reports)[-1]
    filepath = Path("projects") / project_id / "reports" / latest
    return FileResponse(str(filepath), media_type="text/html", filename=latest)
