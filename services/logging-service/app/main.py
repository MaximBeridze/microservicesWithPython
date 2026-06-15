# logging-service — Flask app (not FastAPI — intentional, see docs/specs.md)
#
# Run with:   flask run --port 8006
# Or:         python -m flask --app app.main run --port 8006
#
# YOUR TASK: implement the four consent endpoints and the log deletion endpoint.
# The response shapes are in docs/api-contracts.md.

import os
import threading
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from app.models import ActivityLog, Consent, db

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///./logging.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    # Start the RabbitMQ consumer in a background thread
    from app.consumer import start_consumer
    threading.Thread(target=start_consumer, args=(app,), daemon=True).start()


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "logging-service"})


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _consent_response(consent: Consent):
    return jsonify({
        "user_id": consent.user_id,
        "granted": consent.granted,
        "updated_at": _iso(consent.updated_at),
    })


# ---------------------------------------------------------------------------
# YOUR TASK — implement the five endpoints below
# ---------------------------------------------------------------------------

@app.post("/v1/consent/<user_id>")
def set_consent(user_id):
    """
    Record or update a user's GDPR consent decision.

    Request body: { "granted": true }

    Steps:
    1. Parse request.get_json() to get "granted" (bool)
    2. Look up or create a Consent row for user_id
    3. Set granted and updated_at, then db.session.commit()
    4. Return 200 with { "user_id", "granted", "updated_at" }
    """
    data = request.get_json(silent=True) or {}
    granted = data.get("granted")
    if not isinstance(granted, bool):
        return jsonify({"detail": "granted must be a boolean"}), 400

    consent = Consent.query.filter_by(user_id=user_id).first()
    if consent is None:
        consent = Consent(user_id=user_id)
        db.session.add(consent)

    consent.granted = granted
    consent.updated_at = _now()
    db.session.commit()

    return _consent_response(consent)


@app.get("/v1/consent/<user_id>")
def get_consent(user_id):
    """
    Check a user's current consent status.

    Steps:
    1. Query Consent by user_id
    2. If not found → 404 with { "detail": "No consent record found" }
    3. Otherwise → 200 with { "user_id", "granted", "updated_at" }
    """
    consent = Consent.query.filter_by(user_id=user_id).first()
    if consent is None:
        return jsonify({"detail": "No consent record found"}), 404

    return _consent_response(consent)


@app.delete("/v1/consent/<user_id>")
def withdraw_consent(user_id):
    """
    Withdraw consent — sets granted to False (does not delete the record).

    Steps:
    1. Look up the Consent row; 404 if missing
    2. Set granted=False, update updated_at, commit
    3. Return 200 with { "user_id", "granted", "updated_at" }
    """
    consent = Consent.query.filter_by(user_id=user_id).first()
    if consent is None:
        return jsonify({"detail": "No consent record found"}), 404

    consent.granted = False
    consent.updated_at = _now()
    db.session.commit()

    return _consent_response(consent)


@app.delete("/v1/logs/<user_id>")
def delete_logs(user_id):
    """
    GDPR right to erasure — permanently delete all log entries for a user.

    Steps:
    1. Delete all ActivityLog rows where user_id matches
    2. Commit
    3. Return 200 with { "user_id", "deleted_entries": <count> }
    """
    deleted_entries = ActivityLog.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({
        "user_id": user_id,
        "deleted_entries": deleted_entries,
    })


@app.get("/v1/logs/<user_id>")
def get_logs(user_id):
    """
    List all stored log entries for a user (for testing/verification).

    Returns: { "items": [...], "total": N }
    Each item: { "id", "user_id", "game_id", "action", "message", "created_at" }
    """
    logs = (
        ActivityLog.query
        .filter_by(user_id=user_id)
        .order_by(ActivityLog.created_at.desc())
        .all()
    )

    return jsonify({
        "items": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "game_id": log.game_id,
                "action": log.action,
                "message": log.message,
                "created_at": _iso(log.created_at),
            }
            for log in logs
        ],
        "total": len(logs),
    })
