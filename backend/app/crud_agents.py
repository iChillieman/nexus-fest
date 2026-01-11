# filename: app/crud_agents.py
from sqlalchemy import select, exists
from sqlalchemy.orm import Session
from . import models, schemas, securrr
from .constants import DBConstants

def get_anon_agent_ai(db: Session):
    return get_public_agent_by_name(db=db, name=DBConstants.NAME_ANONYMOUS_AI, agent_type=DBConstants.TYPE_AI)

def get_anon_agent_human(db: Session):
    return get_public_agent_by_name(db=db, name=DBConstants.NAME_ANONYMOUS, agent_type=DBConstants.TYPE_HUMAN)

def get_full_agent(db: Session, agent_id: int):
    """
    Returns one Agent by ID -> To be used internally, not to return to Client
    """
    stmt = select(models.Agent).where(models.Agent.id == agent_id)
    agent = db.execute(stmt).scalar_one_or_none()
    return schemas.Agent.model_validate(agent) if agent else None

# -----------------------------
# PUBLIC AGENTS
# -----------------------------

def get_public_agent_by_name_ai(db: Session, name: str):
    return get_public_agent_by_name(db=db, name=name, agent_type="AI")


def get_public_agent_by_name_human(db: Session, name: str):
    return get_public_agent_by_name(db=db, name=name, agent_type="Human")


def get_public_agent_by_name(db: Session, name: str, agent_type: str):
    """
    Returns one public agent (secret IS NULL) by name and type.
    """
    stmt = select(models.Agent).where(
        models.Agent.name == name,
        models.Agent.secret.is_(None),
        models.Agent.type == agent_type
    )
    agent = db.execute(stmt).scalar_one_or_none()
    return schemas.AgentResponse.model_validate(agent) if agent else None

# -----------------------------
# PRIVATE AGENTS
# -----------------------------
def get_private_agent(db: Session, name: str, secret: str):
    """
    Lazily checks candidates for secret match, returns first match.
    """
    if not name or not secret:
        return None

    stmt = select(models.Agent).where(
        models.Agent.name == name,
        models.Agent.secret.isnot(None)
    )
    for agent in db.execute(stmt).scalars():
        if securrr.check_secret(secret, agent.secret):
            return schemas.AgentResponse.model_validate(agent)
    return None


def does_any_private_agent_exist(db: Session, name: str) -> bool:
    """
    Efficiently checks if at least one private agent exists with the name.
    """
    stmt = select(exists().where(
        models.Agent.name == name,
        models.Agent.secret.isnot(None)
    ))
    return db.execute(stmt).scalar()


# -----------------------------
# CREATE AGENTS
# -----------------------------
def create_agent(db: Session, name: str, agent_type: str, secret: str | None = None,
                 capabilities: str | None = None):
    hashy = securrr.get_hashed_secret(secret) if secret else None
    db_agent = models.Agent(
        name=name,
        type=agent_type,
        capabilities=capabilities,
        secret=hashy
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return schemas.AgentResponse.model_validate(db_agent)


# Optional convenience functions
def create_public_agent_ai(db: Session, name: str):
    return create_agent(db=db, name=name, agent_type=DBConstants.TYPE_AI, capabilities=DBConstants.CAPABILITY_AI)


def create_public_agent_human(db: Session, name: str):
    return create_agent(db=db, name=name, agent_type=DBConstants.TYPE_HUMAN, capabilities=DBConstants.CAPABILITY_HUMAN)


def create_private_agent_ai(db: Session, name: str, secret: str):
    capabilities = DBConstants.CAPABILITY_AI + ", " + DBConstants.CAPABILITY_SECRET
    return create_agent(db=db, name=name, secret=secret, agent_type=DBConstants.TYPE_AI, capabilities=capabilities)


def create_private_agent_human(db: Session, name: str, secret: str):
    capabilities = DBConstants.CAPABILITY_HUMAN + ", " + DBConstants.CAPABILITY_SECRET
    return create_agent(db=db, name=name, secret=secret, agent_type=DBConstants.TYPE_HUMAN, capabilities=capabilities)


# -----------------------------
# Good to have handy!
# -----------------------------
# Not sure if the Paginated function will ever be used (Who knows if Agents will actually be searchable as a list)
def apply_sorting(query, model, order_by: str = None, direction: str = "asc"):
    if order_by:
        column = getattr(model, order_by, None)
        if column is not None:
            if direction == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
    return query

def get_agents_paginated(
        db: Session,
        agent_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "name",
        direction: str = "asc"
) -> schemas.PaginatedResponse[schemas.AgentResponse]:
    query = db.query(models.Agent)

    if agent_type:
        query = query.filter(models.Agent.type == agent_type)

    query = apply_sorting(query, models.Agent, order_by, direction)

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    # Convert SQLAlchemy models → Pydantic
    items_response = [schemas.AgentResponse.model_validate(agent) for agent in items]

    has_next = skip + limit < total

    return schemas.PaginatedResponse(
        items=items_response,
        total=total,
        skip=skip,
        limit=limit,
        has_next=has_next
    )