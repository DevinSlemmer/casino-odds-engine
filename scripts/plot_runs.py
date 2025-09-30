# scripts/plot_runs.py
# Plot casino runs from SQLite (schema v3).
# Metrics: ev (default), roi, hit_rate, ci_width
# Options: --with-ci (EV only), filters, log-x, save to PNG, list metrics.
# New: --group-by {seed, seed+bet} to draw one line per seed or per (seed, bet_on)

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

def expand_betons(spec: str):
    """
    Expand '6' or '1..6' or '1,3,6' into a sorted, unique list of ints.
    """
    xs = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if ".." in part:
            a, b = part.split("..", 1)
            a, b = int(float(a)), int(float(b))
            step = 1 if b >= a else -1
            xs.extend(range(a, b + step, step))
        else:
            xs.append(int(float(part)))
    return sorted(set(xs))


def main():
    ap = argparse.ArgumentParser(description="Plot EV/ROI/HitRate/CI-width vs trials (one line per seed or per (seed, bet)).")
    ap.add_argument("db", nargs="?", help="Path to SQLite DB (e.g. data/sim.db)")
    ap.add_argument("--list-metrics", action="store_true", help="List available metrics and exit")
    ap.add_argument("--metric", choices=METRICS, default="ev", help="Y-axis metric")
    ap.add_argument("--with-ci", action="store_true", help="For metric=ev, fill 95%% CI band using ci_lo/ci_hi")

    # Filters
    ap.add_argument("--min-trials", type=float, default=None, help="Keep runs with trials >= this")
    ap.add_argument("--max-trials", type=float, default=None, help="Keep runs with trials <= this")
    ap.add_argument("--sides", type=int, default=None, help="Filter to number of sides")
    ap.add_argument("--payout", type=float, default=None, help="Filter to payout")
    ap.add_argument("--wager", type=float, default=None, help="Filter to wager")
    ap.add_argument("--bet-on", type=str, default=None, help="Filter to one or more bet_on faces. Accepts CSV or ranges, e.g. '6', '1..6', or '1,3,6'")
    ap.add_argument("--seed", type=int, nargs="*", default=None, help="Only include these seed(s)")

    # Axes / grouping / output
    ap.add_argument("--log-x", action="store_true", help="Use logarithmic x-axis for trials")
    ap.add_argument("--group-by", choices=["seed", "seed+bet"], default="seed",
                    help="Group lines by 'seed' (default) or by 'seed+bet' for one line per (seed, bet_on).")
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
    if args.bet_on:
        bet_list = expand_betons(args.bet_on)
        if len(bet_list) == 0:
            print("Warning: --bet-on provided but parsed no valid values.")
        else:
            df = df[df["bet_on"].isin(bet_list)]
    if args.seed is not None and len(args.seed) > 0:
        df = df[df["seed"].isin(args.seed)]

    # Metric-specific requirements
    metric = args.metric
    need_cols = ["trials", metric]
    # We always need seed for labeling; if grouping by seed+bet, we also need bet_on
    need_cols.append("seed")
    if args.group_by == "seed+bet":
        need_cols.append("bet_on")

    df = df.dropna(subset=need_cols)
    if df.empty:
        print("No rows left after filters.")
        return

    # Sort for nice line drawing
    sort_cols = ["seed", "trials"] if args.group_by == "seed" else ["seed", "bet_on", "trials"]
    df = df.sort_values(sort_cols)

    # Labels
    y_labels = {
        "ev": "EV ($ per play)",
        "roi": "ROI (net_profit / total_bet)",
        "hit_rate": "Hit rate",
        "ci_width": "95% CI width of EV ($/play)"
    }
    ylab = y_labels.get(metric, metric)

    if args.group_by == "seed":
        default_title = f"Dice: {metric} vs trials (one line per seed)"
        legend_title = "Seed"
        group_cols = ["seed"]
        label_fmt = lambda key: f"seed={int(key[0])}"
    else:
        default_title = f"Dice: {metric} vs trials (one line per seed,bet_on)"
        legend_title = "Seed, Bet"
        group_cols = ["seed", "bet_on"]
        label_fmt = lambda key: f"seed={int(key[0])}, bet_on={int(key[1])}"

    title = args.title if args.title else default_title

    # Plot
    plt.figure()
    for key, g in df.groupby(group_cols, dropna=False):
        g = g.drop_duplicates(subset=["trials"], keep="last").sort_values("trials")
        plt.plot(g["trials"], g[metric], label=label_fmt(key))

        # Optional CI band for EV
        if metric == "ev" and args.with_ci and {"ci_lo", "ci_hi"}.issubset(g.columns):
            gg = g.dropna(subset=["ci_lo", "ci_hi"])
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
        plt.legend(title=legend_title, fontsize="small", ncol=2)

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


# # Keep seed fixed, vary bet_on (one line per side)
# python scripts\plot_runs.py data\sim.db --metric ev --sides 6 --payout 5 --seed 42 --group-by seed+bet

# # Multiple seeds, all sides, log-x axis, CI band
# python scripts\plot_runs.py data\sim.db --metric ev --with-ci --sides 6 --payout 5 --group-by seed+bet --log-x

# # Only look at sides 1, 3, and 6
# python scripts\plot_runs.py data\sim.db --metric ev --bet-on 1,3,6

# # Look at all sides (1..6) for seed 42
# python scripts\plot_runs.py data\sim.db --metric ev --seed 42 --bet-on 1..6 --group-by seed+bet

# # Compare even sides only, log-scaled x
# python scripts\plot_runs.py data\sim.db --metric hit_rate --bet-on 2,4,6 --log-x
