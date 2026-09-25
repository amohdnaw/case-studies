#!/usr/bin/env python3
"""Study 11: does a holdout score for name-token inference transfer to the charts it is used on?

Synthetic only. A made-up plant (five equipment classes, 60 tools each, codes like WB-012) carries
charts whose names end in the tool's code. Some charts have no machine ID; the machine is inferred
from the last code-shaped token in the name. The inference is scored on charts that DO have an ID
(the holdout) and the score is then trusted for the blanks. This script checks that trust.

Names are typed with mistakes: the token can be missing, or typed with two digits swapped or one
dropped. A swap can land on another real tool (012 -> 021), which resolves cleanly to the WRONG
machine. That is the only way the inference is silently wrong. Hand-typed charts make these mistakes
more often, by a factor k.

Two ways to leave IDs blank, both with one chart in six blank overall:
  random        blanks drawn independently of how the chart was made
  hand-typed    blanks concentrated in hand-typed charts (35% of them vs ~4% of feed charts)

For each k and regime, RUNS plants are simulated. Reported per run: holdout error (known-ID charts),
true error on the blanks, resolution rates, and a check that uses only what you can see in real data:
is the share of messy names (no token, or a code-shaped token that matches no tool) different between
blank and known charts (two-proportion z-test, p < 0.01)?

Writes data/machine_identity_results.json and docs/figures/mid-fig1.svg, mid-fig2.svg.
The rates are chosen to echo the real system's ratios (1 blank in 6, holdout error under 1%);
they are not measured.
"""
from __future__ import annotations

import json
import math
import os
import re

import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, "docs", "figures")
OUT = os.path.join(ROOT, "data", "machine_identity_results.json")

PAPER, PAPER_DEEP = "#ffffff", "#fafafa"
INK, INK_SOFT, INK_FAINT = "#3d3327", "#58595a", "#877e72"
RUBRIC = "#8c2f22"
TEAL = "#1b7879"
HAIR = "#e2e2e2"

SEED = 20260925
CLASSES = ["WB", "DA", "MD", "TS", "PL"]          # wire bond, die attach, mold, test, plating
PER_CLASS = 60
N_CHARTS = 6000
MANUAL_SHARE = 0.40
BLANK = 1 / 6
FEED = {"missing": 0.005, "typo": 0.003}          # per-chart rates for feed-generated names
HAND = {"missing": 0.020, "typo": 0.015}          # hand-typed names at k = 1
KS = [1, 2, 3, 4, 6]
RUNS = 150
TOKEN = re.compile(r"(?<![A-Z])([A-Z]{2})-(\d{2,3})(?!\d)")

MACHINES = [f"{c}-{i:03d}" for c in CLASSES for i in range(1, PER_CLASS + 1)]
KNOWN = set(MACHINES)
PARAMS = ["WIRE_PULL", "BALL_SHEAR", "BOND_THK", "VOID_PCT", "MOLD_TEMP", "PLATE_THK", "LEAD_COPL"]
PRODUCTS = ["QFN48", "BGA256", "SOIC8", "LGA64", "QFP100", "DFN6"]


def typo(code, rng):
    cls, num = code.split("-")
    d = list(num)
    if rng.random() < 0.7:                         # swap two adjacent digits
        i = rng.integers(0, len(d) - 1)
        d[i], d[i + 1] = d[i + 1], d[i]
    else:                                          # drop one digit
        del d[rng.integers(0, len(d))]
    return f"{cls}-{''.join(d)}"


def plant(k, regime, rng):
    """One synthetic plant: (true machine, hand-typed?, blank?, name) per chart."""
    true = rng.choice(MACHINES, N_CHARTS)
    hand = rng.random(N_CHARTS) < MANUAL_SHARE
    if regime == "random":
        blank = rng.random(N_CHARTS) < BLANK
    else:
        p_hand = 0.35
        p_feed = (BLANK - MANUAL_SHARE * p_hand) / (1 - MANUAL_SHARE)
        blank = rng.random(N_CHARTS) < np.where(hand, p_hand, p_feed)
    names = []
    for m, h in zip(true, hand):
        r = HAND if h else FEED
        miss, ty = (r["missing"] * k, r["typo"] * k) if h else (r["missing"], r["typo"])
        u = rng.random()
        tok = "" if u < miss else (typo(m, rng) if u < miss + ty else m)
        names.append("_".join(x for x in (rng.choice(PRODUCTS), rng.choice(PARAMS), tok) if x))
    return true, hand, blank, names


def infer(name):
    """Last code-shaped token that names a known tool. Returns (machine or None, messy?)."""
    toks = ["-".join(t) for t in TOKEN.findall(name)]
    if not toks:
        return None, True                          # no token at all: visible mess
    t = toks[-1]
    return (t, False) if t in KNOWN else (None, True)   # code-shaped but no such tool: visible mess


def ztest(a, n1, b, n2):
    p = (a + b) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)) if 0 < p < 1 else 0
    if se == 0:
        return 1.0
    z = (a / n1 - b / n2) / se
    return math.erfc(abs(z) / math.sqrt(2))


