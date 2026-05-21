"""
Extraction API routes for ReasonGraph.

What this file does:
- Creates extraction runs for issue reasoning.
- Lists extraction runs for an issue.
- Reads individual extraction runs.
- Uses a local draft extractor for now.

How it fits into ReasonGraph:
- This is the API foundation for the future extraction review screen.
- Later, the extraction service will support OpenAI extraction using the
  provider settings and selected model.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from fastapi import APIRouter, HTTPException

from reasongraph.backend.db.session import get_session
from reasongraph.backend.schemas.extraction import ExtractionCreate, ExtractionRunRead
from reasongraph.backend.services.extraction_service import (
    create_extraction_run,
    get_extraction_run,
    list_issue_extraction_runs,
)

# ---------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------

router = APIRouter(tags=["extraction"])


# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------


@router.post(
    "/issues/{issue_id}/extract",
    response_model=ExtractionRunRead,
    status_code=201,
)
def create_extraction_route(
    issue_id: str,
    extraction_in: ExtractionCreate,
) -> ExtractionRunRead:
    """Create a new extraction run for an issue."""
    with get_session() as session:
        try:
            extraction_run = create_extraction_run(
                session=session,
                issue_id=issue_id,
                extraction_in=extraction_in,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        if extraction_run is None:
            raise HTTPException(status_code=404, detail="Issue not found")

        return ExtractionRunRead.model_validate(extraction_run)


@router.get(
    "/issues/{issue_id}/extractions",
    response_model=list[ExtractionRunRead],
)
def list_issue_extractions_route(issue_id: str) -> list[ExtractionRunRead]:
    """List extraction runs for an issue."""
    with get_session() as session:
        extraction_runs = list_issue_extraction_runs(session=session, issue_id=issue_id)

        if extraction_runs is None:
            raise HTTPException(status_code=404, detail="Issue not found")

        return [
            ExtractionRunRead.model_validate(extraction_run)
            for extraction_run in extraction_runs
        ]


@router.get(
    "/extractions/{extraction_id}",
    response_model=ExtractionRunRead,
)
def get_extraction_route(extraction_id: str) -> ExtractionRunRead:
    """Read one extraction run."""
    with get_session() as session:
        extraction_run = get_extraction_run(
            session=session,
            extraction_id=extraction_id,
        )

        if extraction_run is None:
            raise HTTPException(status_code=404, detail="Extraction run not found")

        return ExtractionRunRead.model_validate(extraction_run)