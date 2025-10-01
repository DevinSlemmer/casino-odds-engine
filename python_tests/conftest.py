# python_tests/conftest.py
import os
from pathlib import Path
import pytest

def find_exe() -> Path:
    # Try common build outputs
    cand = [
        Path("build/src/casino"),
        Path("build/src/Release/casino"),
        Path("build/src/Debug/casino"),
        Path("build/src/Release/casino.exe"),
        Path("build/src/Debug/casino.exe"),
    ]
    for p in cand:
        if p.exists():
            return p
    raise RuntimeError("Could not find built casino executable")

@pytest.fixture(scope="session")
def casino_exe() -> Path:
    return find_exe()

@pytest.fixture
def tmpdb(tmp_path: Path) -> Path:
    db = tmp_path / "pytest.db"
    # ensure parent exists
    db.parent.mkdir(parents=True, exist_ok=True)
    return db
