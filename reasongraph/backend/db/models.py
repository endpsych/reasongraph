from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class IssueMode(StrEnum):
    reasoning_analysis = "reasoning_analysis"
    disagreement_structuring = "disagreement_structuring"


class Project(SQLModel, table=True):
    id: str = Field(default_factory=lambda: new_id("project"), primary_key=True)
    name: str
    description: str = ""
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Issue(SQLModel, table=True):
    id: str = Field(default_factory=lambda: new_id("issue"), primary_key=True)
    project_id: str = Field(index=True)
    title: str
    business_context: str = ""
    decision_question: str = ""
    mode: IssueMode = Field(default=IssueMode.reasoning_analysis)
    in_scope: str = ""
    out_of_scope: str = ""
    status: str = "draft"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Stakeholder(SQLModel, table=True):
    id: str = Field(default_factory=lambda: new_id("stakeholder"), primary_key=True)
    issue_id: str = Field(index=True)
    name: str
    role: str = ""
    organization_unit: str = ""
    created_at: datetime = Field(default_factory=utc_now)


class PositionInput(SQLModel, table=True):
    id: str = Field(default_factory=lambda: new_id("position"), primary_key=True)
    issue_id: str = Field(index=True)
    stakeholder_id: str | None = Field(default=None, index=True)
    label: str
    recommendation: str = ""
    reasoning_text: str
    claims_text: str = ""
    assumptions_text: str = ""
    evidence_text: str = ""
    criteria_text: str = ""
    risks_text: str = ""
    confidence: float | None = None
    would_change_mind: str = ""
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ExtractionRun(SQLModel, table=True):
    id: str = Field(default_factory=lambda: new_id("extraction"), primary_key=True)
    issue_id: str = Field(index=True)
    provider: str
    model: str
    prompt_version: str
    status: str = "draft"
    raw_output_json: str = ""
    error_message: str = ""
    created_at: datetime = Field(default_factory=utc_now)


class LlmPovRun(SQLModel, table=True):
    id: str = Field(default_factory=lambda: new_id("llm_pov"), primary_key=True)
    issue_id: str = Field(index=True)
    provider: str
    model: str
    prompt_version: str
    pov_text: str = ""
    confidence: float | None = None
    status: str = "draft"
    error_message: str = ""
    created_at: datetime = Field(default_factory=utc_now)


class ProviderProfile(SQLModel, table=True):
    id: str = Field(default_factory=lambda: new_id("provider"), primary_key=True)
    provider: str
    profile_name: str = "default"
    selected_model: str = ""
    key_storage_mode: str = "session_only"
    keyring_service_name: str = "reasongraph"
    keyring_username: str = ""
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class EvaluationRun(SQLModel, table=True):
    id: str = Field(default_factory=lambda: new_id("evaluation"), primary_key=True)
    issue_id: str = Field(index=True)
    target_run_id: str
    target_run_type: str
    evaluator_provider: str = ""
    evaluator_model: str = ""
    rubric_version: str
    score_json: str = ""
    notes: str = ""
    created_at: datetime = Field(default_factory=utc_now)