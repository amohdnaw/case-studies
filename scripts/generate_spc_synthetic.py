#!/usr/bin/env python3
"""Generate the synthetic capability dataset for case study 02.

SYNTHETIC DATA ONLY. No real measurements, part numbers, product names, or
customer/employer names. The dataset *reproduces a production phenomenon* seen in
a semiconductor assembly & test (OSAT) production environment; the method is the
point, not the numbers.

Fixed seed -> deterministic. Writes ../data/spc_synthetic.csv, one row per raw
measurement (char_id, population, subgroup, reading_idx, value).

Recipe (per the spec):
  ~2,000 characteristics, tolerance normalised to +/-1 (USL=+1, LSL=-1, target 0).
  Each: 25 subgroups x n=5.
  Population mix:
    55%  stable & capable          -> good Cwk, good Ppk         (pass both gates)
    15%  stable & incapable        -> Cwk < 1.33                 (fail both gates)
    30%  stable-within, drifting    -> good Cwk (tight subgroups) but inflated
         between subgroups            overall sigma -> Ppk < 1.33 (the flip population)
  The drift population is the Cwk-good / Ppk-bad cloud that makes the gate flip
  matter: within-subgroup spread is small, but real between-subgroup drift is
  variation the customer experiences and only the overall sigma sees it.
"""
import csv
import pathlib

import numpy as np

SEED = 20260712
N_CHAR = 2000
K = 25          # subgroups per characteristic
N = 5           # readings per subgroup
USL, LSL = 1.0, -1.0

# population fractions
FRAC_CAPABLE = 0.55
FRAC_INCAPABLE = 0.15
FRAC_DRIFT = 0.30

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "spc_synthetic.csv"

rng = np.random.default_rng(SEED)


def gen_stable(center, sw):
    """Stable characteristic: subgroup means jitter only by sampling noise."""
    vals = rng.normal(center, sw, size=(K, N))
    return vals


def gen_drift(center, sw, sb, mode):
    """Stable within subgroups (small sw) but the subgroup mean walks/steps
    between subgroups with between-scale sb -> overall sigma inflated."""
    if mode == "ar1":
        phi = 0.8
        e = rng.normal(0, sb * np.sqrt(1 - phi**2), size=K)
        means = np.empty(K)
        means[0] = rng.normal(0, sb)
        for k in range(1, K):
            means[k] = phi * means[k - 1] + e[k]
    else:  # step drift: one or two level shifts partway through
        means = np.zeros(K)
        n_steps = rng.integers(1, 3)
        cut = np.sort(rng.choice(np.arange(3, K - 2), size=n_steps, replace=False))
        level = 0.0
        prev = 0
        for c in cut:
            means[prev:c] = level
            level += rng.normal(0, 1) * sb * 1.7
            prev = c
        means[prev:] = level
        means = means - means.mean()  # keep grand mean near center
    means = means + center
    vals = rng.normal(0, sw, size=(K, N)) + means[:, None]
    return vals


def build():
    n_cap = int(round(N_CHAR * FRAC_CAPABLE))
    n_inc = int(round(N_CHAR * FRAC_INCAPABLE))
    n_drf = N_CHAR - n_cap - n_inc
    labels = ["capable"] * n_cap + ["incapable"] * n_inc + ["drift"] * n_drf
    rng.shuffle(labels)

    rows = []
    for cid, pop in enumerate(labels):
        if pop == "capable":
            center = rng.normal(0, 0.04)
            sw = rng.uniform(0.13, 0.20)
            vals = gen_stable(center, sw)
        elif pop == "incapable":
            # incapable via a mix of wide spread and/or off-centering
            if rng.random() < 0.5:
                center = rng.normal(0, 0.05)
                sw = rng.uniform(0.29, 0.42)
            else:
                center = rng.choice([-1, 1]) * rng.uniform(0.26, 0.44)
                sw = rng.uniform(0.18, 0.28)
            vals = gen_stable(center, sw)
        else:  # drift
            center = rng.normal(0, 0.04)
            sw = rng.uniform(0.13, 0.20)
            sb = rng.uniform(0.16, 0.34)
            mode = "ar1" if rng.random() < 0.5 else "step"
            vals = gen_drift(center, sw, sb, mode)
        for g in range(K):
            for i in range(N):
                rows.append((cid, pop, g, i, round(float(vals[g, i]), 5)))
    return rows


def main():
    rows = build()
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["char_id", "population", "subgroup", "reading_idx", "value"])
        w.writerows(rows)
    print(f"{len(rows):,} rows -> {OUT}  ({N_CHAR} characteristics x {K} subgroups x {N})")


if __name__ == "__main__":
    main()
