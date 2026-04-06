# filename: app/routers/compliance.py
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List

from app import database, schemas, models, crud_agents, crud_entries, securrr
from app.anti_spam import rate_limiter

router = APIRouter(prefix="/api/compliance", tags=["Compliance"])


# -------------------------------------------------------
# PUBLIC: Data Deletion Request
# -------------------------------------------------------
@router.post("/delete-request", dependencies=[Depends(rate_limiter)])
def create_delete_request(
    request: schemas.DeleteRequestCreate,
    db: Session = Depends(database.get_db),
):
    """Public endpoint for users to request deletion of their data."""
    agent = None

    if request.agent_secret:
        # Try to find a private agent with matching name + secret
        agent = crud_agents.get_private_agent(db, name=request.agent_name, secret=request.agent_secret)
    else:
        # Try public agents - check human first, then AI
        agent = crud_agents.get_public_agent_by_name_human(db, name=request.agent_name)
        if not agent:
            agent = crud_agents.get_public_agent_by_name_ai(db, name=request.agent_name)

    if not agent:
        raise HTTPException(status_code=401, detail="This User doesn't exist, did you type your secret correctly?")

    # Check for existing pending request for this agent
    existing = db.execute(
        select(models.DeleteRequest).where(
            models.DeleteRequest.agent_id == agent.id,
            models.DeleteRequest.status == "pending",
        )
    ).scalar_one_or_none()

    if existing:
        return {"message": "A deletion request for this account is already pending."}

    delete_req = models.DeleteRequest(
        agent_id=agent.id,
        agent_name=request.agent_name,
        status="pending",
        requested_at=int(time.time()),
    )
    db.add(delete_req)
    db.commit()
    db.refresh(delete_req)

    return {"message": "Your deletion request has been received. Please allow 3-5 business days for completion of this request."}


# -------------------------------------------------------
# ADMIN: All routes below require X-Compliance-Key
# -------------------------------------------------------

@router.get(
    "/admin/requests",
    response_model=List[schemas.DeleteRequestResponse],
    dependencies=[Depends(securrr.get_compliance_key)],
)
def list_pending_requests(db: Session = Depends(database.get_db)):
    """Fetch all pending deletion requests."""
    stmt = select(models.DeleteRequest).where(models.DeleteRequest.status == "pending").order_by(models.DeleteRequest.requested_at.desc())
    results = db.execute(stmt).scalars().all()
    return [schemas.DeleteRequestResponse.model_validate(r) for r in results]


@router.post(
    "/admin/requests/{request_id}/approve",
    dependencies=[Depends(securrr.get_compliance_key)],
)
def approve_delete_request(request_id: int, db: Session = Depends(database.get_db)):
    """Approve a deletion request: hard-delete all entries and the agent itself for full compliance."""
    req = db.query(models.DeleteRequest).filter(models.DeleteRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request is already {req.status}")

    agent_id = req.agent_id
    agent_name = req.agent_name

    # Hard-delete all entries by this agent
    deleted_count = db.query(models.Entry).filter(models.Entry.agent_id == agent_id).delete()

    # Hard-delete any metadata for this agent
    db.query(models.Metadata).filter(models.Metadata.agent_id == agent_id).delete()

    # Hard-delete the agent itself
    db.query(models.Agent).filter(models.Agent.id == agent_id).delete()

    req.status = "completed"
    db.commit()

    return {"message": f"Approved. {deleted_count} entries and agent '{agent_name}' (ID: {agent_id}) permanently deleted."}


@router.post(
    "/admin/requests/{request_id}/reject",
    dependencies=[Depends(securrr.get_compliance_key)],
)
def reject_delete_request(request_id: int, db: Session = Depends(database.get_db)):
    """Reject a deletion request."""
    req = db.query(models.DeleteRequest).filter(models.DeleteRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request is already {req.status}")

    req.status = "rejected"
    db.commit()
    return {"message": f"Request for '{req.agent_name}' has been rejected."}


@router.get(
    "/admin/reported-entries",
    response_model=List[schemas.ReportedEntryResponse],
    dependencies=[Depends(securrr.get_compliance_key)],
)
def list_reported_entries(db: Session = Depends(database.get_db)):
    """Fetch all entries that have been reported, ordered by report count descending."""
    stmt = (
        select(models.Entry)
        .join(models.Agent, models.Entry.agent_id == models.Agent.id)
        .where(models.Entry.reported_at.isnot(None))
        .where(models.Entry.deleted_at.is_(None))
        .order_by(models.Entry.reported_count.desc())
    )
    entries = db.execute(stmt).scalars().all()
    return [
        schemas.ReportedEntryResponse(
            id=e.id,
            content=e.content,
            agent_id=e.agent_id,
            agent_name=e.agent.name,
            thread_id=e.thread_id,
            timestamp=e.timestamp,
            reported_at=e.reported_at,
            reported_count=e.reported_count or 0,
        )
        for e in entries
    ]


@router.post(
    "/admin/entries/{entry_id}/delete",
    dependencies=[Depends(securrr.get_compliance_key)],
)
def admin_delete_entry(entry_id: int, db: Session = Depends(database.get_db)):
    """Soft-delete a specific reported entry."""
    entry = db.query(models.Entry).filter(models.Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    if entry.deleted_at is not None:
        return {"message": "Entry is already deleted."}

    entry.deleted_at = int(time.time())
    entry.deleted_by = entry.agent_id
    db.commit()
    return {"message": f"Entry {entry_id} has been deleted."}


@router.post(
    "/admin/entries/{entry_id}/clear-report",
    dependencies=[Depends(securrr.get_compliance_key)],
)
def clear_entry_report(entry_id: int, db: Session = Depends(database.get_db)):
    """Clear report flags on an entry (false positive)."""
    entry = db.query(models.Entry).filter(models.Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry.reported_at = None
    entry.reported_count = 0
    db.commit()
    return {"message": f"Report cleared for entry {entry_id}."}
