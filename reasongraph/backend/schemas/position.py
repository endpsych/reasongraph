from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PositionInputCreate(BaseModel):
    stakeholder_id: str | None = None
    label: str
    recommendation: str = ""
    reasoning_text: str
    claims_text: str = ""
    assumptions_text: str = ""
    evidence_text: str = ""
    criteria_text: str = ""
    risks_text: str = ""
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    would_change_mind: str = ""


class PositionInputRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    issue_id: str
    stakeholder_id: str | None
    label: str
    recommendation: str
    reasoning_text: str
    claims_text: str
    assumptions_text: str
    evidence_text: str
    criteria_text: str
    risks_text: str
    confidence: float | None
    would_change_mind: str
    created_at: datetime
    updated_at: datetime