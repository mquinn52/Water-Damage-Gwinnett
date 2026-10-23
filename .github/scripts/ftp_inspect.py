"""Inspect the waterdamagegwinnett.com server folder; optionally move garbage.

Copied from the Mitothrum repo (Oct 23, 2026), where a zip extracted on the
server left pages at mode 0660 and took the site down with 403s.

Lists the FTP root (this site's deploy folder) with each entry's mode, size
and modify time. With FIX=1, resets web files (html, txt, xml, css, js,
.htaccess) to 644 when they aren't. Read-only otherwise. Never prints
credentials or the server address. Writes report.txt.
"""
import os
import ftplib
import urllib.request

host = os.environ["FTP_SERVER"].strip()
fix = os.environ.get("FIX") == "1"
SITE = os.environ.get("SITE_URL", "https://waterdamagegwinnett.com").rstrip("/")
WEB_EXT = (".html", ".txt", ".xml", ".css", ".js")

ftp = ftplib.FTP_TLS(timeout=60)
ftp.connect(host, 21)
ftp.auth()
ftp.login(os.environ["FTP_USERNAME"], os.environ["FTP_PASSWORD"])
ftp.prot_p()

lines = ["| name | type | mode | size | modified (UTC) |", "|---|---|---|---|---|"]
entries = []
for name, f in sorted(ftp.mlsd("/", facts=["type", "size", "modify", "unix.mode"])):
    if f.get("type") in ("cdir", "pdir"):
        continue
    entries.append((name, f.get("type"), f.get("unix.mode", "")))
    lines.append(f"| {name} | {f.get('type')} | {f.get('unix.mode', '?')} | {f.get('size', '')} | {f.get('modify', '')} |")

# Recursive listing of subfolders (RECURSE=1): one line per file.
tree = []
def walk(path, depth=0):
    if depth > 6:
        return
    try:
        items = sorted(ftp.mlsd(path, facts=["type", "size", "modify"]))
    except ftplib.all_errors as e:
        tree.append(f"{path}: cannot list ({e})")
        return
    for n, f in items:
        if f.get("type") in ("cdir", "pdir"):
            continue
        full = f"{path.rstrip('/')}/{n}"
        if f.get("type") == "dir":
            tree.append(f"{full}/")
            walk(full, depth + 1)
        else:
            tree.append(f"{full}  {f.get('size', '')}  {f.get('modify', '')[:8]}")
if os.environ.get("RECURSE") == "1":
    for name, kind, _ in entries:
        if kind == "dir":
            tree.append(f"/{name}/")
            walk(f"/{name}")

# Explicit move list (MOVE_PATHS, one path per line): owner-approved garbage
# goes to /_to_delete/ (keeping its relative path) for deletion in cPanel.
for raw in os.environ.get("MOVE_PATHS", "").splitlines():
    src = raw.strip()
    if not src:
        continue
    dst = "/_to_delete/" + src.lstrip("/").replace("/", "__")
    try:
        try:
            ftp.mkd("/_to_delete")
        except ftplib.all_errors:
            pass
        ftp.rename(src, dst)
        tree.append(f"MOVED {src} -> {dst}")
    except ftplib.all_errors as e:
        tree.append(f"MOVE FAILED {src}: {e}")

changes = []
if fix:
    for name, kind, mode in entries:
        if kind != "file" or not (name.endswith(WEB_EXT) or name == ".htaccess"):
            continue
        if mode.lstrip("0") == "644":
            continue
        try:
            ftp.sendcmd(f"SITE CHMOD 644 /{name}")
            changes.append(f"{name}: {mode or '?'} -> 0644")
        except ftplib.all_errors as e:
            changes.append(f"{name}: chmod failed ({e})")
moved = []
if os.environ.get("ARCHIVE_ZIPS") == "1":
    # Owner approved moving old upload zips to _to_delete/ (Oct 23, 2026) for
    # deletion in cPanel. Claude never hard-deletes. .htaccess blocks *.zip.
    names = {n for n, _, _ in entries}
    if "_to_delete" not in names:
        ftp.mkd("/_to_delete")
    for name, kind, _ in entries:
        if kind == "file" and name.lower().endswith(".zip"):
            try:
                ftp.rename(f"/{name}", f"/_to_delete/{name}")
                moved.append(name)
            except ftplib.all_errors as e:
                moved.append(f"{name} (move failed: {e})")
ftp.quit()

status = []
for p in ["/", "/privacy.html", "/es/", "/llms.txt", "/robots.txt"]:
    try:
        req = urllib.request.Request(SITE + p + "?inspect=1",
                                     headers={"User-Agent": "site-monitor (GitHub Actions)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            status.append(f"{p} {r.status}")
    except urllib.error.HTTPError as e:
        status.append(f"{p} {e.code}")
    except Exception as e:
        status.append(f"{p} error {type(e).__name__}")

report = ["**FTP inspect" + (" + permission fix" if fix else " (read-only)") + "**", ""]
if os.environ.get("BRIEF") != "1":
    report += lines + [""]
if fix:
    report.append("Permission changes: " + ("; ".join(changes) if changes else "none needed"))
    report.append("")
if tree:
    # GitHub comments cap at 65,536 characters
    budget, kept = 55000, []
    for t in tree:
        budget -= len(t) + 1
        if budget < 0:
            kept.append(f"... {len(tree) - len(kept)} more lines truncated")
            break
        kept.append(t)
    report += ["```"] + kept + ["```", ""]
if moved:
    report.append(f"Moved {len(moved)} zip(s) to _to_delete/: " + "; ".join(moved))
    report.append("")
report.append("Live status: " + ", ".join(status))
text = "\n".join(report) + "\n"
open("report.txt", "w").write(text)
print(text)
