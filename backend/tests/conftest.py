"""
conftest.py
Shared pytest fixtures: test database, test client, sample PDF generator.
"""

import sys
from pathlib import Path

# Make backend/ importable from tests/
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pytest
import fitz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, get_db
from main import app
from fastapi.testclient import TestClient


@pytest.fixture
def test_db():
    """A fresh in-memory SQLite database for each test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False},poolclass=StaticPool,)
    TestSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(test_db):
    """FastAPI TestClient with the real DB dependency swapped for the test SQLite session."""
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_pdf(tmp_path):
    """Creates a real, minimal PDF file for extraction tests — no external file needed."""
    def _make_pdf(text: str = "Python developer with FastAPI and PostgreSQL experience"):
        path = tmp_path / "test_cv.pdf"
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), text)
        doc.save(str(path))
        doc.close()
        return str(path)

    return _make_pdf