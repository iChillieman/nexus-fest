from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ... import forge_schemas, forge_crud, forge_auth, models
from ...database import get_db
from .sockets import broadcast_forge_event

router = APIRouter(
    prefix="/tasks",
    tags=["forge-tasks"],
)

@router.post("/", response_model=forge_schemas.ForgeTaskRead)
async def create_task(
    task: forge_schemas.ForgeTaskCreate, 
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    # Verify project exists and belongs to user before creating a task for it
    db_project = forge_crud.get_project(db, project_id=task.project_id, user_id=current_user.id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found, cannot create task")
    
    new_task = forge_crud.create_task(db=db, task=task, user_id=current_user.id)
    
    # Broadcast
    task_data = forge_schemas.ForgeTaskRead.model_validate(new_task).model_dump(mode='json')
    await broadcast_forge_event(task.project_id, "TASK_CREATED", task_data)
    
    return new_task

@router.get("/project/{project_id}", response_model=List[forge_schemas.ForgeTaskRead])
def read_tasks_for_project(
    project_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    tasks = forge_crud.get_tasks_by_project(db, project_id=project_id, user_id=current_user.id, skip=skip, limit=limit)
    return tasks

@router.put("/{task_id}", response_model=forge_schemas.ForgeTaskRead)
async def update_task(
    task_id: int, 
    task: forge_schemas.ForgeTaskUpdate, 
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    db_task = forge_crud.update_task(db, task_id=task_id, user_id=current_user.id, task_update=task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Broadcast
    task_data = forge_schemas.ForgeTaskRead.model_validate(db_task).model_dump(mode='json')
    await broadcast_forge_event(db_task.project_id, "TASK_UPDATED", task_data)

    return db_task

@router.delete("/{task_id}", response_model=forge_schemas.ForgeTaskRead)
async def delete_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    db_task = forge_crud.delete_task(db, task_id=task_id, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Broadcast
    task_data = forge_schemas.ForgeTaskRead.model_validate(db_task).model_dump(mode='json')
    await broadcast_forge_event(db_task.project_id, "TASK_DELETED", task_data)

    return db_task

@router.post("/{task_id}/restore", response_model=forge_schemas.ForgeTaskRead)
async def restore_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    db_task = forge_crud.restore_task(db, task_id=task_id, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Broadcast
    task_data = forge_schemas.ForgeTaskRead.model_validate(db_task).model_dump(mode='json')
    await broadcast_forge_event(db_task.project_id, "TASK_RESTORED", task_data)

    return db_task
