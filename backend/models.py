from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime


class ApplicationCreate(BaseModel):
    company: str = Field(..., min_length=1, max_length=200)
    role: str = Field(..., min_length=1, max_length=200)
    status: str
    applied_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=5000)

    @field_validator("applied_date")
    @classmethod
    def no_future_date(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise ValueError("Applied date cannot be in the future")
        return v


class ApplicationUpdate(BaseModel):
    company: Optional[str] = Field(None, min_length=1, max_length=200)
    role: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = None
    applied_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=5000)

    @field_validator("applied_date")
    @classmethod
    def no_future_date(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise ValueError("Applied date cannot be in the future")
        return v


class Application(BaseModel):
    id: int
    company: str
    role: str
    status: str
    applied_date: Optional[date]
    last_updated: datetime
    notes: Optional[str]
    is_manual: bool

    class Config:
        from_attributes = True


VALID_STATUSES = {"Applied", "Interviewing", "Offer Received", "Rejected", "No Response"}
STATUS_RANK = {
    "Applied": 0,
    "Interviewing": 1,
    "Offer Received": 2,
    "Rejected": 2,
    "No Response": 2,
}
