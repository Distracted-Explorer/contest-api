import requests
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from datetime import datetime, timezone

HackerRank=[]

headers = {"User-Agent": "Mozilla/5.0"}

utc_time = int(datetime.now(timezone.utc).timestamp())


#HackerRank
hr = requests.get(
    "https://www.hackerrank.com/rest/contests/upcoming",
    headers=headers,
    timeout=10
).json()    

for c in hr["models"]:
    if not c["ended"] and c["name"] != "ProjectEuler+":
        if utc_time+14*24*3600 >= c["epoch_starttime"]:
            HackerRank.append({
                "platform": "HackerRank",
                "name": c["name"],
                "startTime": c["epoch_starttime"],
                "duration": c["epoch_endtime"] - c["epoch_starttime"],
                "url": f"https://www.hackerrank.com/contests/{c['slug']}/challenges"
            })

AllContests = []

with open("AllContest.json","r") as f:
    TempContest=json.load(f)

AllValidContest=[]

for contest in TempContest:
    if contest["platform"] is not "HackerRank" :
      utc_time = int(datetime.now(timezone.utc).timestamp())
      old_contest_cutoff=utc_time-(3*24*3600)
      if old_contest_cutoff<contest['startTime']:
        AllValidContest.append(contest)

AllContests.append(AllValidContest)
AllContests.append(HackerRank)

with open("AllContest.json", "w") as f:
    json.dump(AllContests, f, indent=2)
