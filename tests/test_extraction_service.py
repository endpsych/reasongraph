"""
Tests for ReasonGraph extraction service helpers.

What this file does:
- Tests the local draft extraction logic.
- Verifies that raw PositionInput fields are converted into structured claims,
  assumptions, evidence, criteria, risks, options, and questions.
- Avoids requiring OpenAI or Neo4j.

How it fits into ReasonGraph:
- This protects the extraction review foundation before adding real LLM calls.
- The future OpenAI extraction should produce the same structured schema shape.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from reasongraph.backend.db.models import Issue, IssueMode, PositionInput
from reasongraph.backend.schemas.extraction import ExtractionMethod
from reasongraph.backend.services.extraction_service import build_local_draft_extraction

# ---------------------------------------------------------------------
# Local draft extraction tests
# ---------------------------------------------------------------------


def test_build_local_draft_extraction_from_position_input() -> None:
    """Local draft extraction should structure raw position input fields."""
    issue = Issue(
        id="issue_test",
        project_id="project_test",
        title="AI provider selection",
        business_context="Choose a provider strategy.",
        decision_question="Should we use OpenAI or local models?",
        mode=IssueMode.reasoning_analysis,
    )

    position = PositionInput(
        id="position_test",
        issue_id="issue_test",
        stakeholder_id="stakeholder_test",
        label="Use OpenAI for the first MVP",
        recommendation="Use OpenAI API initially.",
        reasoning_text="OpenAI is faster to integrate. It has mature SDKs.",
        claims_text="OpenAI has mature APIs. OpenAI reduces implementation complexity.",
        assumptions_text="The MVP will not process sensitive data. API costs are acceptable.",
        evidence_text="The SDK documentation is mature. The API is easy to call.",
        criteria_text="Implementation speed, model quality, developer experience",
        risks_text="External API dependency, cost uncertainty",
        confidence=0.78,
        would_change_mind="Use local models if data sensitivity dominates.",
    )

    extracted = build_local_draft_extraction(issue=issue, positions=[position])

    assert extracted.issue_id == "issue_test"
    assert extracted.issue_title == "AI provider selection"
    assert extracted.extraction_method == ExtractionMethod.local_draft
    assert len(extracted.positions) == 1

    extracted_position = extracted.positions[0]

    assert extracted_position.source_position_id == "position_test"
    assert extracted_position.label == "Use OpenAI for the first MVP"
    assert extracted_position.summary == "OpenAI is faster to integrate"

    assert len(extracted_position.claims) == 2
    assert extracted_position.claims[0].text == "OpenAI has mature APIs"

    assert len(extracted_position.assumptions) == 2
    assert extracted_position.assumptions[0].text == "The MVP will not process sensitive data"

    assert len(extracted_position.evidence) == 2
    assert extracted_position.evidence[0].text == "The SDK documentation is mature"

    assert len(extracted_position.criteria) == 3
    assert extracted_position.criteria[0].name == "Implementation speed"

    assert len(extracted_position.risks) == 2
    assert extracted_position.risks[0].text == "External API dependency"

    assert len(extracted_position.options) == 1
    assert extracted_position.options[0].name == "Use OpenAI for the first MVP"

    assert len(extracted.clarifying_questions) == 3