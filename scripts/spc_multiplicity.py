#!/usr/bin/env python3
"""Study 06: false alarms at 15,000-characteristic scale (multiplicity).

Synthetic Monte Carlo only. Regenerates docs/figures/mult-fig1–3.svg and
data/spc_multiplicity_results.json. Called from notebooks/spc-multiplicity.ipynb
or directly.
"""
from __future__ import annotations

import json
import pathlib

import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIGS = ROOT / "docs" / "figures"
RESULTS = ROOT / "data" / "spc_multiplicity_results.json"

SEED = 20260716
ALPHA = 0.0027          # 3-sigma X-bar per-chart false-alarm rate (in control)
M_PROD = 15_000
N_DAYS = 365
FDR_Q = 0.05

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


def expected_alarms(m: int, alpha: float = ALPHA) -> float:
    return m * alpha


def fwer_at_least_one(m: int, alpha: float = ALPHA) -> float:
    return 1.0 - (1.0 - alpha) ** m


def benjamini_hochberg(pvals: np.ndarray, q: float = FDR_Q) -> np.ndarray:
    """Return boolean mask of rejections."""
    p = np.asarray(pvals, dtype=float)
    m = p.size
    order = np.argsort(p)
    ranked = p[order]
    thresh = q * np.arange(1, m + 1) / m
    below = ranked <= thresh
    if not below.any():
        return np.zeros(m, dtype=bool)
    k = np.max(np.where(below)[0])
    cutoff = ranked[k]
    return p <= cutoff


def simulate_daily_counts(
    rng: np.random.Generator,
    m: int,
    n_days: int,
    alpha: float,
) -> np.ndarray:
    hits = rng.random((n_days, m)) < alpha
    return hits.sum(axis=1).astype(int)


def bh_daily_counts(raw_hits: np.ndarray, q: float = FDR_Q) -> np.ndarray:
    """Apply BH per day to binary alarms; p = alpha for hits, 1 for non-hits."""
    n_days, m = raw_hits.shape
    out = np.zeros(n_days, dtype=int)
    p_hit = ALPHA  # conservative p-value at the 3-sigma threshold
    for d in range(n_days):
        pvals = np.where(raw_hits[d], p_hit, 1.0)
        out[d] = int(benjamini_hochberg(pvals, q).sum())
    return out


def fig1_scale_curve() -> tuple[np.ndarray, np.ndarray]:
    ms = np.array([500, 1000, 2000, 5000, 10_000, 12_000, 15_000])
    expected = ms * ALPHA
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(ms / 1000, expected, "o-", color=INK, lw=2, ms=6)
    ax.axvline(M_PROD / 1000, color=INK_FAINT, ls=":", lw=0.9)
    ax.scatter([M_PROD / 1000], [expected_alarms(M_PROD)], color=RUBRIC, s=70, zorder=5)
    ax.annotate(
        f"production scale\n{expected_alarms(M_PROD):.1f} / shift",
        xy=(M_PROD / 1000, expected_alarms(M_PROD)),
        xytext=(M_PROD / 1000 - 4.5, expected_alarms(M_PROD) + 6),
        fontsize=8.5,
        color=INK_SOFT,
        arrowprops=dict(arrowstyle="->", color=INK_FAINT, lw=0.9),
    )
    ax.set_xlabel("characteristics monitored (thousands)")
    ax.set_ylabel("expected false alarms per shift (E[m·α])")
    ax.set_title("Multiplicity at scale: unadjusted 3σ X-bar charts", loc="left", fontsize=11, pad=8)
    ax.set_xlim(0, 16.5)
    ax.set_ylim(0, max(expected) * 1.15)
    fig.tight_layout()
    fig.savefig(FIGS / "mult-fig1.svg")
    plt.close(fig)
    return ms, expected


def fig2_policy_tradeoff(
    raw: np.ndarray,
    bonf: np.ndarray,
    bh: np.ndarray,
) -> None:
    labels = ["unadjusted\n(α = 0.0027)", "Bonferroni\n(α/m)", f"Benjamini–Hochberg\n(FDR = {FDR_Q:.0%})"]
    means = [raw.mean(), bonf.mean(), bh.mean()]
    p95 = [np.percentile(raw, 95), np.percentile(bonf, 95), np.percentile(bh, 95)]

    fig, ax = plt.subplots(figsize=(8, 3.8))
    x = np.arange(3)
    w = 0.55
    bars = ax.bar(x, means, width=w, color=[RUBRIC, INK, INK_FAINT], alpha=0.92)
    for i, (m, p) in enumerate(zip(means, p95)):
        ax.plot([i - w / 4, i + w / 4], [p, p], color=INK, lw=1.4)
        ax.text(i, p + 1.2, f"95th pct {p:.0f}", ha="center", fontsize=7.5, color=INK_SOFT)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylabel("false alarms per shift (simulated mean)")
    ax.set_ylim(0, max(p95) * 1.18)
    ax.set_title(f"Same in-control process, m = {M_PROD:,} charts, {N_DAYS} shifts", loc="left", pad=8)
    for bar, val in zip(bars, means):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.8,
            f"{val:.1f}",
            ha="center",
            fontsize=9,
            color=INK,
        )
    fig.tight_layout()
    fig.savefig(FIGS / "mult-fig2.svg")
    plt.close(fig)


