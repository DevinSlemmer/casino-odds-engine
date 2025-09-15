# scripts/plot_ev.py
import argparse, re, sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# flexible regex: accepts optional spaces around '=' and commas
SEED_RE   = re.compile(r"(?:^|,)\s*seed\s*=\s*(\d+)(?:\s*,|$)")
SIDES_RE  = re.compile(r"(?:^|,)\s*sides\s*=\s*(\d+)(?:\s*,|$)")
PAYOUT_RE = re.compile(r"(?:^|,)\s*payout\s*=\s*([0-9]+(?:\.[0-9]+)?)(?:\s*,|$)")

def kv(s, pat, cast):
    if s is None:
        return None
    m = pat.search(s)
    return cast(m.group(1)) if m else None

def main():
    ap = argparse.ArgumentParser(description="Plot EV vs trials per seed from SQLite")
    ap.add_argument("db", help="Path to SQLite DB (e.g. data/sim.db)")
    ap.add_argument("--min-trials", type=float, default=None, help="Keep runs with trials >= this")
    ap.add_argument("--max-trials", type=float, default=None, help="Keep runs with trials <= this")
    ap.add_argument("--sides", type=int, default=None, help="Filter to specific sides")
    ap.add_argument("--payout", type=float, default=None, help="Filter to specific payout")
    ap.add_argument("--log-x", action="store_true", help="Use logarithmic x-axis for trials")
    ap.add_argument("--no-legend", action="store_true", help="Hide legend")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    df = pd.read_sql_query(
        """
        SELECT id, created_at, trials, hits, hit_rate, ev, params_json
        FROM games
        WHERE type='dice'
        """,
        con,
    )
    con.close()

    if df.empty:
        print("No dice rows in DB. Run the simulator with --db first.")
        return

    # Ensure numeric (sometimes SQLite → pandas can give object dtype)
    df["trials"] = pd.to_numeric(df["trials"], errors="coerce")
    df["ev"]     = pd.to_numeric(df["ev"], errors="coerce")

    # Parse seed/sides/payout from params_json like "sides=6,bet_on=6,payout=5,seed=42"
    df["seed"]   = df["params_json"].apply(lambda s: kv(s, SEED_RE, int))
    df["sides"]  = df["params_json"].apply(lambda s: kv(s, SIDES_RE, int))
    df["payout"] = df["params_json"].apply(lambda s: kv(s, PAYOUT_RE, float))

    pre = len(df)

    # Apply trial filters
    if args.min_trials is not None:
        df = df[df["trials"] >= args.min_trials]
    if args.max_trials is not None:
        df = df[df["trials"] <= args.max_trials]

    # Apply game filters (only keep rows where we successfully parsed the value)
    if args.sides is not None:
        df = df[df["sides"] == args.sides]
    if args.payout is not None:
        df = df[df["payout"] == args.payout]

    # Drop rows with missing critical values
    df = df.dropna(subset=["trials", "ev", "seed"])

    post = len(df)
    print(f"Rows before filters: {pre}, after filters: {post}")
    if df.empty:
        print("No rows left after filters.")
        return

    # Sort so lines draw left→right
    df = df.sort_values(["seed", "trials"])

    # Plot EV vs trials, one line per seed
    plt.figure()
    for seed, g in df.groupby("seed", dropna=False):
        g = g.drop_duplicates(subset=["trials"], keep="last")
        plt.plot(g["trials"], g["ev"], label=f"seed={seed}")

    if args.log_x:
        plt.xscale("log")

    plt.title("Dice: EV per run by seed")
    plt.xlabel("Number of Trials")
    plt.ylabel("EV per play")
    plt.axhline(0.0, linestyle="--", linewidth=1)

    if not args.no_legend:
        plt.legend(title="Seed", fontsize="small", ncol=2)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
