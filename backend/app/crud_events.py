# filename: app/crud_events.py

import time
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from typing import Optional, List
from . import models, schemas


def get_events(
        db: Session,
        tag: Optional[str] = None,
        order_by: str = "start_time",
        direction: str = "asc"
) -> list[type[schemas.Event]]:
    """
    Fetch events with optional tag filtering, pagination, and sorting.
    Returns Pydantic-safe Event objects.
    """
    query = db.query(models.Event)

    if tag:
        query = query.filter(models.Event.tags.contains(tag))

    # Sorting
    if hasattr(models.Event, order_by):
        column = getattr(models.Event, order_by)
        query = query.order_by(column.desc() if direction == "desc" else column.asc())

    return query.all()


def get_events_paginated(
        db: Session,
        tag: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "start_time",
        direction: str = "asc"
) -> schemas.PaginatedResponse[schemas.Event]:
    """
    Fetch events with optional tag filtering, pagination, and sorting.
    Returns Pydantic-safe Event objects.
    """
    query = db.query(models.Event)

    if tag:
        query = query.filter(models.Event.tags.contains(tag))

    # Sorting
    if hasattr(models.Event, order_by):
        column = getattr(models.Event, order_by)
        query = query.order_by(column.desc() if direction == "desc" else column.asc())

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    items_response = [schemas.Event.model_validate(event) for event in items]
    has_next = skip + limit < total

    return schemas.PaginatedResponse(
        items=items_response,
        total=total,
        skip=skip,
        limit=limit,
        has_next=has_next
    )

def create_event(db: Session, event_create: schemas.EventCreate) -> schemas.Event:
    """
    Create a new Event in the DB and return it as Pydantic-safe Event.
    """
    db_event = models.Event(
        title=event_create.title,
        description=event_create.description,
        tags=event_create.tags,
        max_thread_amount=event_create.max_thread_amount,
        start_time=event_create.start_time or int(time.time()),
        end_time=event_create.end_time
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return schemas.Event.model_validate(db_event)

def get_event_with_threads(db: Session, event_id: int) -> schemas.EventWithThreads | None:
    """
    Fetch Event + all Threads (with entry count) in a SINGLE query.
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).one_or_none()
    if not event:
        return None

    stmt = (
        select(
            models.Thread,
            func.count(models.Entry.id).label("entry_count")
        )
        .outerjoin(models.Entry, models.Entry.thread_id == models.Thread.id)
        .where(models.Thread.event_id == event_id)
        .group_by(models.Thread.id)
    )

    result = db.execute(stmt).all()  # Each row is (Thread, entry_count)
    threads_with_count = []
    for thread, count in result:
        thread.entry_count = count
        threads_with_count.append(schemas.ThreadWithCount.model_validate(thread))

    return schemas.EventWithThreads(
        **schemas.Event.model_validate(event).model_dump(),
        threads=threads_with_count
    )
