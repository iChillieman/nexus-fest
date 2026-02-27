from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import secrets
import time
from ... import forge_schemas, forge_crud, forge_auth, models
from ...database import get_db

router = APIRouter(
    prefix="/workers",
    tags=["forge-workers"],
)

@router.get("/", response_model=List[forge_schemas.ForgeWorkerRead])
def list_workers(
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    """List all workers owned by the current user."""
    return [w for w in current_user.workers if w.deleted_at is None]

@router.post("/", response_model=forge_schemas.ForgeWorkerRead)
def create_worker(
    worker_data: forge_schemas.ForgeWorkerCreate,
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    """Create a new worker."""
    now = int(time.time())
    new_worker = models.ForgeWorker(
        name=worker_data.name,
        user_id=current_user.id,
        created_at=now
    )
    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)
    return new_worker

@router.delete("/{worker_id}")
def delete_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    """Delete a worker."""
    worker = db.query(models.ForgeWorker).filter(
        models.ForgeWorker.id == worker_id,
        models.ForgeWorker.user_id == current_user.id,
        models.ForgeWorker.deleted_at == None
    ).first()
    
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    worker.deleted_at = int(time.time())
    db.commit()
    return {"message": "Worker deleted"}

@router.post("/{worker_id}/keys", response_model=forge_schemas.ForgeAPIKeyResponse)
def create_worker_key(
    worker_id: int,
    key_data: forge_schemas.ForgeAPIKeyCreate,
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    """Create an API Key for a specific worker."""
    # Verify worker ownership
    worker = db.query(models.ForgeWorker).filter(
        models.ForgeWorker.id == worker_id,
        models.ForgeWorker.user_id == current_user.id,
        models.ForgeWorker.deleted_at == None
    ).first()
    
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    raw_key = secrets.token_urlsafe(32)
    key_hash = forge_auth.get_hash(raw_key)
    now = int(time.time())

    api_key = models.ForgeAPIKey(
        key_hash=key_hash,
        name=key_data.name,
        worker_id=worker.id,
        user_id=None, # Explicitly None for Worker Keys
        type="WORKER",
        created_at=now,
        expires_at=None # Worker keys don't expire by default
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return {
        "id": api_key.id,
        "name": api_key.name,
        "created_at": api_key.created_at,
        "expires_at": api_key.expires_at,
        "api_key": raw_key
    }
