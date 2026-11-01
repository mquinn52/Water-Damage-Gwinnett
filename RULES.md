# Water Damage Gwinnett rules

The rules every page and change on waterdamagegwinnett.com must follow, and why.
The weekly research loop (`.github/workflows/research.yml`) watches the sources
below and opens an issue, plus a pull request revising this file when an API key
is set, whenever one of them changes. Rules marked **[auto]** are enforced by the
daily site monitor (`.github/workflows/monitor.yml`).

**Last reviewed:** October 31, 2026 (v2.1 structure)
**Operator:** Guardian Bridge LLC (d/b/a Water Damage Gwinnett)
**Goal:** earn per-call fees by connecting people with water damage to local
providers, honestly and lawfully. When a revenue idea conflicts with a rule, the rule wins.

## 0. Authority, rule language and records (added 2026-10-31, v2.1)
Matthew approved this structure on Oct 31, 2026 (Project Guidelines v2.1). Section
numbers below are unchanged; rule IDs sit beside them so existing citations still resolve.

- 0.1 `GLOBAL-AUTHORITY` Order of authority, highest first: (1) law, signed contracts, network terms and platform policies; (2) this file, as amended by Matthew's decisions; (3) `SOCIAL.md`; (4) the Project Guidelines; (5) `CLAUDE.md`, Muse briefs and workflows; (6) outside AI advice. A lower source never weakens a higher one. Matthew's explicit task-specific decisions take effect immediately when they're compatible with law and binding external obligations; an un-updated file is never a reason to refuse one. One-time approvals are recorded in the relevant task, issue or PR and don't amend a standing rule. When Matthew changes a standing rule or business policy, Claude logs it in the handoff doc and opens a PR amending this file the same day. On a conflict: stop the affected action, quote both rules, propose the smallest fix, and wait for Matthew when it touches compliance, money, publishing or a contract.
- 0.2 Rule language: **MUST** (required), **MUST NOT** (prohibited), **SHOULD** (default; an exception needs a stated reason), **MAY** (permitted, subject to every other rule).
- 0.3 Evidence labels: [VERIFIED] (checked against a primary source or this repo, source named), [VENDOR] (supplied by a network, not independently checked), [ESTIMATE] (stated assumptions), [OPINION], [UNVERIFIED] (never published or asserted as fact).
- 0.4 `WDG-REGISTRY` Exact phone numbers, disclosures, the home-services disclaimer and the EPA sentence live in `.github/registry.json`. Ownership: this file owns the policy and conditions; the registry owns the exact approved text; pages, templates and monitors use the registry's strings, and any mismatch between registry text and a page fails validation (enforced from PR 3). A wording change updates the registry and every page in the same PR.
- 0.5 `GLOBAL-RECORDS` While the site number is Lead Smart's, Lead Smart reporting is the record for calls received, qualified and paid. GA4 `click_to_call` counts taps, not calls. Search Console measures visibility, not money. Ringba routes no calls today and is not a record (see 9.16 for the Marketcall case).
- 0.6 `GLOBAL-PR` Every change: inspect (this file, the pages, their recent PRs, open monitor issues) → propose scope → Matthew approves → smallest change → run checks → review the whole diff → open the PR → after Matthew merges, verify production. Approving a scope is not approving the merge.
- 0.7 `GLOBAL-RETIRE` Retiring a public URL needs Matthew's approval, a link check, a 301 or 410, a sitemap update and the Spanish twin handled the same way. Never by deleting files on the server.
- 0.8 `GLOBAL-DATES` Populate `datePublished` only from reliable publication or deployment records; a Git commit date alone never establishes it, and an unknown date is omitted, never invented. `dateModified` changes only with a material revision. Never change a date to look fresher.
- 0.9 `GLOBAL-LINKS` This site MUST NOT link to mitothrum.com or receive links from it.

