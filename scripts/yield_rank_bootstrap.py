#!/usr/bin/env python3
"""Study 03 extension: lot-clustered bootstrap rank stability on recoverable units.

Synthetic only. Regenerates docs/figures/yield-fig4.svg and merges keys into
data/yield_results.json. Called from notebooks/icos-yield.ipynb or directly.
"""
from __future__ import annotations

import json
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIGS = ROOT / "docs" / "figures"
DATA = ROOT / "data" / "yield_synthetic.csv"
RESULTS = ROOT / "data" / "yield_results.json"

SEED = 20260712
N_BOOT = 2000

# paper-workbench tokens (DESIGN.md)
PAPER = "#ffffff"
INK = "#2e2f31"
INK_SOFT = "#58595a"
INK_FAINT = "#7a7a7a"
RUBRIC = "#c0392b"


def setup_mpl():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Iowan Old Style", "Palatino Linotype", "Georgia", "serif"],
        "font.size": 10,
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "axes.edgecolor": INK_FAINT,
        "axes.labelcolor": INK_SOFT,
        "text.color": INK,
        "xtick.color": INK_SOFT,
        "ytick.color": INK_SOFT,
        "axes.titlesize": 11,
        "axes.labelsize": 9.5,
        "figure.dpi": 110,
    })


