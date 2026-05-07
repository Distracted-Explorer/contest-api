"""
Single aggregator — runs all platform fetchers, merges with existing
AllContest.json (dropping stale entries), then writes the file ONCE.
This replaces the old pattern of each script reading+writing the file.
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

utc_time = int(datetime.now(timezone.utc).timestamp())
old_contest_cutoff = utc_time - (3 * 24 * 3600)  # keep contests up to 3 days old

# --- Load existing data ---
with open(ALLCONTEST_PATH, "r") as f:
    existing = json.load(f)

# --- Fetch fresh data from each platform (failures are isolated) ---
fresh = {}
failed = []
for name, fn in PLATFORMS.items():
    result = fn()
    if result is not None:
        fresh[name] = result
    else:
        failed.append(name)

# --- Merge: keep old entries for platforms that FAILED (so we don't lose data) ---
#           drop old entries for platforms that SUCCEEDED (replaced by fresh data)
merged = []

for contest in existing:
    platform = contest["platform"]
    if platform in failed:
        # Platform scraper failed — keep old entry if not too stale
        if contest["startTime"] > old_contest_cutoff:
            merged.append(contest)
    else:
        # Platform scraper succeeded — old entry will be replaced; skip it
        pass

# Add all freshly fetched contests
for name, contests in fresh.items():
    merged.extend(contests)

# Deduplicate by URL
seen_urls = set()
deduped = []
for c in merged:
    if c["url"] not in seen_urls:
        deduped.append(c)
        seen_urls.add(c["url"])

# Sort by start time
deduped.sort(key=lambda x: x["startTime"])

# --- Write once ---
with open(ALLCONTEST_PATH, "w") as f:
    json.dump(deduped, f, indent=2)

print(f"\n✅ AllContest.json updated: {len(deduped)} contests total.")
if failed:
    print(f"⚠️  Failed platforms (old data kept): {', '.join(failed)}")
