# scripts/plot_ev.py
import argparse
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser(description="Plot EV vs trials per seed from SQLite (schema v2)")
    ap.add_argument("db", help="Path to SQLite DB (e.g. data/sim.db)")
    ap.add_argument("--min-trials", type=float, default=None, help="Keep runs with trials >= this")
    ap.add_argument("--max-trials", type=float, default=None, help="Keep runs with trials <= this")
    ap.add_argument("--sides", type=int, default=None, help="Filter to specific number of sides")
    ap.add_argument("--payout", type=float, default=None, help="Filter to specific payout")
    ap.add_argument("--seed", type=int, nargs="*", default=None, help="Only include these seed(s)")
    ap.add_argument("--log-x", action="store_true", help="Use log x-axis")
    ap.add_argument("--no-legend", action="store_true", help="Hide legend")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    # New schema: seed, sides, bet_on, payout are real columns
    df = pd.read_sql_query(
        """
        SELECT id, created_at, type, seed, sides, bet_on, payout,
               trials, hits, hit_rate, ev
        FROM games
        WHERE type='dice'
        """,
        con,
    )
    con.close()

    if df.empty:
        print("No rows found. Did you run the simulator with --db after upgrading schema?")
        return

    # Ensure numeric
    for col in ["trials", "ev", "hit_rate", "seed", "sides", "bet_on", "payout"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Apply trial filters
    if args.min_trials is not None:
        df = df[df["trials"] >= args.min_trials]
    if args.max_trials is not None:
        df = df[df["trials"] <= args.max_trials]

    # Apply game parameter filters
    if args.sides is not None:
        df = df[df["sides"] == args.sides]
    if args.payout is not None:
        df = df[df["payout"] == args.payout]
    if args.seed is not None and len(args.seed) > 0:
        df = df[df["seed"].isin(args.seed)]

    df = df.dropna(subset=["trials", "ev", "seed"]).sort_values(["seed", "trials"])

    print(f"Rows after filters: {len(df)}")
    if df.empty:
        print("No rows left after filters.")
        return

    # Plot EV vs trials, one line per seed
    plt.figure()
    for seed, g in df.groupby("seed", dropna=False):
        g = g.drop_duplicates(subset=["trials"], keep="last")
        plt.plot(g["trials"], g["ev"], label=f"seed={int(seed)}")

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
