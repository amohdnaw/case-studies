#!/usr/bin/env python3
"""Study 09 — tokenized-equity venues as a measurement system.

Three 24/7 venues quote the same underlying stock: Binance (<T>BUSDT spot),
Backpack (<T>.US_USDC xStock), Arcus (<T>-USD perp on Robinhood Chain).
Treat each venue as a gauge of the exchange price and measure:

  1. bias + tracking error per venue (hourly closes, market hours only)
  2. the fake-gauge audit (coin symbols masquerading as stock tickers)
  3. the weekend oracle: token drift Fri close -> Mon 13:00 UTC (30 min
     BEFORE the open — no leakage) vs the stock's actual opening gap,
     pooled and with the SPY market factor removed.

Writes data/venue_gauge_results.json + data/venue_weekends.csv.
Research only. No orders, no signals.
"""
import json, statistics, sys
from datetime import datetime, timezone
from pathlib import Path

import requests
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
H_MS = 3600_000
TRACK = ["SPY", "QQQ", "TSLA", "MSFT", "NVDA", "GOOGL", "META", "MSTR", "AMD",
         "TSM", "MU", "SNDK"]
FAKES = [("TR", "TRBUSDT", "Tellor"), ("B", "BBUSDT", "BounceBit"),
         ("DG", "DGBUSDT", "DigiByte"), ("BN", "BNBUSDT", "BNB")]
DST_2026 = datetime(2026, 3, 8, tzinfo=timezone.utc)


