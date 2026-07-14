#!/usr/bin/env python3
"""Study 04 — recalibrate the gauge, then re-read the measurements.

The backtest engine is the measuring instrument. Before trusting any number it produced,
run the equivalent of an MSA study on it: is it BIASED, and in which direction?

Two defects, pushing opposite ways — which is why the net P&L looked plausible and hid them:

  STOPS  filled at the price observed on the next poll, not at the resting stop level.
         Price gaps through the stop between polls, so the recorded loss is worse than the
         order could have suffered. Systematically PESSIMISTIC.

  TAKE-PROFITS also filled at the poll price. But a resting limit sell fills AT the limit
         and never better — so booking +18% on a +15% order is money that does not exist.
         Systematically OPTIMISTIC.

A bias in one direction is easy to spot in the aggregate. Two biases in opposite directions
cancel in the mean and hide in the tails. That is the whole lesson.

  python3 scripts/gauge_rr.py     -> data/gauge_results.json + docs/figures/gauge-fig{1,2,3}.svg
"""
import csv, json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "gauge_trades.csv")
FIGS = os.path.join(ROOT, "docs", "figures")
OUT  = os.path.join(ROOT, "data", "gauge_results.json")

STOP_SLIP_PCT = 0.3      # a stop-market order slips past its trigger. 0.3% on a liquid alt.

# Paper Workbench palette (DESIGN.md) — ink for data, rubric for the series under argument.
INK, INK_FAINT, RUBRIC = "#3d3327", "#877e72", "#8c2f22"
PAPER, PAPER_DEEP, HAIR = "#ffffff", "#fafafa", "#e2e2e2"


def style(ax):
    ax.set_facecolor(PAPER_DEEP)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(HAIR)
    ax.tick_params(colors=INK_FAINT, labelsize=8)
    ax.grid(axis="y", color=HAIR, lw=.6, alpha=.6)
    ax.set_axisbelow(True)


def corrected(t):
    """What the fill SHOULD have been, given the order the book actually placed."""
    rec, reason = float(t["pnl_pct_recorded"]), t["exit_reason"]
    sl, tp = float(t["cfg_stop_loss_pct"]), float(t["cfg_take_profit_pct"])
    if reason == "stop_loss":
        # A resting stop triggers intrabar. Crypto trades continuously, so it fills at ~the
        # stop less slippage. Stocks gap overnight, so we keep the worse observed price
        # rather than claim an escape we cannot prove.
        if t["asset_type"] == "stock":
            return rec
        return max(rec, -sl - STOP_SLIP_PCT)
    if reason == "take_profit":
        return min(rec, tp)         # a limit fills AT the limit, never better
    return rec                      # market exits are unchanged


