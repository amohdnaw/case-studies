# Study 11, machine identity: outcome contract

Approved 2026-09-25 ("Approve"). Source: Ammar, "then we can do the machine identity" (queued in
`specs/queued-studies.md`). He picked: headline = testing the name-token inference, ratios only on a
synthetic replica, a new **Data integrity** section, and an experiment on whether the holdout
transfers to the blank charts.

## What you will see

1. The index gains a fifth section, **Data integrity** ("1 study"), after Measurement systems, with
   one italic line. Study 11 sits in it with its own figure-well icon. The standfirst,
   og:description and README say "Eleven".
2. `docs/machine-identity.html` is one study page in the house template (byline, kicker, verdict up
   front, prose, figures, table, margin notes, repro box, footnav in index order).
3. The real story, as ratios only: about one chart in six carries no machine ID; the machine is
   inferred from a token in the chart name; the inference is scored on the charts that do carry an ID
   (0.33% wrong, rerun on every build); inferred machines are shown beside the hard count, never
   merged into it; about a quarter of the blank charts name a machine the SPC system has no record
   of, and that stays an open question rather than a guess.
4. A short contrast paragraph: a product key guessed from the chart name agreed with the real
   column on 11.6% of charts when that column appeared, and was retired the same day.
5. The experiment: a synthetic plant (machines, charts, names with typos, missing tokens and
   sister-tool tokens) built by a fixed-seed generator. Blank IDs are assigned two ways: at random,
   and concentrated in hand-typed charts whose names are messier. Each regime runs many times.
6. A figure compares the holdout's error estimate with the true error on the blanks, per regime, and
   shows how far the estimate falls short as the name-quality gap between blank and known charts
   grows. A table gives both errors with intervals.
7. A check you could run on real data: compare name features (token present, typo rate) between
   blank and known charts; the replica shows the check flags the shifted regime and stays quiet on
   the random one.
8. The verdict reports what the runs show. No outcome is written in advance.
9. `scripts/machine_identity.py` rebuilds the synthetic plant, the runs and the figures with one
   command.
10. After the push, the portfolio home says 11 case studies (stats panel, writing list, og card).

## Not in scope

- The stop-tool funnel or any real count (machines, charts, settings, rows).
- Real machine, product or area codes, file names, paths, and the coworker named in the commits.
- The export-unit trap (an export whose rows were not the unit counted) and the two disputed master lists:
  candidates for a later Data integrity study, noted in `specs/queued-studies.md`.
- Changing anything in `~/html-dashboard`.

## Defaults taken (approval confirms these)

- Working title: "The machine was never recorded. The chart name knew." Drafted, run through unslop,
  shown in a screenshot before the push.
- Section line: "When two systems disagree about what a thing is, which one do you believe?"
- Icon: a chart tile with a blank ID slot and a teal arrow from its name label into the slot.
- The synthetic plant's size and noise rates are chosen to echo the real ratios (about one blank in
  six, sub-1% holdout error in the random regime); the page says they are chosen, not measured.
- Push waits for your OK on the screenshots. Effort ~8 h.
