from typing import Union
from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN
from passlib.context import CryptContext
from .database import get_db
from . import models
import time

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

async def get_api_key_record(
    header: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> models.ForgeAPIKey:
    """
    Internal dependency to retrieve the valid API Key record.
    """
    if not header:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

    # TODO - CHILLIEMAN - Still wildy inefficient
    all_keys = db.query(models.ForgeAPIKey).all()
    for key_record in all_keys:
        if verify_key(header, key_record.key_hash):
            # Check Expiration
            if key_record.expires_at and key_record.expires_at < int(time.time()):
                db.delete(key_record)
                db.commit()
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Session expired"
                )
            return key_record

    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )

async def get_current_user(
    key_record: models.ForgeAPIKey = Depends(get_api_key_record)
) -> models.ForgeUser:
    """
    Strict dependency: Requires a USER or SESSION key.
    Rejects WORKER keys.
    """
    if key_record.type == "WORKER":
         raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Worker access denied for this endpoint"
        )
    return key_record.user

async def get_current_actor(
    key_record: models.ForgeAPIKey = Depends(get_api_key_record)
) -> Union[models.ForgeUser, models.ForgeWorker]:
    """
    Flexible dependency: Returns either User or Worker.
    Used for shared endpoints (Tasks, Comments).
    """
    if key_record.type == "WORKER":
        if key_record.worker.deleted_at is not None:
             raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Worker has been deleted"
            )
        return key_record.worker
    return key_record.user

