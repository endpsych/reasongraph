from sqlmodel import SQLModel

from reasongraph.backend.db.models import (
    EvaluationRun,
    ExtractionRun,
    Issue,
    LlmPovRun,
    PositionInput,
    Project,
    ProviderProfile,
    Stakeholder,
)
from reasongraph.backend.db.session import engine


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


__all__ = [
    "EvaluationRun",
    "ExtractionRun",
    "Issue",
    "LlmPovRun",
    "PositionInput",
    "Project",
    "ProviderProfile",
    "Stakeholder",
    "init_db",
]
