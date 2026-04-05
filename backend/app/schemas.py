from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ─── Event ───────────────────────────────────────────────────────────────────

class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    date: str = Field(..., description="Event date in YYYY-MM-DD format")
    time: Optional[str] = Field(None, description="Event time in HH:MM format")
    capacity: Optional[int] = Field(None, ge=1)


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    location: Optional[str]
    category: Optional[str]
    date: str
    time: Optional[str]
    capacity: Optional[int]
    created_at: datetime
    registration_count: int = 0
    average_rating: Optional[float] = None

    model_config = {"from_attributes": True}


# ─── Student ─────────────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    student_number: Optional[str] = None
    fcm_token: Optional[str] = Field(None, description="FCM device token for push notifications")


class StudentResponse(BaseModel):
    id: int
    name: str
    email: str
    student_number: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Registration ─────────────────────────────────────────────────────────────

class RegistrationRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    student_number: Optional[str] = None
    fcm_token: Optional[str] = Field(None, description="FCM device token for push notifications")


class RegistrationResponse(BaseModel):
    id: int
    event_id: int
    student: StudentResponse
    registered_at: datetime

    model_config = {"from_attributes": True}


# ─── Feedback ────────────────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    email: EmailStr = Field(..., description="Student email (must already be registered for this event)")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 (worst) to 5 (best)")
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    event_id: int
    student: StudentResponse
    rating: int
    comment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackSummary(BaseModel):
    event_id: int
    total_feedback: int
    average_rating: Optional[float]
    rating_breakdown: dict[int, int]  # {1: count, 2: count, ...}
