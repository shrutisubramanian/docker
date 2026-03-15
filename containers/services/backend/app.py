"""
Backend API Service — Flask + MongoDB
Part of the AI-Based Self-Healing Framework for Containers
"""

import os
import time
import logging
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ── App init ─────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# ── MongoDB connection ───────────────────────────────────────────────
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017/")
DB_NAME = os.environ.get("DB_NAME", "selfheal")

client = None
db = None


def get_db():
    """Lazy-connect to MongoDB and return the database handle."""
    global client, db
    if client is None:
        logger.info("Connecting to MongoDB at %s …", MONGO_URI)
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        # Force a connection test
        client.admin.command("ping")
        logger.info("MongoDB connection established.")
    return db


# ── Routes ───────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Root endpoint — basic service info."""
    return jsonify({
        "service": "backend",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    })


@app.route("/health")
def health():
    """Health-check used by Docker & the monitoring stack."""
    try:
        database = get_db()
        database.command("ping")
        return jsonify({"status": "healthy", "mongo": "connected"}), 200
    except Exception as exc:
        logger.error("Health-check failed: %s", exc)
        return jsonify({"status": "unhealthy", "error": str(exc)}), 503


@app.route("/api/events", methods=["GET"])
def get_events():
    """Return all recorded events from MongoDB."""
    try:
        database = get_db()
        events = list(
            database.events.find({}, {"_id": 0}).sort("timestamp", -1).limit(100)
        )
        return jsonify({"events": events}), 200
    except Exception as exc:
        logger.error("Failed to fetch events: %s", exc)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/events", methods=["POST"])
def create_event():
    """Record a new event (container status change, failure, etc.)."""
    try:
        data = request.get_json(force=True)
        data["timestamp"] = datetime.utcnow().isoformat()
        database = get_db()
        database.events.insert_one(data)
        data.pop("_id", None)
        logger.info("Event recorded: %s", data)
        return jsonify({"message": "Event recorded", "event": data}), 201
    except Exception as exc:
        logger.error("Failed to record event: %s", exc)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/status")
def system_status():
    """Aggregate system status for the dashboard."""
    try:
        database = get_db()
        event_count = database.events.count_documents({})
        return jsonify({
            "backend": "running",
            "mongo": "connected",
            "total_events": event_count,
            "uptime": time.process_time(),
        }), 200
    except Exception as exc:
        logger.error("Status check failed: %s", exc)
        return jsonify({"backend": "running", "mongo": "disconnected", "error": str(exc)}), 200


@app.route("/api/stress/cpu")
def stress_cpu():
    """Trigger an artificial CPU spike (for failure-injection demo)."""
    logger.warning("CPU stress endpoint hit — starting infinite loop for 30 s")
    end = time.time() + 30
    while time.time() < end:
        _ = sum(i * i for i in range(10_000))
    return jsonify({"message": "CPU stress complete"}), 200


# ── Entrypoint ───────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info("Starting backend on port %d …", port)
    app.run(host="0.0.0.0", port=port, debug=False)