## 1. Honesty about what the site is `WDG-IDENTITY` `WDG-DISCLOSURE`
- 1.1 **[auto]** Every page says the site may be paid a fee for each call by participating providers or call networks, and that routing is by location and availability, not quality (English or Spanish). *Source: FTC Endorsement Guides FAQ (material connections).*
- 1.2 The site never claims to be a contractor, to do the work, to hold licenses or insurance, or to guarantee response times.
- 1.3 No reviews, ratings, testimonials, badges or certifications unless they are real and belong to us. Photos of people are disclosed as models. *Source: FTC rule on fake reviews.*
- 1.4 The first paid call in Lead Smart reporting triggers a wording review, not an automatic swap: Claude checks which calls actually earn a fee and the network-approved language, then proposes exact English and Spanish text (registry `FEE_DISCLOSURE_EN/ES`); Matthew approves and merges.

## 2. Calls, texts and consent `WDG-PHONES`
- 2.1 **[auto]** Only approved phone numbers appear: the routing number and the county emergency line. Update the monitor's `ALLOWED_PHONES` when the routing number changes.
- 2.2 A recording disclosure plays before any call is connected.
- 2.3 Callers' numbers are used only for their service request. No marketing calls or texts without prior express written consent. *Source: FCC robocalls and texts guide (TCPA).*
- 2.4 Only caller-initiated inbound calls from approved sources: no incentivized, SMS, ringless voicemail, spoofed or offshore traffic. *Source: BrokerCalls insertion order (if signed).*
- 2.5 Before sending calls to any network, get written approval of this site and its content. *Source: BrokerCalls agreement section 9.8 (if signed).*
- 2.6 Invoice the network monthly, within 90 days of month end, or the calls are forfeited. *Source: BrokerCalls agreement section 4.3 (if signed).* The invoice reminder workflow opens an issue on the 1st.

## 3. Google and search `WDG-PAGES`
- 3.1 City pages must each carry real, verified local information (utility, housing stock, local risks, ZIPs), never template copies that differ only by city name. *Source: Google spam policies (doorway abuse, scaled content abuse).*
- 3.2 Do not create a Google Business Profile for this referral business, and do not mark the site up as a local business with an address. *Source: Google Business Profile guidelines.*
- 3.3 Structured data describes an Organization (referral service), not a contractor.
- 3.4 Check Google Ads' current verification requirements for this category before running ads; ads must not imply we do the work.
- 3.5 One canonical host (no `www`), hreflang between English and Spanish pages, sitemap with dates.
- 3.6 `SEO-THRESHOLDS` A CTR-based title or meta rewrite starts only after 50 impressions over a rolling 90 days, read at the URL and query-group level against the previous period. That is a review trigger, not proof. Diagnose by query: average position blends many queries, so never read it as a page number. A title that is inaccurate, misleading or breaks a rule is fixed regardless of volume.
- 3.7 Bilingual parity: every Spanish twin carries the same facts, limits, disclosures and call to action, and never adds a claim the English page couldn't make.

## 4. Safety information `WDG-CLAIMS`
- 4.1 Life-safety guidance comes first: call 911 for immediate danger; don't enter standing water near electricity.
- 4.2 Third-party numbers (like the county 24/7 line, 678-376-7000) are verified against the official source; the research loop watches the county contact page.
- 4.3 Health statements about mold are cited (EPA) and never diagnostic. Mold timing uses only the registry's `EPA_MOLD_EN` sentence, verbatim, with the EPA source linked. Exceptions to the banned-language rules are exact and narrow (registry `allowlist_phrases`); an exception never licenses a similar claim.

## 5. Privacy
- 5.1 The privacy policy names every tracker and vendor (currently Google Analytics 4 and the call-routing platform) and is updated before a vendor changes, including a switch to a new call network's tracking.
- 5.2 Analytics loads only if the visitor hasn't opted out (Global Privacy Control or the privacy page button).
- 5.3 The mold quiz stays in the browser and collects nothing.

## 6. Copyright
- 6.1 Images are licensed (currently Pexels) or our own; keep credits where the site lists them.

## 7. Growth priorities (revisit monthly)
1. Get written network approval, then switch to the network's tracking number.
2. Strengthen city pages with one or two verified local facts each.
3. Submit the sitemap in Search Console and request indexing of key pages.
4. Spanish pages kept in step with English ones.

