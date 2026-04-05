# Campus Event Management System

A REST API backend for managing campus events, student registrations, feedback, and Firebase push notifications. Built as part of an HCI assignment with usability principles including consistency, visibility, error prevention, and simplicity.

---

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLite (via SQLAlchemy)
- **Push Notifications:** Firebase Cloud Messaging (FCM)
- **Server:** Uvicorn

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, router registration
│   ├── database.py          # SQLAlchemy engine and session
│   ├── models.py            # Database models (Event, Student, Registration, Feedback)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── notifications.py     # Firebase Admin SDK + FCM logic
│   └── routers/
│       ├── events.py        # Event CRUD endpoints
│       ├── registrations.py # Student registration endpoint
│       └── feedback.py      # Feedback submission and summary endpoints
├── static/
│   ├── swagger-ui.css
│   └── swagger-ui-bundle.js
├── serviceAccountKey.json   # Firebase credentials (not committed to git)
├── .env                     # Environment variables (not committed to git)
├── requirements.txt
└── run.py                   # Entry point
```

---

## Setup

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Firebase

1. Go to [Firebase Console](https://console.firebase.google.com) → Project Settings → Service Accounts
2. Click **Generate new private key** and download the JSON file
3. Place it in the `backend/` folder
4. Create a `.env` file in `backend/`:

```env
FIREBASE_CREDENTIALS_PATH=your-firebase-adminsdk-file.json
```

> If the credentials file is missing, the server still runs — push notifications are silently skipped.

### 3. Run the server

```bash
python run.py
```

Server starts at `http://0.0.0.0:8000`

Interactive API docs: `http://localhost:8000/docs`

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./events.db` | Database connection string |
| `FIREBASE_CREDENTIALS_PATH` | `serviceAccountKey.json` | Path to Firebase service account JSON |

---

## API Reference

### Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/events/` | List all events. Optional `?category=` filter |
| `GET` | `/events/{id}` | Get a single event by ID |
| `POST` | `/events/` | Create a new event |
| `GET` | `/events/{id}/registrations` | List all students registered for an event |

### Registrations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/events/{id}/register` | Register a student for an event |

### Feedback

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/events/{id}/feedback` | Submit a rating and comment for an event |
| `GET` | `/events/{id}/feedback` | Get feedback summary (average rating, breakdown) |

---

## Request & Response Examples

### Create Event
**POST** `/events/`
```json
{
  "title": "Tech Summit 2026",
  "description": "Annual tech conference",
  "location": "Main Auditorium",
  "category": "Technology",
  "date": "2026-05-10",
  "time": "09:00",
  "capacity": 100
}
```

### Register for Event
**POST** `/events/{id}/register`
```json
{
  "name": "Alice Mensah",
  "email": "alice@university.edu",
  "student_number": "STU001",
  "fcm_token": "device-fcm-token-here"
}
```
> `student_number` and `fcm_token` are optional.

### Submit Feedback
**POST** `/events/{id}/feedback`
```json
{
  "email": "alice@university.edu",
  "rating": 5,
  "comment": "Excellent event!"
}
```
> `rating` must be between 1 and 5. Student must be registered for the event first.

### Feedback Summary Response
**GET** `/events/{id}/feedback`
```json
{
  "event_id": 1,
  "total_feedback": 3,
  "average_rating": 4.33,
  "rating_breakdown": {
    "1": 0,
    "2": 0,
    "3": 1,
    "4": 1,
    "5": 1
  }
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| `404` | Event or student not found |
| `409` | Duplicate registration, duplicate feedback, or event fully booked |
| `403` | Submitted feedback without being registered for the event |
| `422` | Missing or invalid fields in the request body |

---

## Push Notifications

When a new event is created (`POST /events/`), the backend automatically sends an FCM push notification to every student who has an `fcm_token` stored.

### Mobile Integration (Android/iOS)

1. Add the Firebase SDK to your mobile app
2. Request notification permissions from the user
3. Retrieve the FCM token from Firebase:

**Android (Kotlin)**
```kotlin
FirebaseMessaging.getInstance().token.addOnSuccessListener { token ->
    // include this token in the register request body
}
```

**iOS (Swift)**
```swift
Messaging.messaging().token { token, error in
    // include this token in the register request body
}
```

4. Pass the token as `fcm_token` when calling `POST /events/{id}/register`

---

## Database Models

| Model | Key Fields |
|-------|-----------|
| `Event` | `id`, `title`, `description`, `location`, `category`, `date`, `time`, `capacity` |
| `Student` | `id`, `name`, `email`, `student_number`, `fcm_token` |
| `Registration` | `id`, `event_id`, `student_id`, `registered_at` |
| `Feedback` | `id`, `event_id`, `student_id`, `rating`, `comment` |

The database is created automatically on first run. No migrations needed for SQLite.

---

## Notes

- A student is identified by their **email address**. Registering with an existing email updates their FCM token.
- Each student can only register for an event **once**.
- Each student can only submit feedback for an event **once**, and only if they are registered.
- Capacity is enforced at registration time. If `capacity` is `null`, the event has no limit.
