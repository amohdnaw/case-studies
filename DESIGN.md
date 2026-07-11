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
