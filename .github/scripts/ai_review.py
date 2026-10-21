#!/usr/bin/env python3
"""Optional AI review of research changes. Standard library only.

Runs only when ANTHROPIC_API_KEY is set. Sends the week's source diffs and the
current RULES.md to Claude and asks for (1) a plain-English summary of what
changed and whether it affects this site, and (2) a revised RULES.md if, and
only if, a rule should change. Writes research/ai_summary.md and, when rules
should change, RULES.proposed.md. A person reviews and merges the result;
nothing here edits the live site.
"""
import json, os, sys, urllib.request

key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
if not key:
    print("No ANTHROPIC_API_KEY; skipping AI review."); sys.exit(0)

model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")
site = os.environ.get("SITE_URL", "this site")
changes = json.load(open("research/changes.json"))
rules = open("RULES.md", encoding="utf-8").read()
diffs = "\n\n".join(f"## {c['name']} ({c['url']})\nWhy watched: {c['why']}\n```diff\n{c['diff'][:12000]}\n```"
                    for c in changes)

prompt = f"""You maintain the compliance and marketing rules for {site}.

Below are this week's changes to official policy pages we watch, as diffs of their
text, followed by our current RULES.md.

Decide, for each change, whether it is substantive (a new, removed, or reworded
requirement or recommendation) or cosmetic (navigation, dates, formatting,
examples reworded without changing meaning). Be conservative: only propose a rule
change when the source text clearly supports it, quote the exact source wording
that supports it, and never invent requirements. Keep every existing rule unless
the source now contradicts it.

Respond with ONLY a JSON object, no prose around it:
{{"summary": "Markdown. One short section per changed source: what changed, substantive or cosmetic, and whether it affects this site and why.",
  "rules_should_change": true or false,
  "revised_rules": "If rules_should_change, the COMPLETE revised RULES.md (keep its structure, update 'Last reviewed', add a changelog entry quoting the supporting source text). Otherwise an empty string."}}

# Source changes
{diffs}

# Current RULES.md
{rules}
"""

req = urllib.request.Request(
    "https://api.anthropic.com/v1/messages",
    data=json.dumps({"model": model, "max_tokens": 16000,
                     "messages": [{"role": "user", "content": prompt}]}).encode(),
    headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.load(r)
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
    start, end = text.find("{"), text.rfind("}")
    result = json.loads(text[start:end + 1])
except Exception as e:
    open("research/ai_summary.md", "w").write(f"_AI review failed ({e}); review the diffs above manually._\n")
    print("AI review failed:", e); sys.exit(0)

open("research/ai_summary.md", "w", encoding="utf-8").write(result.get("summary", "").strip() + "\n")
if result.get("rules_should_change") and result.get("revised_rules", "").strip():
    open("RULES.proposed.md", "w", encoding="utf-8").write(result["revised_rules"].strip() + "\n")
    print("Proposed rule changes written.")
else:
    print("No rule changes proposed.")
