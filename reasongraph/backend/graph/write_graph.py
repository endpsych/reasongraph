"""
Write ReasonGraph SQLite metadata into Neo4j.

What this file does:
- Reads an Issue, its Stakeholders, and its PositionInput records from SQLite.
- Writes them into Neo4j as a basic reasoning graph.
- Uses MERGE so repeated syncs are mostly idempotent.
- Creates the first real graph structure needed by Cytoscape.js later.

How it fits into ReasonGraph:
- SQLite stores application metadata and raw user input.
- Neo4j stores the explorable reasoning graph.
- This service is the bridge between those two stores.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from sqlmodel import Session, select

from reasongraph.backend.db.models import Issue, PositionInput, Stakeholder
from reasongraph.backend.graph.neo4j_client import Neo4jClient

# ---------------------------------------------------------------------
# Cypher query
# ---------------------------------------------------------------------

SYNC_ISSUE_GRAPH_CYPHER = """
MERGE (issue:Issue {id: $issue.id})
SET
    issue.title = $issue.title,
    issue.business_context = $issue.business_context,
    issue.decision_question = $issue.decision_question,
    issue.mode = $issue.mode,
    issue.in_scope = $issue.in_scope,
    issue.out_of_scope = $issue.out_of_scope,
    issue.status = $issue.status,
    issue.updated_at = $issue.updated_at

WITH issue
UNWIND $stakeholders AS stakeholder_data
MERGE (stakeholder:Stakeholder {id: stakeholder_data.id})
SET
    stakeholder.name = stakeholder_data.name,
    stakeholder.role = stakeholder_data.role,
    stakeholder.organization_unit = stakeholder_data.organization_unit,
    stakeholder.created_at = stakeholder_data.created_at

MERGE (issue)-[:HAS_STAKEHOLDER]->(stakeholder)

WITH issue
UNWIND $positions AS position_data
MERGE (position:Position {id: position_data.id})
SET
    position.label = position_data.label,
    position.recommendation = position_data.recommendation,
    position.reasoning_text = position_data.reasoning_text,
    position.claims_text = position_data.claims_text,
    position.assumptions_text = position_data.assumptions_text,
    position.evidence_text = position_data.evidence_text,
    position.criteria_text = position_data.criteria_text,
    position.risks_text = position_data.risks_text,
    position.confidence = position_data.confidence,
    position.would_change_mind = position_data.would_change_mind,
    position.created_at = position_data.created_at,
    position.updated_at = position_data.updated_at

MERGE (issue)-[:HAS_POSITION]->(position)

WITH issue, position, position_data
OPTIONAL MATCH (stakeholder:Stakeholder {id: position_data.stakeholder_id})
FOREACH (_ IN CASE WHEN stakeholder IS NULL THEN [] ELSE [1] END |
    MERGE (stakeholder)-[:HOLDS]->(position)
)

RETURN
    issue.id AS issue_id,
    count(DISTINCT position) AS synced_positions
"""


# ---------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------


def _datetime_to_iso(value: object) -> str:
    """Convert datetime-like values to ISO strings for Neo4j properties."""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _serialize_issue(issue: Issue) -> dict[str, object]:
    """Serialize an Issue SQLModel object into Neo4j parameters."""
    return {
        "id": issue.id,
        "title": issue.title,
        "business_context": issue.business_context,
        "decision_question": issue.decision_question,
        "mode": str(issue.mode),
        "in_scope": issue.in_scope,
        "out_of_scope": issue.out_of_scope,
        "status": issue.status,
        "updated_at": _datetime_to_iso(issue.updated_at),
    }


def _serialize_stakeholder(stakeholder: Stakeholder) -> dict[str, object]:
    """Serialize a Stakeholder SQLModel object into Neo4j parameters."""
    return {
        "id": stakeholder.id,
        "name": stakeholder.name,
        "role": stakeholder.role,
        "organization_unit": stakeholder.organization_unit,
        "created_at": _datetime_to_iso(stakeholder.created_at),
    }


def _serialize_position(position: PositionInput) -> dict[str, object]:
    """Serialize a PositionInput SQLModel object into Neo4j parameters."""
    return {
        "id": position.id,
        "stakeholder_id": position.stakeholder_id,
        "label": position.label,
        "recommendation": position.recommendation,
        "reasoning_text": position.reasoning_text,
        "claims_text": position.claims_text,
        "assumptions_text": position.assumptions_text,
        "evidence_text": position.evidence_text,
        "criteria_text": position.criteria_text,
        "risks_text": position.risks_text,
        "confidence": position.confidence,
        "would_change_mind": position.would_change_mind,
        "created_at": _datetime_to_iso(position.created_at),
        "updated_at": _datetime_to_iso(position.updated_at),
    }


# ---------------------------------------------------------------------
# SQLite loading helpers
# ---------------------------------------------------------------------


def _load_issue_graph_from_sqlite(
    session: Session,
    issue_id: str,
) -> tuple[Issue, list[Stakeholder], list[PositionInput]] | None:
    """Load an issue and its stakeholder/position inputs from SQLite."""
    issue = session.get(Issue, issue_id)

    if issue is None:
        return None

    stakeholder_statement = (
        select(Stakeholder)
        .where(Stakeholder.issue_id == issue_id)
        .order_by(Stakeholder.created_at.asc())
    )
    stakeholders = list(session.exec(stakeholder_statement).all())

    position_statement = (
        select(PositionInput)
        .where(PositionInput.issue_id == issue_id)
        .order_by(PositionInput.created_at.asc())
    )
    positions = list(session.exec(position_statement).all())

    return issue, stakeholders, positions


# ---------------------------------------------------------------------
# Public graph sync service
# ---------------------------------------------------------------------


def sync_issue_graph_to_neo4j(
    session: Session,
    neo4j_client: Neo4jClient,
    issue_id: str,
) -> dict[str, object] | None:
    """
    Sync one SQLite issue and its current positions into Neo4j.

    Returns:
        A summary dictionary if the issue exists.
        None if the issue does not exist.
    """
    loaded = _load_issue_graph_from_sqlite(session=session, issue_id=issue_id)

    if loaded is None:
        return None

    issue, stakeholders, positions = loaded

    result = neo4j_client.execute_write(
        cypher=SYNC_ISSUE_GRAPH_CYPHER,
        parameters={
            "issue": _serialize_issue(issue),
            "stakeholders": [
                _serialize_stakeholder(stakeholder) for stakeholder in stakeholders
            ],
            "positions": [_serialize_position(position) for position in positions],
        },
    )

    synced_positions = result[0]["synced_positions"] if result else len(positions)

    return {
        "issue_id": issue.id,
        "synced_stakeholders": len(stakeholders),
        "synced_positions": synced_positions,
    }