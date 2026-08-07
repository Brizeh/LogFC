#!/usr/bin/env python3
"""Captures a dps.report log's data into tests/fixtures/.

Downloads the JSON API response (and, for a boss with
Boss.needs_replay_data, the HTML combat-replay data too) and saves them
so the tests can replay the pipeline offline.

    python -m tests.capture_fixture <url> [<url> ...]
    python -m tests.capture_fixture <url> --name <fixture_name>

--name overrides the fixture's file name (defaults to the log's boss
suffix, e.g. "sh"): needed when capturing a second log of a boss
already covered by another fixture.

Remember to then run `python -m tests.test_pipeline --update` to
produce the new boss' reference output, and
`python -m tools.update_mechanic_icd <url>` if it's missing from the
internal-cooldown table.
"""
import gzip
import json
import sys
from pathlib import Path

import grequests

from src import combat_replay
from src.const import REQUEST_HEADERS, DPS_REPORT_JSON_URL
from src.models import boss_facto  # noqa: F401 - importing it populates Boss.registry
from src.models.boss_class import Boss
from src.models.log_class import Log

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SRC_DIR = Path(__file__).resolve().parent.parent / "src"

# A full log weighs several MB, ~60% of which LogFC never reads
# (extended healing stats, buff volumes, per-second series, raw combat
# replay data...). It's stripped from fixtures to keep the repo light.
# Caution: a key is only removed if it appears nowhere in src/ AND it's
# large, so small keys survive even a dynamic access.
STRIP_MIN_BYTES = 10 * 1024


def _source_text():
    return "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in SRC_DIR.rglob("*.py")
    )


def _is_referenced(key, source):
    return f'"{key}"' in source or f"'{key}'" in source


def _strip(container, source):
    """Removes large keys never referenced anywhere in src/."""
    removed = 0
    for key in list(container):
        if _is_referenced(key, source):
            continue
        size = len(json.dumps(container[key], separators=(",", ":")))
        if size >= STRIP_MIN_BYTES:
            del container[key]
            removed += size
    return removed


def strip_unused(pjcontent):
    source = _source_text()
    removed = _strip(pjcontent, source)
    for collection in ("players", "targets", "phases"):
        for entry in pjcontent.get(collection, []):
            if isinstance(entry, dict):
                removed += _strip(entry, source)
    return removed


def capture(urls, names=None):
    FIXTURES_DIR.mkdir(exist_ok=True)
    names = names or [None] * len(urls)

    requests = [grequests.get(DPS_REPORT_JSON_URL + url, headers=REQUEST_HEADERS)
                for url in urls]
    responses = grequests.map(requests, size=len(urls))

    for i, url in enumerate(urls):
        log = Log(url)
        log.set_pjcontent(responses[i])
        if log.pjcontent is None:
            print(f"failed: {url}")
            continue

        removed = strip_unused(log.pjcontent)
        print(f"  stripped: {removed // 1024} KB of unread data removed")

        name = names[i] or log.short_name
        path = FIXTURES_DIR / f"{name}.pjcontent.json.gz"
        with gzip.open(path, "wt", encoding="utf-8") as f:
            json.dump(log.pjcontent, f, separators=(",", ":"))
        print(f"  {path.name} ({path.stat().st_size // 1024} KB)")

        # the original url is needed for replay (it's the key into ARXIV)
        with open(FIXTURES_DIR / f"{name}.url.txt", "w", encoding="utf-8") as f:
            f.write(url)

        boss = Boss.registry.get(log.pjcontent["triggerID"])
        if boss and boss.needs_replay_data:
            combat_replay.fetch_replay_data([log])
            if log.replay_data is None:
                print("  replay data: fetch failed")
            else:
                crpath = FIXTURES_DIR / f"{name}.crdata.json.gz"
                with gzip.open(crpath, "wt", encoding="utf-8") as f:
                    json.dump(log.replay_data, f, separators=(",", ":"))
                print(f"  {crpath.name} ({crpath.stat().st_size // 1024} KB)")

        print(f"{name}: ok")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    args = sys.argv[1:]
    if "--name" in args:
        i = args.index("--name")
        capture([args[0]], names=[args[i + 1]])
    else:
        capture(args)
