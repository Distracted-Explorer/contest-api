import requests
from datetime import datetime, timezone


def fetch():
    contests = []
    headers = {"User-Agent": "Mozilla/5.0"}
    utc_time = int(datetime.now(timezone.utc).timestamp())
    three_days = 3 * 24 * 3600

    try:
        cc = requests.get(
            "https://www.codechef.com/api/list/contests/all",
            headers=headers,
            timeout=10
        ).json()

        # future_contests + present_contests cover upcoming and running
        # past_contests covers recently ended ones
        all_buckets = (
            cc.get("future_contests", []) +
            cc.get("present_contests", []) +
            cc.get("past_contests", [])
        )

        for c in all_buckets:
            dt = datetime.fromisoformat(c["contest_start_date_iso"])
            timestamp = int(dt.timestamp())
            duration_sec = int(c["contest_duration"]) * 60
            end = timestamp + duration_sec
            # Include: upcoming (within 14 days), running, or ended within last 3 days
            if utc_time + 14 * 24 * 3600 >= timestamp and utc_time < end + three_days:
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
