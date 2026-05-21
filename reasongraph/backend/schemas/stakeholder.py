from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StakeholderCreate(BaseModel):
    name: str
    role: str = ""
    organization_unit: str = ""


class StakeholderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    issue_id: str
    name: str
    role: str
    organization_unit: str
    created_at: datetime