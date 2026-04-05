import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_firebase_initialized = False


def _init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return True

    creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")

    if not os.path.exists(creds_path):
        logger.warning(
            "Firebase credentials file not found at '%s'. "
            "FCM notifications will be disabled. "
            "Set FIREBASE_CREDENTIALS_PATH in your .env file.",
            creds_path,
        )
        return False

    try:
        import firebase_admin
        from firebase_admin import credentials

        cred = credentials.Certificate(creds_path)
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("Firebase Admin SDK initialized successfully.")
        return True
    except Exception as exc:
        logger.error("Failed to initialize Firebase Admin SDK: %s", exc)
        return False


def send_new_event_notification(event_title: str, event_id: int, tokens: list[str]) -> None:
    """
    Send an FCM push notification to all registered device tokens
    announcing a new campus event.

    Args:
        event_title: Title of the newly created event.
        event_id:    Database ID of the event.
        tokens:      List of FCM device tokens to notify.
    """
    if not tokens:
        return

    if not _init_firebase():
        logger.info("FCM skipped — Firebase not configured.")
        return

    try:
        from firebase_admin import messaging

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title="New Campus Event",
                body=f"📅 {event_title} has just been added. Tap to register!",
            ),
            data={
                "event_id": str(event_id),
                "type": "new_event",
            },
            tokens=tokens,
        )

        response = messaging.send_each_for_multicast(message)
        logger.info(
            "FCM multicast: %d success, %d failure(s) for event '%s'.",
            response.success_count,
            response.failure_count,
            event_title,
        )
    except Exception as exc:
        logger.error("FCM send failed: %s", exc)
