from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import secrets
from ... import forge_schemas, forge_crud, models, forge_auth
from ...database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["forge-auth"],
)

@router.post("/register", response_model=forge_schemas.ForgeRegisterResponse)
def register(user: forge_schemas.ForgeUserCreate, db: Session = Depends(get_db)):
    if forge_crud.get_user_by_username(db, username=user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if forge_crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = forge_crud.create_user(db, user=user)
    
    raw_key = secrets.token_urlsafe(32)
    key_hash = forge_auth.get_hash(raw_key)
    
    api_key = models.ForgeAPIKey(
        key_hash=key_hash,
        name="Default Key",
        user_id=db_user.id,
        created_at=db_user.created_at
    )
    db.add(api_key)
    db.commit()
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "created_at": db_user.created_at,
        "api_key": raw_key
    }

@router.post("/login", response_model=forge_schemas.ForgeRegisterResponse)
def login(login_request: forge_schemas.ForgeLoginRequest, db: Session = Depends(get_db)):
    user = forge_crud.get_user_by_username(db, username=login_request.username)
    if not user or not forge_auth.verify_key(login_request.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    raw_key = secrets.token_urlsafe(32)
    key_hash = forge_auth.get_hash(raw_key)
    
    api_key = models.ForgeAPIKey(
        key_hash=key_hash,
        name="Session Key",
        user_id=user.id,
        created_at=int(time.time())
    )
    db.add(api_key)
    db.commit()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at,
        "api_key": raw_key
    }
