from datetime import datetime

from pydantic import BaseModel, ConfigDict

from reasongraph.backend.db.models import IssueMode


class IssueCreate(BaseModel):
    title: str
    business_context: str = ""
    decision_question: str = ""
    mode: IssueMode = IssueMode.reasoning_analysis
    in_scope: str = ""
    out_of_scope: str = ""


class IssueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    business_context: str
    decision_question: str
    mode: IssueMode
    in_scope: str
    out_of_scope: str
    status: str
    created_at: datetime
    updated_at: datetime
