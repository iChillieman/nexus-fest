# filename: app/crud_metadata.py
import time

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from . import models, schemas

# --- READ operations ---

def get_metadata(db: Session, agent_id: int) -> schemas.Metadata | None:
    stmt = select(models.Metadata).where(models.Metadata.agent_id == agent_id)
    result = db.execute(stmt).scalar_one_or_none()
    if result:
        return schemas.Metadata.model_validate(result)
    return None

def get_all_metadata(db: Session, skip: int = 0, limit: int = 100) -> list[schemas.Metadata]:
    stmt = select(models.Metadata).offset(skip).limit(limit)
    results = db.execute(stmt).scalars().all()
    return [schemas.Metadata.model_validate(m) for m in results]

# --- CREATE / UPDATE operations ---

def create_metadata(
    db: Session,
    agent_id: int,
    charactership_score: int | None = None,
    ideologies: str | None = None,
    relationships: str | None = None
) -> schemas.Metadata:
    db_meta = models.Metadata(
        agent_id=agent_id,
        charactership_score=charactership_score,
        ideologies=ideologies,
        relationships=relationships,
        timestamp=int(time.time())
    )
    db.add(db_meta)
    db.commit()
    db.refresh(db_meta)
    return schemas.Metadata.model_validate(db_meta)

def update_metadata(
    db: Session,
    agent_id: int,
    charactership_score: int | None = None,
    ideologies: str | None = None,
    relationships: str | None = None
) -> schemas.Metadata | None:
    meta = db.query(models.Metadata).filter(models.Metadata.agent_id == agent_id).one_or_none()
    if not meta:
        return None

    if charactership_score is not None:
        meta.charactership_score = charactership_score
    if ideologies is not None:
        meta.ideologies = ideologies
    if relationships is not None:
        meta.relationships = relationships

    meta.timestamp = int(time.time())

    db.commit()
    db.refresh(meta)
    return schemas.Metadata.model_validate(meta)
