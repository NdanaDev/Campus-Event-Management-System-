# Mobile Developer Guide — Campus Event Management System

This guide covers everything you need to integrate the mobile app with the backend API and Firebase push notifications.

---

## Base URL

```
http://<backend-ip-address>:8000
```

Ask the backend team for the current IP address. All requests go to this base URL.

---

## What You Need to Build

- Browse and filter events
- Register a student for an event
- Submit feedback and ratings after attending
- Receive push notifications when new events are created

---

## Firebase Setup (Push Notifications)

### Step 1 — Add Firebase to your app

Go to [Firebase Console](https://console.firebase.google.com) → your project → Add app (Android or iOS).

Follow the setup wizard:
- Download `google-services.json` (Android) or `GoogleService-Info.plist` (iOS)
- Add it to your project as instructed

### Step 2 — Add dependencies

**Android** (`build.gradle`):
```gradle
implementation 'com.google.firebase:firebase-messaging:23.4.0'
```

**iOS** (`Podfile`):
```ruby
pod 'Firebase/Messaging'
```

### Step 3 — Get the FCM token

You need this token to receive push notifications. Fetch it on app startup and store it.

**Android (Kotlin)**
```kotlin
FirebaseMessaging.getInstance().token.addOnSuccessListener { token ->
    // Save this token — you'll send it when registering for events
    Log.d("FCM", "Token: $token")
}
```

**iOS (Swift)**
```swift
Messaging.messaging().token { token, error in
    if let token = token {
        // Save this token — you'll send it when registering for events
        print("FCM token: \(token)")
    }
}
```

### Step 4 — Request notification permission

**Android** — Add to `AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
```

**iOS (Swift)**
```swift
UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { granted, _ in
    print("Permission granted: \(granted)")
}
```

### What triggers a notification?

Whenever the admin creates a new event via the backend, every student with a stored FCM token automatically receives a push notification. No extra work needed on your side beyond sending the token at registration.

---

## API Integration

### 1. List All Events

**GET** `/events/`

```kotlin
// Android (Kotlin + OkHttp)
val request = Request.Builder()
    .url("http://<backend-ip>:8000/events/")
    .get()
    .build()
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Tech Summit 2026",
    "description": "Annual tech conference",
    "location": "Main Auditorium",
    "category": "Technology",
    "date": "2026-05-10",
    "time": "09:00",
    "capacity": 100,
    "created_at": "2026-04-05T17:22:19.635842",
    "registration_count": 12,
    "average_rating": 4.5
  }
]
```

**Filter by category:**
```
GET /events/?category=Technology
```

---

### 2. Get a Single Event

**GET** `/events/{id}`

```
GET /events/1
```

Returns the same shape as a single item from the list above.

---

### 3. Register for an Event

**POST** `/events/{id}/register`

Send the student's details plus the FCM token so they receive future notifications.

```kotlin
// Android (Kotlin)
val json = JSONObject().apply {
    put("name", "Alice Mensah")
    put("email", "alice@university.edu")
    put("student_number", "STU001")   // optional
    put("fcm_token", fcmToken)        // from Step 3 above
}

val body = json.toString().toRequestBody("application/json".toMediaType())
val request = Request.Builder()
    .url("http://<backend-ip>:8000/events/1/register")
    .post(body)
    .build()
```

**Swift (iOS)**
```swift
var request = URLRequest(url: URL(string: "http://<backend-ip>:8000/events/1/register")!)
request.httpMethod = "POST"
request.setValue("application/json", forHTTPHeaderField: "Content-Type")

let body: [String: Any] = [
    "name": "Alice Mensah",
    "email": "alice@university.edu",
    "student_number": "STU001",
    "fcm_token": fcmToken
]
request.httpBody = try? JSONSerialization.data(withJSONObject: body)
```

**Success Response (201):**
```json
{
  "id": 1,
  "event_id": 1,
  "student": {
    "id": 2,
    "name": "Alice Mensah",
    "email": "alice@university.edu",
    "student_number": "STU001",
    "created_at": "2026-04-05T17:24:09.517958"
  },
  "registered_at": "2026-04-05T17:24:09.520051"
}
```

---

### 4. Submit Feedback

The student must be registered for the event before they can submit feedback.

**POST** `/events/{id}/feedback`

```kotlin
val json = JSONObject().apply {
    put("email", "alice@university.edu")
    put("rating", 5)           // 1 to 5
    put("comment", "Great event!")  // optional
}
```

**Success Response (201):**
```json
{
  "id": 1,
  "event_id": 1,
  "student": { ... },
  "rating": 5,
  "comment": "Great event!",
  "created_at": "2026-04-05T17:25:28.270033"
}
```

---

### 5. Get Feedback Summary

**GET** `/events/{id}/feedback`

```json
{
  "event_id": 1,
  "total_feedback": 10,
  "average_rating": 4.3,
  "rating_breakdown": {
    "1": 0,
    "2": 1,
    "3": 1,
    "4": 4,
    "5": 4
  }
}
```

---

## Error Handling

Always check the HTTP status code before parsing the response body.

| Code | Meaning | What to show the user |
|------|---------|----------------------|
| `200` / `201` | Success | Proceed normally |
| `404` | Event or student not found | "This event doesn't exist" |
| `409` | Already registered / already submitted feedback / event full | "You're already registered" / "Event is fully booked" |
| `403` | Tried to submit feedback without being registered | "You must register first" |
| `422` | Bad request body | Check your field names and types |

**Error response shape:**
```json
{
  "detail": "Student is already registered for this event."
}
```

---

## Tips

- Store the student's **email** locally after first registration — you'll need it to submit feedback.
- Store the **FCM token** and refresh it using `onTokenRefresh` / `onNewToken` callbacks, then re-register or update the token with the backend.
- `registration_count` and `average_rating` in the event list are live — use them to show event popularity.
- `capacity: null` means the event has no limit.
