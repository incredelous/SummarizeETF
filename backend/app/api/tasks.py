from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import RefreshTask
from app.schemas import RefreshTaskResponse
from app.tasks.update_indices import create_refresh_task, run_refresh

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/refresh", response_model=RefreshTaskResponse)
def trigger_refresh(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task = create_refresh_task(db)
    background_tasks.add_task(run_refresh, task.task_id)
    return RefreshTaskResponse(
        task_id=task.task_id,
        status=task.status,
        started_at=task.started_at,
        finished_at=task.finished_at,
        message=task.message,
    )


@router.get("/refresh/{task_id}", response_model=RefreshTaskResponse)
def get_refresh_task(task_id: str, db: Session = Depends(get_db)):
    task: RefreshTask | None = db.get(RefreshTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return RefreshTaskResponse(
        task_id=task.task_id,
        status=task.status,
        started_at=task.started_at,
        finished_at=task.finished_at,
        message=task.message,
    )

