#!/usr/bin/env python3
"""Study 05 — 7,860 strategies across crypto and stocks. Doing nothing beat all of them.

Two datasets, two asset classes, one conclusion reached by two different roads:

  data/exhaustion_crypto.csv  7,524 runs — 22 indicators x 11 coins x 3 combination tiers,
                              on 1h and 1d bars, at 0.15%/side.
  data/exhaustion_stocks.csv    336 runs — the same 21 indicators x 16 liquid US names,
                              daily, at 0.03%/side (5x cheaper).

Every run is scored twice: once with costs (NET) and once with the tolls switched off (GROSS).
That single decomposition is what makes the two failure modes visible, and they are opposites:

  CRYPTO  the signal is often RIGHT and the fees eat it.      -> you lose MONEY
  STOCKS  the signal makes money and still loses to holding.  -> you lose OPPORTUNITY

  python3 scripts/exhaustion.py   ->  docs/figures/exh-fig{1,2,3}.svg + data/exhaustion_results.json
"""
import csv, json, os
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
FIGS = os.path.join(ROOT, "docs", "figures")

# Paper Workbench palette (DESIGN.md): ink for data, rubric for the series under argument.
INK, INK_FAINT, RUBRIC = "#3d3327", "#877e72", "#8c2f22"
PAPER, PAPER_DEEP, HAIR = "#ffffff", "#fafafa", "#e2e2e2"


def style(ax):
    ax.set_facecolor(PAPER_DEEP)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(HAIR)
    ax.tick_params(colors=INK_FAINT, labelsize=8)
    ax.grid(color=HAIR, lw=.6, alpha=.6)
    ax.set_axisbelow(True)


