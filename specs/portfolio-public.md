# Spec — Portfolio site goes public + case-studies section

Status: DEFERRED (decision 2026-07-12: CV links point at the case-studies GitHub Pages until
this executes). Parent contract: `portfolio-evidence-contract.md`.

## Goal

The personal portfolio (`~/apps/portfolio/index.html`, currently localhost:1995 via manual
`python http.server`) becomes publicly reachable and gains a case-studies section linking to
the three studies.

## Open decision for Ammar at execution time (one AskUserQuestion)

Hosting: **GitHub Pages** (static, zero new services — recommended) vs **CF tunnel
subdomain** on amohdnaw.xyz (consistent domain, but adds a permanent service + systemd unit
to a fleet the 2026-07-12 strategic review said to shrink).

## Pre-publish scrub (mandatory, in order)

1. Remove/relocate from the served tree: `index_backup_*.html` (5+ stale copies),
   `cv-*.pdf` (CVs contain phone/address — decide per file), `screenshots/` (review contents).
2. Grep the remaining HTML for phone numbers, home address, employer name — the portfolio may
   name the employer only in CV-standard "experience" terms, never linked to the case-study
   content (studies keep the OSAT descriptor).
3. If Git history will be published (GitHub Pages route), init a FRESH repo for the portfolio
   — do not publish the existing dir's history without the same scrub applied historically.

## Case-studies section

- Design: follow the portfolio's own `design-system.md` (Nothing style) — NOT the case-studies
  Paper Workbench. The section is a portfolio component linking out; the studies keep their
  own register.
- Content: three entries mirroring `docs/index.html` titles + one-line summaries, linking to
  the live case-studies URLs. Mark 02/03 forthcoming until they ship.
- New composition on an existing page → per house rules this needs a quick mock (single page,
  2–3 labeled variants) before building. Small scope: section only, not a redesign.

## Acceptance checks

1. Public URL loads the portfolio; case-studies section visible with working links.
2. No backup files, CV PDFs, or personal identifiers reachable under the public root.
3. CV updated to point at the portfolio URL (this is the moment the "CV re-pointing"
   exclusion from the parent contract lifts).
4. Browser-verified: desktop + mobile, screenshots, before "done".

## Addendum 2026-07-12 (post-overhaul)

- The overhauled portfolio's Live Data section + terminal use BOTH relative `/api/spc-demo`,
  `/api/msa-demo` routes (need the fronting proxy to route them to the SPC/MSA apps) AND an
  absolute `https://spc.amohdnaw.xyz/api/demo` fetch (needs CORS allow for the portfolio
  origin). Hosting choice must satisfy both, or the section falls back to sample data.
- Portfolio is now a git repo (~/apps/portfolio, main) — publishing = push this repo, no scrub
  of backups needed if only index.html + assets are deployed (backups/CVs excluded via the
  deploy path, or scrub per §Pre-publish above).
- CV prints portfolio.amohdnaw.xyz — currently dead. This spec is what makes it live.

## EXECUTED 2026-07-12

Discovery: the chain already existed — CF DNS (proxied) → pvek8 tunnel → Kubuntu nginx
`static-dashboards` site (:1995), including `/api/spc-demo` + `/api/msa-demo` proxy locations.
The "domain dead" note was stale.

Done: nginx root re-pointed working-dir → `~/apps/portfolio/public/` (index.html + CV only;
config backed up as static-dashboards.bak-20260712); exposure of .git/backups/specs verified
CLOSED (404s). CORS for the portfolio origin added to spc-api + msa-api (.env CORS_ORIGINS,
both restarted) — Bench fetches are absolute now, so the page works from ANY host. GitHub
Pages mirror also exists (amohdnaw/portfolio-site, 3 files, custom domain claimed) — redundant
standby; DNS currently rides the tunnel path.

**Deploy flow from now on: edit ~/apps/portfolio/index.html → commit → `cp index.html public/`.**
CV re-pointing exclusion lifted: CV already prints portfolio.amohdnaw.xyz, which is now live.
