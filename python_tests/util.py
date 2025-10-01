# python_tests/util.py
from pathlib import Path

def resolve_exe() -> str:
    """
    Return a path to the built casino executable across generators/platforms.
    Searches common single- and multi-config locations on Linux/macOS/Windows.
    Raises FileNotFoundError with a helpful list if nothing is found.
    """
    candidates = [
        # Linux/macOS single-config (Makefiles/Ninja)
        Path("build/src/casino"),
        Path("build/casino"),

        # Multi-config layouts (Ninja Multi-Config, Visual Studio)
        Path("build/src/Release/casino"),
        Path("build/Release/casino"),
        Path("build/src/Debug/casino"),
        Path("build/Debug/casino"),

        # Windows executables
        Path("build/src/casino.exe"),
        Path("build/src/Release/casino.exe"),
        Path("build/Release/casino.exe"),
        Path("build/src/Debug/casino.exe"),
        Path("build/Debug/casino.exe"),

        # Optional: VS local dev out/ tree (useful for local runs)
        Path("out/build/x64-Debug/src/casino.exe"),
        Path("out/build/x64-Release/src/casino.exe"),
    ]

    for p in candidates:
        if p.exists():
            return str(p)

    tried = "\n  - " + "\n  - ".join(map(str, candidates))
    raise FileNotFoundError(f"casino executable not found. Tried:{tried}")
