#!/usr/bin/env python3
"""Study 10: escape rates of the CV contact-row gates.

Synthetic only. Builds a made-up CV + cover letter pair per case (fake name, example.com
contacts), seeds one defect per case, prints each to PDF with headless Chrome, and runs four
gate versions over every pack:

  V0  no gate
  V1  check 6: every contact token in the first 10 lines of the CV's -raw text
  V2  check 6 on the CV and the cover letter
  V3  V2 plus the layout check: every token on the email's line of the -layout text,
      no trailing or doubled separator

Ground truth does not come from any gate. Designed defects are defects by construction; whether a
row wrapped is measured from word boxes (pdftotext -bbox), a different extraction than either gate
reads. Writes data/gates_results.json and docs/figures/gates-fig1.svg.

Needs: google-chrome (or chromium), pdftotext (poppler), matplotlib.
"""
from __future__ import annotations

import html
import json
import math
import os
import re
import shutil
import subprocess
import tempfile

import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, "docs", "figures")
OUT = os.path.join(ROOT, "data", "gates_results.json")

PAPER, PAPER_DEEP = "#ffffff", "#fafafa"
INK, INK_SOFT, INK_FAINT = "#3d3327", "#58595a", "#877e72"
RUBRIC = "#8c2f22"
HAIR = "#e2e2e2"

TOKENS = ["+60 12-345 6789", "sam.tan@example.com", "Penang, Malaysia",
          "linkedin.com/in/samtan-example", "samtan.example.com", "github.com/samtan-example"]
EMAIL = TOKENS[1]
FIT_PX = 9.0      # the size the real fix settled on
SEP_PX = 10.5     # overflows and breaks at a separator: the shape of the real bug
URL_PX = 9.6      # overflows and breaks inside the github URL, at its hyphen
ROW_MM = 168      # row width; 9.0px fits, the two sizes above wrap. main() asserts all three

BODY = ("Process engineer with six years in semiconductor assembly and test. "
        "Built statistical process control dashboards used by fifteen engineers every day, "
        "ran gauge studies to AIAG fourth edition, and moved capability reporting from "
        "spreadsheets to Postgres. ") * 4
LETTER = ("Dear hiring team, I am writing about the process engineer role. "
          "My work sits where statistics meets the production floor. ") * 5


def page(tokens, px=FIT_PX, sep="|", extra_css="", hrefs=None, row_top=True, body=BODY):
    parts = []
    for i, t in enumerate(tokens):
        if t is None:                       # an emptied slot: its separators stay
            parts.append("")
            continue
        href = (hrefs or {}).get(i)
        cell = html.escape(t)
        if href:
            cell = f'<a href="{html.escape(href)}">{cell}</a>'
        parts.append(f'<span class="t{i}">{cell}</span>')
    row = f' <span class="sep">{sep}</span> '.join(parts)
    row_html = f'<div class="row">{row}</div>'
    css = (f"@page{{size:A4;margin:14mm}} body{{font:10.5px/1.5 Arial,sans-serif;color:#222;margin:0}}"
           f"h1{{font-size:22px;margin:0 0 4px}} .row{{font-size:{px}px;width:{ROW_MM}mm}}"
           f"a{{color:inherit;text-decoration:none}} p{{margin:8px 0}} {extra_css}")
    top = row_html if row_top else ""
    foot = "" if row_top else row_html
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>"
            f"<h1>Sam Tan</h1>{top}<p>{body}</p><p>{body}</p>{foot}</body></html>")


def case(cid, label, kind, cv=None, cl=None, truth=True, note=""):
    return dict(id=cid, label=label, kind=kind, cv=cv or {}, cl=cl or {}, truth=truth, note=note)


def drop(i):
    t = list(TOKENS)
    del t[i]
    return t