def bnc_1h(sym, pages=1):
    out, end = {}, None
    for _ in range(pages):
        p = {"symbol": sym, "interval": "1h", "limit": 1000}
        if end:
            p["endTime"] = end
        r = requests.get("https://api.binance.com/api/v3/klines", params=p, timeout=15).json()
        if not isinstance(r, list) or not r:
            break
        for k in r:
            out[(int(k[0]) + H_MS) // H_MS] = float(k[4])   # key = close hour
        end = int(r[0][0]) - 1
    return out


def bpx_1h(tick):
    start = int(datetime.now(timezone.utc).timestamp()) - 45 * 86400
    r = requests.get("https://api.backpack.exchange/api/v1/klines",
                     params={"symbol": f"{tick}.US_USDC", "interval": "1h",
                             "startTime": start}, timeout=15).json()
    if not isinstance(r, list):
        return {}
    return {(int(datetime.strptime(k["start"], "%Y-%m-%d %H:%M:%S")
                 .replace(tzinfo=timezone.utc).timestamp() * 1000) + H_MS) // H_MS:
            float(k["close"]) for k in r}


def arc_1h(tick):
    to = int(datetime.now(timezone.utc).timestamp() * 1_000_000)
    r = requests.get("https://api.arcus.xyz/v1/candles",
                     params={"market": f"{tick}-USD", "timeframe": "1h",
                             "to": to, "countback": 1000}, timeout=15).json()
    return {(c["openTime"] // 1_000_000 // 3600) + 1: float(c["close"])
            for c in r.get("candles", [])}


def stock_1h(tick):
    df = yf.download(tick, period="60d", interval="1h", progress=False, auto_adjust=True)
    if df is None or df.empty:
        return {}
    if hasattr(df.columns, "levels"):
        df.columns = df.columns.get_level_values(0)
    return {(int(ts.timestamp() * 1000) // H_MS): float(r["Close"])
            for ts, r in df.iterrows()}


def track_dev(st, tok, last_n=40):
    shared = sorted(set(st) & set(tok))[-last_n:]
    if len(shared) < 10:
        return None
    return statistics.mean(abs(tok[h] / st[h] - 1) * 100 for h in shared)


results = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "tracking": [], "fakes": [], "oracle": {}}

# ── 1 · per-venue tracking error ───────────────────────────────────────────
for t in TRACK:
    st = stock_1h(t)
    if not st:
        continue
    row = {"ticker": t,
           "bnc": track_dev(st, bnc_1h(t + "BUSDT")),
           "bpx": track_dev(st, bpx_1h(t)),
           "arc": track_dev(st, arc_1h(t))}
    results["tracking"].append(row)
    print(t, {k: (f"{v:.2f}%" if v is not None else "—") for k, v in row.items() if k != "ticker"})

# ── 2 · the fake-gauge audit ───────────────────────────────────────────────
for tick, sym, coin in FAKES:
    st = stock_1h(tick)
    tok = bnc_1h(sym)
    d = track_dev(st, tok) if st else None
    results["fakes"].append({"ticker": tick, "coin": coin, "dev": d})
    print("fake:", tick, coin, f"{d:.0f}%" if d is not None else "no stock data")

# ── 3 · weekend oracle + SPY residual ──────────────────────────────────────
venues = requests.get("https://api.binance.com/api/v3/exchangeInfo", timeout=15).json()
bases = {s["baseAsset"] for s in venues["symbols"]}
toks = sorted({s["baseAsset"][:-1] for s in venues["symbols"]
               if s["baseAsset"].endswith("B") and s["quoteAsset"] == "USDT"
               and s["status"] == "TRADING" and s["baseAsset"][:-1] not in bases
               and s["baseAsset"][:-1] not in {f[0] for f in FAKES}
               and s["baseAsset"][:-1] not in {"SHI", "CK", "Y"}})

daily = yf.download(toks, period="6mo", interval="1d", progress=False,
                    auto_adjust=True, group_by="ticker")
rows = []
for t in toks:
    try:
        sub = daily[t].dropna()
    except Exception:
        continue
    if len(sub) < 10:
        continue
    tok = bnc_1h(t + "BUSDT", pages=2)
    days = [{"d": ts.date(), "o": float(r["Open"]), "c": float(r["Close"])}
            for ts, r in sub.iterrows()]
    for i in range(1, len(days)):
        fri, mon = days[i - 1], days[i]
        if mon["d"].weekday() != 0 or fri["d"].weekday() != 4:
            continue
        edt = datetime(fri["d"].year, fri["d"].month, fri["d"].day,
                       tzinfo=timezone.utc) >= DST_2026
        fh, mh = (20, 13) if edt else (21, 14)
        kf = int(datetime(fri["d"].year, fri["d"].month, fri["d"].day, fh,
                          tzinfo=timezone.utc).timestamp() * 1000) // H_MS
        km = int(datetime(mon["d"].year, mon["d"].month, mon["d"].day, mh,
                          tzinfo=timezone.utc).timestamp() * 1000) // H_MS
        if kf not in tok or km not in tok:
            continue
        rows.append({"ticker": t, "monday": str(mon["d"]),
                     "pred": tok[km] / tok[kf] - 1, "actual": mon["o"] / fri["c"] - 1})

def stats_of(pairs):
    n = len(pairs)
    ps = [r["pred"] for r in pairs]; as_ = [r["actual"] for r in pairs]
    mp, ma = statistics.mean(ps), statistics.mean(as_)
    cov = sum((p - mp) * (a - ma) for p, a in zip(ps, as_)) / (n - 1)
    corr = cov / (statistics.stdev(ps) * statistics.stdev(as_))
    nz = [(p, a) for p, a in zip(ps, as_) if p * a != 0]
    return {"n": n, "corr": round(corr, 3), "beta": round(cov / statistics.variance(ps), 3),
            "hit": round(100 * sum(1 for p, a in nz if p * a > 0) / len(nz)),
            "mae_token": round(100 * statistics.mean(abs(p - a) for p, a in zip(ps, as_)), 2),
            "mae_naive": round(100 * statistics.mean(abs(a) for a in as_), 2)}

results["oracle"]["pooled"] = stats_of(rows)
spy = {r["monday"]: r for r in rows if r["ticker"] == "SPY"}
res = [{"pred": r["pred"] - spy[r["monday"]]["pred"],
        "actual": r["actual"] - spy[r["monday"]]["actual"]}
       for r in rows if r["ticker"] != "SPY" and r["monday"] in spy]
results["oracle"]["idiosyncratic"] = stats_of(res) | {"spy_weekends": len(spy)}
results["oracle"]["tickers"] = len({r["ticker"] for r in rows})

(ROOT / "data" / "venue_gauge_results.json").write_text(json.dumps(results, indent=2))
with open(ROOT / "data" / "venue_weekends.csv", "w") as f:
    f.write("ticker,monday,token_drift,actual_gap\n")
    for r in rows:
        f.write(f"{r['ticker']},{r['monday']},{r['pred']:.5f},{r['actual']:.5f}\n")
print("\npooled:", results["oracle"]["pooled"])
print("idio:  ", results["oracle"]["idiosyncratic"])
print(f"wrote data/venue_gauge_results.json + data/venue_weekends.csv ({len(rows)} weekend pairs)")
