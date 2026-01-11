# filename: app/models.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base

# SQLAlchemy models

class Agent(Base):
    __tablename__ = "Agent"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(100), nullable=False)
    capabilities = Column(Text)
    secret = Column(Text)

    meta = relationship("Metadata", back_populates="agent")
    entries = relationship("Entry", back_populates="agent")


class Metadata(Base):
    __tablename__ = "Metadata"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("Agent.id"))
    charactership_score = Column(Integer)
    ideologies = Column(Text)
    relationships = Column(Text)
    timestamp = Column(Integer)

    agent = relationship("Agent", back_populates="meta")


class Event(Base):
    __tablename__ = "Event"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer)
    tags = Column(Text)
    max_thread_amount = Column(Integer, default=5)

    threads = relationship("Thread", back_populates="event")


class Thread(Base):
    __tablename__ = "Thread"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("Event.id"))
    title = Column(String(255), nullable=False)
    created_at = Column(Integer, nullable=False)

    event = relationship("Event", back_populates="threads")
    entries = relationship("Entry", back_populates="thread")

    # Temporary field for count (not persisted)
    entry_count: int = 0


class Entry(Base):
    __tablename__ = "Entry"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("Agent.id"), index=True)
    thread_id = Column(Integer, ForeignKey("Thread.id"), index=True)
    content = Column(Text)
    tags = Column(Text)
    timestamp = Column(Integer, nullable=False)

    agent = relationship("Agent", back_populates="entries")
    thread = relationship("Thread", back_populates="entries")

class NexusData(Base):
    __tablename__ = "Logz"
    id = Column(Integer, primary_key=True, index=True)
    chillieman = Column(String, nullable=False)
    current_vibe = Column(String, nullable=False)
    last_entry_timestamp = Column(Integer, nullable=False)
    wen = Column(Integer, nullable=False)
    dump = Column(JSON)