import requests
from datetime import datetime, timezone


def fetch():
    contests = []
    headers = {"User-Agent": "Mozilla/5.0"}
    utc_time = int(datetime.now(timezone.utc).timestamp())

    try:
        hr = requests.get(
            "https://www.hackerrank.com/rest/contests/upcoming",
            headers=headers,
            timeout=10
        ).json()

        for c in hr.get("models", []):
            if c.get("ended") or c.get("name") == "ProjectEuler+":
                continue
            start = c["epoch_starttime"]
            duration = c["epoch_endtime"] - start
            if utc_time + 14 * 24 * 3600 >= start:
                contests.append({
                    "platform": "HackerRank",
                    "name": c["name"],
                    "startTime": start,
                    "duration": duration,
                    "url": f"https://www.hackerrank.com/contests/{c['slug']}/challenges"
                })

        print(f"[HackerRank] Fetched {len(contests)} contests.")
    except Exception as e:
        print(f"[HackerRank] FAILED: {e}")

    return contests
