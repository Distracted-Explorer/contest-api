import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup


def fetch():
    contests = []
    headers = {"User-Agent": "Mozilla/5.0"}
    utc_time = int(datetime.now(timezone.utc).timestamp())
    three_days = 3 * 24 * 3600
    seen = set()

    try:
        url = "https://atcoder.jp/contests/"
        html = requests.get(url, headers=headers, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        # contest-table-recent covers ended contests shown on AtCoder's page
        for table_id in ["contest-table-recent", "contest-table-daily", "contest-table-action", "contest-table-upcoming"]:
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
                end = timestamp + duration_seconds
                # Include: upcoming (within 14 days), running, or ended within last 3 days
                if utc_time + 14 * 24 * 3600 >= timestamp and utc_time < end + three_days:
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
