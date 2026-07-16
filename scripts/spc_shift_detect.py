#!/usr/bin/env python3
"""Study 08: shift detection latency — X-bar vs EWMA vs CUSUM.

Synthetic in-control + step shift. Writes docs/figures/shift-fig1.svg, shift-fig2.svg
and data/spc_shift_results.json.
"""
from __future__ import annotations

import json
import os

import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, "docs", "figures")
OUT = os.path.join(ROOT, "data", "spc_shift_results.json")

SEED = 20260716
K = 40
N = 5
MU0 = 0.0
SIGMA = 0.18
SHIFT_SIGMA_XBAR = 2.0  # step size in X-bar sigma units
SHIFT_AT = 20
N_SIM = 3000
LAM = 0.2
EWMA_L = 3.0
CUSUM_K = 0.5
CUSUM_H = 4.77  # ~ARL0 ≈ 370 for two-sided standardized CUSUM

PAPER, PAPER_DEEP = "#ffffff", "#fafafa"
INK, INK_FAINT, RUBRIC = "#3d3327", "#877e72", "#8c2f22"
HAIR = "#e2e2e2"

SIGMA_XBAR = SIGMA / np.sqrt(N)
SHIFT = SHIFT_SIGMA_XBAR * SIGMA_XBAR


def style(ax):
    ax.set_facecolor(PAPER_DEEP)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(HAIR)
    ax.tick_params(colors=INK_FAINT, labelsize=8)
    ax.grid(color=HAIR, lw=0.6, alpha=0.6)
    ax.set_axisbelow(True)


def gen_series(rng: np.random.Generator, shift: float, shift_at: int) -> np.ndarray:
    means = np.full(K, MU0)
    means[shift_at:] += shift
    return rng.normal(means, SIGMA_XBAR)


def xbar_alarm(xbar: np.ndarray) -> int | None:
    ucl = MU0 + 3 * SIGMA_XBAR
    lcl = MU0 - 3 * SIGMA_XBAR
    for i, x in enumerate(xbar):
        if x > ucl or x < lcl:
            return i
    return None


def ewma_alarm(xbar: np.ndarray) -> int | None:
    sig_z = SIGMA_XBAR * np.sqrt(LAM / (2 - LAM))
    ucl = MU0 + EWMA_L * sig_z
    lcl = MU0 - EWMA_L * sig_z
    z = MU0
    for i, x in enumerate(xbar):
        z = LAM * x + (1 - LAM) * z
        if z > ucl or z < lcl:
            return i
    return None


def cusum_alarm(xbar: np.ndarray) -> int | None:
    s_pos = s_neg = 0.0
    for i, x in enumerate(xbar):
        z = (x - MU0) / SIGMA_XBAR
        s_pos = max(0.0, s_pos + z - CUSUM_K)
        s_neg = max(0.0, s_neg - z - CUSUM_K)
        if s_pos > CUSUM_H or s_neg > CUSUM_H:
            return i
    return None


def run_latency(rng: np.random.Generator) -> dict:
    detect = {"xbar": [], "ewma": [], "cusum": []}
    false = {"xbar": 0, "ewma": 0, "cusum": 0}
    fns = {"xbar": xbar_alarm, "ewma": ewma_alarm, "cusum": cusum_alarm}

    for _ in range(N_SIM):
        x0 = gen_series(rng, 0.0, K + 1)
        xs = gen_series(rng, SHIFT, SHIFT_AT)
        for name, fn in fns.items():
            t0 = fn(x0)
            if t0 is not None:
                false[name] += 1
            ts = fn(xs)
            if ts is not None and ts >= SHIFT_AT:
                detect[name].append(ts - SHIFT_AT)
            else:
                detect[name].append(K - SHIFT_AT)

    out = {}
    for name in detect:
        d = np.array(detect[name], dtype=float)
        out[name] = {
            "median_latency": int(np.median(d)),
            "p90_latency": int(np.percentile(d, 90)),
            "detected_pct": round(100 * float(np.mean(d < (K - SHIFT_AT))), 1),
            "false_alarm_pct": round(100 * false[name] / N_SIM, 2),
        }
    return out


def fig1_example(rng: np.random.Generator) -> None:
    xbar = gen_series(rng, SHIFT, SHIFT_AT)
    ucl = MU0 + 3 * SIGMA_XBAR
    z = MU0
    ewma = []
    for x in xbar:
        z = LAM * x + (1 - LAM) * z
        ewma.append(z)

    fig, axes = plt.subplots(2, 1, figsize=(7.6, 4.2), facecolor=PAPER, sharex=True)
    ax = axes[0]
    ax.plot(xbar, "o-", color=INK, ms=4, lw=1.2)
    ax.axhline(MU0, color=INK_FAINT, lw=1)
    ax.axhline(ucl, color=RUBRIC, ls="--", lw=1)
    ax.axvline(SHIFT_AT, color=INK_FAINT, ls=":", lw=1)
    ax.set_ylabel("X̄", fontsize=8)
    ax.set_title(
        f"Step shift at subgroup {SHIFT_AT} ({SHIFT_SIGMA_XBAR}σ on X̄ scale)",
        color=INK,
        fontsize=9.5,
        loc="left",
    )
    style(ax)

    ax = axes[1]
    ax.plot(ewma, color=INK, lw=1.4, label="EWMA")
    ax.axvline(SHIFT_AT, color=INK_FAINT, ls=":", lw=1)
    ax.set_xlabel("subgroup index", color=INK_FAINT, fontsize=8)
    ax.set_ylabel("EWMA", fontsize=8)
    ax.legend(frameon=False, fontsize=8)
    style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "shift-fig1.svg"))
    plt.close(fig)


def fig2_latency(stats: dict) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 3.0), facecolor=PAPER)
    names = ["xbar", "ewma", "cusum"]
    labels = ["X̄ chart", "EWMA", "CUSUM"]
    med = [stats[n]["median_latency"] for n in names]
    p90 = [stats[n]["p90_latency"] for n in names]
    x = np.arange(3)
    w = 0.36
    ax.bar(x - w / 2, med, w, color=INK, label="median delay (subgroups)")
    ax.bar(x + w / 2, p90, w, color=RUBRIC, label="90th pct delay")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("subgroups after shift")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.set_title(
        f"Time-to-detect ({N_SIM:,} runs · shift = {SHIFT_SIGMA_XBAR}σ on X̄)",
        color=INK,
        fontsize=9.5,
        loc="left",
    )
    style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "shift-fig2.svg"))
    plt.close(fig)


def main():
    rng = np.random.default_rng(SEED)
    stats = run_latency(rng)
    fig1_example(rng)
    fig2_latency(stats)

    results = {
        "synthetic": True,
        "seed": SEED,
        "n_subgroups": K,
        "n_per_subgroup": N,
        "shift_sigma_xbar": SHIFT_SIGMA_XBAR,
        "shift_at_subgroup": SHIFT_AT,
        "n_simulations": N_SIM,
        "charts": stats,
    }
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
        f.write("\n")
    print("shift-fig1.svg, shift-fig2.svg written")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
