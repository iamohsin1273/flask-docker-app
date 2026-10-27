import psycopg2
import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


class FakeCursor:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, query):
        self.query = query

    def fetchone(self):
        return (1,)


class FakeConnection:
    closed = False

    def cursor(self):
        return FakeCursor()

    def close(self):
        self.closed = True


def test_home_returns_greeting(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Hello from Docker Multi-Stage!"


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_db_without_database_url_returns_503(client, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    response = client.get("/db")
    assert response.status_code == 503
    assert response.get_json()["status"] == "error"


def test_db_reports_connected(client, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pw@db:5432/test")
    monkeypatch.setattr(app_module, "get_db_connection", lambda: FakeConnection())
    response = client.get("/db")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "connected"}


def test_db_failure_returns_503(client, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pw@db:5432/test")

    def boom():
        raise psycopg2.OperationalError("connection refused")

    monkeypatch.setattr(app_module, "get_db_connection", boom)
    response = client.get("/db")
    assert response.status_code == 503
    assert response.get_json()["detail"] == "database unavailable"
