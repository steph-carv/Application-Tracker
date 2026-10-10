from datetime import date, datetime, timezone
from enum import Enum
from pydantic import EmailStr
from sqlmodel import SQLModel, Field
from typing import Optional

class Stage(str, Enum):
    not_open_yet = "Not Open Yet"
    to_apply = "To Apply"
    applied = "Applied"
    online_assessment = "Online Assessment"
    video_interview = "Video Interview"
    interview = "Interview"
    assessment_centre = "Assessment Centre"
    offer = "Offer"
    accepted = "Accepted"
    rejected = "Rejected"
    withdrawn = "Withdrawn"
    declined = "Declined"

class Token(SQLModel):
    access_token: str
    token_type: str

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    __tablename__ = "users"
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Season(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    name: str 

class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    season_id: int = Field(foreign_key="season.id", ondelete="CASCADE")
    company: str
    position: str
    current_stage: Stage 
    opening_date: Optional[date] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None
    contact: Optional[str] = None

class StageChange(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id", ondelete="CASCADE")
    stage: Stage
    notes: Optional[str] = None
    changed_at: datetime = Field(default_factory= lambda: datetime.now(timezone.utc))

class SeasonCreate(SQLModel):
    name: str
    user_id: int

class SeasonUpdate(SQLModel):
    name: Optional[str] = None

class SeasonRead(SQLModel):
    id: int
    name: str
    user_id: int

class ApplicationCreate(SQLModel):
    season_id: int
    company: str
    position: str
    stage: Stage = Stage.to_apply
    opening_date: Optional[date] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None
    contact: Optional[str] = None

class ApplicationUpdate(SQLModel):
    company: Optional[str] = None
    position: Optional[str] = None
    opening_date: Optional[date] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None
    contact: Optional[str] = None

class ApplicationRead(SQLModel):
    id: int
    season_id: int
    company: str
    position: str
    current_stage: Stage
    opening_date: Optional[date] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None
    contact: Optional[str] = None

class StageChangeCreate(SQLModel):
    stage: Stage
    notes: Optional[str] = None

class StageChangeRead(SQLModel):
    id: int
    application_id: int
    stage: Stage
    notes: Optional[str] = None
    changed_at: datetime

class UserCreate(SQLModel):
    email: EmailStr
    password: str

class UserRead(SQLModel):
    id: int
    email: EmailStr
    created_at: datetime

