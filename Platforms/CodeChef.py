import requests
from datetime import datetime, timezone


def fetch():
    contests = []
    headers = {"User-Agent": "Mozilla/5.0"}
    utc_time = int(datetime.now(timezone.utc).timestamp())

    try:
        cc = requests.get(
            "https://www.codechef.com/api/list/contests/all",
            headers=headers,
            timeout=10
        ).json()

        for c in cc.get("future_contests", []):
            dt = datetime.fromisoformat(c["contest_start_date_iso"])
            timestamp = int(dt.timestamp())
            duration_sec = int(c["contest_duration"]) * 60
            # Include if not yet ended and starts within 14 days
            if utc_time < timestamp + duration_sec and utc_time + 14 * 24 * 3600 >= timestamp:
                contests.append({
                    "platform": "CodeChef",
                    "name": c["contest_name"],
                    "startTime": timestamp,
                    "duration": duration_sec,
                    "url": f"https://www.codechef.com/{c['contest_code']}"
                })

        print(f"[CodeChef] Fetched {len(contests)} contests.")
    except Exception as e:
        print(f"[CodeChef] FAILED: {e}")

    return contests
