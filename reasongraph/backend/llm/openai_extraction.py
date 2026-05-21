"""
OpenAI extraction provider for ReasonGraph.

What this file does:
- Builds an OpenAI prompt from an issue and its position inputs.
- Calls the OpenAI Responses API.
- Requests structured JSON matching ReasonGraph's extraction schema.
- Validates the returned JSON with Pydantic before storing it.

How it fits into ReasonGraph:
- This module powers LLM-backed extraction.
- The extraction service calls this module when ExtractionMethod.llm is selected.
- The output must match ExtractedReasoningGraph so the review workflow can treat
  local and LLM extraction outputs consistently.

Security notes:
- API keys are passed in memory only.
- API keys must never be logged, stored in extraction outputs, or returned.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import json

from openai import OpenAI

from reasongraph.backend.db.models import Issue, PositionInput
from reasongraph.backend.schemas.extraction import (
    ExtractedReasoningGraph,
    ExtractionMethod,
)

# ---------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------


def build_extraction_prompt(issue: Issue, positions: list[PositionInput]) -> str:
    """Build the user prompt for structured reasoning extraction."""
    position_blocks = []

    for position in positions:
        position_blocks.append(
            "\n".join(
                [
                    f"Position ID: {position.id}",
                    f"Position label: {position.label}",
                    f"Recommendation: {position.recommendation}",
                    f"Reasoning text: {position.reasoning_text}",
                    f"Claims text: {position.claims_text}",
                    f"Assumptions text: {position.assumptions_text}",
                    f"Evidence text: {position.evidence_text}",
                    f"Criteria text: {position.criteria_text}",
                    f"Risks text: {position.risks_text}",
                    f"Confidence: {position.confidence}",
                    f"What would change mind: {position.would_change_mind}",
                ]
            )
        )

    positions_text = "\n\n---\n\n".join(position_blocks)

    return f"""
You are extracting a business reasoning graph for ReasonGraph.

Important rules:
- Focus only on business reasoning.
- Do not add mental health, emotional analysis, demographic analysis, or personal-conflict analysis.
- Use "positions", not "sides".
- Separate claims, assumptions, evidence, criteria, risks, options,
  concepts, and clarifying questions.
- Do not invent evidence. If something is unsupported, represent it as a claim or assumption.
- Keep source_position_id equal to the original Position ID.
- Return only JSON matching the provided schema.

Issue:
- Issue ID: {issue.id}
- Title: {issue.title}
- Business context: {issue.business_context}
- Decision question: {issue.decision_question}
- In scope: {issue.in_scope}
- Out of scope: {issue.out_of_scope}

Positions:
{positions_text}
""".strip()


# ---------------------------------------------------------------------
# Schema helper
# ---------------------------------------------------------------------


def extraction_json_schema() -> dict[str, object]:
    """Return the JSON schema expected from OpenAI structured output."""
    schema = ExtractedReasoningGraph.model_json_schema()
    schema["additionalProperties"] = False
    return schema


# ---------------------------------------------------------------------
# OpenAI extraction
# ---------------------------------------------------------------------


def extract_reasoning_graph_with_openai(
    issue: Issue,
    positions: list[PositionInput],
    api_key: str,
    model: str,
) -> ExtractedReasoningGraph:
    """
    Extract a structured reasoning graph with OpenAI.

    Returns:
        A validated ExtractedReasoningGraph object.
    """
    client = OpenAI(api_key=api_key)

    prompt = build_extraction_prompt(issue=issue, positions=positions)

    response = client.responses.create(
        model=model,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "reason_graph_extraction",
                "schema": extraction_json_schema(),
                "strict": True,
            }
        },
    )

    raw_text = response.output_text
    parsed = json.loads(raw_text)

    extracted = ExtractedReasoningGraph.model_validate(parsed)
    extracted.extraction_method = ExtractionMethod.llm

    return extracted