"""
Pytest configuration and shared fixtures.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import tempfile
import shutil

from app.main import app
from app.config import settings


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def temp_docs_dir():
    """Create a temporary docs directory for testing."""
    temp_dir = tempfile.mkdtemp()
    docs_dir = Path(temp_dir) / "docs"
    docs_dir.mkdir()
    
    # Create a sample markdown file
    sample_file = docs_dir / "test.md"
    sample_file.write_text("# Test Document\n\nThis is a test.")
    
    # Create a subdirectory with a README
    subdir = docs_dir / "architecture"
    subdir.mkdir()
    readme = subdir / "README.md"
    readme.write_text("# Architecture\n\nArchitecture docs.")
    
    yield docs_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_docs_root(monkeypatch, temp_docs_dir):
    """Mock DOCS_ROOT to point to temp directory."""
    # Patch the settings object directly since it's a frozen dataclass
    from app import config
    from dataclasses import replace
    
    # Create a new settings object with updated DOCS_ROOT
    original_settings = config.settings
    new_settings = replace(original_settings, DOCS_ROOT=str(temp_docs_dir))
    
    # Patch the settings in all modules that use it
    monkeypatch.setattr(config, "settings", new_settings)
    
    # Patch in routes/docs.py
    from app.routes import docs
    monkeypatch.setattr(docs, "settings", new_settings)
    
    # Patch in health.py
    from app import health
    monkeypatch.setattr(health, "settings", new_settings)
    
    # Patch in main.py
    from app import main
    monkeypatch.setattr(main, "settings", new_settings)
    
    yield temp_docs_dir


@pytest.fixture(autouse=True)
def reset_env():
    """Reset environment variables before each test."""
    # Store original values
    original_env = os.environ.copy()
    yield
    # Restore original values
    os.environ.clear()
    os.environ.update(original_env)
