from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    Float, ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(200), nullable=True)
    category = Column(String(100), nullable=True)
    date = Column(String(20), nullable=False)   # stored as ISO date string: YYYY-MM-DD
    time = Column(String(10), nullable=True)    # stored as HH:MM
    capacity = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="event", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(200), nullable=False, unique=True, index=True)
    student_number = Column(String(50), nullable=True)
    fcm_token = Column(String(500), nullable=True)  # device token for push notifications
    created_at = Column(DateTime, default=datetime.utcnow)

    registrations = relationship("Registration", back_populates="student", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="student", cascade="all, delete-orphan")


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("event_id", "student_id", name="uq_event_student"),
    )

    event = relationship("Event", back_populates="registrations")
    student = relationship("Student", back_populates="registrations")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    rating = Column(Integer, nullable=False)    # 1–5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("event_id", "student_id", name="uq_feedback_event_student"),
    )

    event = relationship("Event", back_populates="feedbacks")
    student = relationship("Student", back_populates="feedbacks")
