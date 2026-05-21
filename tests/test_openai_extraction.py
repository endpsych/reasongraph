"""
Tests for ReasonGraph OpenAI extraction prompt helpers.

What this file does:
- Tests OpenAI extraction prompt construction.
- Tests extraction JSON schema availability.
- Does not call the OpenAI API.
- Does not require an API key.

How it fits into ReasonGraph:
- OpenAI extraction is network-dependent and should be integration-tested later.
- These unit tests protect local prompt and schema behavior safely.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from reasongraph.backend.db.models import Issue, IssueMode, PositionInput
from reasongraph.backend.llm.openai_extraction import (
    build_extraction_prompt,
    extraction_json_schema,
)

# ---------------------------------------------------------------------
# Prompt tests
# ---------------------------------------------------------------------


def test_build_extraction_prompt_includes_issue_and_position_data() -> None:
    """Prompt should include issue and position content needed for extraction."""
    issue = Issue(
        id="issue_test",
        project_id="project_test",
        title="AI provider selection",
        business_context="Choose an AI provider.",
        decision_question="Should we use OpenAI or local models?",
        mode=IssueMode.reasoning_analysis,
        in_scope="Cost, privacy, quality.",
        out_of_scope="Unrelated AI debates.",
    )

    position = PositionInput(
        id="position_test",
        issue_id="issue_test",
        stakeholder_id="stakeholder_test",
        label="Use OpenAI",
        recommendation="Use OpenAI for the MVP.",
        reasoning_text="OpenAI is faster to integrate.",
        claims_text="OpenAI has mature APIs.",
        assumptions_text="The MVP will not process sensitive data.",
        evidence_text="Documentation is mature.",
        criteria_text="Speed, quality.",
        risks_text="External dependency.",
        confidence=0.8,
        would_change_mind="Use local models if privacy dominates.",
    )

    prompt = build_extraction_prompt(issue=issue, positions=[position])

    assert "AI provider selection" in prompt
    assert "Should we use OpenAI or local models?" in prompt
    assert "Position ID: position_test" in prompt
    assert "OpenAI has mature APIs." in prompt
    assert "Use \"positions\", not \"sides\"." in prompt


def test_extraction_json_schema_has_expected_title() -> None:
    """Extraction JSON schema should describe the extracted reasoning graph."""
    schema = extraction_json_schema()

    assert schema["title"] == "ExtractedReasoningGraph"
    assert "properties" in schema
    assert "positions" in schema["properties"]