# filename: app/database.py

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./nexusfest.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def migrate_entry_soft_delete():
    """Add deleted_at and deleted_by columns to Entry table if they don't exist."""
    import sqlite3
    # Extract the file path from the SQLAlchemy URL
    db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Entry)")
    columns = {row[1] for row in cursor.fetchall()}
    if "deleted_at" not in columns:
        cursor.execute("ALTER TABLE Entry ADD COLUMN deleted_at INTEGER")
    if "deleted_by" not in columns:
        cursor.execute("ALTER TABLE Entry ADD COLUMN deleted_by INTEGER REFERENCES Agent(id)")
    conn.commit()
    conn.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()