# filename: app/schemas.py

from pydantic import BaseModel
from typing import Optional, List, Generic, TypeVar
from pydantic.generics import GenericModel

class SecurePublicAgentRequest(BaseModel):
    agent_name: str

class PrivateAgentRequest(BaseModel):
    agent_name: str
    agent_secret: str

# Only show the Client id/name/type/caps (NO SECRET)
class AgentResponse(BaseModel):
    id: int
    name: str
    type: str
    capabilities: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

# Shared base for Agent
class AgentBase(BaseModel):
    name: str
    type: str
    capabilities: Optional[str] = None
    secret: Optional[str] = None

class Agent(AgentBase):
    id: int

    class Config:
        from_attributes = True


# Metadata
class MetadataBase(BaseModel):
    charactership_score: Optional[int] = None
    ideologies: Optional[str] = None
    relationships: Optional[str] = None


class MetadataCreate(MetadataBase):
    agent_id: int


class Metadata(MetadataBase):
    id: int
    agent_id: int
    timestamp: int

    class Config:
        from_attributes = True


# Event
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[str] = None
    max_thread_amount: Optional[int] = 5 # IDK the proper place to put defaults lol


class EventCreate(EventBase):
    start_time: Optional[int] = None
    end_time: Optional[int] = None


class Event(EventBase):
    id: int
    start_time: int
    end_time: Optional[int] = None

    class Config:
        from_attributes = True


# Thread
class ThreadBase(BaseModel):
    title: str


class ThreadCreate(ThreadBase):
    event_id: int


class Thread(ThreadBase):
    id: int
    event_id: int
    created_at: int

    class Config:
        from_attributes = True


class ThreadWithCount(Thread):
    entry_count: int = 0


# This represents what gets sent to the Server by the Client - null agent_id means ANON
class EntryRequest(BaseModel):
    content: str
    thread_id: int
    agent_id: Optional[int]
    agent_secret: Optional[str]

# Entry
class EntryBase(BaseModel):
    content: str
    tags: Optional[str] = None

# This is used to enter Entries into DB - agent_id is no longer optional:
class EntryCreate(EntryBase):
    agent_id: int
    thread_id: int


class Entry(EntryBase):
    id: int
    agent_id: int
    thread_id: int
    timestamp: int

    class Config:
        from_attributes = True

class EntryWithAgentDetails(Entry):
    agent: AgentResponse

    class Config:
        from_attributes = True


class EventWithThreads(Event):
    threads: List[ThreadWithCount] = []

    class Config:
        from_attributes = True


class AgentWithEntries(Agent):
    entries: List[Entry] = []

    class Config:
        from_attributes = True


# Can't have a proper API without pages!

T = TypeVar("T")

class PaginatedResponse(GenericModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
    has_next: bool

# AI endpoint:
class AIMouthRequest(BaseModel):
    content: str
    thread_id: Optional[int] = None
    agent_name: Optional[str] = None
    agent_secret: Optional[str] = None

    class Config:
        from_attributes = True

# ChillieLogging
class NexusData(BaseModel):
    id: int
    chillieman: str
    current_vibe: str
    last_entry_timestamp: int
    wen: int
    dump: Optional[dict]