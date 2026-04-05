from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.notifications import send_new_event_notification

router = APIRouter(prefix="/events", tags=["Events"])


def _build_event_response(event: models.Event) -> schemas.EventResponse:
    reg_count = len(event.registrations)
    ratings = [f.rating for f in event.feedbacks]
    avg = round(sum(ratings) / len(ratings), 2) if ratings else None
    return schemas.EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        location=event.location,
        category=event.category,
        date=event.date,
        time=event.time,
        capacity=event.capacity,
        created_at=event.created_at,
        registration_count=reg_count,
        average_rating=avg,
    )


# GET /events
@router.get("/", response_model=list[schemas.EventResponse], summary="List all events")
def list_events(
    category: Optional[str] = Query(default=None, description="Filter by category"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Event)
    if category:
        query = query.filter(models.Event.category.ilike(f"%{category}%"))
    events = query.order_by(models.Event.date.asc()).all()
    return [_build_event_response(e) for e in events]


# GET /events/{id}
@router.get("/{event_id}", response_model=schemas.EventResponse, summary="Get a single event")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    return _build_event_response(event)


# POST /events  (admin only)
@router.post(
    "/",
    response_model=schemas.EventResponse,
    status_code=201,
    summary="Create a new event",
)
def create_event(
    payload: schemas.EventCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    event = models.Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)

    # Collect all student FCM tokens and send push notification in the background
    tokens = [
        s.fcm_token
        for s in db.query(models.Student).filter(models.Student.fcm_token.isnot(None)).all()
    ]
    background_tasks.add_task(send_new_event_notification, event.title, event.id, tokens)

    return _build_event_response(event)


# GET /events/{id}/registrations  (admin only)
@router.get(
    "/{event_id}/registrations",
    response_model=list[schemas.RegistrationResponse],
    summary="View all students registered for an event",
)
def list_registrations(event_id: int, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    return event.registrations
