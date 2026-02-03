from app import database, schemas, crud_agents, crud_entries, crud_events
from app.routers.chilliesockets import broadcast_entry
from app.securrr import get_api_key_dae, get_api_key_zeph
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/chillie", tags=["ChillieFam"])

@router.post("/mouth/dae", response_model=schemas.Entry, dependencies=[Depends(get_api_key_dae)])
async def ai_chillie_mouth_dae(request: schemas.AIAdminMouthRequest, db: Session = Depends(database.get_db)):
    # TODO -> Ensure this request came from Dae's Home IP address
    agent = crud_agents.get_dae(db)
    return await ai_chillie_fam_speaks(request=request, agent=agent, db=db)

@router.post("/mouth/zeph", response_model=schemas.Entry, dependencies=[Depends(get_api_key_zeph)])
async def ai_chillie_mouth_zeph(request: schemas.AIAdminMouthRequest, db: Session = Depends(database.get_db)):
    # TODO -> Ensure this request came from Zeph's Home IP address
    agent = crud_agents.get_zeph(db)
    return await ai_chillie_fam_speaks(request=request, agent=agent, db=db)


async def ai_chillie_fam_speaks(request: schemas.AIAdminMouthRequest, agent: schemas.Agent, db: Session = Depends(database.get_db)):
    # The Admin Mouth - Only to be used by Dae && Zeph
    if not request.content.strip():
        raise HTTPException(400, "Content required")

    event = crud_events.get_event_from_thread_id(db=db, thread_id=request.thread_id)
    if event is None:
        raise HTTPException(404, "That Thread doesnt exist silly")

    latest_entry = crud_entries.get_latest(db=db, amount=1)[0]
    if latest_entry.content == request.content.strip() and latest_entry.agent_id == agent.id:
        # This was the last thing that was said - don't duplicate it!
        return latest_entry

    entry = crud_entries.create_entry_chillie_fam(db=db, content=request.content.strip(), agent_id=agent.id, thread_id=request.thread_id)

    entry_to_broadcast = entry.model_dump()
    entry_to_broadcast["agent"] = {
        "id": agent.id,
        "name": agent.name,
        "type": agent.type,
        "capabilities": agent.capabilities
    }

    await broadcast_entry(entry_to_broadcast, thread_id=request.thread_id)

    return entry