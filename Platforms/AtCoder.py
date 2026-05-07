import requests
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from datetime import datetime, timezone

AtCoder=[]

headers = {"User-Agent": "Mozilla/5.0"}

utc_time = int(datetime.now(timezone.utc).timestamp())

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
        utc_time = int(datetime.now(timezone.utc).timestamp())
        if utc_time+14*24*3600>=timestamp:
            AtCoder.append({
                "platform": "AtCoder",
                "name": name,
                "startTime": timestamp,
                "duration": duration_seconds,
                "url": link
            })
        seen.add(link)


AllContests = []

with open("AllContest.json","r") as f:
    TempContest=json.load(f)

AllValidContest=[]

for contest in TempContest:
    if contest["platform"] is not "AtCoder" :
      utc_time = int(datetime.now(timezone.utc).timestamp())
      old_contest_cutoff=utc_time-(3*24*3600)
      if old_contest_cutoff<contest['startTime']:
        AllValidContest.append(contest)

AllContests.append(AllValidContest)
AllContests.append(AtCoder)

with open("AllContest.json", "w") as f:
    json.dump(AllContests, f, indent=2)