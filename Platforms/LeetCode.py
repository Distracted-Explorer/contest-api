import requests
from datetime import datetime, timezone


def fetch():
    contests = []
    headers = {"User-Agent": "Mozilla/5.0"}
    utc_time = int(datetime.now(timezone.utc).timestamp())
    three_days = 3 * 24 * 3600

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

    try:
        lc = requests.post(
            "https://leetcode.com/graphql",
            json=query,
            headers=headers,
            timeout=10
        ).json()

        for c in lc["data"]["allContests"]:
            start = c["startTime"]
            duration = c["duration"]
            end = start + duration
            # Include: upcoming, running, or ended within last 3 days
            if utc_time < end + three_days:
                contests.append({
                    "platform": "LeetCode",
                    "name": c["title"],
                    "startTime": start,
                    "duration": duration,
                    "url": f"https://leetcode.com/contest/{c['titleSlug']}"
                })

        print(f"[LeetCode] Fetched {len(contests)} contests.")
    except Exception as e:
        print(f"[LeetCode] FAILED: {e}")

    return contests
