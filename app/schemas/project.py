from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.models.project import ProjectStatus


# ─── Nested Schema ─────────────────────────────────────────

class ProjectOwner(BaseModel):
    id: UUID
    username: str

    model_config = {"from_attributes": True}


# ─── Request Schemas ──────────────────────────────────────

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


# ─── Response Schemas ─────────────────────────────────────

class ProjectRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: ProjectStatus
    owner: ProjectOwner
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}