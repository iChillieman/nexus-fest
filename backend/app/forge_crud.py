from sqlalchemy.orm import Session
from sqlalchemy import or_
import time
from . import models, forge_schemas, forge_auth

# --- User CRUD ---
def get_user_by_username(db: Session, username: str):
    return db.query(models.ForgeUser).filter(models.ForgeUser.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.ForgeUser).filter(models.ForgeUser.email == email).first()

def create_user(db: Session, user: forge_schemas.ForgeUserCreate):
    hashed_password = forge_auth.get_hash(user.password)
    db_user = models.ForgeUser(
        username=user.username, 
        email=user.email, 
        password_hash=hashed_password,
        created_at=int(time.time())
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Project CRUD ---
def get_project(db: Session, project_id: int, user_id: int, include_deleted: bool = False):
    query = db.query(models.ForgeProject).filter(models.ForgeProject.owner_id == user_id)
    if not include_deleted:
        query = query.filter(models.ForgeProject.deleted_at == None)
    return query.filter(models.ForgeProject.id == project_id).first()

def get_project_by_name(db: Session, name: str, user_id: int, include_deleted: bool = False):
    query = db.query(models.ForgeProject).filter(models.ForgeProject.owner_id == user_id)
    if not include_deleted:
        query = query.filter(models.ForgeProject.deleted_at == None)
    return query.filter(models.ForgeProject.name == name).first()

def get_projects(db: Session, user_id: int, skip: int = 0, limit: int = 100, include_deleted: bool = False):
    query = db.query(models.ForgeProject).filter(models.ForgeProject.owner_id == user_id)
    if not include_deleted:
        query = query.filter(models.ForgeProject.deleted_at == None)
    return query.offset(skip).limit(limit).all()

def create_project(db: Session, project: forge_schemas.ForgeProjectCreate, user_id: int):
    now = int(time.time())
    db_project = models.ForgeProject(
        name=project.name, 
        description=project.description,
        owner_id=user_id,
        created_at=now,
        updated_at=now
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: int, user_id: int, project_update: forge_schemas.ForgeProjectUpdate):
    db_project = get_project(db, project_id, user_id)
    if db_project:
        update_data = project_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)
        db_project.updated_at = int(time.time())
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int, user_id: int):
    db_project = get_project(db, project_id, user_id)
    if db_project:
        db_project.deleted_at = int(time.time())
        db.commit()
        db.refresh(db_project)
    return db_project

def restore_project(db: Session, project_id: int, user_id: int):
    # Retrieve even if deleted
    db_project = db.query(models.ForgeProject).filter(
        models.ForgeProject.id == project_id,
        models.ForgeProject.owner_id == user_id
    ).first()
    
    if db_project:
        db_project.deleted_at = None
        db.commit()
        db.refresh(db_project)
    return db_project


# --- Task CRUD ---
def get_task(db: Session, task_id: int, user_id: int, include_deleted: bool = False):
    query = db.query(models.ForgeTask).join(models.ForgeProject).filter(models.ForgeProject.owner_id == user_id)
    if not include_deleted:
        query = query.filter(models.ForgeTask.deleted_at == None)
    return query.filter(models.ForgeTask.id == task_id).first()

def get_tasks_by_project(db: Session, project_id: int, user_id: int, skip: int = 0, limit: int = 100):
    # Verify ownership via project
    project = get_project(db, project_id, user_id)
    if not project:
        return []
    
    return db.query(models.ForgeTask).filter(
        models.ForgeTask.project_id == project_id,
        models.ForgeTask.deleted_at == None
    ).offset(skip).limit(limit).all()

def create_task(db: Session, task: forge_schemas.ForgeTaskCreate, user_id: int):
    project = get_project(db, task.project_id, user_id)
    if not project:
        return None
    now = int(time.time())
    db_task = models.ForgeTask(
        title=task.title, 
        description=task.description, 
        detail=task.detail, # New Field
        notes=task.notes,   # New Field
        assigned_worker_id=task.assigned_worker_id, # New Field
        project_id=task.project_id,
        created_at=now,
        updated_at=now
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, user_id: int, task_update: forge_schemas.ForgeTaskUpdate):
    db_task = get_task(db, task_id, user_id)
    if db_task:
        # Filter out unset values
        update_data = task_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
            
        db_task.updated_at = int(time.time())
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int, user_id: int):
    db_task = get_task(db, task_id, user_id)
    if db_task:
        db_task.deleted_at = int(time.time())
        db.commit()
        db.refresh(db_task)
    return db_task

def restore_task(db: Session, task_id: int, user_id: int):
    # Retrieve even if deleted
    db_task = db.query(models.ForgeTask).join(models.ForgeProject).filter(
        models.ForgeTask.id == task_id,
        models.ForgeProject.owner_id == user_id
    ).first()
    
    if db_task:
        db_task.deleted_at = None
        db.commit()
        db.refresh(db_task)
    return db_task
    
# --- Status CRUD ---
def seed_forge_statuses(db: Session):
    if db.query(models.ForgeStatus).count() == 0:
        statuses = [
            models.ForgeStatus(id=1, name="To Do"),
            models.ForgeStatus(id=2, name="In Progress"),
            models.ForgeStatus(id=3, name="Done"),
            models.ForgeStatus(id=4, name="Blocked")
        ]
        db.add_all(statuses)
        db.commit()

# --- Comment CRUD ---
def create_task_comment(db: Session, task_id: int, content: str, author_type: str, author_id: int):
    now = int(time.time())
    comment = models.ForgeTaskComment(
        task_id=task_id,
        content=content,
        author_type=author_type,
        author_id=author_id,
        created_at=now
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
