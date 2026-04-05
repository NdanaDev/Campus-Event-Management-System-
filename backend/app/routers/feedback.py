from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/events", tags=["Feedback"])


# POST /events/{id}/feedback
@router.post(
    "/{event_id}/feedback",
    response_model=schemas.FeedbackResponse,
    status_code=201,
    summary="Submit feedback and a rating for an event",
)
def submit_feedback(
    event_id: int,
    payload: schemas.FeedbackRequest,
    db: Session = Depends(get_db),
):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    student = db.query(models.Student).filter(models.Student.email == payload.email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found. Please register for the event first.")

    # Student must be registered to submit feedback
    registered = (
        db.query(models.Registration)
        .filter_by(event_id=event_id, student_id=student.id)
        .first()
    )
    if not registered:
        raise HTTPException(
            status_code=403,
            detail="You must be registered for this event to submit feedback.",
        )

    # Prevent duplicate feedback
    existing = (
        db.query(models.Feedback)
        .filter_by(event_id=event_id, student_id=student.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="You have already submitted feedback for this event.")

    feedback = models.Feedback(
        event_id=event_id,
        student_id=student.id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


# GET /events/{id}/feedback
@router.get(
    "/{event_id}/feedback",
    response_model=schemas.FeedbackSummary,
    summary="Get feedback summary for an event",
)
def get_feedback_summary(event_id: int, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    feedbacks = event.feedbacks
    total = len(feedbacks)
    avg = round(sum(f.rating for f in feedbacks) / total, 2) if total else None
    breakdown = {i: 0 for i in range(1, 6)}
    for f in feedbacks:
        breakdown[f.rating] += 1

    return schemas.FeedbackSummary(
        event_id=event_id,
        total_feedback=total,
        average_rating=avg,
        rating_breakdown=breakdown,
    )
