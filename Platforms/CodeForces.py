import requests
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from datetime import datetime, timezone

CodeForces=[]

headers = {"User-Agent": "Mozilla/5.0"}

utc_time = int(datetime.now(timezone.utc).timestamp())

# CODEFORCES
headers = {"User-Agent": "Mozilla/5.0"}

cf = requests.get(
    "https://codeforces.com/api/contest.list",
    headers=headers,
    timeout=10
).json()

for c in cf["result"]:
    if utc_time<c["startTimeSeconds"]+c["durationSeconds"]:
        CodeForces.append({
            "platform": "CodeForces",
            "name": c["name"],
            "startTime": c["startTimeSeconds"],
            "duration": c["durationSeconds"],
            "url": f"https://codeforces.com/contestRegistration/{c['id']}"
        })

AllContests = []

with open("../AllContest.json","r") as f:
    TempContest=json.load(f)

AllValidContest=[]

for contest in TempContest:
    if contest["platform"] is not "CodeForces" :
      utc_time = int(datetime.now(timezone.utc).timestamp())
      old_contest_cutoff=utc_time-(3*24*3600)
      if old_contest_cutoff<contest['startTime']:
        AllValidContest.append(contest)

AllContests.append(AllValidContest)
AllContests.append(CodeForces)

with open("../AllContest.json", "w") as f:
    json.dump(AllContests, f, indent=2)
