#!/usr/bin/env python3
"""Social pre-check: queued posts against SOCIAL.md and the registry. Standard library only.

Muse runs this on queued posts before scheduling. It reads the same
`.github/registry.json` the site's registry check uses, so the site and social
share one source for exact strings.

Usage:
  python3 social_check.py --registry registry.json posts.json [--strict]
  python3 social_check.py --registry registry.json --text "caption" [--platform pinterest --lang en --link URL --cta]

posts.json is a list (or {"posts": [...]}) of objects:
  id, platform (facebook|instagram|threads|pinterest|youtube|tiktok),
  lang (en|es, default en), text (caption or description), title (optional,
  e.g. pin title), image_text (words printed on the graphic, optional),
  alt (alt text, optional), link (optional), cta (true/false, WDG),
  promotes (true/false, Mitothrum: mentions a product or links product pages),
  has_image, has_video, ai_imagery, ai_label, platform_label (true/false).

Findings: violation (must fix), review (a person decides), exception (allowed).
Exit 1 with --strict if any violation. The site is detected from the registry.
A pass means the detectable rules passed; it never replaces reading the post.
"""
import argparse, json, re, sys, unicodedata
from urllib.parse import urlparse, parse_qs

PLATFORMS = {"facebook", "instagram", "threads", "pinterest", "youtube", "tiktok"}


def norm(t):
    return re.sub(r"\s+", " ", (t or "")).strip()


def first_line(t):
    for ln in (t or "").splitlines():
        if ln.strip():
            return ln.strip()
    return ""


def negated(text, start):
    before = text[max(0, start - 60):start]
    return bool(re.search(r"\b(?:never|not|no|don[’']t|doesn[’']t|isn[’']t|aren[’']t|haven[’']t|won[’']t|without|nunca|sin)\b[^.]{0,40}$", before, re.I))


class Report:
    def __init__(self):
        self.rows = []

    def add(self, kind, rule, pid, field, text):
        self.rows.append((kind, rule, pid, field, norm(text)[:180]))


def check_common(p, R, rep, site_domain, other_domain, platforms):
    pid = str(p.get("id", "?"))
    plat = (p.get("platform") or "").lower()
    text = p.get("text") or ""
    if plat not in platforms:
        rep.add("violation", "SOC-PLATFORM", pid, "platform", f"unknown platform '{plat}'")
    # links
    link = p.get("link") or ""
    links = [link] if link else []
    links += re.findall(r"https?://\S+", text)
    for u in links:
        host = urlparse(u).netloc.lower().removeprefix("www.")
        if other_domain and other_domain in host:
            rep.add("violation", "GLOBAL-LINKS", pid, "link", f"links the other site: {u}")
            continue
        if site_domain in host:
            q = parse_qs(urlparse(u).query)
            if q.get("utm_medium", [""])[0] != "social" or q.get("utm_source", [""])[0] not in platforms or not q.get("utm_campaign"):
                rep.add("violation", "SOC-UTM", pid, "link", f"missing or wrong UTM tags (need utm_source=<platform>&utm_medium=social&utm_campaign=<topic>): {u}")
            elif q.get("utm_source", [""])[0] != plat:
                rep.add("violation", "SOC-UTM", pid, "link", f"utm_source is '{q['utm_source'][0]}' but the post is on {plat}")
    # accessibility
    cap = text.strip()
    if cap:
        ch = cap[0]
        if unicodedata.category(ch) == "So":
            rep.add("violation", "SOC-A11Y", pid, "text", "caption starts with an emoji")
        for sen in re.split(r"(?<=[.!?])\s+|\n+", cap):
            words = [w for w in re.findall(r"[^\W\d_]{2,}", sen)]
            if len(words) >= 3 and all(w.isupper() for w in words):
                rep.add("violation", "SOC-A11Y", pid, "text", "all-caps sentence in the caption (use sentence case): " + sen[:80])
                break
        if re.search(r"([\U0001F300-\U0001FAFF☀-➿])\1", cap):
            rep.add("violation", "SOC-A11Y", pid, "text", "the same emoji repeated in a row")
        for tag in re.findall(r"#(\w{7,})", cap):
            if tag.islower() and tag.lower() not in {"ad"}:
                rep.add("review", "SOC-A11Y", pid, "text", f"#{tag}: use capitalised words (#LikeThis) so screen readers can split it")
    if p.get("has_image"):
        alt = norm(p.get("alt"))
        if not alt:
            rep.add("violation", "SOC-A11Y", pid, "alt", "image post without custom alt text")
        elif alt == norm(text):
            rep.add("violation", "SOC-A11Y", pid, "alt", "alt text is the caption pasted in")
        elif re.match(r"(?i)may be an image of", alt):
            rep.add("violation", "SOC-A11Y", pid, "alt", "platform auto-alt text; write our own")
        img = norm(p.get("image_text"))
        if img and alt and img.lower() not in alt.lower():
            rep.add("review", "SOC-A11Y", pid, "alt", "alt text should include every word printed on the image")
    if p.get("has_video") and not cap:
        rep.add("violation", "SOC-A11Y", pid, "text", "video post needs a caption carrying its key point")
    if p.get("ai_imagery") and not p.get("ai_label"):
        rep.add("violation", "SOC-AI-LABEL", pid, "ai_label", "realistic AI imagery without the platform's AI label")


