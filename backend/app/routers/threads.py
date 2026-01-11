# filename: app/routers/threads.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, database, crud_threads
from ..anti_spam import rate_limiter

router = APIRouter(prefix="/threads", tags=["threads"])


@router.get("/{thread_id}/entries", response_model=List[schemas.Entry], dependencies=[Depends(rate_limiter)])
def list_entries_for_thread(thread_id: int, db: Session = Depends(database.get_db)):
    thread = crud_threads.get_thread(db, thread_id=thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread.entries


@router.post("/", response_model=schemas.Thread, dependencies=[Depends(rate_limiter)])
def create_thread(thread: schemas.ThreadCreate, db: Session = Depends(database.get_db)):
    return crud_threads.create_thread(db=db, thread=thread)
