import requests
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from datetime import datetime, timezone



AtCoder=[]
CodeChef=[]
CodeForces=[]
HackerRank=[]
Leetcode=[]
TopCoder=[]

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



# AtCoder
seen = set()
url = "https://atcoder.jp/contests/"
html = requests.get(url, headers=headers, timeout=10).text
soup = BeautifulSoup(html, "html.parser")
for table_id in ["contest-table-daily", "contest-table-action", "contest-table-upcoming"]:
    table = soup.find("div", id=table_id)
    if not table:
        continue
    rows = table.find_all("tr")[1:]
    for r in rows:
        cols = r.find_all("td")
        name = cols[1].text.strip()
        link = "https://atcoder.jp" + cols[1].find("a")["href"]
        if link in seen:
            continue
        time_str = cols[0].text.strip()
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S%z")
        timestamp = int(dt.timestamp())
        duration_str = cols[2].text.strip()
        h, m = map(int, duration_str.split(":"))
        duration_seconds = h*3600 + m*60
        AtCoder.append({
            "platform": "AtCoder",
            "name": name,
            "startTime": timestamp,
            "duration": duration_seconds,
            "url": link
        })
        seen.add(link)


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
        CodeChef.append({
            "platform": "CodeChef",
            "name": c["contest_name"],
            "startTime": timestamp,
            "duration": int(c["contest_duration"])*60,
            "url": f"https://www.codechef.com/{c['contest_code']}"
        })



#HackerRank
hr = requests.get(
    "https://www.hackerrank.com/rest/contests/upcoming",
    headers=headers,
    timeout=10
).json()    

for c in hr["models"]:
    if not c["ended"] and c["name"] != "ProjectEuler+":
        HackerRank.append({
            "platform": "HackerRank",
            "name": c["name"],
            "startTime": c["epoch_starttime"],
            "duration": c["epoch_endtime"] - c["epoch_starttime"],
            "url": f"https://www.hackerrank.com/contests/{c['slug']}/challenges"
        })



#TopCoder

tc=requests.get(
    "https://api.topcoder.com/v6/challenges/?status=ACTIVE&perPage=100&page=1&sortBy=startDate&sortOrder=desc&tracks%5b%5d=Dev&tracks%5b%5d=Des&tracks%5b%5d=DS&tracks%5b%5d=QA&types%5b%5d=CH&types%5b%5d=F2F&types%5b%5d=MM&types%5b%5d=TSK",
    headers=headers,
    timeout=10
).json()

for c in tc:
    if c["phases"][0]["isOpen"]:
        dt_string=c["registrationStartDate"]
        dt = datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        registration_start = int(dt.timestamp())

        dt_string=c["registrationEndDate"]
        dt = datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        registration_end = int(dt.timestamp())
        TopCoder.append({
            "platform": "TopCoder",
            "name": c["name"],
            "startTime": registration_start,
            "duration": registration_end-registration_start,
            "url": f"https://www.topcoder.com/challenges/{c['id']}"
        })

AllContests = (
    CodeForces + Leetcode + AtCoder +
    CodeChef + HackerRank + TopCoder
)

with open("AllContest.json","r") as f:
    TempContest=json.load(f)

for contest in TempContest:
    if contest not in AllContests:
        utc_time = int(datetime.now(timezone.utc).timestamp())
        old_contest_cutoff=utc_time-(3*24*3600)
        if old_contest_cutoff<contest['startTime']:
            AllContests.append(contest)

AllContests.sort(key=lambda x: x["startTime"])

with open("AllContest.json", "w") as f:
    json.dump(AllContests, f, indent=2)
