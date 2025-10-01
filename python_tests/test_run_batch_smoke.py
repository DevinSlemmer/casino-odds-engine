# python_tests/test_run_batch_smoke.py
import sqlite3
import subprocess
from pathlib import Path
import sys
import os

PY = sys.executable

def count_rows(db: Path) -> int:
    con = sqlite3.connect(str(db))
    try:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM games;")
        return int(cur.fetchone()[0] or 0)
    finally:
        con.close()

def run_batch(db: Path, exe: Path, **kw):
    args = [PY, "scripts/run_batch.py", "--db", str(db), "--exe", str(exe)]
    for k, v in kw.items():
        if isinstance(v, bool):
            if v:
                args.append(f"--{k.replace('_','-')}")
        else:
            args.extend([f"--{k.replace('_','-')}", str(v)])
    print("RUN:", " ".join(args))
    cp = subprocess.run(args, capture_output=True, text=True)
    print(cp.stdout)
    print(cp.stderr, file=sys.stderr)
    assert cp.returncode == 0

def test_run_batch_skip_and_index(tmpdb, casino_exe):
    # small grid: seeds=7..8, trials=200,400, wagers=1, payouts=5
    run_batch(tmpdb, casino_exe,
              seeds="7..8", trials="200,400",
              wagers="1", payouts="5",
              sides=6, bet_on=6,
              dedupe_mode="skip")
    n1 = count_rows(tmpdb)
    # 2 seeds * 2 trials * 1 payout * 1 wager = 4 rows
    assert n1 == 4

    # Re-run same grid with skip -> should not add rows
    run_batch(tmpdb, casino_exe,
              seeds="7..8", trials="200,400",
              wagers="1", payouts="5",
              sides=6, bet_on=6,
              dedupe_mode="skip")
    n2 = count_rows(tmpdb)
    assert n2 == n1

    # Now enforce UNIQUE index and add a new trial -> +2 rows
    run_batch(tmpdb, casino_exe,
              seeds="7..8", trials="600",
              wagers="1", payouts="5",
              sides=6, bet_on=6,
              dedupe_mode="index")
    n3 = count_rows(tmpdb)
    assert n3 == n2 + 2
