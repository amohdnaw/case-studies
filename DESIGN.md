# DESIGN.md — case-studies (frozen 2026-07-12, Direction A "Paper Workbench")

Anchor: `design/direction-mock.html` Direction A. Register: a working scientist's lab
notebook — quiet paper, one rubric red, serif body, mono apparatus. Derived from
`~/design-library/sites/paper-workbench.html`.

## Palette (ONE accent)

| token | value | use |
|---|---|---|
| `--paper` | `oklch(95.6% .017 92)` | page background |
| `--paper-deep` | `oklch(93.2% .021 90)` | figure wells, inset panels |
| `--ink` | `oklch(25% .02 65)` | body text, headings |
| `--ink-soft` | `oklch(38% .02 65)` | standfirst, captions |
| `--ink-faint` | `oklch(52% .018 70)` | margin notes, th labels |
| `--rubric` | `oklch(43% .125 29)` | THE accent: kickers, verdict borders, hits, links |
| `--wash` | `oklch(43% .125 29 / .07)` | verdict box fill |
| `--hair` | `oklch(25% .02 65 / .28)` | strong rules |
| `--hair-faint` | `oklch(25% .02 65 / .14)` | row rules |

No other hues. Charts: ink for data, rubric for the one series being argued about,
ink-faint for baselines/reference. Light theme only (paper is the identity; print-friendly).

## Type

- Serif (body, headings, td first-col): `"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif`
- Mono (kickers, tables, captions, figure labels): `ui-monospace,Menlo,Consolas,monospace`
- Scale: h1 2.1rem/1.18 w600 ls-.01em · standfirst 1.05rem italic ink-soft · body .98rem/1.6
  · table data .8rem mono · kicker/caption .68–.75rem mono uppercase ls .08–.14em
- Measure: 46rem sheet, centered. Prose max ~38rem inside it.

## Component grammar

- **Kicker bar**: mono uppercase, rubric, space-between (label left, meta right), hair
  underline. Opens every page.
- **Verdict box**: `--wash` fill, 3px rubric left border, no radius. One per study.
- **Margin note**: floated right into the right margin (11rem, rubric hairline top,
  ink-faint, .72rem); stacks inline on <76rem viewports.
- **Table**: mono data, serif first column, hair underline on th, hair-faint rows.
  Hits (the numbers being argued) in rubric bold.
- **Figure**: hair border, paper-deep well, ruled-paper background lines
  (`repeating-linear-gradient` 24px), mono figcaption below. Figures are SVG.
- **Footnav**: hair top rule, mono, rubric, space-between (← index / next study →).
- **Byline** (added v4, 2026-07-14): mono, uppercase, ls .18em — `Ammar Nawawi` (rubric, links
  `portfolio.amohdnaw.xyz`) left, `Process Engineer (SPC)` (ink-faint) right, hair-faint underline.
  Sits ABOVE the kicker, forming a two-line masthead. **This component is shared verbatim with the
  portfolio home and bench** — it is the single element that makes two differently-dressed sites
  read as one hand. It wears the LOCAL accent (rubric here, teal there). The name is exactly
  `Ammar Nawawi`, matching the CV; an identical byline that isn't identical is worse than none.

## The estate — ONE ACCENT PER SURFACE (2026-07-14)

The portfolio (`portfolio.amohdnaw.xyz`) was reworked to white paper + **teal** + Manrope +
lowercase first-person prose. **These studies were NOT retheming to match, and must not be.**

A teal recolour was mocked in full and rejected:

- **Red here is rhetoric, not decoration.** The verdict box is an indictment; `−$2,548` and
  `−27.7%` are damages. In teal the verdict reads as a friendly info callout and the damages read
  as neutral statistics — while the chart bars beside them stay red for the same meaning. The
  document ends up saying "bad" in two colours, which is worse than either choice alone.
- **Measured:** teal on cream is **4.57:1**; rubric red is **7.2:1**. Cooler *and* fainter.
- **A case study is a document.** Serif body at a reading measure, mono apparatus, sentence-case
  formal voice, verdict up front, print-friendly — that is what makes it read as research rather
  than a blog post about research. It is the credibility artifact the CV points at. Do not set a
  statistical audit in lowercase Manrope.

The rule is **one accent per surface, not one accent per person**. Teal owns the personal site;
rubric red owns the papers. The estate is unified by the **spine** — the byline, the mono
apparatus, the kicker grammar, the radius rule — never by the hue.

## Rules

- Radius: **0 everywhere** — everything on the page touches the sheet (house radius rule:
  rounded only floats free; nothing here floats).
- Shadows: none. Depth = rules and paper tones only.
- Ban list: dark mode, gradients (except the ruled-line repeating gradient), emoji as icons,
  glassmorphism, border-radius, drop shadows, system-default sans as body, hero-with-cards
  layouts, more than one accent hue.
- Print must work: paper palette is already print-safe; no fixed elements.

## Corrections

Screenshot critiques are judged against this doc. A correction updates this file, not just
the instance.
