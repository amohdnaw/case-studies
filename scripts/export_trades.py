#!/usr/bin/env python3
"""Export the paper-trading log from the live system's backtest.json to data/trades.csv.

Provenance script — runs only on the box that hosts the trading system. The committed
CSV is the reproducible artifact; the notebook needs nothing but the CSV.
Drops the free-text `headline` column (derives is_demo from its '[Demo]' marker).
"""
import csv, json, pathlib

SRC = pathlib.Path.home() / "trading-signals" / "backtest.json"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "trades.csv"

FIELDS = ["id", "ticker", "asset_type", "signal", "confidence", "entry_date",
          "entry_price", "exit_date", "exit_price", "pnl_pct", "correct",
          "evaluated", "is_demo"]

trades = json.loads(SRC.read_text())["trades"]
with OUT.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    for t in trades:
        row = {k: t.get(k) for k in FIELDS if k != "is_demo"}
        row["is_demo"] = str(t.get("headline", "")).startswith("[Demo]")
        w.writerow(row)
print(f"{len(trades)} trades -> {OUT}")
