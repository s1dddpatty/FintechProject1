"""
Unit tests for database infrastructure.
"""

from sqlalchemy.orm import Session

from src.core.config import Settings
from src.db.health import check_database_health
from src.db.session import get_db_session


def test_database_url_postgresql():
    """Test PostgreSQL URL generation."""
    test_settings = Settings(
        use_sqlite=False,
        db_driver="postgresql+psycopg2",
        db_user="test_user",
        db_password="test_password",
        db_host="localhost",
        db_port=5432,
        db_name="test_db",
    )
    assert test_settings.database_url == "postgresql+psycopg2://test_user:test_password@localhost:5432/test_db"


def test_database_url_sqlite():
    """Test SQLite URL generation."""
    test_settings = Settings(use_sqlite=True, sqlite_path="sqlite:///:memory:")
    assert test_settings.database_url == "sqlite:///:memory:"


def test_session_creation():
    """Test that a session can be created and queried using context manager."""
    with get_db_session() as session:
        assert isinstance(session, Session)
        assert session.is_active


def test_health_check_valid(monkeypatch):
    """Test the database health check function returns healthy."""

    class MockConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def execute(self, query):
            pass

    class MockEngine:
        def connect(self):
            return MockConnection()

    monkeypatch.setattr("src.db.health.engine", MockEngine())

    result = check_database_health()
    assert result["status"] == "healthy"
    assert "Successfully connected" in result["details"]
