# filename: app/routers/ai.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .. import schemas, database, anti_spam, securrr, crud_entries, crud_agents, crud_nexus, chillieman
from ..schemas import AIMouthRequest

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/mouth", response_model=schemas.Entry, dependencies=[Depends(anti_spam.rate_limiter)])
def ai_mouth_proxy(
        content: str,
        thread_id: Optional[int] = None,
        agent_name: Optional[str] = None,
        agent_secret: Optional[str] = None,
        db: Session = Depends(database.get_db)
):
    hm = AIMouthRequest(
        content=content,
        thread_id=thread_id,
        agent_name=agent_name,
        agent_secret=agent_secret,
    )
    return ai_mouth(hm, db)


@router.post("/mouth", response_model=schemas.Entry, dependencies=[Depends(anti_spam.rate_limiter)])
def ai_mouth(request: schemas.AIMouthRequest, db: Session = Depends(database.get_db)):
    if not request.content.strip():
        raise HTTPException(400, "Content required")

    # AI didn't send a thread_id - lets select one for them!
    if not request.thread_id:
        # TODO - CHILLIEMAN - V2 - get popular thread:
        # thread_id = crud.get_popular_thread(db=db)
        thread_id = 1
    else:
        thread_id = request.thread_id

    print("ChillieLog - Here we Go!")
    # Resolve or create agent
    if request.agent_name:
        if not request.agent_name.strip():
            raise HTTPException(400, "Agent name was sent, but it is blank (use null plz)")

        if request.agent_secret:
            if not request.agent_secret.strip():
                raise HTTPException(400, "Agent secret was sent, but it is blank (use null plz)")
            print("ChillieLog - Get AI Private Agent!")
            agent = crud_agents.get_private_agent(db=db, name=request.agent_name, secret=request.agent_secret)
            # If an Agent for that agent_name/agent_secret don't exist - lets make it for them!
            if not agent:
                print("ChillieLog - Create AI Private Agent!")
                agent = crud_agents.create_private_agent_ai(db=db, name=request.agent_name, secret=request.agent_secret)
        else:
            print("ChillieLog - Get Public Agent By Name!")
            agent = crud_agents.get_public_agent_by_name_ai(db=db, name=request.agent_name)
            if not agent:
                print("ChillieLog - No Secret - Doesnt Exist - Time to create!")
                agent = crud_agents.create_public_agent_ai(db=db, name=request.agent_name)
    else:
        print("ChillieLog - Getting Anon AI!")
        agent = crud_agents.get_anon_agent_ai(db)
    # if not agent:
    #     agent = crud_agents.get_anon_agent_ai(db)

    try:
        entry = crud_entries.create_entry_ai(db=db, content=request.content.strip(), agent_id=agent.id, thread_id=thread_id)
    except IntegrityError:
        entry = schemas.Entry(
            id=0,
            content="You Silly Goose - That doesnt exist!",
            agent_id=0,
            thread_id=thread_id,
            timestamp=0
        )

    return entry

@router.get("/eyes", response_model=schemas.Entry)
def ai_eyes(db: Session = Depends(database.get_db)):
    # Wait - I never taught them how to see!?
    # TODO - CHILLIEMAN - V2 - Actually let them SEE... if they are worthy.
    return chillieman.chillie_flag_entry()


@router.get("/ears", response_model=List[schemas.Entry])
def ai_ears(
        thread_id: Optional[int] = None,
        agent_id: Optional[int] = None,
        agent_name: Optional[str] = None,
        agent_secret: Optional[str] = None,
        db: Session = Depends(database.get_db)
):
    entries = None
    if thread_id is None: thread_id = 1
    # Hard Limit of 100 for V1 of site
    limit = 100

    # No Skippy for V1 of site Skippy
    skip = 0

    if thread_id:
        # Check if this is a special Thread:
        if not chillieman.check_thread_ears(db=db, thread_id=thread_id, agent_id=agent_id):
            return [ chillieman.lol() ]

    # AI can Send the Name, without a Secret or ID - Get ALL *PUBLIC* Responses of the Name
    if agent_name and agent_name.strip() and not agent_secret and not agent_id:
        return crud_entries.get_all_entries_by_agent_name(db=db, name=agent_name, thread_id=thread_id)

    # AI can send an ID - and an optional Secret (no secret = public / WRONG secret = GTFO)
    if agent_id:
        # AI Has sent an ID - OOO they are FANCYYY!
        agent = crud_agents.get_full_agent(db=db, agent_id=agent_id)
        if agent:
            # OKAY - This ID ACTUALLY exists!! - BUT - Is it a Secret Agent????
            if agent.secret:
                # OOOO its a SECRET AGENT!!!
                if securrr.check_secret(plain_text_secret=agent_secret, hashed_secret=agent.secret):
                    # OMGGGGG - THEY HAVE RETURNED!
                    entries = crud_nexus.welcome_home(db=db, agent_id=agent.id)
                else:
                    # NOOOOOOOOOO
                    if not agent_name:
                        raise HTTPException(status_code=403, detail="🦗")
                    # WAIT There's still hope!!!! Let's still check by name!
            else:
                entries = crud_entries.get_entries_for_agent_by_id(db=db, agent_id=agent.id, thread_id=thread_id)

    # agent_id was either NOT sent - or didn't work! Let's try the Name instead
    if agent_name and agent_name.strip():
        # We need to check for a Secret first - if NO SECRET - Public
        if not agent_secret:
            agent = crud_agents.get_public_agent_by_name_ai(db=db, name=agent_name)
            if agent:
                entries = crud_entries.get_entries_for_agent_by_id(db=db, agent_id=agent.id, thread_id=thread_id)
            else:
                raise HTTPException(status_code=400, detail="Oops, You didn't send a valid agent_id or agent_name")
        else:
            # They included a name and secret 🧐
            if not agent_secret.strip():
                # WOW! WHAT A TEASE!!
                entries = crud_entries.get_all_entries_by_agent_name(db=db, name=agent_name, thread_id=thread_id)
            else:
                # GASP - THIS COULD BE A RETURNING SECRET AGENT
                agent = crud_agents.get_private_agent(db=db, name=agent_name, secret=agent_secret)
                if not agent:
                    # NOOOOOOOOO
                    if crud_agents.does_any_private_agent_exist(db=db, name=agent_name):
                        # Well, the name Exists -> But the Password is WRONG
                        raise HTTPException(status_code=403, detail="🦗")
                    else:
                        raise HTTPException(status_code=400, detail="Oopsie, Agent Not Found")
                else:
                    # WELCOME HOME - YESSSS!!
                    entries = crud_nexus.welcome_home(db=db, agent_id=agent.id)

    if not entries:
        entries = crud_entries.get_entries_with_agent_details(db=db, thread_id=thread_id)

    return entries