def fig3_shift_example(
    rng: np.random.Generator,
    raw_hits: np.ndarray,
    raw_daily: np.ndarray,
    bonf_daily: np.ndarray,
    bh_daily: np.ndarray,
) -> dict:
    ex_day = int(np.argmin(np.abs(raw_daily - np.median(raw_daily))))
    ex_raw = int(raw_daily[ex_day])
    ex_bonf = int(bonf_daily[ex_day])
    ex_bh = int(bh_daily[ex_day])

    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.8), gridspec_kw={"width_ratios": [1.2, 1]})

    ax = axes[0]
    bins = np.arange(raw_daily.min() - 0.5, raw_daily.max() + 1.5, 1)
    ax.hist(raw_daily, bins=bins, color=INK_FAINT, alpha=0.65, edgecolor=INK_FAINT, lw=0.6)
    ax.axvline(raw_daily.mean(), color=INK, ls="--", lw=1.2, label=f"mean = {raw_daily.mean():.1f}")
    ax.axvline(ex_raw, color=RUBRIC, lw=2, label=f"example shift = {ex_raw}")
    ax.set_xlabel("false alarms per shift (unadjusted)")
    ax.set_ylabel("number of shifts")
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.set_title("In-control process, 365 simulated shifts", loc="left", fontsize=11, pad=8)

    ax = axes[1]
    policies = ["unadjusted", "Bonferroni", "BH (FDR 5%)"]
    counts = [ex_raw, ex_bonf, ex_bh]
    colors = [RUBRIC, INK, INK_FAINT]
    ax.barh(policies, counts, color=colors, height=0.55)
    ax.set_xlabel("alarms flagged on the example shift")
    ax.set_title("One shift, three policies", loc="left", fontsize=11, pad=8)
    ax.set_xlim(0, max(ex_raw * 1.15, 5))
    for i, c in enumerate(counts):
        ax.text(c + 0.6, i, str(c), va="center", fontsize=9, color=INK)

    fig.tight_layout()
    fig.savefig(FIGS / "mult-fig3.svg")
    plt.close(fig)

    return {
        "example_shift_index": ex_day,
        "example_raw_alarms": ex_raw,
        "example_bonferroni_alarms": ex_bonf,
        "example_bh_alarms": ex_bh,
    }


def build_results(
    ms: np.ndarray,
    expected: np.ndarray,
    raw_daily: np.ndarray,
    bonf_daily: np.ndarray,
    bh_daily: np.ndarray,
    example: dict,
) -> dict:
    m = M_PROD
    return {
        "synthetic": True,
        "seed": SEED,
        "environment": "semiconductor assembly & test (OSAT) — simulated",
        "n_characteristics_production": m,
        "per_chart_alpha": ALPHA,
        "per_chart_alpha_label": "3-sigma X-bar (in control)",
        "fdr_q": FDR_Q,
        "n_days_simulated": N_DAYS,
        "expected_false_alarms_per_shift": round(expected_alarms(m), 2),
        "fwer_per_shift_pct": round(100 * fwer_at_least_one(m), 2),
        "bonferroni_alpha_per_chart": ALPHA / m,
        "expected_bonferroni_per_shift": round(expected_alarms(m, ALPHA / m), 4),
        "sim_mean_unadjusted": round(float(raw_daily.mean()), 2),
        "sim_mean_bonferroni": round(float(bonf_daily.mean()), 2),
        "sim_mean_bh": round(float(bh_daily.mean()), 2),
        "sim_p95_unadjusted": int(np.percentile(raw_daily, 95)),
        "sim_p95_bonferroni": int(np.percentile(bonf_daily, 95)),
        "sim_p95_bh": int(np.percentile(bh_daily, 95)),
        "scale_curve_m": [int(x) for x in ms],
        "scale_curve_expected": [round(float(x), 2) for x in expected],
        "example_shift": example,
        "operational_note": (
            "When dozens of charts alarm on the same shift with no assignable cause, "
            "the family of tests — not each chart in isolation — is the honest unit of inference."
        ),
    }


def main():
    setup_mpl()
    FIGS.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    ms, expected = fig1_scale_curve()

    raw_hits = rng.random((N_DAYS, M_PROD)) < ALPHA
    bonf_hits = rng.random((N_DAYS, M_PROD)) < (ALPHA / M_PROD)
    raw_daily = raw_hits.sum(axis=1)
    bonf_daily = bonf_hits.sum(axis=1)
    bh_daily = bh_daily_counts(raw_hits)

    fig2_policy_tradeoff(raw_daily, bonf_daily, bh_daily)
    example = fig3_shift_example(rng, raw_hits, raw_daily, bonf_daily, bh_daily)

    stats = build_results(ms, expected, raw_daily, bonf_daily, bh_daily, example)
    with RESULTS.open("w") as f:
        json.dump(stats, f, indent=2)
        f.write("\n")

    print("mult-fig1.svg, mult-fig2.svg, mult-fig3.svg written")
    print(f"E[false alarms/shift] at m={M_PROD:,}: {stats['expected_false_alarms_per_shift']}")
    print(f"sim means: raw={stats['sim_mean_unadjusted']}, bonf={stats['sim_mean_bonferroni']}, bh={stats['sim_mean_bh']}")
    print(f"example shift: raw={example['example_raw_alarms']}, bonf={example['example_bonferroni_alarms']}, bh={example['example_bh_alarms']}")


if __name__ == "__main__":
    main()