CASES = [
    case("C1", "clean pack", "control", truth=False),
    case("C2", "clean, tokens reordered", "benign", cv={"tokens": TOKENS[::-1]},
         cl={"tokens": TOKENS[::-1]}, truth=False),
    case("C3", "clean, 8.5px row", "benign", cv={"px": 8.5}, cl={"px": 8.5}, truth=False),
    *[case(f"D{i+1:02d}", f"CV drops {TOKENS[i].split('/')[0]}", "missing", cv={"tokens": drop(i)})
      for i in range(6)],
    case("D07", "cover letter drops the site", "missing, CL only", cl={"tokens": drop(4)}),
    case("D08", "cover letter drops github", "missing, CL only", cl={"tokens": drop(5)}),
    case("D09", "row breaks at a separator (the real bug)", "wrap", cv={"px": SEP_PX}, cl={"px": SEP_PX}),
    case("D10", "row breaks inside a URL", "wrap", cv={"px": URL_PX}),
    case("D11", "letter row breaks at a separator", "wrap, CL only", cl={"px": SEP_PX}),
    case("D12", "hard line break inside the row", "wrap",
         cv={"extra_css": ".t3::before{content:'';display:block}"}),
    case("D13", "emptied slot, doubled separator", "separator",
         cv={"tokens": TOKENS[:3] + [None] + TOKENS[4:] + [TOKENS[3]]}),
    case("D14", "trailing separator", "separator", cv={"tokens": TOKENS + [None]}),
    case("D15", "site misspelled", "wrong text",
         cv={"tokens": TOKENS[:4] + ["samtan.example.co"] + TOKENS[5:]}),
    case("D16", "zero-width space inside github", "wrong text",
         cv={"tokens": TOKENS[:5] + ["git​hub.com/samtan-example"]}),
    case("D17", "github in white text", "hidden",
         cv={"extra_css": ".t5{color:#fff}"}),
    case("D18", "github link points elsewhere", "wrong link",
         cv={"hrefs": {5: "https://github.com/someone-else"}}),
    case("D19", "contact row moved to the footer", "misplaced", cv={"row_top": False}),
    case("D20", "linkedin clipped by overflow", "hidden",
         cv={"extra_css": ".row{white-space:nowrap;overflow:hidden;width:120mm}"}),
]


def chrome():
    for c in ("google-chrome", "chromium", "chromium-browser"):
        if shutil.which(c):
            return c
    raise SystemExit("needs google-chrome or chromium on PATH")


def render(htmltext, pdf, tmp):
    src = os.path.join(tmp, os.path.basename(pdf) + ".html")
    with open(src, "w", encoding="utf-8") as f:
        f.write(htmltext)
    prof = os.path.join(tmp, "profile")   # one profile for every render: ~2.5 s each instead of ~12
    subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--no-first-run", "--disable-extensions",
                    f"--user-data-dir={prof}",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf}", "file://" + src],
                   check=True, capture_output=True, timeout=60)


def pdftext(pdf, *args):
    return subprocess.run(["pdftotext", *args, pdf, "-"], capture_output=True, text=True).stdout


# ---- the gates, copied from career-ops (tools/ats_check.py check 6, tools/pack_audit.py) ----
def check6(pdf):
    raw = pdftext(pdf, "-raw")
    head10 = re.sub(r"\s+", " ", " ".join(raw.splitlines()[:10]).lower())
    return [t for t in TOKENS if t.lower().rstrip("/") not in head10]


def layout(pdf):
    line = ""
    for ln in pdftext(pdf, "-f", "1", "-l", "1", "-layout").splitlines():
        if EMAIL in ln:
            line = ln.rstrip()
            break
    off = [t for t in TOKENS if t.lower().rstrip("/") not in line.lower()]
    strand = line.endswith("|") or re.search(r"\|\s+\|", line) is not None
    return off, strand


def versions(cv, cl):
    v1 = bool(check6(cv))
    v2 = v1 or bool(check6(cl))
    v3 = v2 or any(bool(o) or s for o, s in (layout(cv), layout(cl)))
    return {"V0": False, "V1": v1, "V2": v2, "V3": v3}


