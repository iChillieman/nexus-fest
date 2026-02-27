from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Union
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
    # Strict: Only Users can create tasks
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
    current_actor: Union[models.ForgeUser, models.ForgeWorker] = Depends(forge_auth.get_current_actor)
):
    # Allow both Users and Workers to view tasks
    if isinstance(current_actor, models.ForgeWorker):
        user_id = current_actor.user_id
    else:
        user_id = current_actor.id

    tasks = forge_crud.get_tasks_by_project(db, project_id=project_id, user_id=user_id, skip=skip, limit=limit)
    return tasks

@router.get("/{task_id}", response_model=forge_schemas.ForgeTaskRead)
def read_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_actor: Union[models.ForgeUser, models.ForgeWorker] = Depends(forge_auth.get_current_actor)
):
    # Allow both Users and Workers to view a specific task
    if isinstance(current_actor, models.ForgeWorker):
        user_id = current_actor.user_id
    else:
        user_id = current_actor.id

    db_task = forge_crud.get_task(db, task_id=task_id, user_id=user_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.put("/{task_id}", response_model=forge_schemas.ForgeTaskRead)
async def update_task(
    task_id: int, 
    task: forge_schemas.ForgeTaskUpdate, 
    db: Session = Depends(get_db),
    current_actor: Union[models.ForgeUser, models.ForgeWorker] = Depends(forge_auth.get_current_actor)
):
    # Determine effective user_id
    if isinstance(current_actor, models.ForgeWorker):
        user_id = current_actor.user_id
        is_worker = True
    else:
        user_id = current_actor.id
        is_worker = False

    db_task = forge_crud.get_task(db, task_id=task_id, user_id=user_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Worker Logic Restrictions
    if is_worker:
        # 1. Must be assigned to this worker
        if db_task.assigned_worker_id != current_actor.id:
            raise HTTPException(status_code=403, detail="Worker not assigned to this task")
        
        # 2. Can only update specific fields
        allowed_fields = {'status_id', 'notes'}
        update_data = task.model_dump(exclude_unset=True)
        for field in update_data.keys():
            if field not in allowed_fields:
                 raise HTTPException(status_code=403, detail=f"Worker cannot update field: {field}")

    updated_task = forge_crud.update_task(db, task_id=task_id, user_id=user_id, task_update=task)
    
    # Broadcast
    task_data = forge_schemas.ForgeTaskRead.model_validate(updated_task).model_dump(mode='json')
    await broadcast_forge_event(updated_task.project_id, "TASK_UPDATED", task_data)

    return updated_task

@router.delete("/{task_id}", response_model=forge_schemas.ForgeTaskRead)
async def delete_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    # Strict: Only Users can delete tasks
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
    # Strict: Only Users can restore tasks
    db_task = forge_crud.restore_task(db, task_id=task_id, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Broadcast
    task_data = forge_schemas.ForgeTaskRead.model_validate(db_task).model_dump(mode='json')
    await broadcast_forge_event(db_task.project_id, "TASK_RESTORED", task_data)

    return db_task

@router.post("/{task_id}/comments", response_model=forge_schemas.ForgeTaskCommentRead)
async def create_comment(
    task_id: int, 
    comment: forge_schemas.ForgeTaskCommentCreate, 
    db: Session = Depends(get_db),
    current_actor: Union[models.ForgeUser, models.ForgeWorker] = Depends(forge_auth.get_current_actor)
):
    # Determine effective user_id
    if isinstance(current_actor, models.ForgeWorker):
        user_id = current_actor.user_id
        author_type = "WORKER"
        author_id = current_actor.id
    else:
        user_id = current_actor.id
        author_type = "USER"
        author_id = current_actor.id

    # Verify task existence
    db_task = forge_crud.get_task(db, task_id=task_id, user_id=user_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    new_comment = forge_crud.create_task_comment(
        db, task_id=task_id, content=comment.content, 
        author_type=author_type, author_id=author_id
    )

    # Broadcast Update to Task (since comments are part of read model)
    # We need to re-fetch the task to get the updated comments list
    db.refresh(db_task)
    task_data = forge_schemas.ForgeTaskRead.model_validate(db_task).model_dump(mode='json')
    await broadcast_forge_event(db_task.project_id, "TASK_UPDATED", task_data)

    return new_comment
