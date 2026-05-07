import requests
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from datetime import datetime, timezone

Leetcode=[]

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
        Leetcode.append({
            "platform": "LeetCode",
            "name": c["title"],
            "startTime": c["startTime"],
            "duration": c["duration"],
            "url": f"https://leetcode.com/contest/{c['titleSlug']}"
        })

AllContests = []

with open("AllContest.json","r") as f:
    TempContest=json.load(f)

AllValidContest=[]

for contest in TempContest:
    if contest["platform"] is not "Leetcode" :
      utc_time = int(datetime.now(timezone.utc).timestamp())
      old_contest_cutoff=utc_time-(3*24*3600)
      if old_contest_cutoff<contest['startTime']:
        AllValidContest.append(contest)

AllContests.append(AllValidContest)
AllContests.append(Leetcode)

with open("AllContest.json", "w") as f:
    json.dump(AllContests, f, indent=2)
