# scripts/run_batch.py
# Serial batch runner for casino sims (dice).
# - Trials spec supports ranges with step: "1000..10000:1000" (and CSV mixing)
# - Dedupe handling: --dedupe-mode {skip,index,none}
# - Ensures DB schema exists; can create UNIQUE index when requested
# - Serial execution to avoid SQLite write-lock contention
# - QoL: --sleep-ms, --dry-run, --verbose

import argparse
import itertools
import os
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import List, Dict

DEFAULT_EXE_WIN = r".\out\build\x64-Debug\src\casino.exe"
DEFAULT_EXE_UNIX = "./build/src/casino"

def ensure_schema(db_path: str):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS games (
      id           INTEGER PRIMARY KEY AUTOINCREMENT,
      created_at   TEXT    DEFAULT CURRENT_TIMESTAMP,
      type         TEXT    NOT NULL,
      seed         INTEGER NOT NULL,
      sides        INTEGER NOT NULL,
      bet_on       INTEGER NOT NULL,
      payout       REAL    NOT NULL,
      wager        REAL    NOT NULL,
      trials       INTEGER NOT NULL,
      hits         INTEGER NOT NULL,
      hit_rate     REAL    NOT NULL,
      total_bet    REAL    NOT NULL,
      total_return REAL    NOT NULL,
      net_profit   REAL    NOT NULL,
      ev           REAL    NOT NULL,
      roi          REAL    NOT NULL,
      variance     REAL    NOT NULL,
      std_err      REAL    NOT NULL,
      ci_lo        REAL    NOT NULL,
      ci_hi        REAL    NOT NULL,
      runtime_ms   INTEGER NOT NULL
    );
    """)
    con.commit()
    con.close()

def create_indexes(db_path: str, unique: bool = False):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    if unique:
        cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uniq_games_combo
        ON games(type, seed, sides, bet_on, payout, wager, trials);
        """)
    else:
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_games_params
        ON games(type, seed, sides, bet_on, payout, wager, trials);
        """)
    con.commit()
    con.close()

def exists_row(db_path: str, params: Dict) -> bool:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""
        SELECT 1 FROM games
        WHERE type=? AND seed=? AND sides=? AND bet_on=?
          AND payout=? AND wager=? AND trials=?
        LIMIT 1;
    """, (
        params["type"], params["seed"], params["sides"], params["bet_on"],
        params["payout"], params["wager"], params["trials"],
    ))
    r = cur.fetchone()
    con.close()
    return r is not None