def main():
    crypto = list(csv.DictReader(open(f"{DATA}/exhaustion_crypto.csv")))
    stocks = list(csv.DictReader(open(f"{DATA}/exhaustion_stocks.csv")))
    for r in crypto:
        for k in ("gross", "net", "buyhold", "cost_drag"):
            r[k] = float(r[k])
    for r in stocks:
        for k in ("gross", "net", "buyhold", "drag", "sharpe", "max_dd"):
            r[k] = float(r[k])

    res = {"n_crypto": len(crypto), "n_stocks": len(stocks), "n_total": len(crypto) + len(stocks)}

    # ── FIG 1 — the two mechanisms, side by side ─────────────────────────────
    c1h = [r for r in crypto if r["tf"] == "1h"]
    ck = sum(1 for r in c1h if r["verdict"] == "cost_killed")
    losers_1h = sum(1 for r in c1h if r["verdict"] != "ok")
    st_lag = sum(1 for r in stocks if r["verdict"] == "lags_hold")
    st_ok = sum(1 for r in stocks if r["verdict"] == "ok")
    res.update({"crypto_1h_cost_killed": ck, "crypto_1h_losers": losers_1h,
                "stocks_lags_hold": st_lag, "stocks_beat_hold": st_ok})

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 3.3), facecolor=PAPER)
    # crypto: gross vs net for the worst toll-booth cases
    worst = sorted([r for r in c1h if r["verdict"] == "cost_killed"],
                   key=lambda r: -r["cost_drag"])[:6]
    y = np.arange(len(worst))
    a1.barh(y + .18, [r["gross"] * 100 for r in worst], .34, color=INK_FAINT, label="gross")
    a1.barh(y - .18, [r["net"] * 100 for r in worst], .34, color=RUBRIC, label="net")
    a1.axvline(0, color=INK, lw=1)
    a1.set_yticks(y); a1.set_yticklabels([f"{r['coin']} {r['strategy'][:11]}" for r in worst], fontsize=7)
    a1.set_xlabel("return (%)", color=INK_FAINT, fontsize=8)
    a1.set_title("CRYPTO — the signal was right,\nthe fees ate it", color=INK, fontsize=9, loc="left")
    a1.legend(frameon=False, fontsize=7, labelcolor=INK, loc="upper center",
              bbox_to_anchor=(0.5, -0.28), ncol=2)
    style(a1)

    # stocks: net vs buy-and-hold, log-ish
    a2.scatter([r["buyhold"] * 100 for r in stocks], [r["net"] * 100 for r in stocks],
               s=13, color=RUBRIC, alpha=.55, edgecolors="none")
    lim = [-100, max(max(r["buyhold"] for r in stocks), max(r["net"] for r in stocks)) * 100 * 1.05]
    a2.plot(lim, lim, color=INK, lw=1.2, ls="--")
    a2.annotate("break-even vs\ndoing nothing", (lim[1] * .52, lim[1] * .70), fontsize=7.5,
                color=INK, ha="left")
    a2.set_xlim(lim); a2.set_ylim(lim)
    a2.set_xlabel("buy & hold (%)", color=INK_FAINT, fontsize=8)
    a2.set_ylabel("strategy, net (%)", color=INK_FAINT, fontsize=8)
    a2.set_title(f"STOCKS — profitable, and still\nbelow the line ({st_ok} of {len(stocks)} above)",
                 color=INK, fontsize=9, loc="left")
    style(a2)
    fig.tight_layout(); fig.savefig(f"{FIGS}/exh-fig1.svg"); plt.close(fig)

    # ── FIG 2 — the frequency ladder (crypto) ────────────────────────────────
    fig, ax = plt.subplots(figsize=(7.6, 3.0), facecolor=PAPER)
    tfs = ["1h", "1d"]
    ck_share, ok_share = [], []
    for tf in tfs:
        sub = [r for r in crypto if r["tf"] == tf]
        lose = [r for r in sub if r["verdict"] != "ok"]
        ck_share.append(sum(1 for r in lose if r["verdict"] == "cost_killed") / max(len(lose), 1) * 100)
        ok_share.append(sum(1 for r in sub if r["verdict"] == "ok") / len(sub) * 100)
    tfs_all = ["1h", "1d", "1w*"]
    ck_share.append(0.4)          # study 6: 1 of 231
    ok_share.append(55.0)
    x = np.arange(3)
    ax.bar(x - .19, ok_share, .38, color=INK, label="profitable (%)")
    ax.bar(x + .19, ck_share, .38, color=RUBRIC, label="of the losers: killed by fees (%)")
    for i, (o, c) in enumerate(zip(ok_share, ck_share)):
        ax.annotate(f"{o:.0f}%", (i - .19, o), ha="center", va="bottom", fontsize=8, color=INK)
        ax.annotate(f"{c:.0f}%", (i + .19, c), ha="center", va="bottom", fontsize=8, color=RUBRIC, weight="bold")
    ax.set_xticks(x); ax.set_xticklabels(["hourly", "daily", "weekly*"])
    ax.set_title("Same indicators. Same coins. The only variable is how often you pay.",
                 color=INK, fontsize=9.5, loc="left")
    ax.legend(frameon=False, fontsize=8, labelcolor=INK, loc="upper center",
              bbox_to_anchor=(0.5, -0.14), ncol=2)
    ax.set_ylim(0, 66)
    style(ax)
    fig.tight_layout(); fig.savefig(f"{FIGS}/exh-fig2.svg"); plt.close(fig)

    # ── FIG 3 — what the median strategy captures of buy-and-hold ────────────
    fig, ax = plt.subplots(figsize=(7.6, 2.6), facecolor=PAPER)
    med_net = float(np.median([r["net"] for r in stocks])) * 100
    med_bh = float(np.median([r["buyhold"] for r in stocks])) * 100
    ax.barh([1], [med_bh], .42, color=INK_FAINT)
    ax.barh([0], [med_net], .42, color=RUBRIC)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["median strategy", "doing nothing"], fontsize=9)
    ax.annotate(f"+{med_bh:.0f}%", (med_bh, 1), va="center", ha="left", fontsize=9,
                color=INK, weight="bold", xytext=(5, 0), textcoords="offset points")
    ax.annotate(f"+{med_net:.0f}%  — {med_net/med_bh*100:.0f}% of it", (med_net, 0), va="center",
                ha="left", fontsize=9, color=RUBRIC, weight="bold",
                xytext=(5, 0), textcoords="offset points")
    ax.set_xlim(0, med_bh * 1.35)
    ax.set_xlabel("total return over ~7 years (%)", color=INK_FAINT, fontsize=8)
    ax.set_title("The stock disease: not wrong. Absent.", color=INK, fontsize=9.5, loc="left")
    style(ax)
    fig.tight_layout(); fig.savefig(f"{FIGS}/exh-fig3.svg"); plt.close(fig)

    res.update({
        "stocks_median_net_pct": round(med_net, 1),
        "stocks_median_buyhold_pct": round(med_bh, 1),
        "stocks_capture_pct": round(med_net / med_bh * 100, 1),
        "stocks_median_cost_drag_pct": round(float(np.median([r["drag"] for r in stocks])) * 100, 1),
        "crypto_verdicts": dict(Counter(r["verdict"] for r in crypto)),
        "stocks_verdicts": dict(Counter(r["verdict"] for r in stocks)),
    })
    json.dump(res, open(f"{DATA}/exhaustion_results.json", "w"), indent=1)
    print(json.dumps(res, indent=1))
    print(f"\nfigures -> {FIGS}/exh-fig1..3.svg")


if __name__ == "__main__":
    main()
