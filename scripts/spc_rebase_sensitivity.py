#!/usr/bin/env python3
"""Study 02 extensions: within-subgroup autocorrelation + gate operating curve.

Synthetic only. Regenerates docs/figures/spc-fig4.svg, spc-fig5.svg and merges
keys into data/spc_results.json. Called from notebooks/spc-rebase.ipynb or directly.
"""
from __future__ import annotations

import json
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIGS = ROOT / "docs" / "figures"
RESULTS = ROOT / "data" / "spc_results.json"

D2, C4_5, A2 = 2.326, 0.9400, 0.577
USL, LSL, GATE = 1.0, -1.0, 1.33
K, N = 25, 5
SEED = 20260712

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


def summarise_matrix(m: np.ndarray, d2: float = D2, a2: float = A2) -> dict:
    """m shape (K, N) — one characteristic."""
    xbar = m.mean(1)
    R = m.max(1) - m.min(1)
    xbb, Rbar = m.mean(), R.mean()
    sw_rd2 = Rbar / d2
    s_over = m.std(ddof=1)
    dist = min(USL - xbb, xbb - LSL)
    cwk = dist / (3 * sw_rd2)
    ppk = dist / (3 * s_over)
    ucl, lcl = xbb + a2 * Rbar, xbb - a2 * Rbar
    stable = bool(((xbar <= ucl) & (xbar >= lcl)).all())
    return {
        "sw_rd2": sw_rd2,
        "s_over": s_over,
        "cwk": cwk,
        "ppk": ppk,
        "stable": stable,
        "within_fail": cwk < GATE,
        "overall_fail": ppk < GATE,
        "flipped": (cwk >= GATE) and (ppk < GATE),
    }


def gen_drift_ar1_n(
    sw: float, sb: float, rng: np.random.Generator, k: int, n: int
) -> np.ndarray:
    center = rng.normal(0, 0.04)
    phi = 0.85
    e = rng.normal(0, sb * np.sqrt(1 - phi**2), k)
    means = np.empty(k)
    means[0] = rng.normal(center, sb * 0.3)
    for i in range(1, k):
        means[i] = center + phi * (means[i - 1] - center) + e[i]
    return rng.normal(0, sw, size=(k, n)) + means[:, None]


def gen_stable(sw: float, rng: np.random.Generator) -> np.ndarray:
    center = rng.normal(0, 0.04)
    return rng.normal(center, sw, size=(K, N))


def gen_subgroup_ar1(sw: float, phi: float, rng: np.random.Generator) -> np.ndarray:
    """Stable process, but readings within each subgroup follow AR(1)."""
    center = rng.normal(0, 0.04)
    m = np.empty((K, N))
    innov_scale = sw * np.sqrt(max(1e-9, 1 - phi**2))
    for g in range(K):
        e = rng.normal(0, innov_scale, N)
        x = np.empty(N)
        x[0] = center + e[0]
        for i in range(1, N):
            x[i] = center + phi * (x[i - 1] - center) + e[i]
        m[g] = x
    return m


def gen_drift_ar1(sw: float, sb: float, rng: np.random.Generator) -> np.ndarray:
    """Between-subgroup AR(1) drift; within-subgroup iid (the flip mechanism)."""
    center = rng.normal(0, 0.04)
    phi = 0.85
    e = rng.normal(0, sb * np.sqrt(1 - phi**2), K)
    means = np.empty(K)
    means[0] = rng.normal(center, sb * 0.3)
    for k in range(1, K):
        means[k] = center + phi * (means[k - 1] - center) + e[k]
    return rng.normal(0, sw, size=(K, N)) + means[:, None]


def autocorrelation_sensitivity(rng: np.random.Generator) -> tuple[list[float], list[float], list[float]]:
    phis = [0.0, 0.2, 0.4, 0.6, 0.8]
    sw = 0.17
    n_rep = 400
    med_cwk, med_ppk, flip_rate = [], [], []
    for phi in phis:
        cwks, ppks, flips = [], [], []
        for _ in range(n_rep):
            m = gen_subgroup_ar1(sw, phi, rng) if phi > 0 else gen_stable(sw, rng)
            s = summarise_matrix(m)
            cwks.append(s["cwk"])
            ppks.append(s["ppk"])
            flips.append(s["flipped"])
        med_cwk.append(float(np.median(cwks)))
        med_ppk.append(float(np.median(ppks)))
        flip_rate.append(float(np.mean(flips)))
    return phis, med_cwk, med_ppk


