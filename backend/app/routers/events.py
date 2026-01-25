# filename: app/routers/events.py

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas, database, crud_events, crud_threads, chillieman
from ..constants import DBConstants

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/", response_model=List[schemas.Event])
def list_events(tag: Optional[str] = None, db: Session = Depends(database.get_db)):
    return crud_events.get_events(db, tag=tag)

@router.get("/single", response_model=schemas.Event)
def list_events(thread_id: int, db: Session = Depends(database.get_db)):
    boop = crud_events.get_event_from_thread_id(db=db, thread_id=thread_id)
    if boop: return boop
    raise HTTPException(status_code=404, detail="Event not found")



@router.get("/{event_id}", response_model=schemas.EventWithThreads)
def get_event_with_threads(event_id: int, db: Session = Depends(database.get_db)):
    event = crud_events.get_event_with_threads(db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


#######################

API_KEY = "supersecretkey"  # TODO - CHILLIEMAN: load from env and/or find a better place to put this
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)  # auto_error=False = nicer 403

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key

# Disabled for now:
# PROTECTED — only calls with correct header can create events
# @router.post("/", response_model=schemas.Event, dependencies=[Depends(get_api_key)])
# def create_event(event: schemas.EventCreate, db: Session = Depends(database.get_db)):
#     return crud_events.create_event(db=db, event_create=event)