def expand_seeds(spec: str) -> List[int]:
    out: List[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if ".." in part:
            a, b = part.split("..", 1)
            a, b = int(float(a)), int(float(b))
            step = 1 if b >= a else -1
            out.extend(range(a, b + step, step))
        else:
            out.append(int(float(part)))
    return out

def expand_trials(spec: str) -> List[int]:
    """
    '1000,2000,5000'
    '1000..10000:1000' => 1000,2000,...,10000
    Mix allowed: '1000..10000:1000,50000,100000'
    """
    out: List[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if ".." in part:
            rng, _, step_str = part.partition(":")
            a_str, _, b_str = rng.partition("..")
            a, b = int(float(a_str)), int(float(b_str))
            if step_str:
                step = int(float(step_str))
                if step <= 0:
                    raise ValueError(f"Step must be > 0 in trials spec: {part}")
            else:
                step = 1 if b >= a else -1
            if (b - a) * step < 0:
                step = -abs(step)
            out.extend(range(a, b + (1 if step > 0 else -1), step))
        else:
            out.append(int(float(part)))
    return sorted(set(out))

def run_one(exe: str, db_path: str, p: Dict, cwd: Path, verbose: bool=False) -> tuple[int, str]:
    args = [
        exe,
        "--game", "dice",
        "--seed", str(p["seed"]),
        "--trials", str(p["trials"]),
        "--sides", str(p["sides"]),
        "--bet-on", str(p["bet_on"]),
        "--payout", str(p["payout"]),
        "--wager", str(p["wager"]),
        "--db", db_path,
    ]
    if verbose:
        print(">", " ".join(args))
    proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    tail = (proc.stdout + "\n" + proc.stderr)[-600:]
    return proc.returncode, tail

def main():
    ap = argparse.ArgumentParser(description="Serial batch runner for casino sims (dice).")
    ap.add_argument("--db", required=True, help="Path to SQLite DB (e.g. data/sim.db)")
    ap.add_argument("--exe", default=DEFAULT_EXE_WIN if os.name == "nt" else DEFAULT_EXE_UNIX,
                    help="Path to casino executable")
    ap.add_argument("--seeds", default="42", help="CSV or ranges, e.g. '1..10' or '1,2,5'")
    ap.add_argument("--trials", default="10000,100000",
                    help="CSV or ranges with step, e.g. '1000..10000:1000,50000,100000'")
    ap.add_argument("--sides", type=int, default=6, help="Number of sides")
    ap.add_argument("--bet-on", type=int, default=6, help="Bet face (1..sides)")
    ap.add_argument("--payouts", default="5", help="CSV of payouts, e.g. '4.5,5,6'")
    ap.add_argument("--wagers", default="1", help="CSV of wagers, e.g. '1,5,10'")
    ap.add_argument("--dedupe-mode", choices=["skip","index","none"], default="skip",
                    help="How to handle duplicates: skip (default), index (enforce UNIQUE), none (allow)")
    ap.add_argument("--sleep-ms", type=int, default=0, help="Sleep this many ms between runs")
    ap.add_argument("--dry-run", action="store_true", help="Print the run plan but do not execute")
    ap.add_argument("--verbose", action="store_true", help="Print each command line before executing")
    args = ap.parse_args()

    db_path = str(Path(args.db))
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    # Ensure schema before indexing
    ensure_schema(db_path)
    create_indexes(db_path, unique=(args.dedupe_mode == "index"))

    # Build parameter grid
    seeds = expand_seeds(args.seeds)
    trials = expand_trials(args.trials)
    payouts = [float(x) for x in args.payouts.split(",") if x.strip()]
    wagers = [float(x) for x in args.wagers.split(",") if x.strip()]

    grid = [{
        "type": "dice",
        "seed": int(seed),
        "trials": int(t),
        "sides": int(args.sides),
        "bet_on": int(args.bet_on),
        "payout": float(payout),
        "wager": float(wager),
    } for seed, t, payout, wager in itertools.product(seeds, trials, payouts, wagers)]

    # Dedupe if requested
    if args.dedupe_mode == "skip":
        before = len(grid)
        grid = [p for p in grid if not exists_row(db_path, p)]
        print(f"Skip mode: {before - len(grid)} existing combos skipped; {len(grid)} to run.")
    else:
        print(f"{len(grid)} total runs to execute.")

    if not grid:
        print("Nothing to do.")
        return

    exe_path = Path(args.exe)
    if not exe_path.exists():
        raise SystemExit(f"Executable not found: {exe_path} "
                         f"(hint: pass --exe .\\out\\build\\x64-Debug\\src\\casino.exe)")
    cwd = exe_path.parent
    db_abs = str(Path(db_path).resolve())

    successes = failures = 0
    total = len(grid)
    sleep_s = max(0, args.sleep_ms) / 1000.0

    if args.dry_run:
        for p in grid:
            tag = f"seed={p['seed']}, trials={p['trials']}, payout={p['payout']}, wager={p['wager']}"
            print("[PLAN]", tag)
        print(f"Planned {total} runs (dry-run).")
        return

    for idx, p in enumerate(grid, start=1):
        tag = f"seed={p['seed']}, trials={p['trials']}, payout={p['payout']}, wager={p['wager']}"
        print(f"({idx}/{total}) running {tag} ...")
        rc, tail = run_one(str(exe_path), db_abs, p, cwd, verbose=args.verbose)
        if rc == 0:
            successes += 1
            print(f"[OK] {tag}")
        else:
            failures += 1
            print(f"[ERR rc={rc}] {tag}\n{tail}\n")
        if sleep_s > 0:
            time.sleep(sleep_s)

    print(f"\nDone. Successes: {successes}, Failures: {failures}")
    if failures > 0:
        print("Tip: if you ever re-enable dedupe=index or parallel runs elsewhere, "
              "ensure your C++ DB layer uses PRAGMA journal_mode=WAL and sqlite3_busy_timeout.")

if __name__ == "__main__":
    main()