# ---- ground truth that no gate reads: word boxes ----
def row_lines(pdf):
    """How many baselines the contact row occupies, from pdftotext -bbox: every word between the
    name and the first body word. Matching known tokens instead would miss a break inside a token,
    which is exactly the case where a token stops being a word (first draft of this probe did)."""
    words = [(round(float(y)), w) for y, w in
             re.findall(r'yMin="([\d.]+)"[^>]*>([^<]+)<', pdftext(pdf, "-f", "1", "-l", "1", "-bbox"))]
    ys = [y for y, w in words]
    try:
        name = max(y for y, w in words if w == "Tan")
        body = min(y for y, w in words if w == "Process" or w == "Dear")
    except ValueError:
        return 0
    return len({y for y in ys if name < y < body})


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def main():
    os.makedirs(FIGS, exist_ok=True)
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for c in CASES:
            pdfs = {}
            for doc, body in (("cv", BODY), ("cl", LETTER)):
                spec = dict(c[doc])
                toks = spec.pop("tokens", TOKENS)
                pdfs[doc] = os.path.join(tmp, f"{c['id']}-{doc}.pdf")
                render(page(toks, body=body, **spec), pdfs[doc], tmp)
            v = versions(pdfs["cv"], pdfs["cl"])
            lines = {d: row_lines(p) for d, p in pdfs.items()}
            rows.append({**{k: c[k] for k in ("id", "label", "kind", "truth")}, "caught": v,
                         "row_lines": lines})
            print(f"{c['id']:4} {c['label']:38} lines cv/cl {lines['cv']}/{lines['cl']}  "
                  + " ".join(f"{k}:{'x' if b else '.'}" for k, b in v.items()))

    # the controls must pass every gate, and the wrap calibration must hold, or nothing below means anything
    by = {r["id"]: r for r in rows}
    assert not any(by["C1"]["caught"].values()), "clean pack failed a gate"
    assert by["C1"]["row_lines"] == {"cv": 1, "cl": 1}, f"clean row wraps: {by['C1']['row_lines']}"
    assert by["D09"]["row_lines"]["cv"] == 2 and by["D10"]["row_lines"]["cv"] == 2, \
        f"wrap cases did not wrap: {by['D09']['row_lines']}, {by['D10']['row_lines']}; recalibrate ROW_MM"

    defects = [r for r in rows if r["truth"]]
    benign = [r for r in rows if not r["truth"]]
    summary = {}
    for ver in ("V0", "V1", "V2", "V3"):
        esc = sum(not r["caught"][ver] for r in defects)
        fa = sum(r["caught"][ver] for r in benign)
        p, lo, hi = wilson(esc, len(defects))
        summary[ver] = {"escaped": esc, "defects": len(defects), "escape_rate": p,
                        "ci95": [lo, hi], "false_alarms": fa, "benign": len(benign)}
        print(f"{ver}: escaped {esc}/{len(defects)} = {p:.0%} (95% CI {lo:.0%}-{hi:.0%}), "
              f"false alarms {fa}/{len(benign)}")

    with open(OUT, "w") as f:
        json.dump({"cases": rows, "summary": summary, "row_mm": ROW_MM,
                   "note": "designed defect library, not a field sample"}, f, indent=1)
    figure(rows)


def figure(rows):
    vers = ["V0", "V1", "V2", "V3"]
    fig, ax = plt.subplots(figsize=(7.2, 0.26 * len(rows) + 0.9), dpi=100)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER_DEEP)
    for y, r in enumerate(rows):
        for x, ver in enumerate(vers):
            hit = r["caught"][ver]
            if r["truth"]:
                col = INK if hit else RUBRIC
                ax.add_patch(plt.Rectangle((x + .08, y + .12), .84, .76, color=col,
                                           alpha=1 if hit else .9, lw=0))
            else:   # benign: a hit here is a false alarm
                ax.add_patch(plt.Rectangle((x + .08, y + .12), .84, .76, fill=False,
                                           ec=RUBRIC if hit else HAIR, lw=1.2, hatch="//" if hit else None))
    ax.set_xlim(0, len(vers))
    ax.set_ylim(len(rows), 0)
    ax.set_xticks([i + .5 for i in range(len(vers))])
    ax.set_xticklabels(["no gate", "check 6\nCV", "check 6\nCV + letter", "+ layout\ncheck"],
                       fontsize=8, color=INK_SOFT)
    ax.xaxis.tick_top()
    ax.set_yticks([i + .5 for i in range(len(rows))])
    ax.set_yticklabels([f"{r['id']}  {r['label']}" for r in rows], fontsize=7.5,
                       color=INK_SOFT, family="monospace")
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "gates-fig1.svg"), facecolor=PAPER)


if __name__ == "__main__":
    main()
