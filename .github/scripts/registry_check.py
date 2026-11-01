#!/usr/bin/env python3
"""Registry check (GLOBAL-PREVALIDATION). Standard library only. No network.

Checks every page in the repository against `.github/registry.json` and the
rule cards in RULES.md, and reports each finding with its rule ID, file,
offending text, and whether it is a violation or an approved exception.

Runs on every pull request. Report-only by default: it always exits 0 and
writes its findings to the job summary and as warnings. Set STRICT=1 to make
any violation fail the run; Matthew turns that on (and makes the check
required in GitHub settings) only after a clean run.

The same file runs in both repos; the registry tells it which site it is on.
"""
import glob, html, json, os, re, sys

ROOT = os.environ.get("REPO_ROOT", ".")
STRICT = os.environ.get("STRICT", "") == "1"
REG_PATH = os.path.join(ROOT, ".github", "registry.json")
findings = []  # (kind, rule, file, text)


def add(kind, rule, f, text):
    findings.append((kind, rule, f, re.sub(r"\s+", " ", text).strip()[:200]))


def visible(s):
    s = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", s, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def norm(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t))).strip()


def jsonld(f, s):
    """Validate JSON-LD, flag banned schema types, and check FAQ text parity."""
    faqs = {}
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            d = json.loads(blk)
        except ValueError as e:
            add("violation", "GLOBAL-STRUCTURED-DATA", f, f"JSON-LD does not parse: {e}")
            continue
        stack = [d]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                t = o.get("@type")
                for bad in ("LocalBusiness", "AggregateRating", "Review"):
                    if t == bad or (isinstance(t, list) and bad in t):
                        add("violation", "STRUCTURED-DATA-TYPE", f, f"schema type {bad}")
                if t == "Question" and isinstance(o.get("acceptedAnswer"), dict):
                    faqs[norm(o.get("name", ""))] = norm(o["acceptedAnswer"].get("text", ""))
                stack.extend(o.values())
            elif isinstance(o, list):
                stack.extend(o)
    for q, a in re.findall(r"<summary>(.*?)</summary>\s*<p class=\"faq-answer\">(.*?)</p>", s, re.S):
        q, a = norm(q), norm(a)
        if q in faqs and faqs[q] != a:
            add("violation", "FAQ-PARITY", f, f"visible FAQ answer differs from schema: {q}")


def pages():
    out = sorted(glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(os.path.join(ROOT, "es", "*.html")))
    return [p for p in out if not re.match(r"google[0-9a-f]+\.html$", os.path.basename(p))]


def rel(p):
    return os.path.relpath(p, ROOT)


def blocks(s):
    """Visible text split at block boundaries, so a heading never merges with the next sentence."""
    s = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"</(?:p|h[1-6]|li|summary|div|td|th|figcaption|section|article|span)>|<br\s*/?>|(?=<p\b)", "\n", s, flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return [re.sub(r"\s+", " ", ln).strip() for ln in t.split("\n") if ln.strip()]


def sentences(lines):
    out = []
    for ln in lines:
        ln = ln.replace("EE. UU.", "EE.\u00a0UU.").replace("U.S. ", "U.S.\u00a0")
        out += re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿“\"])", ln)
    return out


