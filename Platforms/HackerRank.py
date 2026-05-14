import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import re
import time


def fetch():
    contests = {}  # keyed by slug
    headers = {"User-Agent": "Mozilla/5.0"}
    utc_now     = int(datetime.now(timezone.utc).timestamp())
    three_days  = 3  * 24 * 3600
    fourteen_days = 14 * 24 * 3600

    # ── 1. API fetch (upcoming + active) ─────────────────────────────────────
    for url in [
        "https://www.hackerrank.com/rest/contests/upcoming",
        "https://www.hackerrank.com/rest/contests/active",
    ]:
        try:
            data = requests.get(url, headers=headers, timeout=10).json()
            for c in data.get("models", []):
                if c.get("name") == "ProjectEuler+":
                    continue
                slug  = c["slug"]
                start = c["epoch_starttime"]
                end   = c["epoch_endtime"]
                if utc_now + fourteen_days >= start and utc_now < end + three_days:
                    contests[slug] = {
                        "platform":  "HackerRank",
                        "name":      c["name"],
                        "startTime": start,
                        "duration":  end - start,
                        "url":       f"https://www.hackerrank.com/contests/{slug}/challenges",
                        "source":    "api",
                    }
        except Exception as e:
            print(f"[HackerRank] API FAILED ({url}): {e}")

    print(f"[HackerRank] API found {len(contests)} contests.")

    # ── 2. Scrape /contests page for anything the API missed ──────────────────
    scraped_slugs = []
    try:
        resp = requests.get(
            "https://www.hackerrank.com/contests",
            headers=headers,
            timeout=15
        )
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find "Upcoming Contests" section, then walk siblings
        upcoming_header = soup.find(
            lambda tag: tag.name in ("h2", "h3", "h4", "h5", "span", "p", "div")
            and "upcoming" in tag.get_text(strip=True).lower()
            and "contest" in tag.get_text(strip=True).lower()
        )

        seen_names = set()

        if upcoming_header:
            for sibling in upcoming_header.find_next_siblings():
                stext = sibling.get_text(strip=True).lower()
                if any(kw in stext for kw in ("active contest", "archived contest", "college contest")):
                    break
                for a in sibling.find_all("a", href=True):
                    m = re.search(r"/contests/([^/?#]+)", a["href"])
                    if not m:
                        continue
                    slug = m.group(1)
                    if slug in ("archived", "college") or slug in contests:
                        continue
                    name = a.get_text(strip=True)
                    if not name or name in seen_names:
                        continue
                    seen_names.add(name)
                    scraped_slugs.append((slug, name))
        else:
            # Fallback: any link near upcoming-intent keywords
            for a in soup.find_all("a", href=re.compile(r"/contests/[^/?#]+")):
                m = re.search(r"/contests/([^/?#]+)", a["href"])
                if not m:
                    continue
                slug = m.group(1)
                if slug in ("archived", "college") or slug in contests:
                    continue
                parent_text = (a.parent or a).get_text(strip=True).lower()
                if any(kw in parent_text for kw in ("register", "upcoming", "starts", "open till")):
                    name = a.get_text(strip=True) or slug
                    if not name or name in seen_names:
                        continue
                    seen_names.add(name)
                    scraped_slugs.append((slug, name))

    except Exception as e:
        print(f"[HackerRank] Scrape FAILED: {e}")

    # ── 3. Resolve startTime/duration for scraped slugs via per-contest API ───
    for slug, fallback_name in scraped_slugs:
        try:
            time.sleep(0.3)  # be polite
            detail = requests.get(
                f"https://www.hackerrank.com/rest/contests/{slug}",
                headers=headers,
                timeout=10
            ).json()

            model = detail.get("model") or detail  # some endpoints wrap, some don't
            name  = model.get("name") or fallback_name

            if name == "ProjectEuler+":
                continue

            start = model.get("epoch_starttime")
            end   = model.get("epoch_endtime")

            # Both must be present and numeric
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                print(f"[HackerRank] No time data for scraped slug '{slug}', skipping.")
                continue

            start, end = int(start), int(end)

            if utc_now + fourteen_days >= start and utc_now < end + three_days:
                print(f"[HackerRank] Scrape resolved: {name} | start={start} end={end}")
                contests[slug] = {
                    "platform":  "HackerRank",
                    "name":      name,
                    "startTime": start,          # UTC seconds
                    "duration":  end - start,    # seconds
                    "url":       f"https://www.hackerrank.com/contests/{slug}/challenges",
                    "source":    "scrape",
                }

        except Exception as e:
            print(f"[HackerRank] Detail fetch FAILED for '{slug}': {e}")

    result = list(contests.values())
    api_count    = sum(1 for c in result if c["source"] == "api")
    scrape_count = sum(1 for c in result if c["source"] == "scrape")
    print(f"[HackerRank] Total: {len(result)} ({api_count} api, {scrape_count} scrape).")
    return result