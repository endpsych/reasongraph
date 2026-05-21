"""
Reasoning extraction service for ReasonGraph.

What this file does:
- Loads an issue and its PositionInput records from SQLite.
- Creates deterministic local draft extractions from raw position fields.
- Creates OpenAI-backed structured extractions when requested.
- Stores extraction output as JSON in an ExtractionRun.
- Provides read helpers for extraction runs.

How it fits into ReasonGraph:
- This is the foundation for the extraction review workflow.
- Local draft extraction allows offline development and tests.
- LLM extraction uses provider settings and selected models for better
  structured reasoning extraction.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import json
import re

from sqlmodel import Session, select

from reasongraph.backend.db.models import ExtractionRun, Issue, PositionInput
from reasongraph.backend.llm.openai_extraction import extract_reasoning_graph_with_openai
from reasongraph.backend.schemas.extraction import (
    ClaimType,
    ExtractedAssumption,
    ExtractedClaim,
    ExtractedCriterion,
    ExtractedEvidence,
    ExtractedOption,
    ExtractedPosition,
    ExtractedQuestion,
    ExtractedReasoningGraph,
    ExtractedRisk,
    ExtractionCreate,
    ExtractionMethod,
)
from reasongraph.backend.schemas.provider import ProviderConnectionTestRequest, ProviderName
from reasongraph.backend.services.provider_service import resolve_api_key

# ---------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------


def _split_statements(text: str) -> list[str]:
    """Split a text field into simple statement candidates."""
    if not text.strip():
        return []

    parts = re.split(r"[.\n;]+", text)
    return [part.strip() for part in parts if part.strip()]


def _first_sentence(text: str) -> str:
    """Return a short summary from the first sentence-like chunk."""
    statements = _split_statements(text)

    if not statements:
        return ""

    return statements[0]


# ---------------------------------------------------------------------
# Local draft extraction helpers
# ---------------------------------------------------------------------


def _extract_claims(position: PositionInput) -> list[ExtractedClaim]:
    """Create draft claims from the position claims text."""
    statements = _split_statements(position.claims_text)

    if not statements and position.reasoning_text:
        statements = [_first_sentence(position.reasoning_text)]

    return [
        ExtractedClaim(
            text=statement,
            claim_type=ClaimType.belief,
            requires_evidence=True,
            confidence=position.confidence,
        )
        for statement in statements
    ]


def _extract_assumptions(position: PositionInput) -> list[ExtractedAssumption]:
    """Create draft assumptions from the position assumptions text."""
    return [
        ExtractedAssumption(text=statement)
        for statement in _split_statements(position.assumptions_text)
    ]


def _extract_evidence(position: PositionInput) -> list[ExtractedEvidence]:
    """Create draft evidence items from the position evidence text."""
    return [
        ExtractedEvidence(text=statement)
        for statement in _split_statements(position.evidence_text)
    ]


def _extract_criteria(position: PositionInput) -> list[ExtractedCriterion]:
    """Create draft criteria from comma/newline separated criteria text."""
    if not position.criteria_text.strip():
        return []

    parts = re.split(r"[,;\n]+", position.criteria_text)
    criteria = [part.strip() for part in parts if part.strip()]

    return [ExtractedCriterion(name=criterion) for criterion in criteria]


def _extract_risks(position: PositionInput) -> list[ExtractedRisk]:
    """Create draft risks from comma/newline separated risks text."""
    if not position.risks_text.strip():
        return []

    parts = re.split(r"[,;\n]+", position.risks_text)
    risks = [part.strip() for part in parts if part.strip()]

    return [ExtractedRisk(text=risk) for risk in risks]


def _extract_options(position: PositionInput) -> list[ExtractedOption]:
    """Create a draft option from the recommendation field."""
    if not position.recommendation.strip():
        return []

    return [
        ExtractedOption(
            name=position.label,
            description=position.recommendation,
        )
    ]


def _extract_position(position: PositionInput) -> ExtractedPosition:
    """Create a structured local draft extraction for one position."""
    return ExtractedPosition(
        source_position_id=position.id,
        label=position.label,
        recommendation=position.recommendation,
        summary=_first_sentence(position.reasoning_text),
        claims=_extract_claims(position),
        assumptions=_extract_assumptions(position),
        evidence=_extract_evidence(position),
        criteria=_extract_criteria(position),
        risks=_extract_risks(position),
        options=_extract_options(position),
    )


def _build_clarifying_questions(positions: list[PositionInput]) -> list[ExtractedQuestion]:
    """Create simple generic clarifying questions for the issue."""
    if not positions:
        return [
            ExtractedQuestion(
                text="What positions should be considered for this issue?",
                target="issue",
            )
        ]

    return [
        ExtractedQuestion(
            text="Which assumptions are most important to test before making a decision?",
            target="assumptions",
        ),
        ExtractedQuestion(
            text="Which evidence would most change the preferred position?",
            target="evidence",
        ),
        ExtractedQuestion(
            text="Which decision criteria should be weighted most heavily?",
            target="criteria",
        ),
    ]


def build_local_draft_extraction(
    issue: Issue,
    positions: list[PositionInput],
) -> ExtractedReasoningGraph:
    """Build a deterministic local draft extraction for an issue."""
    return ExtractedReasoningGraph(
        issue_id=issue.id,
        issue_title=issue.title,
        extraction_method=ExtractionMethod.local_draft,
        positions=[_extract_position(position) for position in positions],
        concepts=[],
        clarifying_questions=_build_clarifying_questions(positions),
    )


# ---------------------------------------------------------------------
# SQLite loading helpers
# ---------------------------------------------------------------------


def _load_issue_positions(
    session: Session,
    issue_id: str,
) -> tuple[Issue, list[PositionInput]] | None:
    """Load an issue and its positions from SQLite."""
    issue = session.get(Issue, issue_id)

    if issue is None:
        return None

    statement = (
        select(PositionInput)
        .where(PositionInput.issue_id == issue_id)
        .order_by(PositionInput.created_at.asc())
    )
    positions = list(session.exec(statement).all())

    return issue, positions


# ---------------------------------------------------------------------
# LLM extraction helpers
# ---------------------------------------------------------------------


def _build_provider_request(extraction_in: ExtractionCreate) -> ProviderConnectionTestRequest:
    """Build a provider key-resolution request from extraction settings."""
    return ProviderConnectionTestRequest(
        provider=extraction_in.provider,
        model=extraction_in.model,
        profile_name=extraction_in.profile_name,
        key_storage_mode=extraction_in.key_storage_mode,
        api_key=extraction_in.api_key,
    )


def _build_llm_extraction(
    issue: Issue,
    positions: list[PositionInput],
    extraction_in: ExtractionCreate,
) -> ExtractedReasoningGraph:
    """Build an LLM extraction using the configured provider."""
    if extraction_in.provider != ProviderName.openai:
        raise ValueError("Only OpenAI extraction is supported in the MVP.")

    api_key = resolve_api_key(_build_provider_request(extraction_in))

    if not api_key:
        raise ValueError("No API key available for LLM extraction.")

    return extract_reasoning_graph_with_openai(
        issue=issue,
        positions=positions,
        api_key=api_key,
        model=extraction_in.model,
    )


# ---------------------------------------------------------------------
# Extraction run service
# ---------------------------------------------------------------------


def create_extraction_run(
    session: Session,
    issue_id: str,
    extraction_in: ExtractionCreate,
) -> ExtractionRun | None:
    """Create and store a new extraction run for an issue."""
    loaded = _load_issue_positions(session=session, issue_id=issue_id)

    if loaded is None:
        return None

    issue, positions = loaded

    if extraction_in.method == ExtractionMethod.local_draft:
        extracted_graph = build_local_draft_extraction(issue=issue, positions=positions)
    elif extraction_in.method == ExtractionMethod.llm:
        extracted_graph = _build_llm_extraction(
            issue=issue,
            positions=positions,
            extraction_in=extraction_in,
        )
    else:
        raise ValueError(f"Unsupported extraction method: {extraction_in.method}")

    raw_output_json = extracted_graph.model_dump_json(indent=2)

    extraction_run = ExtractionRun(
        issue_id=issue.id,
        provider=str(extraction_in.provider),
        model=extraction_in.model,
        prompt_version=extraction_in.prompt_version,
        status="draft",
        raw_output_json=raw_output_json,
    )

    session.add(extraction_run)
    session.commit()
    session.refresh(extraction_run)

    return extraction_run


def list_issue_extraction_runs(
    session: Session,
    issue_id: str,
) -> list[ExtractionRun] | None:
    """List extraction runs for one issue."""
    issue = session.get(Issue, issue_id)

    if issue is None:
        return None

    statement = (
        select(ExtractionRun)
        .where(ExtractionRun.issue_id == issue_id)
        .order_by(ExtractionRun.created_at.desc())
    )
    return list(session.exec(statement).all())


def get_extraction_run(
    session: Session,
    extraction_id: str,
) -> ExtractionRun | None:
    """Return one extraction run by ID."""
    return session.get(ExtractionRun, extraction_id)


def parse_extraction_output(extraction_run: ExtractionRun) -> dict[str, object]:
    """Parse extraction output JSON for future review workflows."""
    return json.loads(extraction_run.raw_output_json)