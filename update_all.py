"""
Single aggregator — runs all platform fetchers, merges with existing
AllContest.json (dropping stale entries), then writes the file ONCE.

Contests are kept in 3 categories:
  - "future"  : not yet started
  - "running" : currently ongoing
  - "recent"  : ended within the last 3 days
"""
import json
import sys
import os
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

THREE_DAYS = 3 * 24 * 3600


def get_status(contest, now):
    """Return 'future', 'running', or 'recent' -- or None if too old to keep."""
    start = contest["startTime"]
    end = start + contest["duration"]
    if now < start:
        return "future"
    elif now < end:
        return "running"
    elif now < end + THREE_DAYS:
        return "recent"
    else:
        return None  # older than 3 days -- drop it


# --- Load existing data ---
with open(ALLCONTEST_PATH, "r") as f:
    existing = json.load(f)

utc_time = int(datetime.now(timezone.utc).timestamp())

# --- Fetch fresh data from each platform (failures are isolated) ---
fresh = {}
failed = []
for name, fn in PLATFORMS.items():
    result = fn()
    if result is not None:
        fresh[name] = result
    else:
        failed.append(name)

# --- Merge: keep old entries for platforms that FAILED (so we don't lose data)
#            drop old entries for platforms that SUCCEEDED (replaced by fresh data)
merged = []

for contest in existing:
    platform = contest["platform"]
    if platform in failed:
        # Platform scraper failed -- keep old entry only if still in a valid category
        status = get_status(contest, utc_time)
        if status is not None:
            contest["status"] = status
            merged.append(contest)
    # else: platform succeeded -- old entries will be replaced; skip them

# Add all freshly fetched contests, assigning status
for name, contests in fresh.items():
    for contest in contests:
        status = get_status(contest, utc_time)
        if status is not None:
            contest["status"] = status
            merged.append(contest)

# Deduplicate by URL
seen_urls = set()
deduped = []
for c in merged:
    if c["url"] not in seen_urls:
        deduped.append(c)
        seen_urls.add(c["url"])

# Sort: running first, then future (by startTime), then recent (by end time desc)
STATUS_ORDER = {"running": 0, "future": 1, "recent": 2}

def sort_key(c):
    status = c.get("status", "future")
    order = STATUS_ORDER.get(status, 3)
    if status == "recent":
        # Most recently ended first
        return (order, -(c["startTime"] + c["duration"]))
    return (order, c["startTime"])

deduped.sort(key=sort_key)

# --- Summary counts ---
counts = {"future": 0, "running": 0, "recent": 0}
for c in deduped:
    counts[c.get("status", "future")] += 1

# --- Write once ---
with open(ALLCONTEST_PATH, "w") as f:
    json.dump(deduped, f, indent=2)

print(f"\n✅ AllContest.json updated: {len(deduped)} contests total.")
print(f"   🟢 Running : {counts['running']}")
print(f"   🔵 Future  : {counts['future']}")
print(f"   🕐 Recent  : {counts['recent']} (ended within last 3 days)")
if failed:
    print(f"⚠️  Failed platforms (old data kept): {', '.join(failed)}")
