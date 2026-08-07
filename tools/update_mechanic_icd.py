#!/usr/bin/env python3
"""Enrichit src/mechanic_icd.json depuis les pages HTML de dps.report.

    python -m tools.update_mechanic_icd <url> [<url> ...]

Chaque mecanique porte un temps de grace (icd) pendant lequel un nouvel
evenement ne compte pas. LogFC en a besoin pour reproduire les valeurs
agregees d'Elite Insights, mais l'API JSON ne l'expose pas : seule la
page HTML le contient, dans sa variable `_logData`.

C'est donc le seul endroit du projet qui lit encore le HTML, et il ne
tourne qu'a la demande : le programme, lui, n'utilise que l'API JSON.
A relancer quand un boss manque a la table (LogFC l'avertit) ou apres
une mise a jour d'Elite Insights.
"""
import json
import sys
from pathlib import Path

import requests

from src.const import REQUEST_HEADERS

ICD_PATH = Path(__file__).resolve().parent.parent / "src" / "mechanic_icd.json"


def scrape_log_data(html: str):
    """Extrait la variable _logData de la page d'un log.

    Deux formats coexistent selon l'age du log, d'ou les deux tentatives.
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
            print(f"{url} : http {response.status_code}")
            continue
        log_data = scrape_log_data(response.text)
        if log_data is None:
            print(f"{url} : _logData introuvable (format de page modifie ?)")
            continue

        trigger_id = str(log_data["triggerID"])
        # on enregistre toutes les mecaniques joueur, icd nul compris :
        # l'absence d'une entree doit signifier "inconnu", pas "icd nul"
        mechanics = {
            mechanic["name"]: mechanic["icd"]
            for mechanic in log_data["mechanicMap"]
            if mechanic["playerMech"]
        }
        known = table.get(trigger_id, {})
        new = {name: icd for name, icd in mechanics.items() if name not in known}
        table.setdefault(trigger_id, {}).update(mechanics)
        added += len(new)
        print(f"{url}\n  boss {trigger_id} : {len(mechanics)} mecaniques, {len(new)} nouvelles")

    save_table(table)
    print(f"\n{ICD_PATH.name} : {len(table)} boss, {added} mecaniques ajoutees")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
