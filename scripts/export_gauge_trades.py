#!/usr/bin/env python3
"""Export the spot paper trades that study 04 recalibrates, from the live system.

Source: ~/trading-signals/paper_traders.json (13 LLM-signal persona books) plus each
book's configured stop-loss / take-profit, read out of paper_trading.py. Those two config
numbers are what the recalibration needs — they are the ORDER the book intended to place,
against which we compare the fill it actually recorded.

Only spot BUY trades are exported. The book is long-only spot; 32 SELL rows exist in the
raw state from a period when a live short branch in close_position() priced them with
inverted P&L (a separate defect, fixed 2026-07-13). They are excluded rather than
silently averaged in.

  python3 scripts/export_gauge_trades.py   ->  data/gauge_trades.csv
"""
import csv, json, os, re, sys

SRC = os.path.expanduser("~/trading-signals")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "gauge_trades.csv")


def book_configs(path):
    """Map book -> (stop_loss_pct, take_profit_pct) straight from the engine source."""
    src = open(path).read()
    cfgs = {}
    for m in re.finditer(r'^    "(\w+)":\s*\{', src, re.M):
        seg = src[m.start():m.start() + 2000]
        sl = re.search(r'"stop_loss_pct":\s*([\d.]+)', seg)
        tp = re.search(r'"take_profit_pct":\s*([\d.]+)', seg)
        if sl and tp:
            cfgs[m.group(1)] = (float(sl.group(1)), float(tp.group(1)))
    return cfgs


def main():
    cfgs = book_configs(os.path.join(SRC, "paper_trading.py"))
    books = json.load(open(os.path.join(SRC, "paper_traders.json")))

    rows, dropped = [], 0
    for bid, b in books.items():
        for t in b.get("trades", []):
            if t.get("signal") != "BUY":
                dropped += 1                     # phantom shorts — see docstring
                continue
            if bid not in cfgs or "exit_reason" not in t:
                dropped += 1
                continue
            sl, tp = cfgs[bid]
            rows.append({
                "book": bid, "ticker": t["ticker"], "asset_type": t.get("asset_type", "crypto"),
                "entry_date": t["entry_date"][:19], "exit_date": t["exit_date"][:19],
                "entry_price": t["entry_price"], "exit_price": t["exit_price"],
                "cost_usd": t["cost_usd"],
                "pnl_pct_recorded": t["pnl_pct"], "pnl_usd_recorded": t.get("pnl_usd", 0),
                "exit_reason": t["exit_reason"], "confidence": t.get("confidence", ""),
                "fee_pct": t.get("fee_pct", 0.15),
                "cfg_stop_loss_pct": sl, "cfg_take_profit_pct": tp,
            })

    if not rows:
        sys.exit("no trades found — is ~/trading-signals present?")
    rows.sort(key=lambda r: r["entry_date"])
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} spot BUY trades -> {OUT}  ({dropped} rows excluded)")


if __name__ == "__main__":
    main()
