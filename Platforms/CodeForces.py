import requests
from datetime import datetime, timezone


def fetch():
    contests = []
    headers = {"User-Agent": "Mozilla/5.0"}
    utc_time = int(datetime.now(timezone.utc).timestamp())

    try:
        cf = requests.get(
            "https://codeforces.com/api/contest.list",
            headers=headers,
            timeout=10
        ).json()

        for c in cf.get("result", []):
            start = c.get("startTimeSeconds")
            duration = c.get("durationSeconds")
            if start is None or duration is None:
                continue
            # Include if not yet ended and starts within 14 days
            if utc_time < start + duration and utc_time + 14 * 24 * 3600 >= start:
                contests.append({
                    "platform": "CodeForces",
                    "name": c["name"],
                    "startTime": start,
                    "duration": duration,
                    "url": f"https://codeforces.com/contestRegistration/{c['id']}"
                })

        print(f"[CodeForces] Fetched {len(contests)} contests.")
    except Exception as e:
        print(f"[CodeForces] FAILED: {e}")

    return contests
