import time
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from typing import List
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
        created_at=db_user.created_at,
        expires_at=None
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
    # verify_key is used for passwords too here? "forge_auth.verify_key(login_request.password, user.password_hash)"
    # Ah, verify_key uses pwd_context.verify which works for argon2 hashes (passwords) and api keys.
    if not user or not forge_auth.verify_key(login_request.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    raw_key = secrets.token_urlsafe(32)
    key_hash = forge_auth.get_hash(raw_key)
    
    now = int(time.time())
    expires_at = now + 3600 # 1 Hour Expiration

    api_key = models.ForgeAPIKey(
        key_hash=key_hash,
        name="Session Key",
        user_id=user.id,
        created_at=now,
        expires_at=expires_at
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

@router.post("/logout")
def logout(
    header: str = Security(forge_auth.api_key_header),
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    """
    Invalidates the current session token.
    """
    # Find the specific key used for this session
    # Since we don't have the key record from get_current_user, we must find it again.
    # We can iterate only the current user's keys for efficiency.
    
    for key_record in current_user.api_keys:
        if forge_auth.verify_key(header, key_record.key_hash):
            db.delete(key_record)
            db.commit()
            return {"message": "Logged out successfully"}
            
    # Should technically not happen if get_current_user passed, unless race condition or magic.
    return {"message": "Session not found"}

# --- API Key Management Endpoints ---

@router.get("/keys", response_model=List[forge_schemas.ForgeAPIKeyRead])
def get_api_keys(
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    """List all API keys for the current user."""
    # current_user.api_keys is a relationship, so it returns a list of ForgeAPIKey objects
    return current_user.api_keys

@router.post("/keys", response_model=forge_schemas.ForgeAPIKeyResponse)
def create_api_key(
    key_data: forge_schemas.ForgeAPIKeyCreate,
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    """Create a new permanent API key."""
    raw_key = secrets.token_urlsafe(32)
    key_hash = forge_auth.get_hash(raw_key)
    
    now = int(time.time())

    api_key = models.ForgeAPIKey(
        key_hash=key_hash,
        name=key_data.name,
        user_id=current_user.id,
        created_at=now,
        expires_at=None # Never expires
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    # Manually construct response to include the raw key
    return {
        "id": api_key.id,
        "name": api_key.name,
        "created_at": api_key.created_at,
        "expires_at": api_key.expires_at,
        "api_key": raw_key
    }

@router.put("/keys/{key_id}", response_model=forge_schemas.ForgeAPIKeyRead)
def update_api_key(
    key_id: int,
    key_update: forge_schemas.ForgeAPIKeyUpdate,
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    """Rename an API key."""
    # Find the key belonging to the user
    key_record = db.query(models.ForgeAPIKey).filter(
        models.ForgeAPIKey.id == key_id,
        models.ForgeAPIKey.user_id == current_user.id
    ).first()

    if not key_record:
        raise HTTPException(status_code=404, detail="API Key not found")

    key_record.name = key_update.name
    db.commit()
    db.refresh(key_record)
    return key_record

@router.delete("/keys/{key_id}")
def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: models.ForgeUser = Depends(forge_auth.get_current_user)
):
    """Revoke (Delete) an API key."""
    key_record = db.query(models.ForgeAPIKey).filter(
        models.ForgeAPIKey.id == key_id,
        models.ForgeAPIKey.user_id == current_user.id
    ).first()

    if not key_record:
        raise HTTPException(status_code=404, detail="API Key not found")

    db.delete(key_record)
    db.commit()
    return {"message": "API Key revoked successfully"}
