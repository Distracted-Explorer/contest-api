import requests
import json
from datetime import datetime, timezone



AtCoder=[]
CodeChef=[]
Codeforces=[]
HackerEarth=[]
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
    if utc_time<c["startTimeSeconds"]:
        Codeforces.append({
            "platform": "Codeforces",
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
    if utc_time<c["startTime"]:
        Leetcode.append({
            "platform": "LeetCode",
            "name": c["title"],
            "startTime": c["startTime"],
            "duration": c["duration"],
            "url": f"https://leetcode.com/contest/{c['titleSlug']}"
        })



# AtCoder
ac = requests.get(
    "https://kenkoooo.com/atcoder/resources/contests.json",
    headers=headers,
    timeout=10
).json()

for c in ac:
    if c["start_epoch_second"] > utc_time and c["rate_change"] is not None:
        AtCoder.append({
            "platform": "AtCoder",
            "name": c["title"],
            "startTime": c["start_epoch_second"],
            "duration": c["duration_second"],
            "url": f"https://atcoder.jp/contests/{c['id']}"
        })



# CodeChef
cc = requests.get(
    "https://www.codechef.com/api/list/contests/all",
    headers=headers,
    timeout=10
).json()

for c in cc["future_contests"]:
    s=c["contest_start_date"]
    dt = datetime.strptime(s, "%d %b %Y  %H:%M:%S")
    dt = dt.replace(tzinfo=timezone.utc)
    timestamp = int(dt.timestamp())
    if utc_time+1296000>timestamp:
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
    if c["ended"]==False:
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




#HackerEarth
he = requests.get(
    "https://www.hackerearth.com/api/community/challenges/compete/",
    headers=headers,
    timeout=10
).json()

for c in he["data"]:
    date_string = c["start_str"]
    cleaned = date_string.replace(" (UTC)", "").replace(" UTC", "")
    dt = datetime.strptime(cleaned, "%b %d, %Y %I:%M %p")
    dt = dt.replace(tzinfo=timezone.utc)
    start_time = int(dt.timestamp())

    date_string = c["end_str"]
    cleaned = date_string.replace(" (UTC)", "").replace(" UTC", "")
    dt = datetime.strptime(cleaned, "%b %d, %Y %I:%M %p")
    dt = dt.replace(tzinfo=timezone.utc)
    end_time = int(dt.timestamp())

    if end_time > utc_time:
        HackerEarth.append({
            "platform": "HackerEarth",
            "name": c["title"],
            "startTime": start_time,
            "duration": end_time-start_time,
            "url": c['url']
        })

AllContests = (
    Codeforces + Leetcode + AtCoder +
    CodeChef + HackerRank + TopCoder + HackerEarth
)

AllContests.sort(key=lambda x: x["startTime"])

with open("AllContest.json", "w") as f:
    json.dump(AllContests, f, indent=2)

