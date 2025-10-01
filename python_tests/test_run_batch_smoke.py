import os
import sys
import sqlite3
import subprocess
from pathlib import Path
from util import resolve_exe

def run(cmd):
    cp = subprocess.run(cmd, capture_output=True, text=True)
    print(cp.stdout)
    print(cp.stderr, file=sys.stderr)
    return cp.returncode

def test_run_batch_skip_and_index(tmp_path):
    db = tmp_path / "ci.db"
    exe = resolve_exe()

    # first pass — should insert
    rc = run([
        sys.executable, "scripts/run_batch.py",
        "--db", str(db),
        "--exe", exe,
        "--seeds", "7..8",
        "--trials", "200..800:200",
        "--wagers", "1",
        "--payouts", "5",
        "--sides", "6",
        "--bet-on", "6",
        "--dedupe-mode", "skip",
    ])
    assert rc == 0

    # second pass — skip identical combos
    rc = run([
        sys.executable, "scripts/run_batch.py",
        "--db", str(db),
        "--exe", exe,
        "--seeds", "7..8",
        "--trials", "200..800:200",
        "--wagers", "1",
        "--payouts", "5",
        "--sides", "6",
        "--bet-on", "6",
        "--dedupe-mode", "skip",
    ])
    assert rc == 0

    # verify row count (not zero, and duplicates weren’t added)
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM games WHERE type='dice';")
    n = cur.fetchone()[0]
    con.close()
    # 2 seeds × 4 trial sizes = 8 rows expected
    assert n == 8
