# filename: app/crud_threads.py
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from . import models, schemas
import time
from .constants import DBConstants

# -----------------------------
# GET THREADS
# -----------------------------
def get_threads(db: Session, event_id: int | None = None, skip: int = 0, limit: int = 100):
    """
    Returns threads filtered by event_id, paginated, as Pydantic models.
    """
    query = db.query(models.Thread)
    if event_id is not None:
        query = query.filter(models.Thread.event_id == event_id)

    threads = query.offset(skip).limit(limit).all()
    return [schemas.Thread.model_validate(t) for t in threads]


def get_threads_paginated(db: Session, event_id: int | None = None, skip: int = 0,
                          limit: int = 100, order_by: str = "created_at",
                          direction: str = "asc"):
    """
    Paginated threads with total count, ready for API.
    """
    query = db.query(models.Thread)
    if event_id is not None:
        query = query.filter(models.Thread.event_id == event_id)

    # Optional sorting
    column = getattr(models.Thread, order_by, None)
    if column is not None:
        query = query.order_by(column.asc() if direction == "asc" else column.desc())

    total = query.count()
    items = query.offset(skip).limit(limit).all()
    has_next = skip + limit < total

    return schemas.PaginatedResponse[schemas.Thread](
        items=[schemas.Thread.model_validate(t) for t in items],
        total=total,
        skip=skip,
        limit=limit,
        has_next=has_next
    )


def get_thread(db: Session, thread_id: int):
    """
    Get a single thread by ID.
    """
    t = db.query(models.Thread).filter(models.Thread.id == thread_id).one_or_none()
    if t:
        return schemas.Thread.model_validate(t)
    return None


def get_default_thread(db: Session):
    """
    Returns the default "Big Bang" thread.
    """
    t = db.query(models.Thread).filter(models.Thread.title == DBConstants.DEFAULT_THREAD_NAME).first()
    return schemas.Thread.model_validate(t) if t else None


# -----------------------------
# CREATE THREAD
# -----------------------------
def create_thread(db: Session, thread: schemas.ThreadCreate):
    """
    Create a new thread under a specific event. Returns Pydantic model.
    """
    event = db.query(models.Event).filter(models.Event.id == thread.event_id).one_or_none()
    if event is None:
        raise ValueError("Event not found")

    if get_thread_count_for_event(db, thread.event_id) >= event.max_thread_amount:
        raise ValueError("Max threads reached for this event")

    db_thread = models.Thread(
        title=thread.title,
        event_id=thread.event_id,
        created_at=int(time.time())
    )
    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)
    return schemas.Thread.model_validate(db_thread)


# -----------------------------
# THREAD COUNTS
# -----------------------------
def get_thread_count_for_event(db: Session, event_id: int) -> int:
    """
    Return number of threads under a specific event.
    """
    return db.query(func.count(models.Thread.id)).filter(models.Thread.event_id == event_id).scalar()
