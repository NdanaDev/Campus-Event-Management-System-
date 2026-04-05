from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/events", tags=["Registrations"])


# POST /events/{id}/register
@router.post(
    "/{event_id}/register",
    response_model=schemas.RegistrationResponse,
    status_code=201,
    summary="Register a student for an event",
)
def register_for_event(
    event_id: int,
    payload: schemas.RegistrationRequest,
    db: Session = Depends(get_db),
):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    # Check capacity
    if event.capacity is not None and len(event.registrations) >= event.capacity:
        raise HTTPException(status_code=409, detail="Event is fully booked.")

    # Get or create student record
    student = db.query(models.Student).filter(models.Student.email == payload.email).first()
    if not student:
        student = models.Student(
            name=payload.name,
            email=payload.email,
            student_number=payload.student_number,
            fcm_token=payload.fcm_token,
        )
        db.add(student)
        db.flush()
    else:
        # Update FCM token if a new one is provided
        if payload.fcm_token:
            student.fcm_token = payload.fcm_token

    # Check for duplicate registration
    existing = (
        db.query(models.Registration)
        .filter_by(event_id=event_id, student_id=student.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Student is already registered for this event.")

    registration = models.Registration(event_id=event_id, student_id=student.id)
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration
