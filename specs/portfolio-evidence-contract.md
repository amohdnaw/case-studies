# Contract — Portfolio Evidence: trading case study + repo (2026-07-12)

Approved by Ammar 2026-07-12 (grill-gated: 4+3 interview decisions, Direction A mock pick).
Origin: state-of-ammar-2026-07-12.html six-month play, item 1 — "ship the evidence, not more tools."

## What you will see (acceptance checks)

1. **Public repo `amohdnaw/case-studies`** on GitHub with Pages enabled. Opening
   `https://amohdnaw.github.io/case-studies/` shows an **index page in the Paper Workbench
   direction**: three case studies listed, 01 (trading) clickable, 02 (SPC capability rebase)
   and 03 (ICOS yield) marked "forthcoming".
2. **Study 01 page**, Paper Workbench register: headline *"I audited my own trading system —
   and killed my best result"*, verdict box (day-clustered CI includes zero), the sample table,
   and **real figures computed from actual backtest data** — no placeholders.
   Hiring-manager framing: problem → analysis → what the honest answer changed.
3. **A runnable Jupyter notebook** in the repo (day-clustered bootstrap, always-BUY baseline,
   confidence-score correlation) with the trade data included as CSV — a recruiter can re-run
   the whole analysis. README links page + notebook.
4. **`DESIGN.md`** frozen from the picked mock (Direction A tokens: paper/ink/rubric palette,
   serif measure, mono kickers, margin notes, ruled figures).
5. **Two executable specs** in `specs/`: SPC rebase study and ICOS study — each with the
   synthetic-data recipe, OSAT descriptor, narrative outline, and page checks, ready for a
   cheaper model to execute.
6. **Third spec**: portfolio goes public + case-studies section (deferred, per interview pick).
7. **No employer identifiers anywhere**; work context reads
   "a semiconductor assembly & test (OSAT) production environment".
8. `diagrams/` holds the evidence-pipeline flow diagram (data → notebook → page → CV link)
   per house rule.

## Picked mock

`design/direction-mock.html` — **Direction A, Paper Workbench** (screenshot verified during
grill; B Swiss Industrial and C Archival Editorial rejected).

## Interview decisions (locked)

- Hosting: **both** — GitHub repo + Pages now; portfolio-site section spec'd for later.
- Work data: **synthetic data, real methods** for SPC + ICOS (zero employer-data risk).
- Audience: **hiring managers** primary (data analyst roles); USM committee secondary.
- Today's scope: **trading study full draft + specs for the other two**.
- Portfolio site (localhost-only today): **spec it, CV links point at repo Pages for now**.
- Work context descriptor: **"a semiconductor assembly & test (OSAT) production environment"**.
- Null-result framing: **honesty-forward** — the audit itself is the headline.

## Not in scope

- Power BI artifact
- CV re-pointing
- Publishing the portfolio site
- Full SPC/ICOS drafts (specs only)
- Portfolio case-studies section build

## Defaults taken

- Repo name `amohdnaw/case-studies`, public, Pages from `docs/`.
- Trading trade-level data published as CSV (personal paper-trading data; `headline` text
  column dropped, `is_demo` flag derived from it).
- Index-page composition derives from the same Direction A register (not separately mocked).
- Notebook stack: Python/Jupyter, matplotlib figures matching DESIGN.md palette.
- Numbers on the page are **recomputed live** by the notebook (dataset has grown past the
  2026-07-11 audit's n=1,976) — page and notebook must agree.

## Verification

Each numbered check above is verified literally (browser screenshots for pages, live Pages
URL fetch) before reporting done. Corrections update this contract / DESIGN.md, not just the
instance.
