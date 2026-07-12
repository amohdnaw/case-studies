# Case studies — applied statistics from real systems

Live: **https://amohdnaw.github.io/case-studies/**

Three one-page studies from systems I built and run, each reproducible from the data in this
repo.

| # | Study | Status |
|---|-------|--------|
| 01 | [I audited my own trading system — and killed my best result](https://amohdnaw.github.io/case-studies/trading-honesty-audit.html) · [notebook](notebooks/trading-honesty-audit.ipynb) | Live |
| 02 | [Rebasing capability statistics at 15,000-characteristic scale](https://amohdnaw.github.io/case-studies/spc-capability-rebase.html) · [notebook](notebooks/spc-rebase.ipynb) | Live |
| 03 | [Finding the yield signal in inspection data](https://amohdnaw.github.io/case-studies/icos-yield-signal.html) · [notebook](notebooks/icos-yield.ipynb) | Live |

## Reproduce study 01

```bash
python3 -m venv .venv && .venv/bin/pip install pandas numpy matplotlib jupyter
cd notebooks && ../.venv/bin/jupyter execute trading-honesty-audit.ipynb
```

Everything runs from `data/trades.csv` (1,578 real paper trades + the demo/HOLD rows the
study excludes, one row per trade) with a fixed seed — every confidence interval in the study
reproduces exactly. `scripts/export_trades.py` documents how the CSV was extracted from the
live system.

## Layout

- `docs/` — the published pages (GitHub Pages) + generated figures
- `notebooks/` — executed Jupyter notebooks (rendered on GitHub)
- `data/` — the datasets the notebooks run on + computed results
- `specs/` — outcome contracts and executable specs for the forthcoming studies
- `diagrams/` — how the pieces connect (`evidence-pipeline.svg`)
- `DESIGN.md` — the visual system the pages are built to

Studies 02 and 03 use synthetic datasets that reproduce production phenomena from
a semiconductor assembly & test (OSAT) environment; the trading study uses the real
(personal) paper-trading log. No employer data appears in this repository.
