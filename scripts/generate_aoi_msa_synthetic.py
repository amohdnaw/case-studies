#!/usr/bin/env python3
"""Generate synthetic attribute MSA data for AOI pass/fail (Study 07).

SYNTHETIC ONLY — no production images or customer identifiers. Reproduces the
phenomena of automated optical inspection disagreement across machines in a
semiconductor assembly & test (OSAT) line.

Model:
  - n units with a latent true state (pass/fail) from a fixed defect prevalence.
  - Three AOI machines each inspect every unit once (classic attribute MSA layout).
  - M03: slight false-fail bias (strict).
  - M07: strong false-pass bias (lenient — misses defects).
  - M05: best match to the standard (reference-class machine).

Columns: unit_id, true_state, machine, call
  true_state / call: pass | fail
"""
from __future__ import annotations

import csv
import pathlib

import numpy as np

SEED = 20260716
N_UNITS = 300
PREVALENCE_FAIL = 0.18          # true defect rate on the reference panel
MACHINES = ["M03", "M05", "M07"]  # M03/M07 echo Study 03 localization story

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "aoi_msa_synthetic.csv"

# P(call=fail | true=pass), P(call=pass | true=fail)
BIAS = {
    "M03": {"fp": 0.11, "fn": 0.08},   # strict: extra false fails
    "M05": {"fp": 0.03, "fn": 0.05},   # near reference
    "M07": {"fp": 0.02, "fn": 0.42},   # lenient: misses defects
}


def main():
    rng = np.random.default_rng(SEED)
    true = rng.random(N_UNITS) < PREVALENCE_FAIL
    rows = []
    for uid in range(1, N_UNITS + 1):
        t = "fail" if true[uid - 1] else "pass"
        for machine in MACHINES:
            b = BIAS[machine]
            if t == "pass":
                call = "fail" if rng.random() < b["fp"] else "pass"
            else:
                call = "pass" if rng.random() < b["fn"] else "fail"
            rows.append(
                {"unit_id": uid, "true_state": t, "machine": machine, "call": call}
            )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["unit_id", "true_state", "machine", "call"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT}  ({len(rows):,} inspections, {N_UNITS} units x {len(MACHINES)} machines)")


if __name__ == "__main__":
    main()
