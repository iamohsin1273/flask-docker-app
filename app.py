import os
from contextlib import closing

import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)


def get_db_connection():
    """Open a new PostgreSQL connection using the DATABASE_URL setting."""
    return psycopg2.connect(os.environ["DATABASE_URL"], connect_timeout=3)


@app.route("/")
def home():
    return "Hello from Docker Multi-Stage!"


@app.route("/health")
def health():
    """Liveness check used by Docker, Docker Compose and Jenkins."""
    return jsonify(status="ok")


@app.route("/db")
def db_check():
    """Readiness check that proves the app can reach PostgreSQL."""
    if not os.environ.get("DATABASE_URL"):
        return jsonify(status="error", detail="DATABASE_URL is not set"), 503

    try:
        with closing(get_db_connection()) as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
    except psycopg2.Error:
        app.logger.exception("Database check failed")
        return jsonify(status="error", detail="database unavailable"), 503

    return jsonify(status="ok", database="connected")


if __name__ == "__main__":
    # Development server only. In containers the app is served by gunicorn.
    app.run(host="0.0.0.0", port=5000)
