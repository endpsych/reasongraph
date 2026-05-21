from pathlib import Path

from sqlmodel import Session, create_engine

DB_PATH = Path("data/app/reasongraph.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def get_session() -> Session:
    return Session(engine)