def main():
    rows = list(csv.DictReader(open(DATA)))
    for t in rows:
        t["rec"] = float(t["pnl_pct_recorded"])
        t["cor"] = corrected(t)
        t["usd_rec"] = float(t["pnl_usd_recorded"])
        t["usd_cor"] = float(t["cost_usd"]) * t["cor"] / 100
        t["fee"] = float(t["cost_usd"]) * float(t["fee_pct"]) / 100 * 2

    def grp(reason):
        return [t for t in rows if t["exit_reason"] == reason]

    res = {"n_trades": len(rows), "by_reason": {}}
    for r in ("stop_loss", "take_profit", "signal_reversal", "manual_close"):
        g = grp(r)
        if not g:
            continue
        res["by_reason"][r] = {
            "n": len(g),
            "mean_recorded_pct": round(float(np.mean([t["rec"] for t in g])), 2),
            "mean_corrected_pct": round(float(np.mean([t["cor"] for t in g])), 2),
            "usd_recorded": round(sum(t["usd_rec"] for t in g)),
            "usd_corrected": round(sum(t["usd_cor"] for t in g)),
            "worst_recorded_pct": round(min(t["rec"] for t in g), 2),
        }

    fees = sum(t["fee"] for t in rows)
    net_rec = sum(t["usd_rec"] for t in rows) - fees
    net_cor = sum(t["usd_cor"] for t in rows) - fees
    wins = [t["cor"] for t in rows if t["cor"] > 0]
    loss = [t["cor"] for t in rows if t["cor"] <= 0]
    wr = len(wins) / len(rows)
    res.update({
        "fees_usd": round(fees),
        "net_recorded_usd": round(net_rec),
        "net_corrected_usd": round(net_cor),
        "artifact_usd": round(net_cor - net_rec),
        "win_rate_pct": round(wr * 100, 1),
        "payoff_ratio": round(float(np.mean(wins) / abs(np.mean(loss))), 2),
        "breakeven_payoff": round((1 - wr) / wr, 2),
        "stop_slip_pct": STOP_SLIP_PCT,
    })

    # ── fig 1: the gauge bias — two errors, opposite directions ──────────────
    fig, ax = plt.subplots(figsize=(7.6, 3.5), facecolor=PAPER)
    s, t_ = res["by_reason"]["stop_loss"], res["by_reason"]["take_profit"]
    labels = ["Stop-loss exits\n(n=%d)" % s["n"], "Take-profit exits\n(n=%d)" % t_["n"]]
    intended = [-float(rows[0]["cfg_stop_loss_pct"]), 0]      # placeholder, set below
    # intended = the mean CONFIGURED order level for each group
    intended = [
        -float(np.mean([float(t["cfg_stop_loss_pct"]) for t in grp("stop_loss")])),
        float(np.mean([float(t["cfg_take_profit_pct"]) for t in grp("take_profit")])),
    ]
    recorded = [s["mean_recorded_pct"], t_["mean_recorded_pct"]]
    x = np.arange(2)
    w = 0.28
    ax.bar(x - w, intended, w, color=INK_FAINT, label="Order placed (intended)")
    ax.bar(x,     recorded, w, color=RUBRIC,    label="Gauge recorded")
    ax.bar(x + w, [s["mean_corrected_pct"], t_["mean_corrected_pct"]], w,
           color=INK, label="Corrected fill")
    ax.axhline(0, color=HAIR, lw=1)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("mean P&L per trade (%)", color=INK_FAINT, fontsize=9)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK, loc="lower right")
    for i, v in enumerate(recorded):
        ax.annotate(f"{v:+.1f}%", (x[i], v), ha="center",
                    va="bottom" if v > 0 else "top", fontsize=8, color=RUBRIC, weight="bold")
    style(ax)
    ax.set_title("The gauge is biased in BOTH directions", color=INK, fontsize=10,
                 loc="left", pad=10)
    fig.tight_layout(); fig.savefig(os.path.join(FIGS, "gauge-fig1.svg")); plt.close(fig)

    # ── fig 2: the search collapse (Study 1) ─────────────────────────────────
    fig, ax = plt.subplots(figsize=(7.6, 3.2), facecolor=PAPER)
    stages = ["Best of 48\n(in-sample)", "After deflation\n(48 configs tried)", "Untouched\nholdout"]
    vals = [0.67, 0.09, -0.79]
    cols = [INK_FAINT, INK, RUBRIC]
    ax.bar(stages, vals, 0.5, color=cols)
    ax.axhline(0, color=INK, lw=1)
    for i, v in enumerate(vals):
        ax.annotate(f"{v:+.2f}", (i, v), ha="center", va="bottom" if v > 0 else "top",
                    fontsize=9, color=cols[i], weight="bold")
    ax.set_ylabel("Sharpe ratio", color=INK_FAINT, fontsize=9)
    ax.set_title("A strong backtest is the normal output of searching", color=INK,
                 fontsize=10, loc="left", pad=10)
    style(ax)
    fig.tight_layout(); fig.savefig(os.path.join(FIGS, "gauge-fig2.svg")); plt.close(fig)

    # ── fig 3: out-of-sample in POPULATION, not just time (Study 4) ───────────
    coins = ["WLD","LTC","UNI","AVAX","BCH","DEXE","XRP","AAVE","LINK","TRX","BNB","DOGE"]
    strat = [-83,-95,-51,-42,-90,60,-55,-83,-82,8,7,-66]
    hold  = [-76,-69,18,51,26,253,144,246,370,891,1372,2423]
    fig, ax = plt.subplots(figsize=(7.6, 3.6), facecolor=PAPER)
    x = np.arange(len(coins))
    ax.bar(x - .2, strat, .4, color=RUBRIC, label="The strategy")
    ax.bar(x + .2, hold,  .4, color=INK_FAINT, label="Buy & hold")
    ax.axhline(0, color=INK, lw=1)
    ax.set_yscale("symlog", linthresh=50)
    ax.set_xticks(x); ax.set_xticklabels(coins, fontsize=7.5)
    ax.set_ylabel("total return (%, symlog)", color=INK_FAINT, fontsize=9)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK, loc="upper left")
    ax.set_title("12 coins it was never fitted to — it beats holding on 0 of them",
                 color=INK, fontsize=10, loc="left", pad=10)
    style(ax)
    fig.tight_layout(); fig.savefig(os.path.join(FIGS, "gauge-fig3.svg")); plt.close(fig)

    json.dump(res, open(OUT, "w"), indent=1)
    print(json.dumps(res, indent=1))
    print(f"\nfigures -> {FIGS}/gauge-fig1..3.svg")


if __name__ == "__main__":
    main()