# ---------- Water Damage Gwinnett ----------
def check_wdg(reg):
    S = reg["strings"]
    phones = {v["e164"] for v in reg["phones"].values() if v.get("web")}
    county = reg["phones"].get("PHONE_COUNTY", {})
    county_digits = re.sub(r"\D", "", county.get("e164", ""))[-10:]
    banned = [
        (r"\bsame[- ]day\b|\bmismo d[ií]a\b", "WDG-CLAIMS"),
        (r"\bright now\b|\bahora mismo\b", "WDG-CLAIMS"),
        (r"\bevery minute counts\b|\bcada minuto cuenta\b", "WDG-CLAIMS"),
        (r"\bhead start\b", "WDG-CLAIMS"),
        (r"\blicensed (?:&|&amp;|and) insured\b", "WDG-IDENTITY"),
        (r"\bnear me\b|\bcerca de m[ií]\b", "SEO-WRITING"),
    ]
    all_pages = pages()
    names = {rel(p) for p in all_pages}
    for p in all_pages:
        f = rel(p)
        lang = "es" if f.startswith("es" + os.sep) else "en"
        s = open(p, encoding="utf-8").read()
        v = visible(s)
        # disclosures
        if f not in ("privacy.html", "terms.html", os.path.join("es", "privacy.html"), os.path.join("es", "terms.html")):
            key = "FEE_DISCLOSURE_ES" if lang == "es" else "FEE_DISCLOSURE_EN"
            if S[key]["text"] not in v:
                add("violation", "WDG-DISCLOSURE", f, f"missing exact {key}")
            hk = "HOME_SERVICES_DISCLAIMER_ES" if lang == "es" else "HOME_SERVICES_DISCLAIMER_EN"
            if S[hk]["text"] not in v:
                add("violation", "WDG-DISCLOSURE", f, f"missing exact {hk}")
        # phones: tel: links and visible numbers
        for t in re.findall(r'href="tel:([^"]+)"', s):
            if t not in phones:
                add("violation", "WDG-PHONES", f, f"tel:{t} not in registry")
        for m in re.finditer(r"\(?\b\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}\b", v):
            d = re.sub(r"\D", "", m.group())
            if "+1" + d not in phones:
                add("violation", "WDG-PHONES", f, f"visible number {m.group()} not in registry")
        # EPA mold timing
        epa = S["EPA_MOLD_ES" if lang == "es" else "EPA_MOLD_EN"]["text"]
        for sen in sentences(blocks(s)):
            if "EPA" in sen and re.search(r"\b(24|48)\b", sen) and epa not in sen:
                add("violation", "WDG-CLAIMS", f, f"EPA timing not in the approved wording: {sen}")
        # 24/7: only the county line
        for m in re.finditer(r"24\s*/\s*7|24 horas", v):
            ctx = v[max(0, m.start() - 160): m.end() + 160]
            if county_digits and county_digits[-4:] in re.sub(r"\D", "", ctx) or re.search(r"county|condado", ctx, re.I):
                add("exception", "WDG-CLAIMS", f, "24/7 describing the county line: " + ctx[120:260])
            else:
                add("violation", "WDG-CLAIMS", f, "24/7 not tied to the county line: " + ctx[100:260])
        for pat, rule in banned:
            for m in re.finditer(pat, v, re.I):
                add("violation", rule, f, v[max(0, m.start() - 80): m.end() + 80])
        jsonld(f, s)
        # bilingual pairs
        twin = (f[3:] if lang == "es" else os.path.join("es", f))
        if twin not in names:
            add("violation", "WDG-BILINGUAL-RELEASE", f, f"no {'English' if lang == 'es' else 'Spanish'} twin ({twin})")
        else:
            href = "https://waterdamagegwinnett.com/" + (twin.replace(os.sep, "/") if lang == "en" else twin.replace(os.sep, "/"))
            if 'hreflang="' + ("es" if lang == "en" else "en") + '"' not in s:
                add("violation", "WDG-BILINGUAL-RELEASE", f, "missing hreflang to its twin")


