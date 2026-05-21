"""
Reasoning extraction schemas for ReasonGraph.

What this file does:
- Defines structured schemas for extracted reasoning objects.
- Defines API schemas for creating and reading extraction runs.
- Provides the JSON shape that later LLM extraction workflows should produce.

How it fits into ReasonGraph:
- Stakeholders enter raw position text.
- Extraction converts that text into structured positions, claims, assumptions,
  evidence, criteria, risks, options, and clarifying questions.
- The extraction output is stored as JSON in SQLite before being reviewed and
  eventually written to Neo4j.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------
# Extraction enums
# ---------------------------------------------------------------------


class ClaimType(StrEnum):
    """Supported claim categories for extracted reasoning objects."""

    fact = "fact"
    assumed_fact = "assumed_fact"
    belief = "belief"
    interpretation = "interpretation"
    prediction = "prediction"
    preference = "preference"
    value_judgment = "value_judgment"
    risk_claim = "risk_claim"
    constraint = "constraint"
    decision_criterion = "decision_criterion"
    recommendation = "recommendation"
    evidence_statement = "evidence_statement"


class ExtractionMethod(StrEnum):
    """Supported extraction methods."""

    local_draft = "local_draft"
    llm = "llm"


# ---------------------------------------------------------------------
# Extracted reasoning object schemas
# ---------------------------------------------------------------------


class ExtractedClaim(BaseModel):
    """One extracted claim from a position."""

    text: str
    claim_type: ClaimType = ClaimType.belief
    requires_evidence: bool = True
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class ExtractedAssumption(BaseModel):
    """One extracted assumption from a position."""

    text: str
    importance: str = "medium"
    testability: str = "unknown"


class ExtractedEvidence(BaseModel):
    """One extracted evidence statement from a position."""

    text: str
    source_type: str = "unspecified"
    reliability: str = "unknown"


class ExtractedCriterion(BaseModel):
    """One extracted decision criterion from a position."""

    name: str
    priority: str = "medium"


class ExtractedRisk(BaseModel):
    """One extracted risk from a position."""

    text: str
    severity: str = "unknown"


class ExtractedOption(BaseModel):
    """One extracted option or recommendation."""

    name: str
    description: str = ""


class ExtractedConcept(BaseModel):
    """One extracted concept relevant to the issue."""

    name: str
    definition: str = ""
    ambiguity: str = "unknown"


class ExtractedQuestion(BaseModel):
    """One clarifying question generated from the extracted reasoning."""

    text: str
    target: str = "issue"


class ExtractedPosition(BaseModel):
    """Structured extraction for one position."""

    source_position_id: str
    label: str
    recommendation: str = ""
    summary: str = ""
    claims: list[ExtractedClaim] = Field(default_factory=list)
    assumptions: list[ExtractedAssumption] = Field(default_factory=list)
    evidence: list[ExtractedEvidence] = Field(default_factory=list)
    criteria: list[ExtractedCriterion] = Field(default_factory=list)
    risks: list[ExtractedRisk] = Field(default_factory=list)
    options: list[ExtractedOption] = Field(default_factory=list)


class ExtractedReasoningGraph(BaseModel):
    """Complete structured extraction output for one issue."""

    issue_id: str
    issue_title: str
    extraction_method: ExtractionMethod
    positions: list[ExtractedPosition] = Field(default_factory=list)
    concepts: list[ExtractedConcept] = Field(default_factory=list)
    clarifying_questions: list[ExtractedQuestion] = Field(default_factory=list)


# ---------------------------------------------------------------------
# API request and response schemas
# ---------------------------------------------------------------------


class ExtractionCreate(BaseModel):
    """Request to create a new extraction run."""

    method: ExtractionMethod = ExtractionMethod.local_draft
    provider: str = "local"
    model: str = "local-draft"
    prompt_version: str = "extract_reasoning_graph_v0.1"


class ExtractionRunRead(BaseModel):
    """Safe response for an extraction run."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    issue_id: str
    provider: str
    model: str
    prompt_version: str
    status: str
    raw_output_json: str
    error_message: str
    created_at: datetime