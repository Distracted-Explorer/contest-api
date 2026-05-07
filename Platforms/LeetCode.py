import requests
from datetime import datetime, timezone


def fetch():
    contests = []
    headers = {"User-Agent": "Mozilla/5.0"}
    utc_time = int(datetime.now(timezone.utc).timestamp())

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
            # Include if not yet ended
            if utc_time < start + duration:
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
