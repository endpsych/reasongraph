from sqlmodel import Session, select

from reasongraph.backend.db.models import Issue, PositionInput, Stakeholder
from reasongraph.backend.schemas.position import PositionInputCreate
from reasongraph.backend.schemas.stakeholder import StakeholderCreate


def get_issue(session: Session, issue_id: str) -> Issue | None:
    return session.get(Issue, issue_id)


def create_stakeholder_for_issue(
    session: Session,
    issue_id: str,
    stakeholder_in: StakeholderCreate,
) -> Stakeholder | None:
    issue = get_issue(session, issue_id)

    if issue is None:
        return None

    stakeholder = Stakeholder(
        issue_id=issue_id,
        name=stakeholder_in.name,
        role=stakeholder_in.role,
        organization_unit=stakeholder_in.organization_unit,
    )
    session.add(stakeholder)
    session.commit()
    session.refresh(stakeholder)
    return stakeholder


def list_issue_stakeholders(session: Session, issue_id: str) -> list[Stakeholder] | None:
    issue = get_issue(session, issue_id)

    if issue is None:
        return None

    statement = (
        select(Stakeholder)
        .where(Stakeholder.issue_id == issue_id)
        .order_by(Stakeholder.created_at.asc())
    )
    return list(session.exec(statement).all())


def create_position_for_issue(
    session: Session,
    issue_id: str,
    position_in: PositionInputCreate,
) -> PositionInput | None:
    issue = get_issue(session, issue_id)

    if issue is None:
        return None

    if position_in.stakeholder_id is not None:
        stakeholder = session.get(Stakeholder, position_in.stakeholder_id)

        if stakeholder is None or stakeholder.issue_id != issue_id:
            raise ValueError("Stakeholder does not belong to this issue")

    position = PositionInput(
        issue_id=issue_id,
        stakeholder_id=position_in.stakeholder_id,
        label=position_in.label,
        recommendation=position_in.recommendation,
        reasoning_text=position_in.reasoning_text,
        claims_text=position_in.claims_text,
        assumptions_text=position_in.assumptions_text,
        evidence_text=position_in.evidence_text,
        criteria_text=position_in.criteria_text,
        risks_text=position_in.risks_text,
        confidence=position_in.confidence,
        would_change_mind=position_in.would_change_mind,
    )
    session.add(position)
    session.commit()
    session.refresh(position)
    return position


def list_issue_positions(session: Session, issue_id: str) -> list[PositionInput] | None:
    issue = get_issue(session, issue_id)

    if issue is None:
        return None

    statement = (
        select(PositionInput)
        .where(PositionInput.issue_id == issue_id)
        .order_by(PositionInput.created_at.asc())
    )
    return list(session.exec(statement).all())


def get_position(session: Session, position_id: str) -> PositionInput | None:
    return session.get(PositionInput, position_id)