def check_wdg(p, R, rep):
    S = R["strings"]; soc = R.get("social", {})
    pid = str(p.get("id", "?")); lang = (p.get("lang") or "en").lower()
    fields = {k: p.get(k) or "" for k in ("text", "title", "image_text", "alt")}
    allow = [e["text"] for e in R.get("allowlist_exact", {}).get("entries", []) if e.get("text")]
    epa = S["EPA_MOLD_ES" if lang == "es" else "EPA_MOLD_EN"]["text"]
    banned = [
        (r"\b(?:our|nuestro|nuestros)\s+(?:team|crew|technicians|equipo|técnicos)\b|\bcrew\b", "SOC-WDG-FRAMING", "violation"),
        (r"\btrusted\b|\bvetted\b|\bde confianza\b|\bverificados?\b", "SOC-WDG-FRAMING", "violation"),
        (r"\bguarantee[sd]?\b|\bgarantiza(?:mos|do)?\b", "SOC-WDG-FRAMING", "violation"),
        (r"\blicensed\s*(?:&|&amp;|and)\s*insured\b", "WDG-IDENTITY", "violation"),
        (r"\bsame[- ]day\b|\bmismo d[ií]a\b|\bevery minute counts\b|\bcada minuto cuenta\b|\bhead start\b|\bdando ventaja\b|\bbefore it[’']s too late\b|\bantes de que sea demasiado tarde\b", "WDG-CLAIMS", "violation"),
        (r"\b(?:designed|built|made|intended) for (?:urgent|emergency|emergencies)\b|\bpara situaciones urgentes\b", "WDG-CLAIMS", "violation"),
        (r"\bnear me\b|\bcerca de m[ií]\b", "SEO-WRITING", "violation"),
        (r"\$\s?\d", "WDG-CLAIMS", "violation"),
        (r"\b(?:reviews?|testimonials?|ratings?|stars?|reseñas?|testimonios?)\b", "WDG-CLAIMS", "review"),
        (r"\bright now\b|\bahora mismo\b", "WDG-CLAIMS", "violation"),
        (r"\bfast\b|\bquick(?:ly)?\b|\br[aá]pid[oa]\b", "WDG-CLAIMS", "review"),
    ]
    for f, t in fields.items():
        if not t:
            continue
        # phone hold: no phone number at all in social
        for m in re.finditer(r"\(?\b\d{3}\)?[\s.\-]?\d{3}[\s.\-]\d{4}\b|tel:", t):
            rep.add("violation", "SOC-WDG-PHONE", pid, f, f"phone number in a social post (phone hold): {m.group()}")
        for m in re.finditer(r"24\s*/\s*7|24 horas", t):
            ctx = t[max(0, m.start() - 120): m.end() + 120]
            if re.search(r"county|condado", ctx, re.I):
                rep.add("exception", "WDG-CLAIMS", pid, f, "24/7 named as the county's line")
            else:
                rep.add("violation", "WDG-CLAIMS", pid, f, "24/7 not tied to the county's line: " + ctx)
        for pat, rule, kind in banned:
            for m in re.finditer(pat, t, re.I):
                ctx = t[max(0, m.start() - 60): m.end() + 60]
                if kind == "violation" and any(a and a in t for a in allow) and rule == "WDG-CLAIMS" and re.match(r"(?i)right now|ahora mismo", m.group()):
                    rep.add("exception", rule, pid, f, "approved safety phrase: " + ctx); continue
                if negated(t, m.start()):
                    rep.add("exception", rule, pid, f, "negated: " + ctx); continue
                rep.add(kind, rule, pid, f, ctx)
        # EPA mold timing: exact quote only; in titles and image text, leave it out
        for m in re.finditer(r"(?:24\s*(?:-|–|to|a)\s*48|48)\s*(?:hours|horas|hrs?)", t, re.I):
            if f in ("title", "image_text"):
                rep.add("violation", "WDG-CLAIMS", pid, f, "mold-timing claim in a title or on the graphic; leave it out where the exact EPA quote doesn't fit")
            elif epa not in t:
                rep.add("violation", "WDG-CLAIMS", pid, f, "mold timing not in EPA's exact words (registry EPA_MOLD_" + lang.upper() + ")")
    # disclosure on CTA posts
    disc = soc.get("SOCIAL_DISCLOSURE_ES" if lang == "es" else "SOCIAL_DISCLOSURE_EN", {}).get("text", "")
    text = fields["text"]
    is_cta = p.get("cta")
    if is_cta is None and re.search(r"\b(?:call|reach a local provider|get connected|llame|comuníquese)\b", text, re.I):
        rep.add("review", "SOC-WDG-DISCLOSURE", pid, "text", "looks like a call to action; set cta=true/false so the disclosure rule can be applied")
    if is_cta and disc and disc not in text:
        rep.add("violation", "SOC-WDG-DISCLOSURE", pid, "text", f"call-to-action post without the exact disclosure ({'ES' if lang == 'es' else 'EN'})")
    # Spanish posts link to /es/
    link = p.get("link") or ""
    if lang == "es" and link and "/es/" not in urlparse(link).path:
        rep.add("violation", "SOC-LINK", pid, "link", "Spanish post must link to the /es/ page")


