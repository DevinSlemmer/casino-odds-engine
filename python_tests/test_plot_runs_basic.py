import os
import sys
import subprocess
from pathlib import Path
from util import resolve_exe

def run(cmd):
    cp = subprocess.run(cmd, capture_output=True, text=True)
    print(cp.stdout)
    print(cp.stderr, file=sys.stderr)
    return cp.returncode

def test_plot_runs_ev_and_grouping(tmp_path, monkeypatch):
    # Use a headless backend for CI
    monkeypatch.setenv("MPLBACKEND", "Agg")

    db = tmp_path / "plot.db"
    png = tmp_path / "ev.png"
    exe = resolve_exe()

    # Create a few rows for two different trial sizes
    rc = run([exe, "--trials", "500",  "--seed", "123", "--sides", "6", "--bet-on", "6",
              "--payout", "5", "--wager", "1", "--db", str(db)])
    assert rc == 0
    rc = run([exe, "--trials", "1000", "--seed", "123", "--sides", "6", "--bet-on", "6",
              "--payout", "5", "--wager", "1", "--db", str(db)])
    assert rc == 0

    # Plot EV (one line per seed) and save
    rc = run([
        sys.executable, "scripts/plot_runs.py", str(db),
        "--metric", "ev",
        "--with-ci",
        "--sides", "6",
        "--payout", "5",
        "--seed", "123",
        "--save", str(png),
    ])
    assert rc == 0
    assert png.exists() and png.stat().st_size > 0
