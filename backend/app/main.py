from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.database import engine, Base
from app.routers import events, registrations, feedback

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Campus Event Management System API",
    description=(
        "REST API for the Campus Event Management System. "
        "Supports event listing, student registration, feedback & ratings, "
        "and Firebase Cloud Messaging push notifications for new events."
    ),
    version="1.0.0",
    docs_url=None,   # disable default CDN-based docs
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve local Swagger UI assets
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def swagger_ui() -> HTMLResponse:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Campus Event Management API — Docs</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" type="text/css" href="/static/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="/static/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {
                SwaggerUIBundle({
                    url: "/openapi.json",
                    dom_id: '#swagger-ui',
                    presets: [SwaggerUIBundle.presets.apis],
                    layout: "BaseLayout",
                    deepLinking: true
                })
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html)


app.include_router(events.router)
app.include_router(registrations.router)
app.include_router(feedback.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "message": "Campus Event Management API is running. Visit /docs for API documentation.",
    }