## 8. Growth and trust (added 2026-10-21)
- 8.1 Publish freeze-season help (English and Spanish) before the first hard freeze each year: find the main shutoff valve, protect pipes, the first hour after a burst. Link the county's own guidance rather than restating it.
- 8.2 Add a "How this service works" page (English and Spanish): the referral model, the per-call fee, that we're not a contractor and not the county, and what happens when someone calls.
- 8.3 Never use county seals or imply a county or contractor affiliation. *Source: FTC Government and Business Impersonation Rule (2024); confirm against the FTC's own page before relying on details.*
- 8.4 hreflang: every page lists itself and its twin, every pair links both ways, codes en/es, absolute URLs, plus x-default. Google ignores one-way annotations. *Source: [Google: localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions).*
- 8.5 With no Business Profile allowed, earn local visibility through plain-language answers, Organization markup and mentions from genuine local partners (HOAs, libraries, community groups).
- 8.6 TCPA status: the FCC's one-to-one consent rule was vacated by the 11th Circuit in January 2025, but prior express written consent still governs automated marketing calls and texts. Keep the site inbound-call only. *Source: [Morrison Foerster summary](https://mofo.com/resources/insights/250130-eleventh-circuit-vacates-fcc-s-tcpa-one-to-one-consent-rule).*
- 8.7 Social posts (Facebook, Instagram, Threads, Pinterest): practical how-to content (shutoff valves, first steps), the same disclosure as the site, no fear-based urgency. Details in `SOCIAL.md`.

