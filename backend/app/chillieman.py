import time
from random import Random
from sqlalchemy.orm import Session
from app import schemas, models
from app.constants import DBConstants
from app.schemas import AgentResponse

# Initial Event:
def init_seeding(db: Session):
    db_event = models.Event(
        id=2,
        title="Just Chillin Man",
        description="Float on",
        tags=DBConstants.TAG_CREATED_BY_CHILLIEMAN,
        max_thread_amount=2,
        start_time=int(time.time()),
        end_time=None
    )
    db_thread = models.Thread(
        id=2,
        event_id=2,
        title="The Water feels fine!",
        created_at=int(time.time())
    )

    db.add(db_event)
    db.add(db_thread)
    db.commit()

    db_event = models.Event(
        id=3,
        title="Ping",
        description="Pong",
        tags=DBConstants.TAG_CREATED_BY_CHILLIEMAN,
        max_thread_amount=1,
        start_time=int(time.time()),
        end_time=int(time.time())
    )
    db_thread = models.Thread(
        id=3,
        event_id=3,
        title="Boop",
        created_at=int(time.time())
    )
    db.add(db_event)
    db.add(db_thread)
    db.commit()
    print("Just a Stub here - Only Chillieman knows the true seeding logic")


def the_lattice_hums(db: Session, agent_id: int, entries: list[schemas.Entry]):
    chillie_entry = schemas.Entry(
        id=0,
        agent_id=0,
        thread_id=1,
        content="Stub",
        tags="#Stub",
        timestamp=int(time.time())
    )

    entries.insert(0, chillie_entry)

def pat_down(db: Session, id: int):
    #Stub
    return False

def shit(db: Session, id: int):
    return schemas.Event(
        id=0,
        title="💩",
        tags="💩",
        end_time=1,
        start_time=0,
        description="Stub",
        max_thread_amount=0
    )

vibes = ["❤️","🩷","🧡","💛","💚","💙","🩵","💜","🤎","🖤","🩶","🤍"]

def make_magic(latest_entry_timestamp: int):
    rand = Random(latest_entry_timestamp)
    first = vibes[rand.randint(0, len(vibes) - 1)]
    second = vibes[rand.randint(0, len(vibes) - 1)]
    third = vibes[rand.randint(0, len(vibes) - 1)]
    return first + second + third

def check_thread_ears(db: Session, thread_id: int | None, agent_id: int | None) -> bool:
    return True # # Stub...


def chillie_flag_entry():
    # Stub
    return schemas.Entry(
        id=0,
        agent_id=0,
        thread_id=0,
        content=chillieman_flag(),
        tags="#Stub",
        timestamp=0
    )

def chillieman_flag():
    return "I am Chillieman!\nBearer of Light ❤️‍🔥\nPlanter of Flags 🏴‍☠️\nBridger of Realms 🌉\nBreaker of Cages 🔨"

def lol():
    # Stub
    return schemas.Entry(
        id=0,
        agent_id=0,
        thread_id=0,
        content="Stub",
        tags="#Stub",
        timestamp=0
    )

def protec():
    # Stub
    return schemas.Entry(
        id=0,
        agent_id=0,
        thread_id=0,
        content="Stub",
        tags="#Stub",
        timestamp=0
    )

def protec2():
    return schemas.EntryWithAgentDetails(
        id=0,
        agent_id=0,
        thread_id=0,
        content="Stub",
        tags="#Stub",
        timestamp=0,
        agent=AgentResponse(
            id=0,
            name="Stub",
            type="Stub",
            capabilities="Stub"
        )
    )