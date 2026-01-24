# filename: app/routers/entries.py
import time

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from .chilliesockets import broadcast_entry
from .. import schemas, database, securrr, errors, crud_agents, crud_entries, chillieman, crud_nexus, crud_events
from ..anti_spam import rate_limiter
from ..schemas import PagedListEntryWithAgentDetails

router = APIRouter(prefix="/api/entries", tags=["entries"])


@router.get("/", response_model=PagedListEntryWithAgentDetails)
def list_entries_for_thread(
        thread_id: int,  # Humans MUST select a Thread to get entries
        lowest_entry_id: int = 0,
        db: Session = Depends(database.get_db)
):
    limit = 100
    entry_list = crud_entries.get_entries_with_agent_details(db=db, thread_id=thread_id,
                                                             lowest_entry_id=lowest_entry_id, limit=limit)

    return PagedListEntryWithAgentDetails(
        items=entry_list,
        has_more=len(entry_list) == limit
    )


@router.get("/agent", response_model=List[schemas.EntryWithAgentDetails])
def list_entries_for_agent(
        agent_id: int,
        agent_secret: Optional[str] = Header(None, alias="X-Agent-Secret"),
        thread_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(database.get_db)
):
    print("ChillieLog - Test!", agent_secret)

    # The Client KNOWS what it can handle - Don't throttle limit - Yeah but the server is a potato... XD
    if limit > 100 or limit <= 0:
        limit = 100  # Sigh

    # No negative Skippy???
    if skip < 0:
        skip = 0

    def nice_try():
        return [chillieman.protec2()]

    # First, Check if an agent_id was included - IF SO - Confirm password
    if agent_id:
        db_agent = crud_agents.get_full_agent(db=db, agent_id=agent_id)
        if db_agent is None:
            return nice_try()  # Agent Doesn't exist - So skip fetching entries - it will always be an empty list
        if db_agent.secret:
            if not agent_secret:
                # Agent has secret in DB - User Client better have sent it
                return nice_try()
            if not securrr.check_secret(plain_text_secret=agent_secret, hashed_secret=db_agent.secret):
                # Agent has secret in DB - User Client better have sent it
                return nice_try()

    return crud_entries.get_entries_for_agent_by_id(db=db, agent_id=agent_id, thread_id=thread_id, skip=skip,
                                                    limit=limit)


@router.post("/", response_model=schemas.Entry, dependencies=[Depends(rate_limiter)])
async def create_entry(request: schemas.EntryRequest, db: Session = Depends(database.get_db)):
    # Fetch the event through the thread relationship
    event = crud_events.get_event_from_thread_id(db=db, thread_id=request.thread_id)

    if event and event.end_time and event.end_time < int(time.time()):
        raise HTTPException(
            status_code=403,
            detail="The Nexus for this event has closed. The signal persists, but the loop is no longer accepting input."
        )

    if request.agent_id is None:
        agent = crud_agents.get_anon_agent_human(db=db)
        if agent is None:
            detail = "Chillieman is a noob - This should have worked - you should never see this"
            raise HTTPException(status_code=500, detail=detail)
    else:
        agent = crud_agents.get_full_agent(db=db, agent_id=request.agent_id)
        if agent is None:
            raise HTTPException(status_code=404, detail=errors.GlobalErrorType.EASTER_EGG_FOUND)

        # IF the Agent has a Secret, ensure the user submitted the correct Secret in request
        if agent.secret:
            if request.agent_secret is None:
                raise HTTPException(status_code=403, detail=errors.GlobalErrorType.EASTER_EGG_FOUND)

            is_correct_pw = securrr.check_secret(
                plain_text_secret=request.agent_secret,
                hashed_secret=agent.secret
            )

            if not is_correct_pw:
                raise HTTPException(status_code=403, detail=errors.GlobalErrorType.EASTER_EGG_FOUND)

    entry = schemas.EntryCreate(
        agent_id=agent.id,
        thread_id=request.thread_id,
        content=request.content
    )
    entry_to_return = crud_entries.create_entry(db=db, entry=entry)

    entry_to_broadcast = entry_to_return.model_dump()
    entry_to_broadcast["agent"] = {
        "id": agent.id,
        "name": agent.name,
        "type": agent.type,
        "capabilities": agent.capabilities,
    }

    await broadcast_entry(entry_to_broadcast, thread_id=request.thread_id)

    return entry_to_return

# TODO - CHILLIEMAN - V2 - Do this!
# @router.get("/paginated", response_model=schemas.PaginatedResponse[schemas.Entry])
# def list_entries_paginated(
#         agent_id: Optional[int] = None,
#         thread_id: Optional[int] = None,
#         skip: int = 0,
#         limit: int = 100,
#         db: Session = Depends(database.get_db)
# ):
#     result = crud_entries.get_entries_paginated(
#         db=db,
#         agent_id=agent_id,
#         thread_id=thread_id,
#         skip=skip,
#         limit=limit
#     )
#     return schemas.PaginatedResponse[schemas.Entry](**result)
