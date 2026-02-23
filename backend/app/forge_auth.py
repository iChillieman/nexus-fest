from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN
from passlib.context import CryptContext
from .database import get_db
from . import models

# Context for hashing API keys
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# The header key we expect
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_key(plain_key: str, hashed_key: str) -> bool:
    """Verifies a plain API key against a hash."""
    return pwd_context.verify(plain_key, hashed_key)

def get_hash(plain_key: str) -> str:
    """Hashes a plain API key."""
    return pwd_context.hash(plain_key)

async def get_current_user(
    header: str = Security(api_key_header),
    db: Session = Depends(get_db)
):
    """
    Dependency that retrieves the user associated with the given API key.
    If the key is invalid or missing, raises 403.
    """
    if not header:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

    # TODO - CHILLIEMAN - Filter this by username - this seems WILDLY inefficient (huge datasets might lag)
    all_keys = db.query(models.ForgeAPIKey).all()
    for key_record in all_keys:
        if verify_key(header, key_record.key_hash):
            return key_record.user

    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )
