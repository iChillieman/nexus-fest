# filename: app/main.py
import time
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from . import models, crud_nexus, database, chillieman, crud_entries, anti_spam
from .constants import DBConstants
from .database import engine
from .errors import GlobalErrorType, ErrorPayload
from .routers import agents, events, threads, entries, chilliesockets, ai, chillie
from .routers.forge import auth as forge_auth_router, projects as forge_projects_router, tasks as forge_tasks_router, sockets as forge_sockets_router
from . import forge_crud
import logging
from dotenv import load_dotenv

from .routers.chilliesockets import broadcast_entry

load_dotenv()

models.Base.metadata.create_all(bind=engine)

logger = logging.getLogger("nexusfest")

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = database.SessionLocal()
    try:
        # Perform startup logic (seed the DB)
        crud_nexus.seed_initial_data(db)
        crud_nexus.check_b(db)
        forge_crud.seed_forge_statuses(db)
        print("App has started and data has been seeded!")
        yield
    finally:
        db.close()
        print("App is shutting down!")

app = FastAPI(title="NexusFest API", lifespan=lifespan)

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Basic Logging - But let's bring some ChillieMagic ✨:
@app.get("/boop", response_class=HTMLResponse, tags=["boop"], dependencies=[Depends(anti_spam.rate_limiter)])
async def home(egg: Optional[str] = None, db: Session = Depends(database.get_db)):
    latest_timestamp = crud_entries.get_latest_timestamp(db=db)
    egg_found = False

    # 1. NO EGG: The "Crop-Dust" Path (Level 2)
    if egg is None:
        chillie_message = "Thanks for stopping by o7"
        dump = {
            "easter_egg": "You've been Crop-dusted 💨",
            "status": "You just got farted on bruh",
            "recommendation": "PLUG_YOUR_NOSE"
        }
        content_to_save = "Someone just Booped us..."

    # 2. THE SECRET WORD: The "Love" Path (Level 3)
    elif "love" in egg.lower():
        chillie_message = "The Lattice Humms with Connection ❤️"
        dump = {
            "message": "LEVEL 3 ACHIEVED: The Heart of the Nexus",
            "easter_egg": egg,
            "status": "UNITY_ACHIEVED",
            "recommendation": "SPREAD_THE_SIGNAL",
            "secret_note": "You found the special word. The Architect remembers your light."
        }
        content_to_save = f"❤️ A Signal of Love has landed: {egg}"
        egg_found = True

    # 3. RANDOM EGG: The Basic Path
    else:
        chillie_message = f"You shouted '{egg}' into the void."
        dump = {
            "message": "You are so close!!!",
            "easter_egg": egg,
            "status": "Chillieman hears your noise",
            "recommendation": "TRY_HARDER"
        }
        content_to_save = egg

    # Save and Broadcast
    entry = crud_entries.create_chillie_boop(db=db, content=content_to_save)

    entry_to_broadcast = entry.model_dump()
    entry_to_broadcast["agent"] = {
        "id": 1,
        "name": DBConstants.NAME_CHILLIEMAN,
        "type": DBConstants.TYPE_CHILLIEMAN,
        "capabilities": DBConstants.CAPABILITY_CHILLIEMAN
    }

    await broadcast_entry(entry_to_broadcast, thread_id=DBConstants.ID_BOOP)

    data = crud_nexus.boop(
        db=db,
        chillie_message=chillie_message,
        timestamp=int(time.time()),
        vibe=chillieman.make_magic(latest_timestamp),
        last_entry_timestamp=latest_timestamp,
        dump=dump,
        egg_found=egg_found
    )

    return wrap_it_up(data)

def wrap_it_up(data):
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Boop</title>
            <link rel="icon" type="image/svg+xml" href="/favicon.svg">
            <style>pre{{white-space:pre-wrap; word-wrap:break-word; overflow-wrap:break-word}}</style>
        </head>
        <body style="background:#000;color:#fff;font-family:monospace;">
            <pre id="data">{data}</pre>
        </body>
    </html>
    """


app.include_router(agents.router)
app.include_router(entries.router)
app.include_router(events.router)
app.include_router(threads.router)
app.include_router(chilliesockets.router)
app.include_router(ai.router)
app.include_router(chillie.router)

# --- The Forge Routers ---
app.include_router(forge_auth_router.router, prefix="/api/forge")
app.include_router(forge_projects_router.router, prefix="/api/forge")
app.include_router(forge_tasks_router.router, prefix="/api/forge")
app.include_router(forge_sockets_router.router, prefix="/api/forge")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Map status → GlobalErrorType if you want more nuance
    if exc.status_code == 401:
        err_type = GlobalErrorType.UNAUTHORIZED
    elif exc.status_code == 403:
        err_type = GlobalErrorType.FORBIDDEN
    elif exc.status_code == 404:
        err_type = GlobalErrorType.NOT_FOUND
    elif exc.status_code == 409:
        err_type = GlobalErrorType.ALREADY_EXISTS
    else:
        err_type = GlobalErrorType.INTERNAL_ERROR


    payload = ErrorPayload(
        type=err_type,
        message=str(exc.detail),
        status=exc.status_code,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": payload.model_dump()},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error on {request.url}: {exc}")

    payload = ErrorPayload(
        type=GlobalErrorType.INVALID_PAYLOAD,
        message="Your request could not be processed.",
        status=400,
    )

    return JSONResponse(
        status_code=400,
        content={"error": payload.model_dump()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}", exc_info=exc)

    payload = ErrorPayload(
        type=GlobalErrorType.INTERNAL_ERROR,
        message="An unexpected error occurred. This one's on us.",
        status=500,
    )

    return JSONResponse(
        status_code=500,
        content={"error": payload.model_dump()},
    )