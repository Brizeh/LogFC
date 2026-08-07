#!/usr/bin/env python3
"""Enriches src/mechanic_icd.json from dps.report's HTML pages.

    python -m tools.update_mechanic_icd <url> [<url> ...]

Each mechanic carries an internal cooldown (icd) during which a new
event does not count. LogFC needs it to reproduce Elite Insights'
aggregated values, but the JSON API doesn't expose it: only the HTML
page contains it, in its `_logData` variable.

This is therefore the only place in the project that still reads HTML,
and it only runs on demand: the program itself only uses the JSON API.
Rerun it when a boss is missing from the table (LogFC warns about it)
or after an Elite Insights update.
"""
import json
import sys
from pathlib import Path

import requests

from src.const import REQUEST_HEADERS

ICD_PATH = Path(__file__).resolve().parent.parent / "src" / "mechanic_icd.json"


def scrape_log_data(html: str):
    """Extracts the _logData variable from a log's page.

    Two formats coexist depending on the log's age, hence the two attempts.
    """
    try:
        raw = html.split('var _logData = ')[1] \
                  .split('var logData = _logData;')[0].rsplit(';', 1)[0]
        return json.loads(raw.strip())
    except (IndexError, ValueError):
        pass
    try:
        raw = html.split('const _logData = ')[1] \
                  .split('const _crData =')[0].rsplit(';', 1)[0]
        return json.loads(raw.strip())
    except (IndexError, ValueError):
        return None


def load_table():
    try:
        with open(ICD_PATH, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_table(table):
    ICD_PATH.write_text(
        json.dumps(table, indent=1, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(urls):
    table = load_table()
    added = 0

    for url in urls:
        response = requests.get(url, headers=REQUEST_HEADERS)
        if not response.ok:
            print(f"{url}: http {response.status_code}")
            continue
        log_data = scrape_log_data(response.text)
        if log_data is None:
            print(f"{url}: _logData not found (page format changed?)")
            continue

        trigger_id = str(log_data["triggerID"])
        # record every player mechanic, zero icd included: a missing
        # entry must mean "unknown", not "icd zero"
        mechanics = {
            mechanic["name"]: mechanic["icd"]
            for mechanic in log_data["mechanicMap"]
            if mechanic["playerMech"]
        }
        known = table.get(trigger_id, {})
        new = {name: icd for name, icd in mechanics.items() if name not in known}
        table.setdefault(trigger_id, {}).update(mechanics)
        added += len(new)
        print(f"{url}\n  boss {trigger_id}: {len(mechanics)} mechanics, {len(new)} new")

    save_table(table)
    print(f"\n{ICD_PATH.name}: {len(table)} bosses, {added} mechanics added")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
