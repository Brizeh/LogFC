"""Reproduction of Elite Insights' mechanics table.

dps.report exposes two things: a JSON API, and an HTML page from which a
richer structure can be extracted. The latter contains a
`mechanicStats` table already aggregated by player and by phase, which
LogFC used to read by scraping the HTML.

This module recomputes that table from the raw events of the JSON API
alone. The rule, found by comparing 7676 reference cells and then
confirmed in Elite Insights' source, comes down to three points:

- the value is a **sum of weights** (`weight`), not an event count: a
  "Breakbar Damage" weighs the amount of damage dealt
- each mechanic carries an **internal cooldown** (icd) during which a
  new event does not count
- this window starts at t=0 and **rearms on every event**, even ignored
  ones: a burst of closely spaced events therefore only counts the first

The icd only exists on the HTML page: it is frozen into
`mechanic_icd.json`, fed by `tools/update_mechanic_icd.py`.
"""
import json
from pathlib import Path

_ICD_PATH = Path(__file__).resolve().parent / "mechanic_icd.json"

try:
    with open(_ICD_PATH, encoding="utf-8") as _file:
        ICD_TABLE = json.load(_file)
except FileNotFoundError:
    ICD_TABLE = {}

# Status mechanics, which the HTML did not count among player
# mechanics even though their actors are players. Excluded explicitly.
STATUS_MECHANICS = {"Dead", "Downed", "Got up", "Res"}

_warned = set()


def _warn_once(key, message):
    if key not in _warned:
        _warned.add(key)
        print(message)


def get_icd(trigger_id: int, mech_name: str):
    """Internal cooldown of a mechanic, 0 if unknown (with a warning)."""
    boss = ICD_TABLE.get(str(trigger_id))
    if boss is None:
        _warn_once(trigger_id,
                   f"mechanic icd: boss {trigger_id} missing from mechanic_icd.json, "
                   "assuming icd 0 (see tools/update_mechanic_icd.py)")
        return 0
    if mech_name not in boss:
        _warn_once((trigger_id, mech_name),
                   f"mechanic icd: {mech_name!r} unknown for boss {trigger_id}, "
                   "assuming icd 0 (see tools/update_mechanic_icd.py)")
        return 0
    return boss[mech_name]


def player_mechanics(pjcontent):
    """Mechanics suffered by players, in the order of the HTML page."""
    players = {player["name"] for player in pjcontent["players"]}
    mechanics = []
    for mechanic in pjcontent["mechanics"]:
        if mechanic["fullName"] in STATUS_MECHANICS:
            continue
        actors = {data["actor"] for data in mechanic["mechanicsData"]}
        if actors and actors <= players:
            mechanics.append(mechanic)
    return mechanics


def mech_value(mechanic, actor: str, icd: int, start: int, end: int, exclude=()):
    """Value of a mechanic for a player over a time interval.

    `exclude` is an iterable of (start_ms, end_ms) ranges: events falling
    in any of them are dropped before the icd window is applied, as if
    they had never fired. Used for boss-specific one-off adjustments,
    see Boss.mechanic_exclusions.
    """
    events = sorted(
        (data["time"], data.get("weight", 1))
        for data in mechanic["mechanicsData"]
        if data["actor"] == actor and start <= data["time"] <= end
        and not any(lo <= data["time"] <= hi for lo, hi in exclude)
    )
    total, last = 0, 0
    for time, weight in events:
        if time - last >= icd:
            total += weight
        last = time
    return total
