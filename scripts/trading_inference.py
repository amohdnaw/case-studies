#!/usr/bin/env python3
"""Study 01 extension: robust inference table (incl. Newey–West HAC SE).

Reads data/trades.csv, writes data/trading_inference.json.
Matches notebooks/trading-honesty-audit.ipynb filters and fee model.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "trades.csv"
OUT = ROOT / "data" / "trading_inference.json"
SEED = 20260716
N_BOOT = 3000
FEE_RT = 0.30


def load_real_trades() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    df["entry_date"] = pd.to_datetime(df["entry_date"], format="ISO8601", utc=True)
    df = df[df["evaluated"]].copy()
    df["day"] = df["entry_date"].dt.date
    df["net"] = df["pnl_pct"].astype(float) - FEE_RT
    real = df[~df["is_demo"] & df["signal"].isin(["BUY", "SELL"])].copy()
    days_sorted = sorted(real.day.unique())
    blocks = [days_sorted[i : i + 3] for i in range(0, len(days_sorted), 3)]
    bmap = {d: i for i, blk in enumerate(blocks) for d in blk}
    real["block"] = real.day.map(bmap)
    return real


def newey_west_ci(daily: pd.Series) -> tuple[float, float, float]:
    y = daily.values.astype(float)
    n = len(y)
    mu = float(y.mean())
    e = y - mu
    lag = max(1, int(np.floor(n ** 0.25)))
    var = np.dot(e, e) / n
    for lag_i in range(1, lag + 1):
        w = 1.0 - lag_i / (lag + 1)
        cov = np.dot(e[lag_i:], e[:-lag_i]) / n
        var += 2.0 * w * cov
    se = np.sqrt(var / n)
    return mu, mu - 1.96 * se, mu + 1.96 * se


def bootstrap_iid(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float, float]:
    means = np.array([rng.choice(values, size=len(values), replace=True).mean() for _ in range(N_BOOT)])
    point = float(values.mean())
    lo, hi = np.percentile(means, [2.5, 97.5])
    return point, float(lo), float(hi)


def bootstrap_cluster(groups: list[np.ndarray], rng: np.random.Generator) -> tuple[float, float, float]:
    idx = np.arange(len(groups))
    means = np.empty(N_BOOT)
    for i in range(N_BOOT):
        picked = np.concatenate([groups[j] for j in rng.choice(idx, len(groups))])
        means[i] = picked.mean()
    all_vals = np.concatenate(groups)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(all_vals.mean()), float(lo), float(hi)


def bootstrap_block(groups: list[np.ndarray], rng: np.random.Generator) -> tuple[float, float, float]:
    idx = np.arange(len(groups))
    means = np.empty(N_BOOT)
    for i in range(N_BOOT):
        picked = np.concatenate([groups[j] for j in rng.choice(idx, len(groups))])
        means[i] = picked.mean()
    all_vals = np.concatenate(groups)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(all_vals.mean()), float(lo), float(hi)


def main():
    real = load_real_trades()
    rng = np.random.default_rng(SEED)
    net = real["net"].values
    day_groups = [g["net"].values for _, g in real.groupby("day")]
    block_groups = [g["net"].values for _, g in real.groupby("block")]
    daily_net = real.groupby("day")["net"].mean()

    rows = []
    pt, lo, hi = bootstrap_iid(net, rng)
    rows.append({"method": "iid bootstrap (trades)", "point": round(pt, 3), "ci_lo": round(lo, 3), "ci_hi": round(hi, 3)})

    pt, lo, hi = bootstrap_cluster(day_groups, rng)
    rows.append({"method": "day-clustered bootstrap", "point": round(pt, 3), "ci_lo": round(lo, 3), "ci_hi": round(hi, 3)})

    pt, lo, hi = bootstrap_block(block_groups, rng)
    rows.append({"method": "3-day block bootstrap", "point": round(pt, 3), "ci_lo": round(lo, 3), "ci_hi": round(hi, 3)})

    pt, lo, hi = newey_west_ci(daily_net)
    rows.append({"method": "Newey–West HAC (daily means)", "point": round(pt, 3), "ci_lo": round(lo, 3), "ci_hi": round(hi, 3)})

    out = {
        "n_trades": int(len(real)),
        "n_days": int(real.day.nunique()),
        "n_blocks": int(real.block.nunique()),
        "fee_rt_pct": FEE_RT,
        "trade_weighted_mean_net_pct": round(float(net.mean()), 3),
        "day_weighted_mean_net_pct": round(float(daily_net.mean()), 3),
        "inference_rows": rows,
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
