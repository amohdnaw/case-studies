#!/usr/bin/env python3
"""Study 05 extension: multiplicity on 7,860 strategy search.

Expected maximum Sharpe under null, Benjamini–Hochberg FDR, and deflated Sharpe
for the best observed strategy. Regenerates docs/figures/exh-fig4.svg, exh-fig5.svg
and merges keys into data/exhaustion_results.json.
"""
from __future__ import annotations

import csv
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
FIGS = os.path.join(ROOT, "docs", "figures")
RESULTS = os.path.join(DATA, "exhaustion_results.json")

SEED = 20260716
T_STOCK = 1760          # ~7 years of daily bars
FDR_Q = 0.05
N_SIM = 8000
FEE_RT = 0.0015 * 2     # round-trip fee scale for crypto null SE

# Paper Workbench (DESIGN.md)
PAPER, PAPER_DEEP = "#ffffff", "#fafafa"
INK, INK_FAINT, RUBRIC = "#3d3327", "#877e72", "#8c2f22"
HAIR = "#e2e2e2"


def style(ax):
    ax.set_facecolor(PAPER_DEEP)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(HAIR)
    ax.tick_params(colors=INK_FAINT, labelsize=8)
    ax.grid(color=HAIR, lw=0.6, alpha=0.6)
    ax.set_axisbelow(True)


def load_rows() -> tuple[list[dict], list[dict]]:
    stocks = list(csv.DictReader(open(os.path.join(DATA, "exhaustion_stocks.csv"))))
    crypto = list(csv.DictReader(open(os.path.join(DATA, "exhaustion_crypto.csv"))))
    for r in stocks:
        for k in ("gross", "net", "buyhold", "sharpe"):
            r[k] = float(r[k])
    for r in crypto:
        for k in ("gross", "net", "buyhold", "cost_drag"):
            r[k] = float(r[k])
        r["n_trades"] = max(int(float(r["n_trades"])), 1)
    return stocks, crypto


def effective_T(stocks: list[dict], crypto: list[dict]) -> np.ndarray:
    t_stock = np.full(len(stocks), T_STOCK)
    t_crypto = np.array([max(r["n_trades"], 30) for r in crypto], dtype=float)
    return np.concatenate([t_stock, t_crypto])


def one_sided_pvalues(stocks: list[dict], crypto: list[dict]) -> np.ndarray:
    p_stock = []
    for r in stocks:
        t = r["sharpe"] * np.sqrt(T_STOCK)
        p_stock.append(1.0 - stats.t.cdf(t, df=T_STOCK - 1))
    p_crypto = []
    for r in crypto:
        se = FEE_RT * np.sqrt(r["n_trades"]) * 0.5 + 0.05
        p_crypto.append(1.0 - stats.norm.cdf(r["net"] / se))
    return np.array(p_stock + p_crypto)


def benjamini_hochberg(pvals: np.ndarray, q: float = FDR_Q) -> np.ndarray:
    m = pvals.size
    order = np.argsort(pvals)
    ranked = pvals[order]
    thresh = q * np.arange(1, m + 1) / m
    below = ranked <= thresh
    if not below.any():
        return np.zeros(m, dtype=bool)
    k = np.max(np.where(below)[0])
    cutoff = ranked[k]
    return pvals <= cutoff


def simulate_null_max(T_vec: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    sigmas = 1.0 / np.sqrt(T_vec)
    draws = rng.normal(0.0, sigmas, size=(N_SIM, T_vec.size))
    return draws.max(axis=1)


def deflated_sharpe(sr: float, T: int, e_max: float) -> float:
    sr_std = np.sqrt(1.0 / T)
    return float(stats.norm.cdf((sr - e_max) / sr_std))


def fig4_null_max(max_null: np.ndarray, obs_best_sr: float, e_max: float, n_trials: int) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 3.2), facecolor=PAPER)
    bins = np.linspace(max_null.min() * 0.95, max(max_null.max(), obs_best_sr) * 1.05, 45)
    ax.hist(max_null, bins=bins, color=INK_FAINT, alpha=0.7, edgecolor=HAIR, lw=0.5, density=True)
    ax.axvline(e_max, color=INK, ls="--", lw=1.2, label=f"E[max SR] = {e_max:.2f}")
    ax.axvline(obs_best_sr, color=RUBRIC, lw=2.2, label=f"best observed = {obs_best_sr:.2f}")
    ymax = ax.get_ylim()[1]
    ax.annotate(
        "looks like a winner\nuntil you compare the null",
        xy=(obs_best_sr, ymax * 0.35),
        xytext=(obs_best_sr - 0.55, ymax * 0.78),
        fontsize=8,
        color=INK,
        arrowprops=dict(arrowstyle="->", color=INK_FAINT, lw=0.9),
    )
    ax.set_xlabel("maximum Sharpe across all trials (null simulation)", color=INK_FAINT, fontsize=8)
    ax.set_ylabel("density", color=INK_FAINT, fontsize=8)
    ax.set_title(f"Expected best Sharpe from {n_trials:,} tries under H₀",
                 color=INK, fontsize=9.5, loc="left")
    ax.legend(frameon=False, fontsize=8, labelcolor=INK, loc="upper left")
    style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "exh-fig4.svg"))
    plt.close(fig)


