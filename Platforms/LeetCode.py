import requests
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from datetime import datetime, timezone

LeetCode=[]

headers = {"User-Agent": "Mozilla/5.0"}

utc_time = int(datetime.now(timezone.utc).timestamp())

# LEETCODE
query = {
 "query": """
 query {
  allContests {
   title
   titleSlug
   startTime
   duration
  }
 }
 """
}

lc = requests.post(
    "https://leetcode.com/graphql",
    json=query,
    headers=headers,
    timeout=10
).json()

for c in lc["data"]["allContests"]:
    if utc_time<c["startTime"]+c["duration"]:
        LeetCode.append({
            "platform": "LeetCode",
            "name": c["title"],
            "startTime": c["startTime"],
            "duration": c["duration"],
            "url": f"https://leetcode.com/contest/{c['titleSlug']}"
        })

AllContests = []

with open("AllContest.json", "r") as f:
    TempContest=json.load(f)

AllContests = []

with open("AllContest.json", "r") as f:
    TempContest = json.load(f)

utc_time = int(datetime.now(timezone.utc).timestamp())
old_contest_cutoff = utc_time - (3 * 24 * 3600)

for contest in TempContest:
    if contest["platform"] != "LeetCode":
        if old_contest_cutoff < contest["startTime"]:
            AllContests.append(contest)

# add new contests
AllContests.extend(LeetCode)

# sort by start time
AllContests.sort(key=lambda x: x["startTime"])

with open("AllContest.json", "w") as f:
    json.dump(AllContests, f, indent=2)
