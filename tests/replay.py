"""Replays the LogFC pipeline against fixtures, without any network.

Used by the tests and for any manual check. The replay is
deterministic: each call starts from a fresh Analysis, wingman calls
are neutralized, and CUSTOM_NAMES is empty so the output doesn't depend
on the local nicknames file.
"""
import gzip
import json
from pathlib import Path

from src import func
from src import wingman
from src.analysis import Analysis
from src.const import CUSTOM_NAMES
from src.input import InputParser
from src.models.boss_facto import BossFactory
from src.models.log_class import Log

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

FIXED_PERCENTILE = 50


def _fixed_percentiles(bosses):
    """Replaces the wingman pass with a constant grade."""
    for boss in bosses:
        boss.wingman_percentile = FIXED_PERCENTILE


def available():
    return sorted(p.name.split(".")[0] for p in FIXTURES_DIR.glob("*.url.txt"))


def load(name, directory=FIXTURES_DIR):
    directory = Path(directory)
    url = (directory / f"{name}.url.txt").read_text(encoding="utf-8").strip()
    with gzip.open(directory / f"{name}.pjcontent.json.gz", "rt", encoding="utf-8") as f:
        pjcontent = json.load(f)
    crpath = directory / f"{name}.crdata.json.gz"
    replay_data = None
    if crpath.exists():
        with gzip.open(crpath, "rt", encoding="utf-8") as f:
            replay_data = json.load(f)
    return url, pjcontent, replay_data


def build(names, language="FR", directory=FIXTURES_DIR):
    """Prepares an Analysis and its Logs, without creating the bosses yet."""
    analysis = Analysis(language=language)
    loaded = [load(name, directory) for name in names]
    # InputParser feeds analysis.dups, which the fail count comes from
    urls = InputParser("\n".join(url for url, _, _ in loaded), analysis).urls

    by_url = {url: (pjcontent, replay_data) for url, pjcontent, replay_data in loaded}
    logs = []
    for url in urls:
        log = Log(url)
        log.pjcontent, log.replay_data = by_url[url]
        logs.append(log)
    return analysis, logs


def message_of(analysis):
    return "\n".join(func.get_message_reward(analysis))


def no_network():
    """Context that neutralizes the wingman pass and local nicknames."""
    class _Patch:
        def __enter__(self):
            CUSTOM_NAMES.clear()
            self.original = wingman.fetch_percentiles
            wingman.fetch_percentiles = _fixed_percentiles
        def __exit__(self, *exc):
            wingman.fetch_percentiles = self.original
    return _Patch()


def run(names, language="FR", directory=FIXTURES_DIR):
    """Replays a full run and returns (message, copy of the arxiv)."""
    with no_network():
        analysis, logs = build(names, language, directory)
        for log in logs:
            BossFactory.create_boss(log, analysis)
        wingman.fetch_percentiles(analysis.bosses)
        return message_of(analysis), json.loads(json.dumps(analysis.arxiv))
