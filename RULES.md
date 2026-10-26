# Water Damage Gwinnett rules

The rules every page and change on waterdamagegwinnett.com must follow, and why.
The weekly research loop (`.github/workflows/research.yml`) watches the sources
below and opens an issue, plus a pull request revising this file when an API key
is set, whenever one of them changes. Rules marked **[auto]** are enforced by the
daily site monitor (`.github/workflows/monitor.yml`).

**Last reviewed:** October 21, 2026
**Operator:** Guardian Bridge LLC (d/b/a Water Damage Gwinnett)
**Goal:** earn per-call fees by connecting people with water damage to local
providers, honestly and lawfully. When a revenue idea conflicts with a rule, the rule wins.

## 1. Honesty about what the site is
- 1.1 **[auto]** Every page says the site may be paid a fee for each call by participating providers or call networks, and that routing is by location and availability, not quality (English or Spanish). *Source: FTC Endorsement Guides FAQ (material connections).*
- 1.2 The site never claims to be a contractor, to do the work, to hold licenses or insurance, or to guarantee response times.
- 1.3 No reviews, ratings, testimonials, badges or certifications unless they are real and belong to us. Photos of people are disclosed as models. *Source: FTC rule on fake reviews.*
- 1.4 Change "may be paid" to "are paid" once per-call payments start.

## 2. Calls, texts and consent
- 2.1 **[auto]** Only approved phone numbers appear: the routing number and the county emergency line. Update the monitor's `ALLOWED_PHONES` when the routing number changes.
- 2.2 A recording disclosure plays before any call is connected.
- 2.3 Callers' numbers are used only for their service request. No marketing calls or texts without prior express written consent. *Source: FCC robocalls and texts guide (TCPA).*
- 2.4 Only caller-initiated inbound calls from approved sources: no incentivized, SMS, ringless voicemail, spoofed or offshore traffic. *Source: BrokerCalls insertion order (if signed).*
- 2.5 Before sending calls to any network, get written approval of this site and its content. *Source: BrokerCalls agreement section 9.8 (if signed).*
- 2.6 Invoice the network monthly, within 90 days of month end, or the calls are forfeited. *Source: BrokerCalls agreement section 4.3 (if signed).* The invoice reminder workflow opens an issue on the 1st.

## 3. Google
- 3.1 City pages must each carry real, verified local information (utility, housing stock, local risks, ZIPs), never template copies that differ only by city name. *Source: Google spam policies (doorway abuse, scaled content abuse).*
- 3.2 Do not create a Google Business Profile for this referral business, and do not mark the site up as a local business with an address. *Source: Google Business Profile guidelines.*
- 3.3 Structured data describes an Organization (referral service), not a contractor.
- 3.4 Check Google Ads' current verification requirements for this category before running ads; ads must not imply we do the work.
- 3.5 One canonical host (no `www`), hreflang between English and Spanish pages, sitemap with dates.

## 4. Safety information
- 4.1 Life-safety guidance comes first: call 911 for immediate danger; don't enter standing water near electricity.
- 4.2 Third-party numbers (like the county 24/7 line, 678-376-7000) are verified against the official source; the research loop watches the county contact page.
- 4.3 Health statements about mold are cited (EPA) and never diagnostic.

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

## Changelog
- 2026-10-26: 8.7 widened to all four social profiles; social playbook moved to SOCIAL.md.
- 2026-10-21: Added growth and trust rules from verified research.
- 2026-10-20: First version, distilled from the October 2026 audit, the BrokerCalls agreement review and research.
