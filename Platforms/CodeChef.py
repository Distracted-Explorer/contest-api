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

with open("AllContest.json", "r") as f:
    TempContest = json.load(f)

utc_time = int(datetime.now(timezone.utc).timestamp())
old_contest_cutoff = utc_time - (3 * 24 * 3600)

for contest in TempContest:
    if contest["platform"] != "CodeChef":
        if old_contest_cutoff < contest["startTime"]:
            AllContests.append(contest)

# add new contests
AllContests.extend(CodeChef)

# sort by start time
AllContests.sort(key=lambda x: x["startTime"])

with open("AllContest.json", "w") as f:
    json.dump(AllContests, f, indent=2)