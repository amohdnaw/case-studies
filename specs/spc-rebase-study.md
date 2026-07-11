# Spec — Case study 02: "Rebasing capability statistics at 15,000-characteristic scale"

Status: READY FOR EXECUTION (any capable model; contract + DESIGN.md govern, no re-grilling needed).
Parent contract: `portfolio-evidence-contract.md`. Design: repo `DESIGN.md` (Paper Workbench).
Reference for structure/tone: `docs/trading-honesty-audit.html` — match its register exactly.

## The story (hiring-manager framing)

An SPC platform monitoring ~15,000 measured characteristics in **a semiconductor assembly &
test (OSAT) production environment** computed its capability indices correctly — and still told
the wrong story. Under the AIAG & VDA 2026 harmonization, within-subgroup indices (now Cwk)
answer "is the process capable when stable?", while overall-σ indices (Cpk-if-stable-else-Ppk)
answer "what does the customer actually receive?". The platform's classification gate ran on
within-σ. Flipping the gate to overall-σ roughly **doubled the fail list** — and that was the
correct answer, because between-subgroup drift is real variation the customer experiences.

Arc: correct math ≠ correct decision → what the two σ's measure → the gate flip → why more
red is more honest. Verdict box: the fail-list doubling framed as the honest outcome.

## Hard constraints

- **Synthetic data only.** No real measurements, part numbers, product names, customer names,
  or the employer's name. Work context descriptor is exactly the OSAT phrase above.
- The *phenomenon* is real; the *numbers on the page* come from the committed synthetic
  dataset. Say so plainly on the page ("simulated dataset reproducing the production
  phenomenon; the method is the point").

## Synthetic-data recipe (commit generator + output)

`scripts/generate_spc_synthetic.py`, fixed seed, writes `data/spc_synthetic.csv`:

- ~2,000 characteristics (enough to show scale behavior; state that production ran ~15,000).
- Each: 25 subgroups × n=5, target/tolerance normalized to ±1.
- Mix: ~55% stable & capable; ~15% stable & incapable; ~30% **stable-within but drifting
  between subgroups** (add between-subgroup mean shifts, AR(1) or step drift) — these are the
  Cwk-good/Ppk-bad population that makes the gate flip matter.
- Compute per characteristic: σ_within (Rbar/d2 and pooled/c4 — note both), σ_overall (total
  sd), Cwk, Ppk, a stability flag (e.g. subgroup-mean control test).

## Notebook (`notebooks/spc-rebase.ipynb`)

Sections: generate/load → the two σ's (one characteristic walked through) → population view →
gate comparison (fail counts under within-σ vs overall-σ) → who flips and why (the drift
population) → what changed operationally.

## Figures (DESIGN.md tokens; ink=data, rubric=the argued series, direct labels, no color-alone)

1. Scatter Cwk vs Ppk, diagonal reference; drift population highlighted in rubric — the
   off-diagonal cloud IS the story.
2. Fail-list bar: within-σ gate vs overall-σ gate, counts labeled (the "doubling").
3. One characteristic's subgroup chart showing within-spread vs between-drift (small multiples
   ok: stable vs drifting).

## Page (`docs/spc-capability-rebase.html`)

Same skeleton as study 01: kicker (Case studies · 02 · Process capability), h1, standfirst,
verdict box, §-numbered sections, figures with captions, repro box (generator + notebook
links), footnav (prev: 01, next: 03 forthcoming). Update `docs/index.html`: study 02 becomes
clickable, meta loses "Forthcoming".

## Acceptance checks

1. Page renders in Paper Workbench register, desktop + 390px mobile, no layout breaks.
2. Every number on the page reproduces from the committed generator + notebook (fixed seed).
3. Zero employer identifiers (grep the diff for the employer name before commit).
4. Fig 2's two bars show the fail-list roughly doubling; verdict box explains why that's correct.
5. Index page updated; both pages screenshot-verified before "done".
