"""
Tests for ReasonGraph SQLite-to-Neo4j graph write helpers.

What this file does:
- Tests pure serialization helpers used before writing data to Neo4j.
- Verifies that Issue, Stakeholder, and PositionInput SQLModel objects are
  converted into Neo4j-safe dictionaries.
- Avoids requiring a live Neo4j instance, making these tests suitable for CI.

How it fits into ReasonGraph:
- The graph write layer is a critical bridge between SQLite metadata and
  the Neo4j reasoning graph.
- These tests protect the structure of the data sent to Cypher queries.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from datetime import UTC, datetime

from reasongraph.backend.db.models import Issue, IssueMode, PositionInput, Stakeholder
from reasongraph.backend.graph.write_graph import (
    _serialize_issue,
    _serialize_position,
    _serialize_stakeholder,
)

# ---------------------------------------------------------------------
# Issue serialization tests
# ---------------------------------------------------------------------


def test_serialize_issue() -> None:
    """Issue serialization should preserve key issue metadata."""
    now = datetime(2026, 5, 21, 12, 0, tzinfo=UTC)

    issue = Issue(
        id="issue_test",
        project_id="project_test",
        title="AI provider selection",
        business_context="Choose an AI provider strategy.",
        decision_question="Should we use OpenAI or local models?",
        mode=IssueMode.reasoning_analysis,
        in_scope="Cost, quality, privacy.",
        out_of_scope="Unrelated AI debates.",
        status="draft",
        created_at=now,
        updated_at=now,
    )

    serialized = _serialize_issue(issue)

    assert serialized["id"] == "issue_test"
    assert serialized["title"] == "AI provider selection"
    assert serialized["business_context"] == "Choose an AI provider strategy."
    assert serialized["decision_question"] == "Should we use OpenAI or local models?"
    assert serialized["mode"] == "reasoning_analysis"
    assert serialized["in_scope"] == "Cost, quality, privacy."
    assert serialized["out_of_scope"] == "Unrelated AI debates."
    assert serialized["status"] == "draft"
    assert serialized["updated_at"] == "2026-05-21T12:00:00+00:00"


# ---------------------------------------------------------------------
# Stakeholder serialization tests
# ---------------------------------------------------------------------


def test_serialize_stakeholder() -> None:
    """Stakeholder serialization should preserve stakeholder identity and role."""
    now = datetime(2026, 5, 21, 12, 0, tzinfo=UTC)

    stakeholder = Stakeholder(
        id="stakeholder_test",
        issue_id="issue_test",
        name="CTO",
        role="Technology decision maker",
        organization_unit="Technology",
        created_at=now,
    )

    serialized = _serialize_stakeholder(stakeholder)

    assert serialized["id"] == "stakeholder_test"
    assert serialized["name"] == "CTO"
    assert serialized["role"] == "Technology decision maker"
    assert serialized["organization_unit"] == "Technology"
    assert serialized["created_at"] == "2026-05-21T12:00:00+00:00"


# ---------------------------------------------------------------------
# Position serialization tests
# ---------------------------------------------------------------------


def test_serialize_position() -> None:
    """Position serialization should preserve reasoning fields."""
    now = datetime(2026, 5, 21, 12, 0, tzinfo=UTC)

    position = PositionInput(
        id="position_test",
        issue_id="issue_test",
        stakeholder_id="stakeholder_test",
        label="Use OpenAI for the first MVP",
        recommendation="Use OpenAI initially.",
        reasoning_text="OpenAI is faster to integrate for the MVP.",
        claims_text="OpenAI has mature APIs.",
        assumptions_text="The MVP will not process highly sensitive data.",
        evidence_text="SDKs and documentation are mature.",
        criteria_text="Speed, quality, reliability.",
        risks_text="External API dependency.",
        confidence=0.78,
        would_change_mind="Local models become preferable if data sensitivity dominates.",
        created_at=now,
        updated_at=now,
    )

    serialized = _serialize_position(position)

    assert serialized["id"] == "position_test"
    assert serialized["stakeholder_id"] == "stakeholder_test"
    assert serialized["label"] == "Use OpenAI for the first MVP"
    assert serialized["recommendation"] == "Use OpenAI initially."
    assert serialized["reasoning_text"] == "OpenAI is faster to integrate for the MVP."
    assert serialized["claims_text"] == "OpenAI has mature APIs."
    assert serialized["assumptions_text"] == "The MVP will not process highly sensitive data."
    assert serialized["evidence_text"] == "SDKs and documentation are mature."
    assert serialized["criteria_text"] == "Speed, quality, reliability."
    assert serialized["risks_text"] == "External API dependency."
    assert serialized["confidence"] == 0.78
    assert (
        serialized["would_change_mind"]
        == "Local models become preferable if data sensitivity dominates."
    )
    assert serialized["created_at"] == "2026-05-21T12:00:00+00:00"
    assert serialized["updated_at"] == "2026-05-21T12:00:00+00:00"