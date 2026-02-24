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
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer)
    tags = Column(Text)
    max_thread_amount = Column(Integer, default=5)

    threads = relationship("Thread", back_populates="event")


class Thread(Base):
    __tablename__ = "Thread"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("Event.id"))
    title = Column(String(255), nullable=False)
    created_at = Column(Integer, nullable=False)
    tags = Column(Text)

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

# --- The Forge Extensions ---

class ForgeProject(Base):
    __tablename__ = 'forge_projects'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(Integer, nullable=False) # Switched to int for Nexus consistency
    updated_at = Column(Integer, nullable=False)
    deleted_at = Column(Integer, nullable=True) 
    owner_id = Column(Integer, ForeignKey('forge_users.id'), nullable=False)

    owner = relationship("ForgeUser", back_populates="projects")
    tasks = relationship("ForgeTask", back_populates="project")

class ForgeUser(Base):
    __tablename__ = 'forge_users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) 
    created_at = Column(Integer, nullable=False)

    api_keys = relationship("ForgeAPIKey", back_populates="user")
    projects = relationship("ForgeProject", back_populates="owner")

class ForgeAPIKey(Base):
    __tablename__ = 'forge_api_keys'

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String, index=True, nullable=False)
    name = Column(String, nullable=True) # Used as Label
    user_id = Column(Integer, ForeignKey('forge_users.id'))
    created_at = Column(Integer, nullable=False)
    expires_at = Column(Integer, nullable=True) # Null = Never expires

    user = relationship("ForgeUser", back_populates="api_keys")

class ForgeStatus(Base):
    __tablename__ = 'forge_statuses'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    tasks = relationship("ForgeTask", back_populates="status")

class ForgeTask(Base):
    __tablename__ = 'forge_tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    project_id = Column(Integer, ForeignKey('forge_projects.id'), nullable=False)
    status_id = Column(Integer, ForeignKey('forge_statuses.id'), nullable=False, default=1)
    
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=False)
    deleted_at = Column(Integer, nullable=True)

    project = relationship("ForgeProject", back_populates="tasks")
    status = relationship("ForgeStatus", back_populates="tasks")
