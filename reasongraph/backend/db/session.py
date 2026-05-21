"""
SQLite session management for ReasonGraph.

What this file does:
- Creates the SQLModel engine for the local SQLite metadata database.
- Ensures the parent directory for the SQLite database exists.
- Provides a small helper for opening database sessions.

How it fits into ReasonGraph:
- SQLite stores app metadata such as projects, issues, raw position inputs,
  provider settings metadata, LLM run metadata, and evaluation run metadata.
- The reasoning graph itself will be stored in Neo4j.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from pathlib import Path

from sqlmodel import Session, create_engine

from reasongraph.backend.core.settings import get_settings

# ---------------------------------------------------------------------
# Engine configuration
# ---------------------------------------------------------------------

settings = get_settings()

DB_PATH = Path(settings.sqlite_path)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


# ---------------------------------------------------------------------
# Session helper
# ---------------------------------------------------------------------


def get_session() -> Session:
    """Create a new SQLModel session."""
    return Session(engine)