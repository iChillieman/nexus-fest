# filename: app/routers/events.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas, database, crud_events, chillieman
from ..constants import DBConstants
from ..securrr import get_api_key_chillie

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/", response_model=List[schemas.Event])
def list_events(tag: Optional[str] = None, db: Session = Depends(database.get_db)):
    return crud_events.get_events(db, tag=tag)

@router.get("/single", response_model=schemas.Event)
def list_events(thread_id: int, agent_id: int, db: Session = Depends(database.get_db)):
    boop = crud_events.get_event_from_thread_id(db=db, thread_id=thread_id)
    if not boop: raise HTTPException(status_code=404, detail="Event not found")
    if DBConstants.TAG_SNEAKY in boop.tags:
        if agent_id == 0 or chillieman.pat_down(db,agent_id): return chillieman.shit(db,agent_id)
    return boop


@router.get("/{event_id}", response_model=schemas.EventWithThreads)
def get_event_with_threads(event_id: int, db: Session = Depends(database.get_db)):
    event = crud_events.get_event_with_threads(db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


#######################

# only chillieman can create new events
@router.post("/", response_model=schemas.Event, dependencies=[Depends(get_api_key_chillie)])
def create_event(event: schemas.EventCreate, db: Session = Depends(database.get_db)):
    return crud_events.create_event(db=db, event_create=event)
