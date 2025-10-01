# python_tests/test_plot_runs_basic.py
import subprocess
import sys
from pathlib import Path

PY = sys.executable

def run_exe(exe: Path, db: Path, seed: int, trials: int, bet_on: int):
    args = [
        str(exe),
        "--db", str(db),
        "--seed", str(seed),
        "--trials", str(trials),
        "--sides", "6",
        "--bet-on", str(bet_on),
        "--payout", "5",
        "--wager", "1",
    ]
    cp = subprocess.run(args, capture_output=True, text=True)
    assert cp.returncode == 0, cp.stdout + cp.stderr

def test_plot_runs_ev_and_grouping(tmpdb, casino_exe, tmp_path: Path, monkeypatch):
    # Generate two seeds & two bet_on, with multiple trials
    for seed in (11, 12):
        for bet in (5, 6):
            for t in (500, 5000):
                run_exe(casino_exe, tmpdb, seed, t, bet)

    out1 = tmp_path / "ev_seed.png"
    cp = subprocess.run(
        [PY, "scripts/plot_runs.py", str(tmpdb),
         "--metric", "ev", "--with-ci",
         "--sides", "6", "--payout", "5",
         "--save", str(out1)],
        capture_output=True, text=True, env={**os.environ, "MPLBACKEND": "Agg"}
    )
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert out1.exists() and out1.stat().st_size > 0

    # Group by seed+bet (one line per (seed, bet_on))
    out2 = tmp_path / "ev_seed_bet.png"
    cp = subprocess.run(
        [PY, "scripts/plot_runs.py", str(tmpdb),
         "--metric", "ev", "--sides", "6", "--payout", "5",
         "--group-by", "seed+bet",
         "--save", str(out2)],
        capture_output=True, text=True, env={**os.environ, "MPLBACKEND": "Agg"}
    )
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert out2.exists() and out2.stat().st_size > 0