def gate_operating_curve(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sb_grid = np.linspace(0.06, 0.40, 25)
    sw = 0.17
    n_rep = 250
    overall_fail = []
    flip_prob = []
    for sb in sb_grid:
        o_fail, flips = [], []
        for _ in range(n_rep):
            m = gen_drift_ar1(sw, float(sb), rng)
            s = summarise_matrix(m)
            o_fail.append(s["overall_fail"])
            flips.append(s["flipped"])
        overall_fail.append(100 * np.mean(o_fail))
        flip_prob.append(100 * np.mean(flips))
    return sb_grid, np.array(overall_fail), np.array(flip_prob)


SUBGROUP_CONST = {
    3: (1.693, 1.023),
    5: (2.326, 0.577),
    10: (3.078, 0.308),
}


def subgroup_size_stress(rng: np.random.Generator) -> dict:
    """Flip rate on pure drift population vs subgroup size n."""
    sw, sb = 0.17, 0.25
    n_rep = 400
    out = {}
    for n, (d2, a2) in SUBGROUP_CONST.items():
        flips, ppk_fail = [], []
        for _ in range(n_rep):
            m = gen_drift_ar1_n(sw, sb, rng, K, n)
            s = summarise_matrix(m, d2, a2)
            flips.append(s["flipped"])
            ppk_fail.append(s["overall_fail"])
        out[n] = {
            "flip_pct": round(100 * float(np.mean(flips)), 1),
            "ppk_fail_pct": round(100 * float(np.mean(ppk_fail)), 1),
        }
    base = out[5]["flip_pct"]
    for n in out:
        out[n]["flip_ratio_vs_n5"] = round(out[n]["flip_pct"] / max(base, 1e-9), 2)
    return out


def fig6_subgroup(stress: dict) -> None:
    ns = sorted(stress.keys())
    flip = [stress[n]["flip_pct"] for n in ns]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    colors = [INK_FAINT if n != 5 else RUBRIC for n in ns]
    ax.bar([str(n) for n in ns], flip, color=colors, width=0.55)
    ax.set_xlabel("subgroup size n (readings per subgroup)")
    ax.set_ylabel("flip rate % (drift population, Monte Carlo)")
    ax.set_title("Gate flip persists across subgroup sizes", loc="left", fontsize=11, pad=8)
    for i, (n, v) in enumerate(zip(ns, flip)):
        ax.text(i, v + 1.5, f"{v:.0f}%\nratio {stress[n]['flip_ratio_vs_n5']:.2f}×",
                ha="center", fontsize=8, color=INK_SOFT)
    ax.set_ylim(0, max(flip) * 1.25)
    fig.tight_layout()
    fig.savefig(FIGS / "spc-fig6.svg")
    plt.close(fig)


def fig4_autocorr(phis: list[float], med_cwk: list[float], med_ppk: list[float]) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(phis, med_cwk, "o-", color=INK, lw=1.8, ms=6, label="median Cwk (within-σ index)")
    ax.plot(phis, med_ppk, "s--", color=INK_FAINT, lw=1.4, ms=5, label="median Ppk (overall-σ index)")
    ax.axhline(GATE, color=RUBRIC, lw=1, ls=":", alpha=0.85)
    ax.text(0.02, GATE + 0.04, f"gate = {GATE}", color=RUBRIC, fontsize=8.5)
    infl = med_cwk[0]
    if infl > 0:
        ax.annotate(
            f"+{(med_cwk[-1] / infl - 1) * 100:.0f}% Cwk at φ=0.8\n(same physical spread)",
            xy=(0.8, med_cwk[-1]),
            xytext=(0.45, med_cwk[-1] + 0.35),
            fontsize=8.5,
            color=INK_SOFT,
            arrowprops=dict(arrowstyle="->", color=INK_FAINT, lw=0.9),
        )
    ax.set_xlabel("within-subgroup AR(1) correlation φ (readings in the same subgroup)")
    ax.set_ylabel("capability index (stable, capable process)")
    ax.set_xticks(phis)
    ax.set_ylim(0, max(med_cwk) * 1.15)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.set_title("Autocorrelation inflates the within index", loc="left", fontsize=11, pad=8)
    fig.tight_layout()
    fig.savefig(FIGS / "spc-fig4.svg")
    plt.close(fig)


def fig5_oc(sb_grid: np.ndarray, overall_fail: np.ndarray, flip_prob: np.ndarray) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(sb_grid, overall_fail, color=RUBRIC, lw=2, label="Ppk fail rate (drift population)")
    ax.plot(sb_grid, flip_prob, color=INK, lw=1.8, ls="--", label="flip rate (pass Cwk, fail Ppk)")
    ax.axhline(50, color=INK_FAINT, lw=0.8, ls=":")
    ax.axvline(0.25, color=INK_FAINT, lw=0.8, ls=":", alpha=0.7)
    # mark sb range used in committed generator (~0.16–0.34)
    ax.axvspan(0.16, 0.34, color=RUBRIC, alpha=0.06)
    ax.text(0.25, 3, "generator\nsb range", ha="center", fontsize=7.5, color=INK_FAINT)
    ax.set_xlabel("between-subgroup drift scale sb (σ of subgroup-mean walk)")
    ax.set_ylabel("% of simulated drift characteristics")
    ax.set_ylim(0, 105)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    ax.set_title("Gate operating curve: drift strength vs fail / flip", loc="left", fontsize=11, pad=8)
    fig.tight_layout()
    fig.savefig(FIGS / "spc-fig5.svg")
    plt.close(fig)


def merge_results(phis, med_cwk, med_ppk, sb_grid, overall_fail, flip_prob, stress: dict) -> dict:
    with RESULTS.open() as f:
        base = json.load(f)
    base.update({
        "autocorr_phi_grid": phis,
        "autocorr_median_cwk": [round(x, 3) for x in med_cwk],
        "autocorr_median_ppk": [round(x, 3) for x in med_ppk],
        "autocorr_cwk_inflation_pct_at_phi_0_8": round((med_cwk[-1] / med_cwk[0] - 1) * 100, 1),
        "oc_sb_grid": [round(float(x), 3) for x in sb_grid],
        "oc_overall_fail_pct": [round(float(x), 1) for x in overall_fail],
        "oc_flip_pct": [round(float(x), 1) for x in flip_prob],
        "oc_sb_50pct_overall_fail": round(float(sb_grid[np.searchsorted(overall_fail, 50)]),
                                          3) if overall_fail[-1] >= 50 else None,
        "oc_sb_50pct_flip": round(float(sb_grid[np.searchsorted(flip_prob, 50)]),
                                  3) if flip_prob[-1] >= 50 else None,
        "subgroup_n_grid": [int(n) for n in sorted(stress.keys())],
        "subgroup_flip_pct": [stress[n]["flip_pct"] for n in sorted(stress.keys())],
        "subgroup_ppk_fail_pct": [stress[n]["ppk_fail_pct"] for n in sorted(stress.keys())],
        "subgroup_flip_ratio_vs_n5": [stress[n]["flip_ratio_vs_n5"] for n in sorted(stress.keys())],
    })
    with RESULTS.open("w") as f:
        json.dump(base, f, indent=2)
        f.write("\n")
    return base


def main():
    setup_mpl()
    FIGS.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED + 99)

    phis, med_cwk, med_ppk = autocorrelation_sensitivity(rng)
    sb_grid, overall_fail, flip_prob = gate_operating_curve(rng)
    stress = subgroup_size_stress(rng)

    fig4_autocorr(phis, med_cwk, med_ppk)
    fig5_oc(sb_grid, overall_fail, flip_prob)
    fig6_subgroup(stress)
    stats = merge_results(phis, med_cwk, med_ppk, sb_grid, overall_fail, flip_prob, stress)

    print("spc-fig4.svg, spc-fig5.svg, spc-fig6.svg written")
    print(f"Cwk inflation at phi=0.8: +{stats['autocorr_cwk_inflation_pct_at_phi_0_8']}%")
    print(f"OC: 50% overall-fail near sb ≈ {stats['oc_sb_50pct_overall_fail']}")
    print(f"OC: 50% flip near sb ≈ {stats['oc_sb_50pct_flip']}")


if __name__ == "__main__":
    main()
