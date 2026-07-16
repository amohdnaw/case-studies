#!/usr/bin/env python3
"""Study 07 — attribute MSA for AOI pass/fail between machines.

Synthetic only. Reads data/aoi_msa_synthetic.csv, writes docs/figures/attr-fig1–3.svg
and data/aoi_msa_results.json.
"""
from __future__ import annotations

import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "aoi_msa_synthetic.csv")
FIGS = os.path.join(ROOT, "docs", "figures")
OUT = os.path.join(ROOT, "data", "aoi_msa_results.json")

PAPER, PAPER_DEEP = "#ffffff", "#fafafa"
INK, INK_SOFT, INK_FAINT = "#3d3327", "#58595a", "#877e72"
RUBRIC = "#8c2f22"
HAIR = "#e2e2e2"


def style(ax):
    ax.set_facecolor(PAPER_DEEP)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(HAIR)
    ax.tick_params(colors=INK_FAINT, labelsize=8)
    ax.grid(color=HAIR, lw=0.6, alpha=0.6)
    ax.set_axisbelow(True)


def cohens_kappa(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Binary Cohen's kappa (pass=0, fail=1)."""
    t = (y_true == "fail").astype(int)
    p = (y_pred == "fail").astype(int)
    n = t.size
    po = (t == p).mean()
    pt = t.mean()
    pp = p.mean()
    pe = pt * pp + (1 - pt) * (1 - pp)
    if pe >= 1.0:
        return 1.0
    return float((po - pe) / (1 - pe))


def fleiss_kappa(matrix: np.ndarray) -> float:
    """Binary Fleiss κ. matrix shape (n_units, n_raters), values 0=pass 1=fail."""
    n, m = matrix.shape
    n1 = matrix.sum(axis=1)
    n0 = m - n1
    P_i = (n0 * (n0 - 1) + n1 * (n1 - 1)) / (m * (m - 1))
    P_bar = float(P_i.mean())
    p1 = float(matrix.mean())
    p0 = 1.0 - p1
    P_e = p0**2 + p1**2
    if P_e >= 1.0:
        return 1.0
    return (P_bar - P_e) / (1 - P_e)


def effectiveness(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    t = y_true == "fail"
    p = y_pred == "fail"
    tp = int((t & p).sum())
    tn = int((~t & ~p).sum())
    fp = int((~t & p).sum())
    fn = int((t & ~p).sum())
    n = len(y_true)
    return {
        "n": n,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "effectiveness_pct": round(100 * (tp + tn) / n, 1),
        "miss_rate_pct": round(100 * fn / max(int(t.sum()), 1), 1),
        "false_alarm_pct": round(100 * fp / max(int((~t).sum()), 1), 1),
        "kappa": round(cohens_kappa(y_true, y_pred), 3),
    }


def fig1_confusion(df: pd.DataFrame, machines: list[str]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(8.2, 3.0), facecolor=PAPER)
    labels = ["pass", "fail"]
    for ax, machine in zip(axes, machines):
        sub = df[df.machine == machine]
        ct = pd.crosstab(sub.true_state, sub.call, normalize="index")
        for lab in labels:
            if lab not in ct.columns:
                ct[lab] = 0.0
            if lab not in ct.index:
                pass
        ct = ct.reindex(index=labels, columns=labels, fill_value=0.0)
        im = ax.imshow(ct.values, cmap=plt.cm.Greys, vmin=0, vmax=1, aspect="auto")
        for i in range(2):
            for j in range(2):
                val = ct.values[i, j]
                color = RUBRIC if (labels[i] == "pass" and labels[j] == "fail") or (
                    labels[i] == "fail" and labels[j] == "pass"
                ) else INK
                weight = "bold" if val > 0.15 and i != j else "normal"
                ax.text(j, i, f"{100*val:.0f}%", ha="center", va="center", fontsize=9, color=color, weight=weight)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["call pass", "call fail"], fontsize=7.5)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["true pass", "true fail"], fontsize=7.5)
        color = RUBRIC if machine == "M07" else (INK if machine == "M05" else INK_SOFT)
        ax.set_title(machine, color=color, fontsize=10, loc="left")
    fig.suptitle("Agreement with the reference panel (row = truth)", color=INK, fontsize=9.5, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(os.path.join(FIGS, "attr-fig1.svg"))
    plt.close(fig)


def fig2_kappa(stats: dict, machines: list[str]) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 3.0), facecolor=PAPER)
    kappas = [stats[m]["kappa"] for m in machines]
    eff = [stats[m]["effectiveness_pct"] for m in machines]
    x = np.arange(len(machines))
    w = 0.36
    ax.bar(x - w / 2, kappas, width=w, color=INK, label="Cohen's κ vs truth")
    ax.bar(x + w / 2, np.array(eff) / 100, width=w, color=INK_FAINT, label="effectiveness")
    ax.axhline(0.7, color=RUBRIC, ls=":", lw=1, alpha=0.8)
    ax.text(len(machines) - 0.55, 0.72, "κ = 0.7 (typical accept gate)", fontsize=7.5, color=RUBRIC)
    ax.set_xticks(x)
    ax.set_xticklabels(machines)
    ax.set_ylabel("κ / effectiveness (0–1 scale)")
    ax.set_ylim(0, 1.05)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.set_title("Attribute agreement by machine", color=INK, fontsize=9.5, loc="left")
    for i, k in enumerate(kappas):
        ax.text(i - w / 2, k + 0.02, f"{k:.2f}", ha="center", fontsize=8, color=INK)
    style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "attr-fig2.svg"))
    plt.close(fig)


