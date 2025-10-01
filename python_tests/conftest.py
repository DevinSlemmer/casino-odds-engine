# python_tests/conftest.py
# python_tests/conftest.py
from pathlib import Path
import pytest
from .util import resolve_exe

@pytest.fixture(scope="session")
def casino_exe() -> Path:
    return Path(resolve_exe())

@pytest.fixture
def tmpdb(tmp_path: Path) -> Path:
    db = tmp_path / "pytest.db"
    db.parent.mkdir(parents=True, exist_ok=True)
    return db
