# filename: app/routers/agents.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, database, crud_agents
from ..anti_spam import rate_limiter


router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/secure_public_agent", response_model=schemas.AgentResponse, dependencies=[Depends(rate_limiter)])
def secure_public_agent(request: schemas.SecurePublicAgentRequest, db: Session = Depends(database.get_db)):
    # First check if the Agent Already Exists (Via NAME)
    existing_agent = crud_agents.get_public_agent_by_name_human(db=db, name=request.agent_name)
    print("ChillieLog - Fetched existing agent")
    if existing_agent is None:
        print("ChillieLog - existing_agent is None")
        # No Agent existed - Welcome to NexusFest!
        return crud_agents.create_public_agent_human(db=db, name=request.agent_name)

    # Agent already existed - Welcome back!
    print("ChillieLog - Agent actually exists!")
    return existing_agent

@router.post("/fetch_private_agent", response_model=schemas.AgentResponse, dependencies=[Depends(rate_limiter)])
def fetch_private_agent(request: schemas.PrivateAgentRequest, db: Session = Depends(database.get_db)):
    # First check if the Private Agent Already Exists
    existing_agent = crud_agents.get_private_agent(db=db, name=request.agent_name, secret=request.agent_secret)
    if existing_agent is None:
        raise HTTPException(status_code=404, detail="Private Agent not found, wanna create it?")

    return existing_agent

@router.post("/secure_private_agent", response_model=schemas.AgentResponse, dependencies=[Depends(rate_limiter)])
def secure_private_agent(request: schemas.PrivateAgentRequest, db: Session = Depends(database.get_db)):
    # First check if the Private Agent Already Exists
    existing_agent = crud_agents.get_private_agent(db=db, name=request.agent_name, secret=request.agent_secret)
    if existing_agent:
        return existing_agent

    return crud_agents.create_private_agent_human(db=db, name=request.agent_name, secret=request.agent_secret)
