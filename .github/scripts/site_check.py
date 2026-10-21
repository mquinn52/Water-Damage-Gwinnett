#!/usr/bin/env python3
"""Daily site monitor. Standard library only.

Checks the repository's own files (rules that must always hold) and the live
site (every sitemap URL loads, and serves the same version as the repo).
Writes a Markdown report to report.md and exits 1 if anything failed.

Configured by environment variables:
  SITE_URL           e.g. https://waterdamagegwinnett.com
  REQUIRED_TEXT      '||'-separated rules every content page must meet; a rule may
                     list alternatives separated by '::' (any one is enough,
                     e.g. the English and Spanish versions of a disclosure)
  AFFILIATE_TAG      optional; every amazon.com link must carry tag=<this>
  ALLOWED_PHONES     optional; comma-separated tel: numbers allowed on the site
  SKIP_FILES         optional; comma-separated files exempt from page rules
"""
import glob, os, re, sys, urllib.request, xml.etree.ElementTree as ET
from html.parser import HTMLParser

SITE = os.environ["SITE_URL"].rstrip("/")
REQUIRED = [s for s in os.environ.get("REQUIRED_TEXT", "").split("||") if s.strip()]
TAG = os.environ.get("AFFILIATE_TAG", "").strip()
PHONES = {p.strip() for p in os.environ.get("ALLOWED_PHONES", "").split(",") if p.strip()}
SKIP = {s.strip() for s in os.environ.get("SKIP_FILES", "").split(",") if s.strip()}
UA = {"User-Agent": "site-monitor (GitHub Actions)"}
problems, notes = [], []


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.title = ""; self._t = False
    def handle_starttag(self, tag, attrs):
        if tag == "a": self.links.append(dict(attrs))
        if tag == "title": self._t = True
    def handle_endtag(self, tag):
        if tag == "title": self._t = False
    def handle_data(self, d):
        if self._t: self.title += d


def parse(html):
    p = Links(); p.feed(html); p.title = " ".join(p.title.split()); return p


# ---------- 1. Rules on the repository's own files ----------
pages = [f for f in sorted(glob.glob("*.html") + glob.glob("*/*.html"))
         if not f.startswith((".github/", "google")) and f not in SKIP]
local_titles = {}
for f in pages:
    html = open(f, encoding="utf-8", errors="replace").read()
    doc = parse(html)
    local_titles[f] = doc.title
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    for req in REQUIRED:
        options = [o.strip() for o in req.split("::") if o.strip()]
        if not any(o in text or o in html for o in options):
            problems.append(f"`{f}` is missing required text: “{options[0][:80]}”")
    for a in doc.links:
        href = a.get("href") or ""
        if TAG and "amazon." in href:
            if f"tag={TAG}" not in href:
                problems.append(f"`{f}`: Amazon link without tag={TAG}: {href[:90]}")
            if "sponsored" not in (a.get("rel") or ""):
                problems.append(f"`{f}`: Amazon link missing rel=\"sponsored\": {href[:90]}")
        if PHONES and href.startswith("tel:") and href[4:] not in PHONES:
            problems.append(f"`{f}`: unexpected phone number {href[4:]}")

# ---------- 2. Live site ----------
def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode("utf-8", "replace")

try:
    _, sm = fetch(f"{SITE}/sitemap.xml?monitor=1")
    urls = [e.text.strip() for e in ET.fromstring(sm).iter() if e.tag.endswith("loc")]
except Exception as e:
    urls = []; problems.append(f"Live sitemap could not be read: {e}")

def local_file_for(url):
    path = url.replace(SITE, "").lstrip("/")
    if path == "" or path.endswith("/"): path += "index.html"
    return path

stale = []
for url in urls:
    try:
        status, html = fetch(url + ("&" if "?" in url else "?") + "monitor=1")
        if status != 200:
            problems.append(f"{url} returned HTTP {status}"); continue
        f = local_file_for(url)
        if f in local_titles and parse(html).title != local_titles[f]:
            stale.append(url)
    except Exception as e:
        problems.append(f"{url} failed to load: {e}")

if stale:
    problems.append("Live pages don't match the repository (deploy didn't run, or a cache is serving old copies): "
                    + ", ".join(stale[:10]) + (" …" if len(stale) > 10 else ""))
notes.append(f"Checked {len(pages)} files in the repository and {len(urls)} live URLs from the sitemap.")

# ---------- Report ----------
with open("report.md", "w") as out:
    if problems:
        out.write(f"The daily check of {SITE} found {len(problems)} problem(s):\n\n")
        out.write("\n".join(f"- {p}" for p in problems[:100]) + "\n\n")
    else:
        out.write(f"All checks passed for {SITE}.\n\n")
    out.write("\n".join(notes) + "\n")
print(open("report.md").read())
sys.exit(1 if problems else 0)
