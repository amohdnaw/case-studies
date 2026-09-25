# Study 10, gates that pass vacuously: outcome contract

Approved 2026-09-25 ("Approve"). Source: Ammar, "start gates study" (queued in
`specs/queued-studies.md`). He picked: the three-gate chain plus an escape-rate experiment, the
Measurement systems section, counts only with a synthetic CV.

## What you will see

1. The index lists **Study 10** under Measurement systems (after 04, 07, 09), with its own
   figure-well icon, a meta line, a title, a two-sentence summary and "Read the study →". The section
   count reads "4 studies"; the standfirst, og:description and README say "Ten".
2. `docs/cv-gates.html` is one study page in the house template: byline, kicker, title, standfirst,
   a verdict box up front, prose, figures, a table, margin notes and the footnav (← index / next).
3. The story section walks the real chain with real counts and no company names:
   - no gate: a forked CV shipped 3 times without the portfolio link;
   - check 6 (CV text layer): failed correctly on the broken PDF, and could not see the cover
     letter, which carried the same missing link;
   - presence check: passed all 18 packs of 2026-09-07 while every one wrapped the contact row,
     because it rejoins lines on purpose;
   - layout check: fails at the old 9.6px, passes at 9.0px.
   Plus a short box on two more gates from the same files that lied (the stderr lint gate that could
   never pass or fail, the A4 substring check).
4. The experiment: a made-up CV and cover letter (fake name, `example.com` contacts) rendered to
   PDF, about 20 seeded defects (dropped link, each wrap size, stranded and doubled separators, text
   present but hidden, link text right but the URL wrong, cover-letter-only defects, and so on), run
   against four gate versions: none, check 6, check 6 on both files, plus the layout check.
5. A figure shows the escape matrix (defects × gate versions, caught in ink, escaped in red), and a
   table gives each version's escape rate with a Wilson 95% interval.
6. The verdict reports whatever the run shows, including any defect the final gate still misses.
   No outcome is written in advance.
7. `scripts/gates_escape.py` rebuilds every PDF and the matrix from scratch with one command, and
   the page says so. The study ships its synthetic inputs, never a real CV or pack.
8. Framing line: every gate is a gauge, and "watch it fail" validates it against one known-bad
   part; an escape rate needs a library of them.

## Not in scope

- Company names, pack names, or anything from a real application.
- Changing career-ops itself (the study reads its history; the gates are copied into the script).
- The wider catalogue of blind gates from other projects (the 404 art check, the clip audit): at
  most one sentence of them, no reproductions.
- A new og image.

## Defaults taken (approval confirms these)

- The escape rate is measured over a **designed** defect library, not sampled from the field. The
  page says so plainly and does not present it as a field miss rate.
- Title and copy are drafted by me, run through unslop, and shown to you in a screenshot before the
  push. Working title: "Every gate passed. Every CV was broken."
- Icon: three gates in a row, a red defect slipping past the last one.
- Rendering uses the same Chrome print path as career-ops (`google-chrome --print-to-pdf`).
- Commit and push publish; the push waits for your OK on the screenshots (page + index, desktop and
  phone).
- Effort: ~6-7 h, one session.
