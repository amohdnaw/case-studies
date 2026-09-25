# Index sections and study icons: outcome contract

Approved 2026-09-25. Source: Ammar, "need to have a better categorization and follow the way we put
icons on showcasing the projects". He picked: 4 sections keeping the numbers, one icon per study,
**C · figure-well squares** (`specs/index-sections-mock.png`, right column).

## What you will see

1. `docs/index.html` groups the nine studies under four section headings, in this order:
   - **Process control**: 02, 06, 08
   - **Measurement systems**: 04, 07, 09
   - **Yield and defects**: 03
   - **Research honesty**: 01, 05
   Each heading is a mono teal label with "N studies" on the right, a hair rule, then one italic line
   saying what the section asks.
2. Study numbers and URLs are unchanged. Inside a section, studies run in number order. Each row keeps
   its meta line, title, summary and "Read the study →".
3. Every study row has a 56px square icon on its left: paper-deep well, hair border, radius 0, ink
   marks, red only on the finding, teal only on the answer. Each draws its own study:
   - 01: a tall result bar, dashed and struck through in red, beside a short one.
   - 02: a narrow and a wide bell between spec lines, the wide one's tail in red.
   - 03: Pareto bars with the third bar in red (the one worth fixing).
   - 04: a gauge dial with two red ticks pulling opposite ways.
   - 05: a fan of faint strategy lines ending below one teal buy-and-hold line.
   - 06: a wall of small charts with three red alarm dots.
   - 07: a camera with a κ mark.
   - 08: three curves racing to a dashed red limit, the teal one (CUSUM) first.
   - 09: seven venue dots on a line: two teal (qualify), one ink (fails), four red (counterfeits). Corrected at build from "three teal"; the study says two qualify.
4. Hovering a row, or scrolling it into view once, redraws the icon's mark (under 1.5 s). With reduced
   motion the icons stay still.
5. The standfirst says "Nine studies" and no longer lists every study (the sections do that now).
   og:description and README.md say nine too.
6. Phone and 320px: icon drops to 44px, no horizontal scroll. Print still shows the icons.
7. DESIGN.md gains an "Index icons" rule describing item 3.

## Not in scope

- Writing any new study. The three queued ones (preregistered trade test, machine identity at scale,
  gates that pass vacuously) go to `specs/queued-studies.md`, each with its own grill later.
- Renumbering, study pages, footnav order.
- A new og image (the current one predates 09; flagged, not redone).

## Defaults taken (approval confirms these)

- Section names and their italic lines are drafts, run through unslop, and shown to you in the
  build screenshot.
- Yield and defects has one study for now; it stays its own section rather than merging.
- Commit and push publish via GitHub Pages; the push waits for your OK on the screenshot.
