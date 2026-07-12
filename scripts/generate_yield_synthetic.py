#!/usr/bin/env python3
"""Generate a synthetic AOI (automated optical inspection) defect log for case study 03.

SYNTHETIC DATA — no production data is used. This script reproduces, with a fixed seed,
the *phenomena* of a semiconductor assembly & test (OSAT) inspection line so the yield
analysis in ../notebooks/icos-yield.ipynb is fully reproducible from the committed CSV.

Model (one row per *flagged* unit — a clean-pass unit generates no row):
  - 60 inspection days x 40 lots/day x UNITS_PER_LOT units, one AOI machine per lot.
  - Each inspected unit is clean, or carries exactly one primary defect (multinomial draw).
  - Each defect category has a signature: an incidence (drives raw COUNT) and a
    recover-rate (fraction of flagged units salvaged by rework/retest -> no yield loss).
  - A flagged unit is `recoverable=True` when it was salvaged (disposition retested/reworked);
    `recoverable=False` when it was scrapped -> that scrap is the yield loss, and the count of
    scrap attributable to a driver is exactly the yield a root-cause fix would RECOVER.
  - Category signatures encode the story: one loud cosmetic category (high count, mostly
    salvaged -> little recoverable yield), one mid-count low-salvage category (the real
    lever -> most recoverable yield), one rare category concentrated on two machines
    (systemic/localized), plus background categories.

Columns: date, lot, machine, defect_category, recoverable, disposition
"""
import csv
import pathlib

import numpy as np
import pandas as pd

SEED = 20260712
DAYS = 60
LOTS_PER_DAY = 40
UNITS_PER_LOT = 300          # units inspected per lot (hundreds/lot; fixed for a clean denominator)
MACHINES = [f"M{i:02d}" for i in range(1, 11)]   # M01..M10
CONC_MACHINES = ["M03", "M07"]                    # where the rare systemic defect concentrates

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "yield_synthetic.csv"

# name, per-unit incidence, recover-rate (P salvaged | flagged), salvage disposition
CATEGORIES = [
    ("cosmetic mark",         0.050, 0.90, "retested"),   # LOUD: #1 by count, mostly salvaged
    ("placement offset",      0.030, 0.28, "reworked"),   # LEVER: mid count, low salvage -> #1 recoverable
    ("surface contamination", 0.024, 0.85, "retested"),   # loud but salvageable
    ("solder void",           0.022, 0.42, "reworked"),
    ("mold flash",            0.018, 0.88, "retested"),   # cosmetic-class, salvaged
    ("wire bond fault",       0.013, 0.45, "reworked"),
    ("die crack",             0.008, 0.05, "reworked"),   # rare-ish, almost all scrap
    ("delamination",          0.006, 0.18, "reworked"),
    ("lead lift",             0.005, 0.12, "reworked"),   # RARE + concentrated on 2 machines
]
LEAD_LIFT = "lead lift"
# categories that occasionally "bleed" a whole lot (correlated burst)
BLEED = {"lead lift": 6.0, "die crack": 5.0, "delamination": 4.0}
BLEED_P = 0.05

# subtle per-machine quality drift so the machine x category heatmap is not flat
MACHINE_DRIFT = {
    "solder void":      {"M05": 1.8, "M06": 1.4},
    "wire bond fault":  {"M09": 2.0},
    "mold flash":       {"M02": 1.5},
}


def machine_mult(cat, machine):
    if cat == LEAD_LIFT:
        return 6.0 if machine in CONC_MACHINES else 0.12
    return MACHINE_DRIFT.get(cat, {}).get(machine, 1.0)


def main():
    rng = np.random.default_rng(SEED)
    dates = pd.bdate_range("2026-04-06", periods=DAYS).strftime("%Y-%m-%d")
    cat_names = [c[0] for c in CATEGORIES]
    base = np.array([c[1] for c in CATEGORIES])
    recover = np.array([c[2] for c in CATEGORIES])
    disp_ok = [c[3] for c in CATEGORIES]

    rows = []
    lot_seq = 0
    for date in dates:
        for _ in range(LOTS_PER_DAY):
            lot_seq += 1
            lot = f"L{lot_seq:05d}"
            machine = MACHINES[rng.integers(len(MACHINES))]

            # effective per-unit incidence for this lot
            p = base.copy()
            for j, cat in enumerate(cat_names):
                p[j] *= machine_mult(cat, machine)
                if cat in BLEED and rng.random() < BLEED_P:   # whole-lot bleed event
                    p[j] *= BLEED[cat]
            p = np.clip(p, 0, None)
            p_none = max(1.0 - p.sum(), 0.0)
            probs = np.append(p, p_none)
            probs /= probs.sum()

            counts = rng.multinomial(UNITS_PER_LOT, probs)     # last bucket = clean units
            for j, cat in enumerate(cat_names):
                k = int(counts[j])
                if not k:
                    continue
                salvaged = int(rng.binomial(k, recover[j]))    # salvaged -> no yield loss
                scrapped = k - salvaged
                for _ in range(salvaged):
                    rows.append((date, lot, machine, cat, True, disp_ok[j]))
                for _ in range(scrapped):
                    rows.append((date, lot, machine, cat, False, "scrapped"))

    # deterministic order, then stable shuffle within the file for realism (seeded)
    rows_arr = rows
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "lot", "machine", "defect_category", "recoverable", "disposition"])
        w.writerows(rows_arr)

    n_units = DAYS * LOTS_PER_DAY * UNITS_PER_LOT
    n_flag = len(rows_arr)
    n_scrap = sum(1 for r in rows_arr if r[4] is False)
    print(f"units inspected : {n_units:,}  ({DAYS} days x {LOTS_PER_DAY} lots x {UNITS_PER_LOT} units)")
    print(f"flagged rows    : {n_flag:,}  ({100*n_flag/n_units:.1f}% of units)")
    print(f"scrapped (loss) : {n_scrap:,}  -> overall yield {100*(1-n_scrap/n_units):.2f}%")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
