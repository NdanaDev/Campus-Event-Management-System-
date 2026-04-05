# Web Developer Guide — Campus Event Management System

This guide covers everything you need to build the web app using HTML, CSS, and JavaScript.

---

## Base URL

```
http://<backend-ip-address>:8000
```

Ask the backend team for the current IP address. Store it as a constant at the top of your JS file so you only need to change it in one place.

```js
const API_BASE = "http://<backend-ip-address>:8000";
```

---

## What You Need to Build

- Display a list of events (with optional category filter)
- Show a single event's details
- Allow a student to register for an event
- Allow a student to submit feedback after attending
- Show a feedback summary for an event

---

## Making API Requests

Use the `fetch` API. CORS is fully open on the backend so no proxy or special headers are needed beyond `Content-Type`.

### GET request template

```js
async function getEvents() {
    const res = await fetch(`${API_BASE}/events/`);
    if (!res.ok) {
        const err = await res.json();
        console.error(err.detail);
        return;
    }
    const events = await res.json();
    console.log(events);
}
```

### POST request template

```js
async function postData(endpoint, body) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail);
    return data;
}
```

---

## API Integration

### 1. List All Events

**GET** `/events/`

```js
async function loadEvents(category = "") {
    const url = category
        ? `${API_BASE}/events/?category=${encodeURIComponent(category)}`
        : `${API_BASE}/events/`;

    const res = await fetch(url);
    const events = await res.json();

    events.forEach(event => {
        console.log(event.title, event.date, event.registration_count);
    });
}
```

**Response shape:**
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

**Rendering example:**
```html
<div id="events-list"></div>

<script>
async function loadEvents() {
    const res = await fetch(`${API_BASE}/events/`);
    const events = await res.json();
    const container = document.getElementById("events-list");

    container.innerHTML = events.map(e => `
        <div class="event-card">
            <h2>${e.title}</h2>
            <p>${e.date} ${e.time ?? ""} — ${e.location ?? "TBD"}</p>
            <p>${e.description ?? ""}</p>
            <span>${e.registration_count} registered</span>
            ${e.average_rating ? `<span>★ ${e.average_rating}</span>` : ""}
            <button onclick="showEvent(${e.id})">View</button>
        </div>
    `).join("");
}

loadEvents();
</script>
```

---

### 2. Get a Single Event

**GET** `/events/{id}`

```js
async function showEvent(id) {
    const res = await fetch(`${API_BASE}/events/${id}`);
    if (!res.ok) {
        alert("Event not found.");
        return;
    }
    const event = await res.json();
    console.log(event);
}
```

---

### 3. Register for an Event

**POST** `/events/{id}/register`

```html
<form id="register-form">
    <input type="text" id="name" placeholder="Full Name" required />
    <input type="email" id="email" placeholder="Email" required />
    <input type="text" id="student-number" placeholder="Student Number (optional)" />
    <button type="submit">Register</button>
</form>

<script>
document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const eventId = 1; // get this from your current page context

    const body = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        student_number: document.getElementById("student-number").value || null
    };

    try {
        const res = await fetch(`${API_BASE}/events/${eventId}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.detail); // e.g. "Student is already registered for this event."
            return;
        }

        // Save email to localStorage — needed later for submitting feedback
        localStorage.setItem("studentEmail", body.email);
        alert("Successfully registered!");

    } catch (err) {
        alert("Something went wrong. Please try again.");
    }
});
</script>
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

The student must be registered for the event before submitting feedback.

**POST** `/events/{id}/feedback`

```html
<form id="feedback-form">
    <label>Rating (1–5)</label>
    <input type="number" id="rating" min="1" max="5" required />
    <textarea id="comment" placeholder="Leave a comment (optional)"></textarea>
    <button type="submit">Submit Feedback</button>
</form>

<script>
document.getElementById("feedback-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const eventId = 1; // get from page context
    const email = localStorage.getItem("studentEmail");

    if (!email) {
        alert("Please register for the event first.");
        return;
    }

    const body = {
        email: email,
        rating: parseInt(document.getElementById("rating").value),
        comment: document.getElementById("comment").value || null
    };

    const res = await fetch(`${API_BASE}/events/${eventId}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    const data = await res.json();

    if (!res.ok) {
        alert(data.detail);
        return;
    }

    alert("Feedback submitted. Thank you!");
});
</script>
```

---

### 5. Show Feedback Summary

**GET** `/events/{id}/feedback`

```js
async function loadFeedback(eventId) {
    const res = await fetch(`${API_BASE}/events/${eventId}/feedback`);
    const data = await res.json();

    document.getElementById("avg-rating").textContent =
        data.average_rating ? `★ ${data.average_rating}` : "No ratings yet";

    document.getElementById("total-feedback").textContent =
        `${data.total_feedback} review(s)`;

    // Render breakdown
    for (let i = 1; i <= 5; i++) {
        document.getElementById(`rating-${i}`).textContent = data.rating_breakdown[i];
    }
}
```

**Response:**
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

Always check `res.ok` before using the response data. All errors come back as:

```json
{ "detail": "Human-readable error message here." }
```

| Status Code | Meaning | Suggested UI message |
|-------------|---------|----------------------|
| `404` | Event or student not found | "This event could not be found." |
| `409` | Already registered / duplicate feedback / event full | Show `data.detail` directly — it's readable |
| `403` | Feedback without registration | "You need to register before submitting feedback." |
| `422` | Missing or wrong fields | Check your form field names match the API |

---

## Useful Patterns

### Category filter dropdown

```html
<select id="category-filter" onchange="loadEvents(this.value)">
    <option value="">All Categories</option>
    <option value="Technology">Technology</option>
    <option value="Sports">Sports</option>
    <option value="Arts">Arts</option>
    <option value="Academic">Academic</option>
</select>
```

### Show capacity status

```js
function capacityLabel(event) {
    if (event.capacity === null) return "Open";
    if (event.registration_count >= event.capacity) return "Fully Booked";
    return `${event.capacity - event.registration_count} spots left`;
}
```

### Disable register button if full

```js
const isFull = event.capacity !== null && event.registration_count >= event.capacity;
registerBtn.disabled = isFull;
registerBtn.textContent = isFull ? "Fully Booked" : "Register";
```

---

## Tips

- Store the student's **email in `localStorage`** after registration — you'll need it when submitting feedback since the feedback form only asks for email, not name.
- `capacity: null` means unlimited — always null-check before showing remaining spots.
- `average_rating` is `null` if no feedback has been submitted yet — handle this in your UI.
- The full interactive API docs are available at `http://<backend-ip>:8000/docs` — use it to test endpoints directly in the browser.
