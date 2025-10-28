"""Basic tests to verify setup is correct."""

import sys
from pathlib import Path


def test_python_version():
    """Test that Python version is 3.11 or higher."""
    assert sys.version_info >= (3, 11), "Python 3.11+ is required"


def test_project_structure():
    """Test that essential directories exist."""
    base_path = Path(__file__).parent.parent
    
    assert (base_path / "src").is_dir(), "src directory should exist"
    assert (base_path / "tests").is_dir(), "tests directory should exist"
    assert (base_path / "config").is_dir(), "config directory should exist"
    assert (base_path / "docs").is_dir(), "docs directory should exist"


def test_config_files_exist():
    """Test that essential configuration files exist."""
    base_path = Path(__file__).parent.parent
    
    assert (base_path / "pyproject.toml").is_file(), "pyproject.toml should exist"
    assert (base_path / "docker-compose.yml").is_file(), "docker-compose.yml should exist"
    assert (base_path / ".env.example").is_file(), ".env.example should exist"
    assert (base_path / "README.md").is_file(), "README.md should exist"


def test_source_files_exist():
    """Test that essential source files exist."""
    base_path = Path(__file__).parent.parent
    
    assert (base_path / "src" / "__init__.py").is_file(), "src/__init__.py should exist"
    assert (base_path / "src" / "main.py").is_file(), "src/main.py should exist"
    assert (base_path / "config" / "settings.py").is_file(), "config/settings.py should exist"


def test_imports():
    """Test that essential modules can be imported."""
    try:
        import fastapi
        import pydantic
        import redis
        import celery
        assert True
    except ImportError as e:
        assert False, f"Failed to import required module: {e}"
