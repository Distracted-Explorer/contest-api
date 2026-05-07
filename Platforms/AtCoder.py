import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup


def fetch():
    contests = []
    headers = {"User-Agent": "Mozilla/5.0"}
    utc_time = int(datetime.now(timezone.utc).timestamp())
    seen = set()

    try:
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
                if len(cols) < 3:
                    continue
                name = cols[1].text.strip()
                link = "https://atcoder.jp" + cols[1].find("a")["href"]
                if link in seen:
                    continue
                time_str = cols[0].text.strip()
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S%z")
                timestamp = int(dt.timestamp())
                duration_str = cols[2].text.strip()
                h, m = map(int, duration_str.split(":"))
                duration_seconds = h * 3600 + m * 60
                # Include contests within next 14 days OR currently running
                if utc_time < timestamp + duration_seconds and utc_time + 14 * 24 * 3600 >= timestamp:
                    contests.append({
                        "platform": "AtCoder",
                        "name": name,
                        "startTime": timestamp,
                        "duration": duration_seconds,
                        "url": link
                    })
                seen.add(link)

        print(f"[AtCoder] Fetched {len(contests)} contests.")
    except Exception as e:
        print(f"[AtCoder] FAILED: {e}")

    return contests
