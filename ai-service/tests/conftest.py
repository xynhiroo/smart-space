import pytest
from sqlalchemy import text
from app.database import SessionLocal, engine


@pytest.fixture(scope="session")
def check_db_connection():
    """Verify that the shared MySQL database is reachable."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


@pytest.fixture(scope="function")
def db_session(check_db_connection):
    """Provide a scoped SQLAlchemy database session for tests."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
