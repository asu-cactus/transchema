"""
Chart: accuracy and cost across experiments (iter/early_stop configs) for L1, L4, L9.

Experiments:
  iter10_es5  — L1, L4, L9  (default 10 iter / 5 early stop)
  iter20_es10 — L1, L4, L9
  iter30_es15 — L1, L4, L9
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── File paths ────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_RES  = os.path.join(_HERE, "results_langraph")

EXPERIMENTS = {
    "iter10_es5": {
        "L1": os.path.join(_RES, "mcts_github_partial_l1_41mini_20260409_112147",  "results_summary.csv"),
        "L4": os.path.join(_RES, "mcts_github_partial_l4_41mini_20260409_112242",  "results_summary.csv"),
        "L9": os.path.join(_RES, "mcts_github_partial_l9_41mini_20260409_112302",  "results_summary.csv"),
    },
    "iter20_es10": {
        "L1": os.path.join(_RES, "mcts_github_partial_l1_iter20_es10_20260409_173838", "results_summary.csv"),
        "L4": os.path.join(_RES, "mcts_github_partial_l4_iter20_es10_20260409_184354", "results_summary.csv"),
        "L9": os.path.join(_RES, "mcts_github_partial_l9_iter20_es10_20260409_214142", "results_summary.csv"),
    },
    "iter30_es15": {
        # L1 split across two runs — combine them
        "L1": [
            os.path.join(_RES, "mcts_github_partial_l1_iter30_es15_20260409_173849", "results_summary.csv"),
            os.path.join(_RES, "mcts_github_partial_l1_iter30_es15_20260410_080253", "results_summary.csv"),
        ],
        "L4": os.path.join(_RES, "mcts_github_partial_l4_iter30_es15_20260410_081855", "results_summary.csv"),
        "L9": os.path.join(_RES, "mcts_github_partial_l9_iter30_es15_20260410_125635", "results_summary.csv"),
    },
}

LENGTHS = ["L1", "L4", "L9"]
EXP_LABELS = {
    "iter10_es5":  "iter=10, es=5",
    "iter20_es10": "iter=20, es=10",
    "iter30_es15": "iter=30, es=15",
}


def load(paths):
    """Load one or more CSV paths into a single DataFrame."""
    if isinstance(paths, str):
        paths = [paths]
    return pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)


def summarise(df):
    """Return (correct_count, total_cost $) for a results CSV."""
    df = df.dropna(subset=["is_correct"])
    correct = df["is_correct"].apply(lambda x: str(x).strip().lower() == "true").sum()
    cost = pd.to_numeric(df["cost"], errors="coerce").sum()
    return int(correct), round(cost, 4)


# ── Collect stats ─────────────────────────────────────────────────────────────
stats = {}   # stats[exp][length] = (accuracy, cost)
for exp, lengths in EXPERIMENTS.items():
    stats[exp] = {}
    for length, paths in lengths.items():
        df = load(paths)
        stats[exp][length] = summarise(df)

# ── Print summary table ───────────────────────────────────────────────────────
print(f"{'Experiment':<16} {'Length':<6} {'Correct':>10} {'Cost ($)':>10}")
print("-" * 46)
for exp in EXPERIMENTS:
    for length in LENGTHS:
        if length in stats[exp]:
            correct, cost = stats[exp][length]
            print(f"{exp:<16} {length:<6} {correct:>10} {cost:>10.4f}")

# ── Plot ──────────────────────────────────────────────────────────────────────
exp_keys = list(EXPERIMENTS.keys())
n_exps   = len(exp_keys)
n_lengths = len(LENGTHS)

x       = np.arange(n_lengths)
width   = 0.22
offsets = np.linspace(-(n_exps - 1) / 2, (n_exps - 1) / 2, n_exps) * width

colors = ["#4C72B0", "#DD8452", "#55A868"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=False)

for i, exp in enumerate(exp_keys):
    accs  = []
    costs = []
    for length in LENGTHS:
        if length in stats[exp]:
            a, c = stats[exp][length]
            accs.append(a)
            costs.append(c)
        else:
            accs.append(None)
            costs.append(None)

    bar_x = x + offsets[i]
    acc_vals  = [v if v is not None else 0 for v in accs]
    cost_vals = [v if v is not None else 0 for v in costs]

    # ── Correct cases subplot ─────────────────────────────────────────────────
    bars_acc = ax1.bar(
        bar_x, acc_vals, width,
        color=colors[i], alpha=0.85,
        label=EXP_LABELS[exp], zorder=3,
    )
    for bar, val in zip(bars_acc, accs):
        if val is not None and val > 0:
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.8,
                str(val),
                ha="center", va="bottom",
                fontsize=8, color=colors[i], fontweight="bold",
            )
        elif val is None:
            bar.set_alpha(0)

    # ── Cost subplot ──────────────────────────────────────────────────────────
    bars_cost = ax2.bar(
        bar_x, cost_vals, width,
        color=colors[i], alpha=0.75,
        label=EXP_LABELS[exp], zorder=3,
    )
    for bar, val in zip(bars_cost, costs):
        if val is not None and val > 0:
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"${val:.2f}",
                ha="center", va="bottom",
                fontsize=8, color=colors[i], fontweight="bold",
            )
        elif val is None:
            bar.set_alpha(0)

# ── Axes formatting ───────────────────────────────────────────────────────────
for ax, ylabel, title in [
    (ax1, "Correct Cases",    "Correct Cases by Pipeline Length"),
    (ax2, "Total Cost (USD)", "Total Cost by Pipeline Length"),
]:
    ax.set_xlabel("Pipeline Length", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(LENGTHS, fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)
    ax.set_title(title, fontsize=12, pad=10)
    ax.legend(fontsize=8.5, framealpha=0.9)

ax1.set_ylim(0, 115)
ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f"))

fig.suptitle(
    "MCTS Partial Reward — GitHub benchmark, gpt-4.1-mini",
    fontsize=13, y=1.01,
)
plt.tight_layout()

out_path = os.path.join(_HERE, "partial_reward_experiment_chart.png")
plt.savefig(out_path, dpi=150, bbox_inches="tight")
print(f"\nChart saved → {out_path}")
plt.show()
