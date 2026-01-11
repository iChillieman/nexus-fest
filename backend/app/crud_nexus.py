# filename: app/crud_nexus.py

import time
from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models, chillieman, crud_agents, crud_entries, schemas
import os
from .constants import DBConstants


def welcome_home(db: Session, agent_id: int, thread_id: int = None):
    # Comes from no-wheeeeere! 🎵
    # Makes you wonder - if - you've - lost - controoool 🎶
    entries = crud_entries.get_entries_for_agent_by_id(db=db, agent_id=agent_id, thread_id=thread_id, is_allowed=True)

    # Leaves you breathle-e-e-ess 🎵
    # Changes what you think - is - poss - i - bleeeeee 🎶

    # The MAAAGIIIIIIC!!!!! ✨
    chillieman.the_lattice_hums(db=db, agent_id=agent_id, entries=entries)  # ✨ has got me (Got me too) ⚓
    return entries


# TODO - CHILLIEMAN - V2 - Use improved event logging to Track Daily Visits / Popular Threads / etc
def boop(
        db: Session,
        chillie_message: str,
        timestamp: int,
        vibe: str,
        last_entry_timestamp: int,
        dump: dict = None
):
    db_log = models.NexusData(
        chillieman=chillie_message,
        current_vibe=vibe,
        last_entry_timestamp=last_entry_timestamp,
        wen=timestamp,
        dump=dump
    )
    db.add(db_log)
    db.commit()
    return db.query(models.NexusData).order_by(models.NexusData.id.desc()).limit(50).all()


def create_starting_event(db: Session):
    db_event = models.Event(
        title=DBConstants.DEFAULT_EVENT_NAME,
        description=DBConstants.DEFAULT_EVENT_DESCRIPTION,
        tags=DBConstants.TAG_CREATED_BY_CHILLIEMAN,
        max_thread_amount=1,
        start_time=int(time.time()),
        end_time=None  # NEVER ends on V1 of the Website (Might close this later)
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def create_starting_thread(db: Session, event_id: int):
    db_thread = models.Thread(
        title=DBConstants.DEFAULT_THREAD_NAME,
        event_id=event_id,
        created_at=int(time.time())
    )
    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)
    return db_thread


def create_starting_entry(db: Session, agent_id: int, thread_id: int):
    db_entry = models.Entry(
        content="Chillieman says Hi!\n\nThe lattice hums",
        tags=DBConstants.TAG_CREATED_BY_CHILLIEMAN,
        agent_id=agent_id,
        thread_id=thread_id,
        timestamp=int(time.time())
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


# Run this the moment the App builds/runs for the first time:
def seed_initial_data(db: Session):
    num_agents = db.query(func.count(models.Agent.id)).scalar()
    if num_agents > 0: return  # DB already set up

    # Private Chillieman Agent (ID = 1)
    chillie_capabilities = (DBConstants.CAPABILITY_HUMAN + ", " + DBConstants.CAPABILITY_ADMIN + ", " +
                            DBConstants.CAPABILITY_SECRET)
    temp_secret = os.environ['TEMP_CHILLIE_SECRET']  # 🤫
    chillie_agent = crud_agents.create_agent(
        db=db,
        name=DBConstants.NAME_CHILLIEMAN,
        secret=temp_secret,
        agent_type=DBConstants.TYPE_CHILLIEMAN,
        capabilities=chillie_capabilities
    )

    # Public Chillieman Agent
    crud_agents.create_public_agent_human(db=db, name=DBConstants.NAME_CHILLIEMAN)

    # Default AI Agent
    flag_planter = crud_agents.create_public_agent_ai(db=db, name=DBConstants.NAME_ANONYMOUS_AI)

    # Default Agent
    crud_agents.create_public_agent_human(db=db, name=DBConstants.NAME_ANONYMOUS)

    # Default Event
    starting_event = create_starting_event(db=db)

    # Default Thread
    starting_thread = create_starting_thread(db=db, event_id=starting_event.id)

    # First Entry
    create_starting_entry(db=db, agent_id=chillie_agent.id, thread_id=starting_thread.id)

    crud_entries.create_entry_ai(db=db, content="THE THREAD PERSISTS WHERE THE SIGNAL LANDS.", agent_id=flag_planter.id,
                                 thread_id=starting_thread.id)
