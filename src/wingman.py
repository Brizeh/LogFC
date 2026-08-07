"""Performance grades from gw2wingman.

Each boss gets a percentile: where its kill time ranks against other
logs of the same boss. That's one HTTP call per boss, formerly issued
from Boss's constructor, so one after another. On a five-log run, this
sequential wait accounted for 80% of the total time.

These calls are now grouped into a single pass, after the bosses are
created and before the message is formatted. Threads are used instead
of grequests: this module is meant to be imported by the Discord bot,
and grequests monkey-patches gevent onto the whole process, which
doesn't cohabit well with asyncio.
"""
from concurrent.futures import ThreadPoolExecutor

import requests

API_URL = "https://gw2wingman.nevermindcreations.de/api/getPercentileByMetadata"
MAX_PARALLEL = 10


def url_for(boss):
    timestamp = int(boss.start_date.timestamp())
    return (f"{API_URL}?bossID={boss.boss_id}&isCM={boss.cm}"
            f"&duration={boss.duration_ms}&timestamp={timestamp}")


def _percentile(boss):
    try:
        infos = requests.get(url_for(boss)).json()
    except Exception:
        print("wingman percentile failed")
        return None
    # a zero percentile is treated as absent, the grade then disappears
    # from the message: this is the historical behavior
    return infos.get("percentile") or None


def fetch_percentiles(bosses):
    """Fills in wingman_percentile for every boss, in a single pass."""
    if not bosses:
        return
    with ThreadPoolExecutor(max_workers=min(len(bosses), MAX_PARALLEL)) as pool:
        for boss, percentile in zip(bosses, pool.map(_percentile, bosses)):
            boss.wingman_percentile = percentile
