# Spec — Case study 03: "Finding the yield signal in inspection data"

Status: READY FOR EXECUTION (any capable model; contract + DESIGN.md govern, no re-grilling needed).
Parent contract: `portfolio-evidence-contract.md`. Design: repo `DESIGN.md` (Paper Workbench).
Reference for structure/tone: `docs/trading-honesty-audit.html`.

## The story (hiring-manager framing)

Automated optical inspection in **a semiconductor assembly & test (OSAT) production
environment** produces thousands of unit-level pass/fail records per day, tagged with defect
category, machine, and lot. Intuition says chase the loudest defect category; the data says
rank by **recoverable units** — expected yield gained if a driver is fixed — which reorders
the priority list. The study shows the Pareto discipline: from raw inspection records to a
ranked loss-driver table a production meeting can act on.

Arc: the raw records → naive ranking by count → recoverable-units ranking (some frequent
defects are unrecoverable/retest-recoverable; some rare ones bleed whole lots) → machine/lot
concentration (is the loss systemic or localized?) → what the meeting does differently.
Verdict box: "the loudest defect wasn't the biggest lever" with the two rankings side by side.

## Hard constraints

Identical to study 02: **synthetic data only**, OSAT descriptor verbatim, no employer
identifiers, page states plainly that the dataset is simulated and the method is the point.

## Synthetic-data recipe (commit generator + output)

`scripts/generate_yield_synthetic.py`, fixed seed, writes `data/yield_synthetic.csv`:

- ~60 days × ~40 lots/day × ~500 units/lot; overall yield ~92%.
- 8–10 defect categories with distinct signatures: one high-count/low-recoverability cosmetic
  category, one mid-count/high-recoverability category (the real lever), one rare category
  concentrated in 2 machines (systemic), background categories.
- Columns: date, lot, machine (8–12 ids like M01…), defect_category (generic names:
  "placement offset", "solder void" class of vocabulary — industry-generic, not
  product-specific), recoverable flag, unit disposition.

## Notebook (`notebooks/icos-yield.ipynb`)

Sections: load → naive Pareto by count → recoverable-units ranking (define the metric, show
the reorder) → machine/lot concentration for the top driver → the actionable table.

## Figures (DESIGN.md tokens, direct labels)

1. Paired Pareto: rank-by-count vs rank-by-recoverable-units — the reorder is the story
   (rubric on the category that jumps rank).
2. Daily yield trend with the top driver's contribution shaded.
3. Machine × category heatmap (sequential single-hue ramp from ink, per dataviz rules)
   showing the concentration.

## Page (`docs/icos-yield-signal.html`)

Same skeleton as study 01. Kicker: Case studies · 03 · Yield analytics. Update
`docs/index.html`: study 03 clickable, "Forthcoming" removed; footnav on study 02 updated.

## Acceptance checks

1. Page renders in Paper Workbench register, desktop + 390px mobile.
2. Every number reproduces from committed generator + notebook (fixed seed).
3. Zero employer identifiers (grep before commit).
4. Fig 1 visibly reorders the top drivers between the two rankings; verdict box names the lever.
5. Index + study-02 footnav updated; screenshots verified before "done".
