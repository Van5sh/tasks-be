from fastapi import APIRouter, Depends, HTTPException, Query
from bson.errors import InvalidId
from app.db.database import get_db
from app.dependency.auth import get_current_user
from app.models.tasks import TaskCreate, TaskUpdate, TaskOut
from app.services.tasks_service import (
    create_task,
    list_tasks,
    get_task,
    update_task,
    delete_task,
)

router = APIRouter()


@router.post("/tasks", response_model=TaskOut)
async def create(task: TaskCreate, db=Depends(get_db), user=Depends(get_current_user)):
    return await create_task(db, user["sub"], task)


@router.get("/tasks", response_model=list[TaskOut])
async def list_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    return await list_tasks(db, user["sub"], skip, limit)


@router.get("/tasks/{task_id}", response_model=TaskOut)
async def get_one(task_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        task = await get_task(db, user["sub"], task_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid task id")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=TaskOut)
async def update(task_id: str, task: TaskUpdate, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        updated = await update_task(db, user["sub"], task_id, task)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid task id")
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/tasks/{task_id}")
async def remove(task_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        ok = await delete_task(db, user["sub"], task_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid task id")
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}
