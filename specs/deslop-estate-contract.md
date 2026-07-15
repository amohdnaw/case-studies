# Contract — De-slop the estate (2026-07-15)

Trigger: Ammar ran Impeccable's anti-pattern detector (impeccable.style, Paul Bakaus) against the
live pages and decided the flagged patterns "feel too common AI-generated." Surgical remediation —
keep the estate's identity, remove the tells. Grill gate run; Direction **A (enclosed)** picked from
`scratchpad/deslop-mock.html`.

Spans TWO repos: `~/apps/portfolio` (home + bench) and `~/projects/career/case-studies` (6 studies +
index). Same contract copied into both repos' `specs/`.

## What you will see

1. **No side-tab accent borders anywhere.** The case-study **verdict box** loses its rubric-red
   `border-left:3px` and becomes a **full hairline box (all four sides)** with a mono uppercase red
   `VERDICT` label on its own line; red still lives in that label + the `.hit` damage figures, so it
   still reads as THE indictment. The **pull-quote** loses its left border (large italic serif +
   indent instead). The **bench sim-tiles + demo cards** lose `border-left:3px solid teal` and become
   **full hairline boxes**, teal only in the title.
2. **No "01 / 02 / 03" section markers** in the case studies. The number is dropped; the heading
   stands alone. (Direction A — no scaffold, not a folio or kicker substitute.)
3. **No em-dashes in body copy**, on home, bench, and all six case studies — replaced with commas /
   colons / periods so meaning is preserved. (This aligns the estate with Ammar's own CLAUDE.md rule
   banning em-dashes as an AI tell — he had been violating it.)
4. **The bench animates `transform`, not width/height/padding** (the flagged layout-thrash perf
   finding).
5. **Re-running Impeccable's detector shows those findings gone** on bench + studies (verified the
   same way they were found: `node run-detect.mjs` in the trial dir).

## Defaults taken (approving this confirms them)

- **Home stays plain.** The `single-font` and `flat-hierarchy` findings on the home page are
  **won't-fix** — the one-Manrope, modest-scale farza-plain look is a deliberate, recruiter-validated
  v4 choice. Home changes ONLY: em-dashes removed. Its instrument rail, story, byline all untouched.
- **Direction A applied consistently** across all three devices (verdict, markers, tiles). No per-device mixing.
- **Serif stays Iowan** on the studies (the mock's Newsreader was a web-font stand-in only).
- **The estate identity is preserved** — teal/white home+bench, cream... white-paper/serif/rubric-red
  studies, the shared byline spine, red = argument. Nothing structural moves.

## Not in scope

- The home page's plainness (see Defaults).
- `/drive`, `/lab` — the 3D worlds; and `/lab`'s notebook already de-slopped separately.
- The "technically also flagged" items Ammar chose NOT to chase (repeated-section-kickers,
  aphoristic-cadence copy) — surgical scope covers the detector's *warnings* on the load-bearing
  devices + em-dashes + the perf finding, not the estate's whole voice.
- Installing Impeccable or its hooks. The detector is used as a one-off external advisory only.

## Files

- Portfolio: `bench.html` (tile borders + layout-anim + em-dashes), `index.html` (em-dashes only),
  `DESIGN.md` (record: no side-tabs, em-dash ban applies to page copy too). Deploy = `cp` to `public/`.
- Case studies: all six `docs/*.html` (verdict box + pull-quote + section markers + em-dashes),
  `DESIGN.md` (record the verdict-box + marker change). Commit + push (GitHub Pages).

## Diagram

N/A — pure visual de-slop, no system/data-flow change. The mock + this contract are the artifacts.

## Verification

Per-repo browser screenshots (verdict box, a section heading, a bench tile) before "done"; re-run
the Impeccable detector on the changed pages and confirm side-tab / numbered-markers / em-dash
findings are gone; confirm the verdict still reads as the verdict and red still marks the argument.
Fetch the served case-study pages after the Pages push (not just local files).
