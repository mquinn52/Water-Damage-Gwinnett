# Water Damage Gwinnett — working notes for Claude

Referral and call-routing site (https://waterdamagegwinnett.com), English and
Spanish (/es/). Operated by Guardian Bridge LLC; owner Matthew Quinn. Static
HTML, no build step. Not a contractor; earns per-call fees once a call network
is signed.

## Read first
- `RULES.md` — compliance and growth rules, each tied to a source. Follow it;
  when a revenue idea conflicts with a rule, the rule wins.
- `SOCIAL.md` — social playbook (Facebook, Instagram, Threads, Pinterest):
  framing, disclosure, destinations, UTM tags, pillars, cadence. Read before
  drafting any post or social-linked page.

## How changes go live
- Push to `main` → `.github/workflows/deploy.yml` uploads to GoDaddy over FTPS
  (secrets FTP_SERVER = cPanel shared IP, FTP_USERNAME, FTP_PASSWORD) into
  `public_html`, which is this site's folder (the FTP account is rooted there,
  `server-dir: ./`). Commits touching only research/, RULES.md, CLAUDE.md or
  .github/ don't deploy.
- `public_html/mitothrum.com/` is the mitothrum.com site (separate repo:
  mquinn52/Mitothrum, its own FTP account). Never deploy into or change that
  subfolder from here. (Corrected Oct 23, 2026 from a server inventory — an
  earlier note had the layout reversed.)
- Never upload or extract zips on the server by hand: on Oct 23, 2026 that
  left mitothrum.com's pages at mode 0660 and the site returned 403 everywhere.
- `FTP inspect` (manual workflow) lists the server folder and can move files
  into `_to_delete/` for the owner to delete in cPanel. It never deletes.
- Every English page has a Spanish twin in /es/ with hreflang; change both.

## Automation already running
- `registry-check.yml` on every PR and push to main: `.github/scripts/registry_check.py`
  checks every page against `.github/registry.json` and the RULES.md rule cards,
  naming the rule ID, file, text and whether it's a violation or an approved
  exception. Strict and required on `main` since Nov 1, 2026: a violation blocks
  the merge. Planning baseline: Business Models v9 (Side Hustle Project).
- `monitor.yml` daily 7 a.m. ET and after each deploy: payment disclosure on
  every page (EN or ES), only allowed phone numbers, every live sitemap URL
  loads and matches the repo; opens/closes `site-monitor` issues.
- `research.yml` Mondays: snapshots policy sources in `research/sources.json`
  (Google, Business Profile guidelines, Federal Register FTC/FCC feeds,
  Gwinnett water contact page); saves snapshots on the `research-snapshots` branch (main
  requires the Registry check, which blocks the bot's direct pushes), and opens
  a `research` issue on change.
- `invoice-reminder.yml` on the 1st: 90-day invoicing deadline issue.

## Hard rules (details in RULES.md)
- Footer disclosure (EN/ES): "may be paid a fee for each call … routed based on
  location and availability, not a ranking of quality." Exact EN/ES text lives
  in `.github/registry.json`. The first paid call triggers a wording review
  (RULES.md 1.4), not an automatic switch to "are paid."
- Allowed phone numbers: +16788330791 (routing) and +16783767000 (Gwinnett
  County 24/7 water emergency line, verified on the county site). Update
  ALLOWED_PHONES in monitor.yml when the routing number changes.
- No Google Business Profile; structured data stays `Organization`.
- City pages need verified local facts, never template copies.
- The homepage is the Gwinnett County hub; Lawrenceville has its own city page
  (lawrenceville.html, es/lawrenceville.html) since Oct 31, 2026. Service pages
  target Gwinnett County, not one city. Footer "Lawrenceville" links go to the
  city page, not "/".
- City pages each carry a "Drainage and Stormwater Resources" section linking
  the city's own page. Never add municipal phone numbers (the monitor allows
  only the routing and county numbers); link the official page instead, and
  date any infrastructure figure.
- gwinnett-county-flood-maps.html (EN/ES) is the county flood-map guide; it
  never states a property's flood risk.

## Open items (as of 2026-10-21)
- BrokerCalls insertion order and agreement (unsigned; owner is consulting a
  lawyer about the personal guaranty and uncapped indemnity). If signed: get
  written approval of the site (section 9.8), swap in their tracking number on
  all 46 pages, update the privacy policy's call vendor and recording terms,
  and update ALLOWED_PHONES.
- Strengthen each city page with one or two verified local facts.

## Environment notes
- The web-fetch tool may serve stale copies of pages; verify live changes with
  a cache-busting query (?v=…) or ask the owner to check in a private window.
