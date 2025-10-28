#!/usr/bin/env python3
"""Verify that the development environment is properly configured."""

import os
import sys
from pathlib import Path


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False


def check_directory_exists(dirpath: str, description: str) -> bool:
    """Check if a directory exists."""
    if Path(dirpath).is_dir():
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description} missing: {dirpath}")
        return False


def main() -> int:
    """Run all verification checks."""
    print("=" * 60)
    print("FacilIAuto Chatbot - Setup Verification")
    print("=" * 60)
    print()

    checks = []

    # Check project structure
    print("📁 Checking project structure...")
    checks.append(check_directory_exists("src", "Source directory"))
    checks.append(check_directory_exists("src/api", "API directory"))
    checks.append(check_directory_exists("src/services", "Services directory"))
    checks.append(check_directory_exists("src/models", "Models directory"))
    checks.append(check_directory_exists("src/tasks", "Tasks directory"))
    checks.append(check_directory_exists("src/utils", "Utils directory"))
    checks.append(check_directory_exists("tests", "Tests directory"))
    checks.append(check_directory_exists("tests/unit", "Unit tests directory"))
    checks.append(check_directory_exists("tests/integration", "Integration tests directory"))
    checks.append(check_directory_exists("tests/e2e", "E2E tests directory"))
    checks.append(check_directory_exists("config", "Config directory"))
    checks.append(check_directory_exists("docs", "Docs directory"))
    print()

    # Check configuration files
    print("⚙️  Checking configuration files...")
    checks.append(check_file_exists("pyproject.toml", "Poetry config"))
    checks.append(check_file_exists("docker-compose.yml", "Docker Compose config"))
    checks.append(check_file_exists("Dockerfile", "Dockerfile"))
    checks.append(check_file_exists(".env.example", "Environment template"))
    checks.append(check_file_exists(".pre-commit-config.yaml", "Pre-commit config"))
    checks.append(check_file_exists(".gitignore", "Git ignore"))
    checks.append(check_file_exists("Makefile", "Makefile"))
    checks.append(check_file_exists("README.md", "README"))
    print()

    # Check source files
    print("📄 Checking source files...")
    checks.append(check_file_exists("src/__init__.py", "Main package init"))
    checks.append(check_file_exists("src/main.py", "Main application"))
    checks.append(check_file_exists("config/settings.py", "Settings module"))
    checks.append(check_file_exists("config/init.sql", "Database init script"))
    print()

    # Check environment
    print("🔧 Checking environment...")
    if Path(".env").exists():
        print("✅ Environment file: .env")
        checks.append(True)
    else:
        print("⚠️  Environment file not found. Copy .env.example to .env")
        checks.append(False)
    print()

    # Summary
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total) * 100 if total > 0 else 0

    print(f"Results: {passed}/{total} checks passed ({percentage:.1f}%)")
    print("=" * 60)
    print()

    if passed == total:
        print("🎉 All checks passed! Environment is ready.")
        print()
        print("Next steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Run 'make install' to install dependencies")
        print("3. Run 'make docker-up' to start services")
        print("4. Run 'make dev' to start the development server")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