def fig3_yield_trap(df: pd.DataFrame, machines: list[str]) -> None:
    """Pass rate vs truth — lenient machine looks like yield hero."""
    fig, ax = plt.subplots(figsize=(7.6, 3.0), facecolor=PAPER)
    true_fail = (df.true_state == "fail").mean() * 100
    pass_rates = []
    for m in machines:
        sub = df[df.machine == m]
        pass_rates.append(100 * (sub.call == "pass").mean())
    x = np.arange(len(machines))
    ax.bar(x, pass_rates, width=0.5, color=[INK_SOFT, INK, RUBRIC])
    ax.axhline(100 - true_fail, color=INK, ls="--", lw=1.2, label=f"true pass rate ({100-true_fail:.0f}%)")
    ax.set_xticks(x)
    ax.set_xticklabels(machines)
    ax.set_ylabel("% units called pass")
    ax.set_ylim(0, 105)
    ax.set_title("The lenient gauge looks like yield — until you MSA it", color=INK, fontsize=9.5, loc="left")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    for i, v in enumerate(pass_rates):
        ax.text(i, v + 1.5, f"{v:.0f}%", ha="center", fontsize=9, color=INK, weight="bold")
    style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "attr-fig3.svg"))
    plt.close(fig)


def main():
    df = pd.read_csv(DATA)
    machines = sorted(df.machine.unique())
    stats = {m: effectiveness(df[df.machine == m].true_state.values, df[df.machine == m].call.values) for m in machines}

    mat = np.column_stack([
        (df[df.machine == m].call.values == "fail").astype(int) for m in machines
    ])
    fk = round(fleiss_kappa(mat), 3)

    worst = max(machines, key=lambda m: stats[m]["miss_rate_pct"])
    best = max(machines, key=lambda m: stats[m]["kappa"])

    os.makedirs(FIGS, exist_ok=True)
    fig1_confusion(df, machines)
    fig2_kappa(stats, machines)
    fig3_yield_trap(df, machines)

    n_units = int(df.unit_id.nunique())
    true_fail_pct = round(100 * (df.true_state == "fail").mean(), 1)

    results = {
        "synthetic": True,
        "seed": 20260716,
        "environment": "semiconductor assembly & test (OSAT) — simulated AOI attribute MSA",
        "n_units": n_units,
        "n_machines": len(machines),
        "machines": machines,
        "true_fail_prevalence_pct": true_fail_pct,
        "fleiss_kappa_all_machines": fk,
        "best_machine": best,
        "worst_machine": worst,
        "by_machine": stats,
        "operational_note": (
            "Ranking yield or defect Pareto by raw inspection counts before attribute MSA "
            "confuses gauge leniency with process quality."
        ),
    }
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
        f.write("\n")

    print("attr-fig1.svg, attr-fig2.svg, attr-fig3.svg written")
    print(f"Fleiss κ = {fk}  |  best {best} κ={stats[best]['kappa']}  worst {worst} κ={stats[worst]['kappa']}")


if __name__ == "__main__":
    main()