def fig5_discovery_funnel(raw_n: int, bh_n: int, beat_bh_n: int, n_total: int) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 3.0), facecolor=PAPER)
    labels = ["raw p < 0.05\n(Sharpe > 0)", f"BH FDR {FDR_Q:.0%}\nsurvivors", "beat buy-and-hold\n(stocks only)"]
    vals = [raw_n, bh_n, beat_bh_n]
    colors = [INK_FAINT, INK, RUBRIC]
    x = np.arange(3)
    ax.bar(x, vals, width=0.55, color=colors)
    for i, v in enumerate(vals):
        ax.text(i, v + n_total * 0.01, f"{v:,}", ha="center", fontsize=9, color=INK, weight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylabel("strategies flagged", color=INK_FAINT, fontsize=8)
    ax.set_ylim(0, max(vals) * 1.18)
    ax.set_title(f"7,860 hypotheses — multiplicity control vs the honest null", color=INK, fontsize=9.5, loc="left")
    style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "exh-fig5.svg"))
    plt.close(fig)


def merge_results(extra: dict) -> dict:
    with open(RESULTS) as f:
        base = json.load(f)
    base.update(extra)
    with open(RESULTS, "w") as f:
        json.dump(base, f, indent=1)
        f.write("\n")
    return base


# module-level for fig4 title (set in main)
T_vec: np.ndarray = np.array([])


def main():
    stocks, crypto = load_rows()
    n_total = len(stocks) + len(crypto)
    T_vec = effective_T(stocks, crypto)

    pvals = one_sided_pvalues(stocks, crypto)
    bh_mask = benjamini_hochberg(pvals)
    raw_n = int((pvals < 0.05).sum())
    bh_n = int(bh_mask.sum())

    nets = np.array([r["net"] for r in stocks] + [r["net"] for r in crypto])
    buyhold = np.array([r["buyhold"] for r in stocks] + [r["buyhold"] for r in crypto])
    beat_bh_stocks = sum(1 for r in stocks if r["net"] > r["buyhold"])

    rng = np.random.default_rng(SEED)
    max_null = simulate_null_max(T_vec, rng)
    e_max = float(max_null.mean())
    p95_max = float(np.percentile(max_null, 95))

    best = max(stocks, key=lambda r: r["sharpe"])
    obs_best_sr = best["sharpe"]
    dsr_best = deflated_sharpe(obs_best_sr, T_STOCK, e_max)

    fig4_null_max(max_null, obs_best_sr, e_max, n_total)
    fig5_discovery_funnel(raw_n, bh_n, beat_bh_stocks, n_total)

    extra = {
        "multiplicity_n_trials": n_total,
        "multiplicity_null_sim_n": N_SIM,
        "multiplicity_expected_max_sharpe": round(e_max, 3),
        "multiplicity_p95_max_sharpe": round(p95_max, 3),
        "multiplicity_observed_best_sharpe": round(obs_best_sr, 3),
        "multiplicity_best_strategy": f"{best['ticker']} {best['strategy']}",
        "multiplicity_best_net_pct": round(best["net"] * 100, 1),
        "multiplicity_best_buyhold_pct": round(best["buyhold"] * 100, 1),
        "multiplicity_deflated_sharpe_best": round(dsr_best, 4),
        "multiplicity_raw_p005": raw_n,
        "multiplicity_bh_fdr005": bh_n,
        "multiplicity_beat_buyhold_stocks": beat_bh_stocks,
        "multiplicity_fdr_q": FDR_Q,
    }
    out = merge_results(extra)

    print("exh-fig4.svg, exh-fig5.svg written")
    print(f"E[max SR] under null: {e_max:.3f}  (observed best {obs_best_sr:.3f})")
    print(f"DSR best: {dsr_best:.3f}  |  raw p<0.05: {raw_n}  BH: {bh_n}  beat B&H: {beat_bh_stocks}")
    return out


if __name__ == "__main__":
    main()
