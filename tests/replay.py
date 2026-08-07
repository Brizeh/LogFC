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
from src.analysis import Analysis
from src.const import CUSTOM_NAMES
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


def build(names, directory=FIXTURES_DIR):
    """Prepare une Analysis et ses Log, sans encore creer les boss."""
    analysis = Analysis()
    loaded = [load(name, directory) for name in names]
    # InputParser alimente analysis.dups, d'ou vient le comptage des fails
    urls = InputParser("\n".join(url for url, _, _ in loaded), analysis).urls

    by_url = {url: (jc, pjc) for url, jc, pjc in loaded}
    logs = []
    for url in urls:
        log = Log(url)
        log.jcontent, log.pjcontent = by_url[url]
        logs.append(log)
    return analysis, logs


def message_of(analysis):
    return "\n".join(func.get_message_reward(analysis))


def no_network():
    """Contexte neutralisant les appels wingman et les surnoms locaux."""
    class _Patch:
        def __enter__(self):
            CUSTOM_NAMES.clear()
            self.original = boss_class.requests.get
            boss_class.requests.get = _no_network
        def __exit__(self, *exc):
            boss_class.requests.get = self.original
    return _Patch()


def run(names, language="FR", directory=FIXTURES_DIR):
    """Rejoue un run complet et renvoie (message, copie de l'arxiv)."""
    LANGUES["selected_language"] = LANGUES[language]
    with no_network():
        analysis, logs = build(names, directory)
        for log in logs:
            BossFactory.create_boss(log, analysis)
        return message_of(analysis), json.loads(json.dumps(analysis.arxiv))
