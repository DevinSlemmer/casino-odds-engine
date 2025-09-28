# scripts/plot_runs.py
# Plot casino runs from SQLite (schema v3). One line per seed.
# Metrics: ev (default), roi, hit_rate, ci_width
# Options: --with-ci (EV only), filters, log-x, save to PNG, list metrics.

import argparse
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

METRICS = ["ev", "roi", "hit_rate", "ci_width"]

def load_runs(db_path: str) -> pd.DataFrame:
    con = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        """
        SELECT
            id, created_at, type,
            seed, sides, bet_on, payout, wager,
            trials, hits, hit_rate,
            total_bet, total_return, net_profit,
            ev, roi,
            variance, std_err, ci_lo, ci_hi,
            runtime_ms
        FROM games
        WHERE type='dice'
        """,
        con,
    )
    con.close()
    numeric_cols = [
        "seed","sides","bet_on","payout","wager","trials","hits",
        "hit_rate","total_bet","total_return","net_profit","ev","roi",
        "variance","std_err","ci_lo","ci_hi","runtime_ms"
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # derive ci_width if bounds exist
    if "ci_lo" in df.columns and "ci_hi" in df.columns:
        df["ci_width"] = df["ci_hi"] - df["ci_lo"]
    else:
        df["ci_width"] = None
    return df

def main():
    ap = argparse.ArgumentParser(description="Plot EV/ROI/HitRate/CI-width vs trials (one line per seed).")
    ap.add_argument("db", nargs="?", help="Path to SQLite DB (e.g. data/sim.db)")
    ap.add_argument("--list-metrics", action="store_true", help="List available metrics and exit")
    ap.add_argument("--metric", choices=METRICS, default="ev", help="Y-axis metric")
    ap.add_argument("--with-ci", action="store_true", help="For metric=ev, fill 95%% CI band using ci_lo/ci_hi")
    ap.add_argument("--min-trials", type=float, default=None, help="Keep runs with trials >= this")
    ap.add_argument("--max-trials", type=float, default=None, help="Keep runs with trials <= this")
    ap.add_argument("--sides", type=int, default=None, help="Filter to number of sides")
    ap.add_argument("--payout", type=float, default=None, help="Filter to payout")
    ap.add_argument("--wager", type=float, default=None, help="Filter to wager")
    ap.add_argument("--bet-on", type=int, default=None, help="Filter to bet_on face")
    ap.add_argument("--seed", type=int, nargs="*", default=None, help="Only include these seed(s)")
    ap.add_argument("--log-x", action="store_true", help="Use logarithmic x-axis for trials")
    ap.add_argument("--title", type=str, default=None, help="Custom plot title")
    ap.add_argument("--no-legend", action="store_true", help="Hide legend")
    ap.add_argument("--save", type=str, default=None, help="Save PNG to this path instead of showing")
    args = ap.parse_args()

    if args.list_metrics:
        print("Available metrics:", ", ".join(METRICS))
        return

    if not args.db:
        print("Usage: python scripts/plot_runs.py data/sim.db [--metric ev|roi|hit_rate|ci_width] [options]")
        return

    df = load_runs(args.db)
    if df.empty:
        print("No rows found. Run the simulator with --db to populate the database.")
        return

    # Filters
    if args.min_trials is not None:
        df = df[df["trials"] >= args.min_trials]
    if args.max_trials is not None:
        df = df[df["trials"] <= args.max_trials]
    if args.sides is not None:
        df = df[df["sides"] == args.sides]
    if args.payout is not None:
        df = df[df["payout"] == args.payout]
    if args.wager is not None:
        df = df[df["wager"] == args.wager]
    if args.bet_on is not None:
        df = df[df["bet_on"] == args.bet_on]
    if args.seed is not None and len(args.seed) > 0:
        df = df[df["seed"].isin(args.seed)]

    # Metric-specific requirements
    metric = args.metric
    need_cols = ["trials", "seed", metric]
    df = df.dropna(subset=need_cols)
    if df.empty:
        print("No rows left after filters.")
        return

    df = df.sort_values(["seed", "trials"])

    # Labels
    y_labels = {
        "ev": "EV ($ per play)",
        "roi": "ROI (net_profit / total_bet)",
        "hit_rate": "Hit rate",
        "ci_width": "95% CI width of EV ($/play)"
    }
    ylab = y_labels.get(metric, metric)
    default_title = f"Dice: {metric} vs trials (one line per seed)"
    title = args.title if args.title else default_title

    # Plot
    plt.figure()
    for seed, g in df.groupby("seed", dropna=False):
        g = g.drop_duplicates(subset=["trials"], keep="last")

        # main line
        plt.plot(g["trials"], g[metric], label=f"seed={int(seed)}")

        # Optional CI band for EV
        if metric == "ev" and args.with_ci and "ci_lo" in g.columns and "ci_hi" in g.columns:
            gg = g.dropna(subset=["ci_lo","ci_hi"])
            if not gg.empty:
                plt.fill_between(gg["trials"], gg["ci_lo"], gg["ci_hi"], alpha=0.15)

    if args.log_x:
        plt.xscale("log")

    # Theory line for EV=0 on fair dice
    if metric == "ev":
        plt.axhline(0.0, linestyle="--", linewidth=1)

    plt.title(title)
    plt.xlabel("Number of trials")
    plt.ylabel(ylab)

    if not args.no_legend:
        plt.legend(title="Seed", fontsize="small", ncol=2)

    plt.tight_layout()

    if args.save:
        out_path = Path(args.save)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=120)
        print(f"Saved figure to: {out_path.resolve()}")
    else:
        plt.show()

if __name__ == "__main__":
    main()


# # List metrics
# python scripts\plot_runs.py --list-metrics

# # EV with 95% CI band
# python scripts\plot_runs.py data\sim.db --metric ev --with-ci --sides 6 --payout 5

# # CI width shrinking vs trials (per seed)
# python scripts\plot_runs.py data\sim.db --metric ci_width --sides 6 --payout 5 --log-x

# # ROI by seed
# python scripts\plot_runs.py data\sim.db --metric roi --sides 6 --payout 5

# # Hit rate (should approach 1/sides)
# python scripts\plot_runs.py data\sim.db --metric hit_rate --sides 6 --payout 5

# # Save a PNG for your README
# python scripts\plot_runs.py data\sim.db --metric ev --with-ci --sides 6 --payout 5 --save docs/ev_by_seed.png