def check_mito(p, R, rep):
    soc = R.get("social", {})
    pid = str(p.get("id", "?"))
    text = p.get("text") or ""
    fields = {k: p.get(k) or "" for k in ("text", "title", "image_text", "alt")}
    banned = [
        (r"\b(?:we|i)(?:[’']ve)?\s+tested\b|\bhands-on test", "MITO-PRICES", "violation"),
        (r"\bFDA[- ]approved\b", "MITO-CLAIMS", "violation"),
        (r"\bdetox\w*\b|\bcures?\b|\bheals?\b|\btreats?\b|\btreatment\b|\bguaranteed results?\b", "MITO-CLAIMS", "violation"),
        (r"\b\d[\d,.]*\s*(?:customer\s+)?(?:reviews|ratings)\b|\b\d(?:\.\d)?\s*(?:out of 5\s*)?stars\b", "MITO-PRICES", "violation"),
        (r"(?<![\w$])\$\s?\d", "MITO-PRICES", "violation"),
        (r"\bonly \d+ left\b|\btoday only\b|\bcountdown\b|\bofficial (?:store|site)\b", "RULES-11", "violation"),
        (r"\bbefore\s*(?:/|and|&)\s*after\b", "MITO-CLAIMS", "violation"),
        (r"\bI use (?:this|it)\b", "MITO-PRICES", "review"),
    ]
    for f, t in fields.items():
        for pat, rule, kind in banned:
            for m in re.finditer(pat, t, re.I):
                ctx = t[max(0, m.start() - 60): m.end() + 60]
                if negated(t, m.start()) or re.match(r"\s*claims?", t[m.end(): m.end() + 8], re.I):
                    rep.add("exception", rule, pid, f, "negated or discussing: " + ctx); continue
                rep.add(kind, rule, pid, f, ctx)
        for u in re.findall(r"https?://\S+", t):
            if re.search(r"amazon\.|amzn\.", u):
                rep.add("violation", "SOC-MITO-LINK", pid, f, "bare Amazon link in a post; link the site page instead")
    link = p.get("link") or ""
    if re.search(r"amazon\.|amzn\.", link):
        rep.add("violation", "SOC-MITO-LINK", pid, "link", "post links straight to Amazon; link the site page instead")
    promotes = p.get("promotes")
    if promotes is None and (link or re.search(r"https?://", text)):
        rep.add("review", "SOC-MITO-DISCLOSURE", pid, "text", "has a link; set promotes=true/false so the disclosure rule can be applied")
    if promotes:
        d = soc.get("SOCIAL_DISCLOSURE_FIRST_LINE", {}).get("text", "")
        if d and not first_line(text).startswith(d):
            rep.add("violation", "SOC-MITO-DISCLOSURE", pid, "text", "disclosure must be the caption's first line, exactly")
        if not re.search(r"(?<!\w)#ad\b", text, re.I):
            rep.add("violation", "SOC-MITO-DISCLOSURE", pid, "text", "missing #ad")
        if (p.get("platform") or "").lower() in {"youtube", "tiktok", "instagram", "facebook"} and not p.get("platform_label"):
            rep.add("violation", "SOC-MITO-DISCLOSURE", pid, "platform_label", "turn on the platform's paid-promotion label")
        if (p.get("platform") or "").lower() == "pinterest" and d and d not in text:
            rep.add("violation", "SOC-MITO-DISCLOSURE", pid, "text", "pin description itself must carry the disclosure")
    tags = re.findall(r"#\w+", text)
    if len([t for t in tags if t.lower() != "#ad"]) > 3:
        rep.add("violation", "SOC-A11Y", pid, "text", "more than three hashtags")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("posts", nargs="?")
    ap.add_argument("--registry", required=True)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--text"); ap.add_argument("--title"); ap.add_argument("--platform", default="pinterest")
    ap.add_argument("--lang", default="en"); ap.add_argument("--link"); ap.add_argument("--cta", action="store_true"); ap.add_argument("--promotes", action="store_true")
    a = ap.parse_args()
    R = json.load(open(a.registry, encoding="utf-8"))
    if a.text is not None:
        posts = [{"id": "text", "platform": a.platform, "lang": a.lang, "text": a.text.replace("\\n", "\n"), "title": a.title, "link": a.link,
                  "cta": a.cta if a.cta else None, "promotes": a.promotes if a.promotes else None}]
    else:
        if not a.posts:
            ap.error("give a posts.json file or --text")
        data = json.load(open(a.posts, encoding="utf-8"))
        posts = data["posts"] if isinstance(data, dict) else data
    soc = R.get("social", {})
    site = soc.get("site")
    rep = Report()
    for p in posts:
        check_common(p, R, rep, soc.get("domain", ""), soc.get("other_domain", ""), set(soc.get("platforms", PLATFORMS)))
        if site == "wdg":
            check_wdg(p, R, rep)
        elif site == "mitothrum":
            check_mito(p, R, rep)
        else:
            rep.add("violation", "REGISTRY", "-", "registry", "registry has no social.site; add the social section")
    viol = [r for r in rep.rows if r[0] == "violation"]
    revs = [r for r in rep.rows if r[0] == "review"]
    exc = [r for r in rep.rows if r[0] == "exception"]
    print(f"## Social pre-check ({site}): {len(posts)} post(s), {len(viol)} violation(s), {len(revs)} to review, {len(exc)} approved exception(s)\n")
    if rep.rows:
        print("| Kind | Rule | Post | Field | Text |\n| --- | --- | --- | --- | --- |")
        for k, rule, pid, f, t in viol + revs + exc:
            print(f"| {k} | `{rule}` | {pid} | {f} | {t.replace('|', '/')} |")
    clean = sorted({str(p.get('id')) for p in posts} - {r[2] for r in viol + revs})
    if clean:
        print(f"\nClean: {', '.join(clean)}")
    sys.exit(1 if (a.strict and viol) else 0)


if __name__ == "__main__":
    main()
