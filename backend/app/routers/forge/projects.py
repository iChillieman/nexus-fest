from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ... import forge_schemas, forge_crud, forge_auth, models
from ...database import get_db

router = APIRouter(
    prefix="/projects",
    tags=["forge-projects"],
)

@router.post("/", response_model=forge_schemas.ForgeProjectRead)
def create_project(
    project: forge_schemas.ForgeProjectCreate, 
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    db_project = forge_crud.get_project_by_name(db, name=project.name, user_id=current_user.id)
    if db_project:
        raise HTTPException(status_code=400, detail="You already have a project with this name")
    return forge_crud.create_project(db=db, project=project, user_id=current_user.id)

@router.get("/", response_model=List[forge_schemas.ForgeProjectRead])
def read_projects(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    projects = forge_crud.get_projects(db, user_id=current_user.id, skip=skip, limit=limit)
    return projects

@router.get("/{project_id}", response_model=forge_schemas.ForgeProjectRead)
def read_project(
    project_id: int, 
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    db_project = forge_crud.get_project(db, project_id=project_id, user_id=current_user.id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.put("/{project_id}", response_model=forge_schemas.ForgeProjectRead)
def update_project(
    project_id: int, 
    project: forge_schemas.ForgeProjectUpdate, 
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    db_project = forge_crud.update_project(db, project_id=project_id, user_id=current_user.id, project_update=project)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.delete("/{project_id}", response_model=forge_schemas.ForgeProjectRead)
def delete_project(
    project_id: int, 
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    db_project = forge_crud.delete_project(db, project_id=project_id, user_id=current_user.id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project
