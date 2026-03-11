"""Shared pytest fixtures for ProBharatAI backend tests."""
import os
import sys
import sqlite3
import types
import pytest
from unittest.mock import MagicMock

# Ensure backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Stub out heavy optional dependencies that may not be installed ──
# These are only needed at runtime, not for unit tests.
_OPTIONAL_MODULES = [
    "telegram", "telegram.ext",
    "playwright", "playwright.sync_api", "playwright.async_api",
    "pyautogui",
    "openai",
    "anthropic",
    "google", "google.generativeai",
    "groq",
    "langchain", "langgraph",
    "celery", "redis",
    "gspread",
]

for mod_name in _OPTIONAL_MODULES:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()


@pytest.fixture(autouse=True)
def _patch_db(tmp_path, monkeypatch):
    """Redirect all DB access to a temporary SQLite database per test."""
    db_path = tmp_path / "test.db"
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)

    # Patch config values BEFORE importing models
    monkeypatch.setattr("config.DATA_DIR", data_dir)

    # Patch the DB_PATH inside models so every get_connection() uses the temp DB
    import database.models as models
    monkeypatch.setattr(models, "DB_PATH", db_path)

    # Initialize schema in the temp DB
    models.init_db()
    yield


@pytest.fixture()
def client():
    """Create a Flask test client."""
    from main import create_app
    app, _ = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