def run(k, regime, rng):
    true, hand, blank, names = plant(k, regime, rng)
    got = [infer(n) for n in names]
    pred = np.array([g[0] or "" for g in got])
    messy = np.array([g[1] for g in got])
    res = pred != ""
    wrong = res & (pred != true)
    kn, bl = ~blank, blank
    err = lambda m: wrong[m & res].sum() / max(1, (m & res).sum())
    p = ztest(messy[bl].sum(), bl.sum(), messy[kn].sum(), kn.sum())
    return {"holdout_err": err(kn), "blank_err": err(bl),
            "holdout_res": res[kn].mean(), "blank_res": res[bl].mean(),
            "messy_known": messy[kn].mean(), "messy_blank": messy[bl].mean(),
            "flag": p < 0.01, "hand_in_blank": hand[bl].mean()}


def band(xs):
    a = np.array(xs)
    return float(a.mean()), float(np.percentile(a, 5)), float(np.percentile(a, 95))


def main():
    rng = np.random.default_rng(SEED)
    out = {"seed": SEED, "runs": RUNS, "ks": KS, "regimes": {}}
    for regime in ("random", "hand-typed"):
        out["regimes"][regime] = {}
        for k in KS:
            rs = [run(k, regime, rng) for _ in range(RUNS)]
            s = {m: band([r[m] for r in rs]) for m in rs[0] if m != "flag"}
            s["flag_rate"] = float(np.mean([r["flag"] for r in rs]))
            s["ratio"] = s["blank_err"][0] / s["holdout_err"][0] if s["holdout_err"][0] else float("nan")
            out["regimes"][regime][str(k)] = s
            print(f"{regime:10} k={k}  holdout {s['holdout_err'][0]:.3%}  blank {s['blank_err'][0]:.3%}  "
                  f"x{s['ratio']:.2f}  messy known/blank {s['messy_known'][0]:.2%}/{s['messy_blank'][0]:.2%}  "
                  f"flag {s['flag_rate']:.0%}")
    # sanity: with random blanks the holdout must be unbiased, or the simulation is wrong
    for k in KS:
        s = out["regimes"]["random"][str(k)]
        assert abs(s["ratio"] - 1) < 0.25, f"random regime biased at k={k}: {s['ratio']:.2f}"
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    fig1(out)
    fig2(out)


def style(ax):
    ax.set_facecolor(PAPER_DEEP)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(HAIR)
    ax.tick_params(colors=INK_FAINT, labelsize=8)
    ax.grid(color=HAIR, lw=0.6, alpha=0.6)
    ax.set_axisbelow(True)


def fig1(out):
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), dpi=100, sharey=True)
    fig.patch.set_facecolor(PAPER)
    for ax, regime in zip(axes, ("random", "hand-typed")):
        style(ax)
        R = out["regimes"][regime]
        for key, col, lab in (("holdout_err", INK, "holdout estimate"), ("blank_err", RUBRIC, "true error on blanks")):
            m = [R[str(k)][key][0] * 100 for k in KS]
            lo = [R[str(k)][key][1] * 100 for k in KS]
            hi = [R[str(k)][key][2] * 100 for k in KS]
            ax.fill_between(KS, lo, hi, color=col, alpha=.12, lw=0)
            ax.plot(KS, m, color=col, lw=1.8, marker="o", ms=3.5, label=lab)
        ax.set_title(f"blanks {'at random' if regime == 'random' else 'in hand-typed charts'}",
                     fontsize=9, color=INK_SOFT, loc="left")
        ax.set_xlabel("how much messier hand-typed names are (k)", fontsize=8, color=INK_FAINT)
        ax.set_xticks(KS)
    axes[0].set_ylabel("wrong machine, % of resolved charts", fontsize=8, color=INK_FAINT)
    axes[0].legend(frameon=False, fontsize=7.5, labelcolor=INK_SOFT, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "mid-fig1.svg"), facecolor=PAPER)


def fig2(out):
    fig, ax = plt.subplots(figsize=(7.2, 2.4), dpi=100)
    fig.patch.set_facecolor(PAPER)
    style(ax)
    w = .36
    x = np.arange(len(KS))
    for i, (regime, col) in enumerate((("random", INK_FAINT), ("hand-typed", TEAL))):
        v = [out["regimes"][regime][str(k)]["flag_rate"] * 100 for k in KS]
        ax.bar(x + (i - .5) * w, v, w * .92, color=col, label=f"blanks {'at random' if regime == 'random' else 'in hand-typed charts'}")
        for xi, vi in zip(x + (i - .5) * w, v):
            ax.text(xi, vi + 2, f"{vi:.0f}", ha="center", fontsize=7.5, color=INK_SOFT)
    ax.set_xticks(x)
    ax.set_xticklabels([f"k = {k}" for k in KS])
    ax.set_ylabel("runs flagged, %", fontsize=8, color=INK_FAINT)
    ax.set_ylim(0, 105)
    ax.legend(frameon=False, fontsize=7.5, labelcolor=INK_SOFT, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "mid-fig2.svg"), facecolor=PAPER)


if __name__ == "__main__":
    main()
