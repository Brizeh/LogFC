"""Geometry helpers for the HTML page's combat-replay data (_crData).

dps.report's public JSON API (getJson) does not expose hazard entities
that carry no combat stats. Some, like Soulless Horror's moving walls
("SurgingSoul" in Elite Insights), only exist as decorations in the
page's own combat replay viewer, driven by this blob.

This is therefore the only other place in the project that reads the
HTML page (besides tools/update_mechanic_icd.py), and only for bosses
that declare Boss.needs_replay_data = True -- currently just SH.
fetch_replay_data must run before the corresponding Boss objects are
constructed: MVP/LVP computation happens synchronously in
Boss.__init__, unlike wingman.fetch_percentiles which runs on
already-built bosses afterwards.
"""
import json

import grequests

from .const import REQUEST_HEADERS
from .models.boss_class import Boss

RECTANGLE_TYPE = 15


def parse(html: str):
    """Extracts and parses the _crData blob from a log's HTML page.

    Only present on the newer page template (paired with `const
    _logData =`). Returns None if absent or malformed; callers must
    treat that as "no replay data available", not fail.
    """
    try:
        raw = html.split('const _crData = ')[1].split('const _graphData =')[0].rsplit(';', 1)[0]
        return json.loads(raw.strip())
    except (IndexError, ValueError):
        return None


def fetch_replay_data(logs):
    """Fetches _crData for logs whose boss needs it, in one parallel pass."""
    needing = [log for log in logs
               if Boss.registry.get(log.pjcontent['triggerID'], Boss).needs_replay_data]
    if not needing:
        return
    responses = grequests.map(
        [grequests.get(log.url, headers=REQUEST_HEADERS) for log in needing],
        size=len(needing),
    )
    for log, response in zip(needing, responses):
        log.replay_data = parse(response.content.decode("utf-8")) if response else None


def _pairs(flat):
    return [(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)]


def rectangles(crdata, color_substring: str):
    """Moving rectangle decorations of a given color.

    Half-extents are resolved to pixel space (the same space as
    players' combatReplayData positions) via inchToPixel, so callers
    never handle the inch/pixel conversion themselves.
    """
    if not crdata:
        return []
    inch_to_pixel = crdata["inchToPixel"]
    polling_rate = crdata["pollingRate"]
    actors_by_id = {a["id"]: a for a in crdata["actors"] if "id" in a}
    signatures = {
        d["signature"]: d
        for d in crdata["decorationMetadata"]
        if d.get("type") == RECTANGLE_TYPE and color_substring in d.get("color", "")
    }

    result = []
    for rendering in crdata["decorationRenderings"]:
        meta = signatures.get(rendering.get("metadataSignature"))
        if meta is None:
            continue
        actor = actors_by_id.get(rendering["connectedTo"]["masterID"])
        if actor is None:
            continue
        result.append({
            "start": rendering["start"],
            "end": rendering["end"],
            "half_width": meta["width"] * inch_to_pixel / 2,
            "half_height": meta["height"] * inch_to_pixel / 2,
            "positions": _pairs(actor["positions"]),
            "actor_start": actor["start"],
            "polling_rate": polling_rate,
        })
    return result


def contains(rectangle, xy, t: int) -> bool:
    """Whether a point is inside a moving rectangle at time t."""
    if not (rectangle["start"] <= t <= rectangle["end"]):
        return False
    index = (t - rectangle["actor_start"]) // rectangle["polling_rate"]
    positions = rectangle["positions"]
    if not (0 <= index < len(positions)):
        return False
    cx, cy = positions[index]
    x, y = xy
    return abs(x - cx) <= rectangle["half_width"] and abs(y - cy) <= rectangle["half_height"]
