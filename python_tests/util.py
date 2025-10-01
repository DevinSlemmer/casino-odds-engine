# python_tests/util.py
from pathlib import Path

def resolve_exe() -> str:
    """
    Return a path to the built casino executable across generators/platforms.
    Checks common single and multi-config locations on Linux/macOS/Windows.
    """
    candidates = [
        # Linux/macOS single-config (Make/Ninja)
        Path("build/src/casino"),
        # Multi-config (Ninja Multi-Config, Visual Studio) – Release/Debug
        Path("build/src/Release/casino"),
        Path("build/src/Debug/casino"),
        # Windows .exe locations
        Path("build/src/casino.exe"),
        Path("build/src/Release/casino.exe"),
        Path("build/src/Debug/casino.exe"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    raise FileNotFoundError(f"casino executable not found in: {', '.join(map(str, candidates))}")
