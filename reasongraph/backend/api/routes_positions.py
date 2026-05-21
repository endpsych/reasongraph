from fastapi import APIRouter, HTTPException

from reasongraph.backend.db.session import get_session
from reasongraph.backend.schemas.position import PositionInputCreate, PositionInputRead
from reasongraph.backend.schemas.stakeholder import StakeholderCreate, StakeholderRead
from reasongraph.backend.services.position_service import (
    create_position_for_issue,
    create_stakeholder_for_issue,
    get_position,
    list_issue_positions,
    list_issue_stakeholders,
)

router = APIRouter(tags=["positions"])


@router.post(
    "/issues/{issue_id}/stakeholders",
    response_model=StakeholderRead,
    status_code=201,
    tags=["stakeholders"],
)
def create_stakeholder_route(
    issue_id: str,
    stakeholder_in: StakeholderCreate,
) -> StakeholderRead:
    with get_session() as session:
        stakeholder = create_stakeholder_for_issue(session, issue_id, stakeholder_in)

        if stakeholder is None:
            raise HTTPException(status_code=404, detail="Issue not found")

        return StakeholderRead.model_validate(stakeholder)


@router.get(
    "/issues/{issue_id}/stakeholders",
    response_model=list[StakeholderRead],
    tags=["stakeholders"],
)
def list_issue_stakeholders_route(issue_id: str) -> list[StakeholderRead]:
    with get_session() as session:
        stakeholders = list_issue_stakeholders(session, issue_id)

        if stakeholders is None:
            raise HTTPException(status_code=404, detail="Issue not found")

        return [
            StakeholderRead.model_validate(stakeholder)
            for stakeholder in stakeholders
        ]


@router.post(
    "/issues/{issue_id}/positions",
    response_model=PositionInputRead,
    status_code=201,
)
def create_position_route(
    issue_id: str,
    position_in: PositionInputCreate,
) -> PositionInputRead:
    with get_session() as session:
        try:
            position = create_position_for_issue(session, issue_id, position_in)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        if position is None:
            raise HTTPException(status_code=404, detail="Issue not found")

        return PositionInputRead.model_validate(position)


@router.get(
    "/issues/{issue_id}/positions",
    response_model=list[PositionInputRead],
)
def list_issue_positions_route(issue_id: str) -> list[PositionInputRead]:
    with get_session() as session:
        positions = list_issue_positions(session, issue_id)

        if positions is None:
            raise HTTPException(status_code=404, detail="Issue not found")

        return [PositionInputRead.model_validate(position) for position in positions]


@router.get("/positions/{position_id}", response_model=PositionInputRead)
def get_position_route(position_id: str) -> PositionInputRead:
    with get_session() as session:
        position = get_position(session, position_id)

        if position is None:
            raise HTTPException(status_code=404, detail="Position not found")

        return PositionInputRead.model_validate(position)