# ---------- Mitothrum ----------
def check_mito(reg):
    S, L = reg["strings"], reg["links"]
    tag, relv = L["AMAZON_TAG"]["value"], L["AMAZON_REL"]["value"]
    group = (S["GROUP_DISCLOSURE_PLURAL"]["text"], S["GROUP_DISCLOSURE_SINGULAR"]["text"])
    core = S["NOT_MEDICAL_ADVICE"]["text"]
    banned = [
        (r"\bwe tested\b|\bwe've tested\b|\bhands-on test", "MITO-PRICES"),
        (r"\bFDA[- ]approved\b", "MITO-CLAIMS"),
        (r"\bdetox(?:es|ify|ifying)?\b", "MITO-CLAIMS"),
        (r"\b\d[\d,.]*\s*(?:customer )?(?:reviews|ratings)\b|\b\d(?:\.\d)?\s*(?:out of 5\s*)?stars\b", "MITO-PRICES"),
        (r"\bofficial (?:store|site)\b", "RULES-11.2"),
        (r"\bonly \d+ left\b|\btoday only\b|\bcountdown\b", "RULES-11.4"),
    ]
    for p in pages():
        f = rel(p)
        s = open(p, encoding="utf-8").read()
        v = visible(s)
        if S["AMAZON_ASSOCIATE_LINE"]["text"] not in v:
            add("violation", "MITO-DISCLOSURE", f, "missing exact AMAZON_ASSOCIATE_LINE")
        if core not in v:
            add("violation", "MITO-CLAIMS", f, "missing exact NOT_MEDICAL_ADVICE")
        for m in re.finditer(r"Educational content[^.]*not medical advice", v):
            if not m.group().startswith(core[:-1]):
                add("violation", "MITO-CLAIMS", f, "variant medical-advice wording: " + m.group())
        amazon = re.findall(r'<a\b[^>]*href="[^"]*amazon\.com[^"]*"[^>]*>', s)
        for a in amazon:
            if tag not in a:
                add("violation", "MITO-LINKS", f, "Amazon link without " + tag)
            r = re.search(r'rel="([^"]*)"', a)
            if not r or r.group(1) != relv:
                add("violation", "MITO-LINKS", f, f'Amazon link rel is "{r.group(1) if r else ""}", expected "{relv}"')
        if amazon and not any(g in v for g in group):
            add("violation", "MITO-DISCLOSURE", f, "affiliate links with no group disclosure on the page")
        for m in re.finditer(r"(?<![\w$])\$\s?\d", v):
            add("violation", "MITO-PRICES", f, "printed price: " + v[max(0, m.start() - 60): m.end() + 40])
        for pat, rule in banned:
            for m in re.finditer(pat, v, re.I):
                ctx = v[max(0, m.start() - 90): m.end() + 60]
                before = v[max(0, m.start() - 60): m.start()]
                neg = re.search(r"\b(?:never|not|no|don[’']t|doesn[’']t|isn[’']t|aren[’']t|haven[’']t|won[’']t|without|fake|cut every)\b[^.]{0,40}$", before, re.I)
                if not neg and re.match(r"detox", m.group(), re.I) and re.match(r"\s*(?:claim|myth)", v[m.end(): m.end() + 8], re.I):
                    neg = True  # discussing detox claims, not making one
                add("exception" if neg else "violation", rule, f, ("negated: " if neg else "") + ctx)
        jsonld(f, s)


def main():
    try:
        reg = json.load(open(REG_PATH, encoding="utf-8"))
    except (OSError, ValueError) as e:
        add("violation", "REGISTRY", ".github/registry.json", f"registry missing or invalid: {e}")
        reg = None
    if reg is not None:
        if "phones" in reg:
            check_wdg(reg)
        elif "links" in reg:
            check_mito(reg)
        else:
            add("violation", "REGISTRY", ".github/registry.json", "unrecognized registry layout")
    viol = [x for x in findings if x[0] == "violation"]
    exc = [x for x in findings if x[0] == "exception"]
    mode = "strict" if STRICT else "report-only"
    lines = [f"## Registry check ({mode})", "",
             f"**{len(viol)} violation(s), {len(exc)} approved exception(s)** across {len(pages())} pages.", ""]
    if findings:
        lines += ["| Kind | Rule | File | Text |", "| --- | --- | --- | --- |"]
        for k, r, f, t in viol + exc:
            lines.append(f"| {k} | `{r}` | `{f}` | {t.replace('|', '/')} |")
    report = "\n".join(lines) + "\n"
    print(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(report)
    for k, r, f, t in viol:
        print(f"::{'error' if STRICT else 'warning'} file={f},title={r}::{t}")
    sys.exit(1 if (STRICT and viol) else 0)


if __name__ == "__main__":
    main()
