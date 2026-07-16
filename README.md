# Case studies — applied statistics from real systems

Live: **https://amohdnaw.github.io/case-studies/**

Eight one-page studies from systems I built and run, each reproducible from the data in this
repo.

| # | Study | Status |
|---|-------|--------|
| 01 | [I audited my own trading system — and killed my best result](https://amohdnaw.github.io/case-studies/trading-honesty-audit.html) · [notebook](notebooks/trading-honesty-audit.ipynb) | Live |
| 02 | [Rebasing capability statistics at 15,000-characteristic scale](https://amohdnaw.github.io/case-studies/spc-capability-rebase.html) · [notebook](notebooks/spc-rebase.ipynb) | Live |
| 03 | [Finding the yield signal in inspection data](https://amohdnaw.github.io/case-studies/icos-yield-signal.html) · [notebook](notebooks/icos-yield.ipynb) | Live |
| 04 | [My backtest was a gauge that had never passed GR&R](https://amohdnaw.github.io/case-studies/backtest-gauge.html) · [notebook](notebooks/backtest-gauge.ipynb) | Live |
| 05 | [I tested 7,860 strategies across crypto and stocks. Doing nothing beat all of them.](https://amohdnaw.github.io/case-studies/exhaustion.html) · [script](scripts/exhaustion.py) | Live |
| 06 | [When forty charts fire and nothing changed](https://amohdnaw.github.io/case-studies/spc-false-alarms.html) · [script](scripts/spc_multiplicity.py) | Live |
| 07 | [Before you rank the defects, calibrate the camera](https://amohdnaw.github.io/case-studies/aoi-attribute-msa.html) · [notebook](notebooks/aoi-attribute-msa.ipynb) | Live |
| 08 | [Which chart catches the shift first?](https://amohdnaw.github.io/case-studies/spc-shift-detect.html) · [script](scripts/spc_shift_detect.py) | Live |

## Reproduce study 04

```bash
python3 -m venv .venv && .venv/bin/pip install pandas numpy scipy matplotlib jupyter
python3 scripts/export_gauge_trades.py                    # 163 spot trades from the live system
cd notebooks && ../.venv/bin/jupyter execute backtest-gauge.ipynb
```

Runs on `data/gauge_trades.csv` (163 spot paper trades, one row per trade, each carrying the
stop-loss and take-profit the book actually configured). The recalibration compares every
recorded fill against the *order the engine intended to place* — which is the whole audit.
The 32 short-side rows in the raw state are excluded, not averaged in.

## Reproduce study 01

```bash
python3 -m venv .venv && .venv/bin/pip install pandas numpy matplotlib jupyter
cd notebooks && ../.venv/bin/jupyter execute trading-honesty-audit.ipynb
python3 scripts/trading_inference.py   # inference table incl. Newey–West HAC row
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

Studies 02, 03, 06, 07, and 08 use synthetic datasets that reproduce production phenomena from
a semiconductor assembly & test (OSAT) environment; the trading study uses the real
(personal) paper-trading log. No employer data appears in this repository.
