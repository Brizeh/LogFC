"""Rejoue le pipeline LogFC sur des fixtures, sans reseau.

Sert aux tests et a toute verification manuelle. Le rejeu est
deterministe : l'etat global est reinitialise, les appels wingman sont
neutralises et CUSTOM_NAMES est vide pour que la sortie ne depende pas
du fichier local de surnoms.
"""
import gzip
import json
from pathlib import Path

from src import func
from src.const import (
    ALL_BOSSES, ALL_PLAYERS, ARXIV, CUSTOM_NAMES, DUPS_CHECKER, EXTRA_MECHS,
)
from src.input import InputParser
from src.languages import LANGUES
from src.models import boss_class
from src.models.boss_facto import BossFactory
from src.models.log_class import Log

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

FIXED_PERCENTILE = 50


class _FakeWingmanResponse:
    """Reponse wingman constante, pour un rejeu sans reseau ni aleas."""

    @staticmethod
    def json():
        return {"percentile": FIXED_PERCENTILE}


def _no_network(*args, **kwargs):
    return _FakeWingmanResponse()


def available():
    return sorted(p.name.split(".")[0] for p in FIXTURES_DIR.glob("*.url.txt"))


def load(name, directory=FIXTURES_DIR):
    directory = Path(directory)
    url = (directory / f"{name}.url.txt").read_text(encoding="utf-8").strip()
    payloads = []
    for kind in ("jcontent", "pjcontent"):
        with gzip.open(directory / f"{name}.{kind}.json.gz", "rt", encoding="utf-8") as f:
            payloads.append(json.load(f))
    return url, payloads[0], payloads[1]


def reset_state():
    ALL_BOSSES.clear()
    ALL_PLAYERS.clear()
    ARXIV.clear()
    EXTRA_MECHS.clear()
    DUPS_CHECKER.clear()
    CUSTOM_NAMES.clear()


def run(names, language="FR", directory=FIXTURES_DIR):
    """Rejoue un run complet et renvoie (message, copie d'ARXIV)."""
    reset_state()
    LANGUES["selected_language"] = LANGUES[language]

    original_get = boss_class.requests.get
    boss_class.requests.get = _no_network
    try:
        loaded = [load(name, directory) for name in names]
        # InputParser alimente DUPS_CHECKER, dont depend le comptage des fails
        urls = InputParser("\n".join(url for url, _, _ in loaded)).urls

        by_url = {url: (jc, pjc) for url, jc, pjc in loaded}
        logs = []
        for url in urls:
            log = Log(url)
            log.jcontent, log.pjcontent = by_url[url]
            logs.append(log)

        for log in logs:
            BossFactory.create_boss(log)

        message = "\n".join(func.get_message_reward(ALL_BOSSES, ALL_PLAYERS))
        return message, json.loads(json.dumps(ARXIV))
    finally:
        boss_class.requests.get = original_get
