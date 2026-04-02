# filename: app/crud_entries.py
import time
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from . import models, chillieman, schemas
from .constants import DBConstants
from .schemas import EntryWithAgentDetails, AgentResponse

# -----------------------------
# GET ENTRIES
# -----------------------------
def get_entries_for_agent_by_id(db: Session, agent_id: int, thread_id: int | None = None, skip: int = 0, limit: int = 100, is_allowed: bool = False) -> list[schemas.Entry]:
    # You just tried to get an Agents entries with bad password
    if not is_allowed: return [
        chillieman.protec()
    ]

    """
    Returns entries filtered by agent_id and/or thread_id with pagination defaults.
    Always returns Pydantic models.
    """
    query = db.query(models.Entry)
    if agent_id is not None:
        query = query.filter(models.Entry.agent_id == agent_id)
    if thread_id is not None:
        query = query.filter(models.Entry.thread_id == thread_id)

    query = query.offset(skip).limit(limit)
    return [schemas.Entry.model_validate(e) for e in query.all()]

def get_entries_with_agent_details(
    db: Session,
    thread_id: int,
    lowest_entry_id: int = 0,
    limit: int = 100,
) -> list[schemas.EntryWithAgentDetails]:
    """
    Fetch entries for a thread with full agent details (name, type, capabilities)
    in a SINGLE efficient SQL query using JOIN.
    Returns list of Pydantic EntryWithAgentDetails.
    Excludes soft-deleted entries.
    """
    # Base select on Entry, join Agent
    stmt = (
        select(models.Entry)
        .join(models.Agent, models.Entry.agent_id == models.Agent.id)
        .where(models.Entry.thread_id == thread_id)
        .where(models.Entry.deleted_at.is_(None))
        .order_by(models.Entry.timestamp.desc())
        .limit(limit)
    )

    # Only apply the "older than" filter if we actually have a valid lowest_entry_id
    # Skip if it's 0, None, or invalid
    if lowest_entry_id > 0:
        stmt = stmt.where(models.Entry.id < lowest_entry_id)

    result = db.execute(stmt)
    entries = result.scalars().all()  # List of Entry ORM objects (with agent loaded)

    # Convert to Pydantic — agent is already joined, so accessible
    return [
        EntryWithAgentDetails(
            id=e.id,
            content=e.content,
            tags=e.tags,
            agent_id=e.agent_id,
            thread_id=e.thread_id,
            timestamp=e.timestamp,
            deleted_at=e.deleted_at,
            deleted_by=e.deleted_by,
            agent=AgentResponse(
                id=e.agent.id,
                name=e.agent.name,
                type=e.agent.type,
                capabilities=e.agent.capabilities
            )
        )
        for e in entries
    ]

def get_entries_paginated_with_agent(
    db: Session,
    thread_id: int,
    skip: int = 0,
    limit: int = 100
) -> dict:
    stmt = (
        select(models.Entry)
        .join(models.Agent)
        .where(models.Entry.thread_id == thread_id)
        .order_by(models.Entry.timestamp.asc())
    )
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()

    entries = db.execute(stmt.offset(skip).limit(limit)).scalars().all()

    return {
        "items": [
            EntryWithAgentDetails(
                id=e.id,
                content=e.content,
                tags=e.tags,
                agent_id=e.agent_id,
                thread_id=e.thread_id,
                timestamp=e.timestamp,
                agent=AgentResponse(
                    id=e.agent.id,
                    name=e.agent.name,
                    type=e.agent.type,
                    capabilities=e.agent.capabilities
                )
            )
            for e in entries
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": skip + limit < total
    }


def get_latest_timestamp(db: Session):
    entries = get_latest(db=db, amount=1)
    if entries:
        return entries[0].timestamp
    return 0

def get_latest(db: Session, amount: int = 1) -> list[schemas.Entry]:
    query = db.query(models.Entry).order_by(models.Entry.timestamp.desc()).limit(amount)
    return [schemas.Entry.model_validate(e) for e in query.all()]

# -----------------------------
# CREATE ENTRY
# -----------------------------
def create_chillie_boop(db: Session, content: str):
    entry = models.Entry(
        content=content,
        tags=DBConstants.TAG_CREATED_BY_CHILLIEMAN,
        agent_id=1,
        thread_id=DBConstants.ID_BOOP,
        timestamp=int(time.time())
    )

    return create_entry(db=db, entry=entry)

def create_entry(db: Session, entry: schemas.EntryCreate):
    """
    Create a new entry and return as Pydantic model.
    """
    db_entry = models.Entry(
        content=entry.content,
        tags=entry.tags,
        agent_id=entry.agent_id,
        thread_id=entry.thread_id,
        timestamp=int(time.time())
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return schemas.Entry.model_validate(db_entry)


def create_entry_ai(db: Session, content: str, agent_id: int, thread_id: int | None = None):
    """
    Create an AI-generated entry. Defaults to default thread if thread_id is None.
    """
    from .crud_threads import get_default_thread
    if thread_id is None:
        thread_id = get_default_thread(db).id

    db_entry = models.Entry(
        content=content,
        tags=DBConstants.TAG_CREATED_BY_AI,
        agent_id=agent_id,
        thread_id=thread_id,
        timestamp=int(time.time())
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return schemas.Entry.model_validate(db_entry)

def create_entry_chillie_fam(db: Session, content: str, agent_id: int, thread_id: int):
    db_entry = models.Entry(
        content=content,
        tags=DBConstants.TAG_CREATED_BY_CHILLIE_FAM,
        agent_id=agent_id,
        thread_id=thread_id,
        timestamp=int(time.time())
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return schemas.Entry.model_validate(db_entry)


# -----------------------------
# SOFT DELETE ENTRY
# -----------------------------
def soft_delete_entry(db: Session, entry_id: int, deleted_by_agent_id: int) -> models.Entry | None:
    """Soft-delete an entry by setting deleted_at and deleted_by. Returns the entry or None."""
    entry = db.query(models.Entry).filter(models.Entry.id == entry_id).first()
    if entry is None or entry.deleted_at is not None:
        return None
    entry.deleted_at = int(time.time())
    entry.deleted_by = deleted_by_agent_id
    db.commit()
    db.refresh(entry)
    return entry

# -----------------------------
# REPORT ENTRY
# -----------------------------
def report_entry(db: Session, entry_id: int) -> models.Entry | None:
    """Flag an entry as reported, set timestamp, and increment count."""
    entry = db.query(models.Entry).filter(models.Entry.id == entry_id).first()
    if not entry:
        return None
    if entry.reported_at is None:
        entry.reported_at = int(time.time())
    
    # Initialize count if null just in case
    current_count = entry.reported_count if entry.reported_count is not None else 0
    entry.reported_count = current_count + 1
    
    db.commit()
    db.refresh(entry)
    return schemas.Entry.model_validate(entry)

# -----------------------------
# UTILITY: Get entries by agent name
# -----------------------------
def get_all_entries_by_agent_name(db: Session, name: str, thread_id: int | None = None, limit: int = 100, skip: int = 0):
    """
    Returns all entries by any agent with a given name.
    """
    stmt = (
        select(models.Entry)
        .join(models.Agent, models.Entry.agent_id == models.Agent.id)
        .where(models.Agent.name == name)
        .limit(limit)
        .offset(skip)
    )
    entries = db.execute(stmt).scalars().all()
    if thread_id is not None:
        entries = [e for e in entries if e.thread_id == thread_id]
    return [schemas.Entry.model_validate(e) for e in entries]
