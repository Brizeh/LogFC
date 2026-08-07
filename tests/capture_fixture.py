#!/usr/bin/env python3
"""Capture les donnees d'un log dps.report dans tests/fixtures/.

Telecharge la reponse de l'API JSON et l'enregistre pour que les tests
puissent rejouer le pipeline sans reseau.

    python -m tests.capture_fixture <url> [<url> ...]

Penser a lancer ensuite `python -m tests.test_pipeline --update` pour
produire la sortie de reference du nouveau boss, et
`python -m tools.update_mechanic_icd <url>` s'il manque a la table des
temps de grace.
"""
import gzip
import json
import sys
from pathlib import Path

import grequests

from src.const import REQUEST_HEADERS, DPS_REPORT_JSON_URL
from src.models.log_class import Log

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SRC_DIR = Path(__file__).resolve().parent.parent / "src"

# Un log complet pese plusieurs Mo, dont ~60% de donnees que LogFC ne lit
# jamais (statistiques de soin etendues, volumes de buffs, series par
# seconde, donnees de combat replay brutes...). On les retire des fixtures
# pour garder le depot leger. Prudence : une cle n'est retiree que si elle
# n'apparait nulle part dans src/ ET qu'elle est volumineuse, pour que les
# petites cles restent presentes meme en cas d'acces dynamique.
STRIP_MIN_BYTES = 10 * 1024


def _source_text():
    return "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in SRC_DIR.rglob("*.py")
    )


def _is_referenced(key, source):
    return f'"{key}"' in source or f"'{key}'" in source


def _strip(container, source):
    """Retire les cles volumineuses jamais referencees dans src/."""
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


def capture(urls):
    FIXTURES_DIR.mkdir(exist_ok=True)

    requests = [grequests.get(DPS_REPORT_JSON_URL + url, headers=REQUEST_HEADERS)
                for url in urls]
    responses = grequests.map(requests, size=len(urls))

    for i, url in enumerate(urls):
        log = Log(url)
        log.set_pjcontent(responses[i])
        if log.pjcontent is None:
            print(f"echec: {url}")
            continue

        removed = strip_unused(log.pjcontent)
        print(f"  elagage: {removed // 1024} Ko de donnees non lues retirees")

        name = log.short_name
        path = FIXTURES_DIR / f"{name}.pjcontent.json.gz"
        with gzip.open(path, "wt", encoding="utf-8") as f:
            json.dump(log.pjcontent, f, separators=(",", ":"))
        print(f"  {path.name} ({path.stat().st_size // 1024} Ko)")

        # l'url d'origine est necessaire au rejeu (elle sert de cle dans ARXIV)
        with open(FIXTURES_DIR / f"{name}.url.txt", "w", encoding="utf-8") as f:
            f.write(url)
        print(f"{name}: ok")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    capture(sys.argv[1:])
