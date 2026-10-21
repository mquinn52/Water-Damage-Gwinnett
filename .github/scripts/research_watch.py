#!/usr/bin/env python3
"""Research watcher. Standard library only.

Reads research/sources.json, fetches each source page, reduces it to its main
text, and compares it with the snapshot saved in research/snapshots/. Writes:
  research/changes.md  – human-readable report of what changed (empty if none)
  research/changes.json – machine-readable list for the optional AI review
First run for a source just records a baseline. Fetch failures are reported
but never treated as a change, so a blocked site can't spam you; a source that
fails 3 runs in a row is listed in research/stuck.md so the workflow can flag it.

Source types:
  "page" (default) – an ordinary web page; robots.txt is respected.
  "federal_register" – the Federal Register's public API (built for programs);
     "query" holds the API query string. The snapshot is the list of matching
     documents (date, type, title, link), so a new rule or notice shows up as
     an added line.
"""
import hashlib, json, os, re, sys, difflib, urllib.parse, urllib.request, urllib.robotparser
from html.parser import HTMLParser

ROOT = "research"
SNAP = os.path.join(ROOT, "snapshots")
UA = {"User-Agent": "Mozilla/5.0 (compatible; site-research-watch/1.0; +https://github.com)"}
os.makedirs(SNAP, exist_ok=True)


class MainText(HTMLParser):
    """Collect visible text, preferring <main>/<article> when the page has them."""
    SKIP = {"script", "style", "noscript", "svg", "nav", "header", "footer", "form", "button"}
    BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "dt", "dd", "br", "div", "section", "tr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.all, self.main = [], []
        self.skip = 0; self.in_main = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP: self.skip += 1
        if tag in ("main", "article"): self.in_main += 1
        if tag in self.BLOCK: self._nl()

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip: self.skip -= 1
        if tag in ("main", "article") and self.in_main: self.in_main -= 1
        if tag in self.BLOCK: self._nl()

    def _nl(self):
        self.all.append("\n")
        if self.in_main: self.main.append("\n")

    def handle_data(self, d):
        if self.skip: return
        self.all.append(d)
        if self.in_main: self.main.append(d)

    def text(self):
        raw = "".join(self.main) if len("".join(self.main).strip()) > 500 else "".join(self.all)
        lines = [" ".join(l.split()) for l in raw.splitlines()]
        return "\n".join(l for l in lines if l)


def fetch_text(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        body = r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
    p = MainText(); p.feed(body)
    return p.text()


_robots = {}
def robots_allow(url):
    parts = urllib.parse.urlsplit(url)
    base = f"{parts.scheme}://{parts.netloc}"
    if base not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            req = urllib.request.Request(base + "/robots.txt", headers=UA)
            with urllib.request.urlopen(req, timeout=20) as r:
                rp.parse(r.read().decode("utf-8", "replace").splitlines())
        except Exception:
            rp.parse([])          # no readable robots.txt: allowed
        _robots[base] = rp
    return _robots[base].can_fetch(UA["User-Agent"], url)


def fetch_federal_register(query):
    url = "https://www.federalregister.gov/api/v1/documents.json?" + query
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        data = json.load(r)
    rows = [f"{d.get('publication_date','')} | {d.get('type','')} | {d.get('title','').strip()} | {d.get('html_url','')}"
            for d in data.get("results", [])]
    header = f"Federal Register documents matching: {urllib.parse.unquote(query)}"
    # pad so a short-but-valid list isn't mistaken for a blocked page
    return header + "\n" + "\n".join(sorted(rows, reverse=True)) + "\n" + "-" * 300


def clean(text, ignore):
    out = []
    for line in text.splitlines():
        if any(re.search(rx, line, re.I) for rx in ignore):
            continue
        out.append(line)
    return "\n".join(out).strip() + "\n"


cfg = json.load(open(os.path.join(ROOT, "sources.json")))
GLOBAL_IGNORE = cfg.get("ignore_lines", [])
changes, failures, baselines = [], [], []
FAILS = os.path.join(ROOT, "failures.json")
fail_count = json.load(open(FAILS)) if os.path.exists(FAILS) else {}

for src in cfg["sources"]:
    sid, url = src["id"], src["url"]
    path = os.path.join(SNAP, f"{sid}.txt")
    try:
        if src.get("type") == "federal_register":
            text = fetch_federal_register(src["query"]) + "\n"
        else:
            if not robots_allow(url):
                failures.append(f"- **{src['name']}** ({url}): the site's robots.txt asks automated visitors not to fetch it; skipped")
                fail_count[sid] = fail_count.get(sid, 0) + 1
                continue
            text = clean(fetch_text(url), GLOBAL_IGNORE + src.get("ignore_lines", []))
    except Exception as e:
        failures.append(f"- **{src['name']}** ({url}): couldn't fetch — {e}")
        fail_count[sid] = fail_count.get(sid, 0) + 1
        continue
    if len(text) < 300:
        failures.append(f"- **{src['name']}** ({url}): page came back nearly empty (blocked or changed format); snapshot kept")
        fail_count[sid] = fail_count.get(sid, 0) + 1
        continue
    fail_count.pop(sid, None)
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    if old is None:
        baselines.append(src["name"])
    elif hashlib.sha256(old.encode()).hexdigest() != hashlib.sha256(text.encode()).hexdigest():
        diff = list(difflib.unified_diff(old.splitlines(), text.splitlines(), "before", "after", n=1, lineterm=""))
        added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
        removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
        changes.append({"id": sid, "name": src["name"], "url": url, "why": src.get("why", ""),
                        "added": added, "removed": removed, "diff": "\n".join(diff)})
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

with open(os.path.join(ROOT, "changes.json"), "w") as f:
    json.dump(changes, f, indent=1)
with open(FAILS, "w") as f:
    json.dump(fail_count, f, indent=1, sort_keys=True)
names = {s["id"]: (s["name"], s["url"]) for s in cfg["sources"]}
stuck = [f"- **{names[k][0]}** ({names[k][1]}): failed {v} runs in a row" for k, v in sorted(fail_count.items())
         if v == 3 and k in names]   # flag once, on the third straight failure
with open(os.path.join(ROOT, "stuck.md"), "w") as f:
    f.write("\n".join(stuck))

report = []
if changes:
    report.append(f"{len(changes)} watched source(s) changed since the last check. "
                  "Review each against `RULES.md`; update the rules (and the site, if needed) when a change matters.\n")
    for c in changes:
        d = c["diff"]
        if len(d) > 6000:
            d = d[:6000] + "\n… (diff truncated; full history is in research/snapshots/)"
        report.append(f"### {c['name']}\n{c['url']}\n\n*Why we watch it:* {c['why']}\n\n"
                      f"+{c['added']} / −{c['removed']} lines\n\n```diff\n{d}\n```\n")
if baselines:
    report.append("Baseline recorded (first check, nothing to compare yet): " + ", ".join(baselines) + "\n")
if failures:
    report.append("**Couldn't check this time** (not treated as a change):\n" + "\n".join(failures) + "\n")

with open(os.path.join(ROOT, "changes.md"), "w") as f:
    f.write("\n".join(report))
print("\n".join(report) or "No changes.")
# exit code 10 = something changed, so the workflow knows to open an issue
sys.exit(10 if changes else 0)