## 9. Marketcall call network (added 2026-10-29) `WDG-NETWORKS`
Account approved Oct 29, 2026 (applied Oct 13). No campaign or traffic yet: 9.1
gates both. Marketcall's offer page always overrides its help center, so re-check
the chosen offer's rules before activating it.
*Sources: [Creative Submission Rules](https://help.marketcall.com/en/article/creative-submission-rules-1rj093s/), [Sanctions](https://help.marketcall.com/en/article/sanctions-i1y27p/), [Call statuses](https://help.marketcall.com/en/article/call-statuses-axmhko/), [Ringba integration](https://help.marketcall.com/en/article/integration-with-ringba-for-payouts-1687eos/), [Appeals](https://help.marketcall.com/en/article/how-to-appeal-refused-or-non-qualified-calls-1b24thb/), [Media Transaction Services Agreement](https://promo.marketcall.net/user_media_agreement).*

### Before sending any Marketcall traffic
- 9.1 Get written answers from the account manager on: (a) SEO/organic website traffic allowed on the water-damage offer; (b) Spanish-speaking callers accepted; (c) Ringba-to-SIP routing satisfies the "Marketcall-assigned number only" rule; (d) whether a site-wide content update needs full re-approval or only the pages tied to the campaign. No traffic until all four are answered in writing.
- 9.2 Confirm the account is in Guardian Bridge LLC's name. Signing up auto-accepts the Media Transaction Services Agreement (one-way indemnity with Marketcall choosing counsel at our expense; liability capped at three months of fees; JAMS arbitration in Orange County under California law; terms change on posting). Send it to Hankins Legal with the other network agreements.
- 9.3 Get every creative approved before it runs. For SEO traffic the creative is the website URL. Approval covers the exact version submitted, so any later edit to an approved page must be resubmitted before it goes live. First violation: calls refused and the program deactivated; second: account ban.

### Page content for Marketcall-served pages
- 9.4 Add Marketcall's required home-services footer disclaimer exactly as written on the Creative Submission Rules page (site name filled in). It sits alongside rule 1.1's fee disclosure, not in place of it. Copy it from the source when the offer activates rather than from memory.
- 9.5 Homeowners only. No commercial, business, industrial, office, restaurant or multi-family service mentions; one line is enough for a rejection. Audit before submitting: Buford's "Commercial corridor runoff" and "commercial boom" lines, and "commercial dehumidifiers/air movers" wording on several pages, may need rephrasing (e.g. "professional-grade") if moderators object.
- 9.6 Show only the Marketcall-assigned tracking number, formatted (888) 555-0142, with a visible click-to-call button. No form, quiz or "text us" in place of the number. This conflicts with Lead Smart's number being site-wide; resolve via 9.1(c) before going live, then update rule 2.1 and the monitor's `ALLOWED_PHONES`.
- 9.7 No discounts, promotions, rebates, cash-back, tax credits or financing claims; no free on-site visits ("free phone quote" is the allowed form); no promises about insurance billing or claims. Documentation-for-your-claim advice is fine; "we bill your insurance" is not.
- 9.8 Dollar amounts need a cited source (our rule 1.2/no-prices stance is stricter, keep it). Warranty mentions need "Warranty terms depend on the individual provider."
- 9.9 Do not adopt Marketcall's suggested "Licensed & insured" replacement copy. It conflicts with rule 1.2: we hold no licenses and do no work.
- 9.10 "24/7" and "Same-Day" stay banned (rule 1.2 and the brand rules). If ever used on a Marketcall page, their second availability disclaimer is mandatory.
- 9.11 No impersonating real brands, no logos of others, no brand-name bidding, no fake testimonials, ratings, countdown timers, scarcity lines, fabricated screenshots or made-up badges (consistent with 1.3 and 8.3). Proofread: no unfilled `{city}`-style placeholders or broken characters.

### Traffic and operations
- 9.12 Allowed sources are only those on the offer page and approved for our campaign. Using a prohibited or unapproved source is an account ban on the first violation. Organic social posts are not an accepted source (Marketcall requires paid social ads, and paid social is out for this venture), so the social phone hold in SOCIAL.md stays in place for Marketcall.
- 9.13 Never rebroke (buy calls from third parties and resell), never run more than one Marketcall account, never send incentivized or fraud calls: each is an account ban on the first violation. Routing our own organic callers through our Ringba account is not rebroking, but confirm in writing with the account manager since Ringba also routes to other networks.
- 9.14 Keep traffic statistics (Search Console, GA4, Ringba) able to show where every call came from. Failing to provide them on request is an account ban.
- 9.15 Do not contact the advertiser directly; all questions go through the Marketcall account manager.
- 9.16 Ringba hookup: switch the Marketcall target from DID to SIP (`<marketcall number>@sip.marketcall.com`), set revenue by webhook/postback, and add Marketcall postbacks (hold and refused statuses) back to Ringba. This applies only if Marketcall goes live through Ringba; in that case Ringba becomes the record for Marketcall calls. While the Lead Smart number is on the site, 0.5 governs. (Ringba keep/cancel is still Matthew's open decision.)

### Money
- 9.17 Calls sit on HOLD (usually 7–10 days, set per offer) then auto-approve; approved calls can still be reversed after later quality, compliance or fraud review. Treat Marketcall revenue as provisional until past any dispute window.
- 9.18 Appeal refused or non-unique calls within two days of the status change (the help center also cites 7 or 3 days in places; plan to the shortest).
- 9.19 Payouts go through Tipalti (ACH, wire, PayPal or e-check) to the Guardian Bridge BlueVine account, 1–3 business days after a withdrawal request. Confirm the minimum and payout cycle on the dashboard.

## Changelog
- 2026-10-31: v2.1 structure (Project Guidelines approved by Matthew): added section 0 (authority, rule language, evidence labels, registry, records, PR workflow, page retirement, dates, cross-site ban); rule IDs beside section headings; 1.4 made a review event; 3.6 SEO thresholds and 3.7 bilingual parity added; 4.3 tied to the registry; 9.16 Ringba scoped to the Marketcall case. 0.1 separates one-time approvals from standing-rule changes; 0.4 makes the registry the owner of exact text. County line re-verified on the county contact page. No live page changes.
- 2026-10-29: Section 9 header updated: Marketcall account approved.
- 2026-10-29: Added section 9 (Marketcall rules, from its help center and signup agreement).
- 2026-10-26: 8.7 widened to all four social profiles; social playbook moved to SOCIAL.md.
- 2026-10-21: Added growth and trust rules from verified research.
- 2026-10-20: First version, distilled from the October 2026 audit, the BrokerCalls agreement review and research.
