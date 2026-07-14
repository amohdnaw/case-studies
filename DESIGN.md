# DESIGN.md — case-studies (frozen 2026-07-12, Direction A "Paper Workbench")

Anchor: `design/direction-mock.html` Direction A. Register: a working scientist's lab
notebook — quiet paper, one rubric red, serif body, mono apparatus. Derived from
`~/design-library/sites/paper-workbench.html`.

## Palette (ONE accent)

| token | value | use |
|---|---|---|
| `--paper` | `oklch(100% 0 0)` | page background — **white since 2026-07-14**, shares the portfolio's sheet |
| `--paper-deep` | `oklch(97.6% 0 0)` | figure wells, inset panels |
| `--ink` | `oklch(25% .02 65)` | body text, headings |
| `--ink-soft` | `oklch(38% .02 65)` | standfirst, captions |
| `--ink-faint` | `oklch(52% .018 70)` | margin notes, th labels |
| `--rubric` | `oklch(43% .125 29)` | THE accent: kickers, verdict borders, hits, links |
| `--wash` | `oklch(43% .125 29 / .07)` | verdict box fill |
| `--hair` | `oklch(25% .02 65 / .28)` | strong rules |
| `--hair-faint` | `oklch(25% .02 65 / .14)` | row rules |

No other hues. Charts: ink for data, rubric for the one series being argued about,
ink-faint for baselines/reference. Light theme only; print-friendly.

**Paper history:** the sheet was cream (`oklch(95.6% .017 92)`) from the v1 freeze until
2026-07-14, when it went white to bridge to the reworked portfolio. Cream was doing real work —
it said "printed thing" before you read a word, and it made the serif look chosen rather than
defaulted. It was given up deliberately, judged from a side-by-side mock, because the jump from
the (white) home page to a cream study read as two different people. The serif, the sentence
case and the rubric red are what carry the document register now. **If the pages ever start
reading like generic articles, the cream is the first thing to try putting back.**

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

## The estate — TEAL CHROME, RED ARGUMENT (revised 2026-07-14, supersedes the section below)

Two tokens now, and the split is the whole point:

| token | value | owns |
|---|---|---|
| `--accent` | `oklch(48% .085 196)` (teal) | **chrome** — links, byline, kicker, section numbers, footnav, pull-quote rule, margin-note rule |
| `--rubric` | `oklch(43% .125 29)` (red) | **the argument, and nothing else** — the verdict box (border + lead-in) and `.hit` (the damage figures) |

The rule reads in one line: **red means "this is the bad finding". Teal means "this is Ammar's
site".** Red appears nowhere else, so it never has to compete with itself — and the figures,
which have always drawn defects and losses in red, now agree with the prose instead of
contradicting it.

Contrast on the white sheet: teal **5.24:1**, rubric red **8.25:1**. Both pass; the red is
stronger, which is correct — it carries the claims.

### Why the first attempt failed (keep this, it is the reason for the split)

A *full* teal recolour — chrome AND verdict AND hits — was mocked and rejected:

- **Red here is rhetoric, not decoration.** The verdict box is an indictment; `−$2,548` and
  `−27.7%` are damages. In teal the verdict reads as a friendly info callout and the damages read
  as neutral statistics — while the chart bars beside them stay red for the same meaning. The
  document ends up saying "bad" in two colours, which is worse than either choice alone.
- **Measured (on the then-cream sheet):** teal **4.57:1**; rubric red **7.2:1**. Cooler *and*
  fainter. On the white sheet rubric red is stronger still — the argument only hardens.
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
- Print must work: white sheet is print-native; no fixed elements.

## Corrections

Screenshot critiques are judged against this doc. A correction updates this file, not just
the instance.

## Figures — the paper is baked in, twice

Figure SVGs are matplotlib exports, so the sheet colour lives in TWO places: the rendered
`docs/figures/*.svg` AND the `PAPER, PAPER_DEEP, HAIR` triple at the top of each generator
(`scripts/*.py`, `notebooks/*.ipynb`). Change one without the other and the next notebook run
silently reverts the site.

Gotcha found 2026-07-14: the creams were **not one hex**. Studies 01–03 used `#f4f0e4`; 04–05
used `#f4efe4` + `#ece5d6`. One character apart, and a naive find-and-replace catches only half
the figures — leaving cream plots sitting on a white page. Sweep by *luminance*, not by the hex
you happen to remember.
