"""Rejoue le pipeline LogFC sur des fixtures, sans reseau.

Sert aux tests et a toute verification manuelle. Le rejeu est
deterministe : chaque appel part d'une Analysis neuve, les appels
wingman sont neutralises et CUSTOM_NAMES est vide pour que la sortie ne
depende pas du fichier local de surnoms.
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
    """Remplace la passe wingman par une note constante."""
    for boss in bosses:
        boss.wingman_percentile = FIXED_PERCENTILE


def available():
    return sorted(p.name.split(".")[0] for p in FIXTURES_DIR.glob("*.url.txt"))


def load(name, directory=FIXTURES_DIR):
    directory = Path(directory)
    url = (directory / f"{name}.url.txt").read_text(encoding="utf-8").strip()
    with gzip.open(directory / f"{name}.pjcontent.json.gz", "rt", encoding="utf-8") as f:
        return url, json.load(f)


def build(names, language="FR", directory=FIXTURES_DIR):
    """Prepare une Analysis et ses Log, sans encore creer les boss."""
    analysis = Analysis(language=language)
    loaded = [load(name, directory) for name in names]
    # InputParser alimente analysis.dups, d'ou vient le comptage des fails
    urls = InputParser("\n".join(url for url, _ in loaded), analysis).urls

    by_url = dict(loaded)
    logs = []
    for url in urls:
        log = Log(url)
        log.pjcontent = by_url[url]
        logs.append(log)
    return analysis, logs


def message_of(analysis):
    return "\n".join(func.get_message_reward(analysis))


def no_network():
    """Contexte neutralisant la passe wingman et les surnoms locaux."""
    class _Patch:
        def __enter__(self):
            CUSTOM_NAMES.clear()
            self.original = wingman.fetch_percentiles
            wingman.fetch_percentiles = _fixed_percentiles
        def __exit__(self, *exc):
            wingman.fetch_percentiles = self.original
    return _Patch()


def run(names, language="FR", directory=FIXTURES_DIR):
    """Rejoue un run complet et renvoie (message, copie de l'arxiv)."""
    with no_network():
        analysis, logs = build(names, language, directory)
        for log in logs:
            BossFactory.create_boss(log, analysis)
        wingman.fetch_percentiles(analysis.bosses)
        return message_of(analysis), json.loads(json.dumps(analysis.arxiv))
