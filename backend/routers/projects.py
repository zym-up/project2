"""Project management routes."""
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from backend.deps import pm
from backend.models.schemas import MergeDataRequest

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("")
async def list_projects():
    return pm.list_projects()


@router.post("")
async def create_project(name: str = Form(...), file: UploadFile = File(...)):
    project_id = str(uuid.uuid4())
    upload_dir = Path("uploads") / project_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    content = await file.read()
    file_path.write_bytes(content)
    pid = pm.create_project(name, str(file_path))
    return {"project_id": pid, "name": name}


@router.get("/{project_id}")
async def get_project(project_id: str):
    result = pm.load_project(project_id)
    if result is None:
        raise HTTPException(status_code=404, detail="项目不存在")
    return result


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    pm.delete_project(project_id)
    return {"status": "ok"}


@router.get("/{project_id}/info")
async def get_project_info(project_id: str):
    return pm.get_project_info(project_id)


@router.get("/{project_id}/data")
async def list_data(project_id: str):
    return pm.list_data_files(project_id)


@router.post("/{project_id}/data")
async def add_data(project_id: str, file: UploadFile = File(...)):
    upload_dir = Path("uploads") / project_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    content = await file.read()
    file_path.write_bytes(content)
    return {"filename": pm.add_data(project_id, str(file_path))}


@router.post("/{project_id}/data/merge")
async def merge_data(project_id: str, req: MergeDataRequest):
    df = pm.merge_selected_data(project_id, req.selected_files)
    return {"row_count": len(df), "col_count": len(df.columns)}


@router.get("/{project_id}/reports")
async def list_reports(project_id: str):
    return pm.list_reports(project_id)
