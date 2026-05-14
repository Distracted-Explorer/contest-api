"""
Aggregator — fetches fresh contest data from all platforms, merges into
AllContest.json, and keeps contests in exactly 3 categories:

  "future"  — not yet started
  "running" — currently ongoing
  "recent"  — ended within the last 3 days

How merging works:
  - AllContest.json is the source of truth / persistent store.
  - On each run, fresh data is fetched from every platform.
  - New contests (by URL) are added to the file.
  - Existing contests get their status refreshed.
  - Contests older than 3 days after their end time are removed.
  - If a platform fetch fails, its existing entries in the file are kept
    (so we don't lose data on a bad run).
"""

import json
import os
import sys
from datetime import datetime, timezone

# Make sure Platforms/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Platforms"))

import AtCoder
import CodeChef
import CodeForces
import HackerRank
import LeetCode

PLATFORMS = {
    "AtCoder":    AtCoder.fetch,
    "CodeChef":   CodeChef.fetch,
    "CodeForces": CodeForces.fetch,
    "HackerRank": HackerRank.fetch,
    "LeetCode":   LeetCode.fetch,
}

ALLCONTEST_PATH = os.path.join(os.path.dirname(__file__), "AllContest.json")
THREE_DAYS_SEC  = 3 * 24 * 3600


def get_status(start, duration, now):
    """
    Return the category string for a contest, or None if it should be dropped.
      'future'  — starts in the future
      'running' — started but not yet ended
      'recent'  — ended, but within the last 3 days
      None      — ended more than 3 days ago → remove
    """
    end = start + duration
    if now < start:
        return "future"
    if now < end:
        return "running"
    if now < end + THREE_DAYS_SEC:
        return "recent"
    return None  # too old, drop it


# ── Load existing data ────────────────────────────────────────────────────────

if os.path.exists(ALLCONTEST_PATH):
    with open(ALLCONTEST_PATH, "r") as f:
        existing = json.load(f)
else:
    existing = []

# Build a lookup: url → contest dict (existing store)
stored = {c["url"]: c for c in existing}

# ── Fetch fresh data ──────────────────────────────────────────────────────────

fresh_by_platform: dict[str, list] = {}
failed: list[str] = []

for name, fn in PLATFORMS.items():
    result = fn()
    if result is not None:
        fresh_by_platform[name] = result
    else:
        failed.append(name)

# ── Merge ─────────────────────────────────────────────────────────────────────
#
# Strategy:
#   1. Start with the existing store.
#   2. For every freshly fetched contest:
#        - If it's already in the store, update its fields (name/duration may
#          change, e.g. rescheduled contest).
#        - If it's new, add it.
#   3. For platforms that SUCCEEDED, we trust the fresh data completely —
#      any contest from that platform that wasn't returned is considered gone
#      (the platform itself dropped it), UNLESS it's still "recent" in the
#      store (the platform may not return past contests even if they just ended).
#   4. For platforms that FAILED, keep all their existing entries as-is.
#   5. Finally, recalculate status for every entry and drop anything too old.

now = int(datetime.now(timezone.utc).timestamp())

# Collect URLs returned by each successful platform fetch
fresh_urls_by_platform: dict[str, set] = {
    name: {c["url"] for c in contests}
    for name, contests in fresh_by_platform.items()
}

# Upsert fresh contests into the store
for name, contests in fresh_by_platform.items():
    for c in contests:
        stored[c["url"]] = {
            "platform":  c["platform"],
            "name":      c["name"],
            "startTime": c["startTime"],
            "duration":  c["duration"],
            "url":       c["url"],
        }

# Remove stale entries for successful platforms:
#   drop a stored contest if its platform fetched successfully BUT didn't
#   return it AND it is no longer "recent" (i.e. it truly ended long ago
#   or was cancelled).
urls_to_remove = []
for url, c in stored.items():
    platform = c["platform"]
    if platform in fresh_urls_by_platform:
        # Platform fetch succeeded
        if url not in fresh_urls_by_platform[platform]:
            # Not in fresh data — keep only if it's still recent (just ended)
            status = get_status(c["startTime"], c["duration"], now)
            if status != "recent":
                urls_to_remove.append(url)

for url in urls_to_remove:
    del stored[url]

# ── Recalculate status & drop old contests ────────────────────────────────────

final = []
for c in stored.values():
    status = get_status(c["startTime"], c["duration"], now)
    if status is None:
        continue  # older than 3 days after end — remove
    final.append({**c, "status": status})

# ── Sort: running → future (by startTime) → recent (most-recently-ended first)

STATUS_ORDER = {"running": 0, "future": 1, "recent": 2}

def sort_key(c):
    order = STATUS_ORDER.get(c["status"], 3)
    if c["status"] == "recent":
        return (order, -(c["startTime"] + c["duration"]))
    return (order, c["startTime"])

final.sort(key=sort_key)

# ── Write ─────────────────────────────────────────────────────────────────────

with open(ALLCONTEST_PATH, "w") as f:
    json.dump(final, f, indent=2)

# ── Summary ───────────────────────────────────────────────────────────────────

counts = {"running": 0, "future": 0, "recent": 0}
for c in final:
    counts[c["status"]] += 1

print(f"\n✅ AllContest.json updated — {len(final)} contests kept.")
print(f"   🟢 Running : {counts['running']}")
print(f"   🔵 Future  : {counts['future']}")
print(f"   🕐 Recent  : {counts['recent']}  (ended within last 3 days)")
if failed:
    print(f"\n⚠️  Fetch failed (existing entries kept): {', '.join(failed)}")