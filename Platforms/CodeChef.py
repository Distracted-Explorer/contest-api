import requests
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from datetime import datetime, timezone

CodeChef=[]

headers = {"User-Agent": "Mozilla/5.0"}

utc_time = int(datetime.now(timezone.utc).timestamp())

# CodeChef
cc = requests.get(
    "https://www.codechef.com/api/list/contests/all",
    headers=headers,
    timeout=10
).json()

for c in cc["future_contests"]:
    dt = datetime.fromisoformat(c["contest_start_date_iso"])
    timestamp = int(dt.timestamp())
    if utc_time<timestamp+(int(c["contest_duration"])*60):
        if utc_time+14*24*3600>=timestamp :
            CodeChef.append({
                "platform": "CodeChef",
                "name": c["contest_name"],
                "startTime": timestamp,
                "duration": int(c["contest_duration"])*60,
                "url": f"https://www.codechef.com/{c['contest_code']}"
            })

AllContests = []

with open("../AllContest.json","r") as f:
    TempContest=json.load(f)

AllValidContest=[]

for contest in TempContest:
    if contest["platform"] is not "Leetcode" :
      utc_time = int(datetime.now(timezone.utc).timestamp())
      old_contest_cutoff=utc_time-(3*24*3600)
      if old_contest_cutoff<contest['startTime']:
        AllValidContest.append(contest)

AllContests.append(AllValidContest)
AllContests.append(CodeChef)

with open("../AllContest.json", "w") as f:
    json.dump(AllContests, f, indent=2)