def lot_category_matrix(df: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    """Rows = lots, cols = categories; values = scrapped (recoverable) units."""
    scrapped = df[df.scrapped]
    pivot = (
        scrapped.pivot_table(
            index="lot",
            columns="defect_category",
            aggfunc="size",
            fill_value=0,
        )
        .astype(np.int32)
    )
    return pivot.values, pivot.columns.tolist()


def run_bootstrap(lot_matrix: np.ndarray, categories: list[str], rng: np.random.Generator) -> dict:
    n_lots, n_cat = lot_matrix.shape
    point = lot_matrix.sum(axis=0)
    order = np.argsort(-point)
    rank1, rank2 = categories[order[0]], categories[order[1]]

    recov = np.empty((N_BOOT, n_cat), dtype=np.float64)
    share = np.empty((N_BOOT, n_cat), dtype=np.float64)
    rank = np.empty((N_BOOT, n_cat), dtype=np.int16)

    for b in range(N_BOOT):
        idx = rng.integers(0, n_lots, size=n_lots)
        totals = lot_matrix[idx].sum(axis=0)
        recov[b] = totals
        total = totals.sum()
        share[b] = 100 * totals / max(total, 1)
        order_desc = np.argsort(-totals)
        r = np.empty(n_cat, dtype=np.int16)
        r[order_desc] = np.arange(1, n_cat + 1, dtype=np.int16)
        rank[b] = r

    gap = recov[:, order[0]] - recov[:, order[1]]

    def pct(x, q):
        return float(np.percentile(x, q))

    p_rank1 = {categories[i]: float(np.mean(rank[:, i] == 1)) for i in range(n_cat)}

    return {
        "categories": categories,
        "rank1": rank1,
        "rank2": rank2,
        "recov": recov,
        "share": share,
        "rank": rank,
        "gap": gap,
        "point_recov": {categories[i]: int(point[i]) for i in range(n_cat)},
        "p_rank1": p_rank1,
        "gap_ci_units": [int(round(pct(gap, 2.5))), int(round(pct(gap, 97.5)))],
        "gap_excludes_zero_pct": round(100 * float(np.mean(gap > 0)), 1),
    }


def fig4_rank_bootstrap(stats: dict) -> None:
    categories = stats["categories"]
    cat_idx = {c: i for i, c in enumerate(categories)}
    rank1, rank2 = stats["rank1"], stats["rank2"]
    focus = [rank1, rank2, "cosmetic mark", "die crack"]
    seen: set[str] = set()
    focus = [c for c in focus if not (c in seen or seen.add(c))]

    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.9), gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    y = np.arange(len(focus))[::-1]
    for i, cat in enumerate(focus):
        yy = len(focus) - 1 - i
        j = cat_idx[cat]
        med = float(np.median(stats["share"][:, j]))
        lo, hi = np.percentile(stats["share"][:, j], [2.5, 97.5])
        color = RUBRIC if cat == rank1 else (INK if cat == rank2 else INK_SOFT)
        lw = 2.2 if cat in (rank1, rank2) else 1.2
        ax.hlines(yy, lo, hi, color=color, lw=lw, alpha=0.95)
        ax.plot(med, yy, "o", color=color, ms=7 if cat in (rank1, rank2) else 5, zorder=3)
        if cat == rank1:
            ax.annotate(
                f"rank 1 in {100 * stats['p_rank1'][cat]:.1f}% of replicates",
                xy=(hi, yy),
                xytext=(hi + 1.2, yy + 0.35),
                fontsize=8,
                color=INK_SOFT,
                arrowprops=dict(arrowstyle="->", color=INK_FAINT, lw=0.8),
            )

    ax.set_yticks(y)
    ax.set_yticklabels([c.replace(" ", "\n") for c in focus], fontsize=8.5)
    ax.set_xlabel("share of total scrap (recoverable units), %")
    ax.set_title("Lot-clustered bootstrap 95% CI", loc="left", fontsize=11, pad=8)
    ax.set_xlim(0, max(float(np.percentile(stats["share"][:, cat_idx[rank1]], 97.5)) * 1.35, 35))

    ax = axes[1]
    contested = [rank1, rank2, "cosmetic mark"]
    x = np.arange(len(contested))
    p1 = [100 * stats["p_rank1"][c] for c in contested]
    p_top3 = [100 * float(np.mean(stats["rank"][:, cat_idx[c]] <= 3)) for c in contested]
    w = 0.36
    ax.bar(x - w / 2, p1, width=w, color=RUBRIC, label="P(rank = 1)")
    ax.bar(x + w / 2, p_top3, width=w, color=INK_FAINT, label="P(rank ≤ 3)")
    ax.set_xticks(x)
    ax.set_xticklabels([c.replace(" ", "\n") for c in contested], fontsize=8.5)
    ax.set_ylabel("% of bootstrap replicates")
    ax.set_ylim(0, 105)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.set_title("Rank stability under lot resampling", loc="left", fontsize=11, pad=8)

    gap_lo, gap_hi = stats["gap_ci_units"]
    fig.text(
        0.5,
        0.02,
        f"Gap {rank1} − {rank2}: "
        f"{stats['point_recov'][rank1] - stats['point_recov'][rank2]:,} units "
        f"(95% CI [{gap_lo:,}, {gap_hi:,}]; "
        f"{stats['gap_excludes_zero_pct']:.0f}% of replicates rank #1 above #2)",
        ha="center",
        fontsize=8.5,
        color=INK_SOFT,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(FIGS / "yield-fig4.svg")
    plt.close(fig)


def merge_results(stats: dict) -> dict:
    with RESULTS.open() as f:
        base = json.load(f)

    top5 = sorted(stats["point_recov"], key=stats["point_recov"].get, reverse=True)[:5]
    cat_idx = {c: i for i, c in enumerate(stats["categories"])}

    boot_cats = []
    for cat in top5:
        j = cat_idx[cat]
        boot_cats.append({
            "category": cat,
            "recoverable_units": int(stats["point_recov"][cat]),
            "share_pct": round(float(np.median(stats["share"][:, j])), 2),
            "share_ci_pct": [round(float(x), 2) for x in np.percentile(stats["share"][:, j], [2.5, 97.5])],
            "p_rank1": round(stats["p_rank1"][cat], 4),
            "p_rank_top3": round(float(np.mean(stats["rank"][:, j] <= 3)), 4),
        })

    base.update({
        "bootstrap_n": N_BOOT,
        "bootstrap_cluster": "lot",
        "bootstrap_rank1_category": stats["rank1"],
        "bootstrap_rank2_category": stats["rank2"],
        "bootstrap_p_rank1_top_lever": round(stats["p_rank1"][stats["rank1"]], 4),
        "bootstrap_p_rank1_cosmetic_mark": round(stats["p_rank1"]["cosmetic mark"], 4),
        "bootstrap_gap_rank1_rank2_units": int(
            stats["point_recov"][stats["rank1"]] - stats["point_recov"][stats["rank2"]]
        ),
        "bootstrap_gap_rank1_rank2_ci_units": stats["gap_ci_units"],
        "bootstrap_gap_excludes_zero_pct": stats["gap_excludes_zero_pct"],
        "bootstrap_top5": boot_cats,
    })

    with RESULTS.open("w") as f:
        json.dump(base, f, indent=2)
        f.write("\n")
    return base


def main():
    setup_mpl()
    FIGS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA)
    df["scrapped"] = ~df.recoverable.astype(bool)

    lot_matrix, categories = lot_category_matrix(df)
    rng = np.random.default_rng(SEED + 99)

    stats = run_bootstrap(lot_matrix, categories, rng)
    fig4_rank_bootstrap(stats)
    out = merge_results(stats)

    print("yield-fig4.svg written")
    print(f"rank 1 stability ({stats['rank1']}): {100 * out['bootstrap_p_rank1_top_lever']:.1f}%")
    print(f"gap {stats['rank1']} − {stats['rank2']}: {out['bootstrap_gap_rank1_rank2_units']:,} units "
          f"CI {out['bootstrap_gap_rank1_rank2_ci_units']}")
    print(f"cosmetic mark P(rank=1): {100 * out['bootstrap_p_rank1_cosmetic_mark']:.1f}%")


if __name__ == "__main__":
    main()
