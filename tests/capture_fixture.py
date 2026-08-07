#!/usr/bin/env python3
"""Capture les donnees d'un log dps.report dans tests/fixtures/.

Telecharge les deux charges utiles d'un log (jcontent scrape depuis la
page HTML, pjcontent depuis l'API JSON) et les enregistre pour que les
tests puissent rejouer le pipeline sans reseau.

    python -m tests.capture_fixture <url> [<url> ...]

Les fichiers sont gzippes : un log pese environ 1 Mo en JSON brut, une
centaine de Ko compresse.
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


def strip_unused(jcontent, pjcontent):
    source = _source_text()
    removed = 0
    for payload in (jcontent, pjcontent):
        removed += _strip(payload, source)
        for collection in ("players", "targets", "phases"):
            for entry in payload.get(collection, []):
                if isinstance(entry, dict):
                    removed += _strip(entry, source)
    return removed


def capture(urls):
    FIXTURES_DIR.mkdir(exist_ok=True)

    requests = []
    for url in urls:
        requests.append(grequests.get(url))
        requests.append(grequests.get(DPS_REPORT_JSON_URL + url, headers=REQUEST_HEADERS))
    responses = grequests.map(requests, size=2 * len(urls))

    for i, url in enumerate(urls):
        log = Log(url)
        log.set_jcontent(responses[2 * i])
        log.set_pjcontent(responses[2 * i + 1])
        if log.jcontent is None or log.pjcontent is None:
            print(f"echec: {url}")
            continue

        removed = strip_unused(log.jcontent, log.pjcontent)
        print(f"  elagage: {removed // 1024} Ko de donnees non lues retirees")

        name = log.short_name
        for suffix, data in (("jcontent", log.jcontent), ("pjcontent", log.pjcontent)):
            path = FIXTURES_DIR / f"{name}.{suffix}.json.gz"
            with gzip.open(path, "wt", encoding="utf-8") as f:
                json.dump(data, f, separators=(",", ":"))
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
