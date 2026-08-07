#!/usr/bin/env python3
"""Tests hors-ligne de LogFC.

    python -m tests.test_pipeline

Aucune dependance externe, aucun acces reseau : le pipeline est rejoue
sur les fixtures de tests/fixtures (voir tests/capture_fixture.py pour
en ajouter).

Pour regenerer la sortie de reference apres un changement volontaire :

    python -m tests.test_pipeline --update
"""
import sys
from pathlib import Path

from src.const import BOSS_DICT, EXTRA_BOSS_DICT
from src.languages_dict.english import english
from src.languages_dict.french import french
from src.models.boss_facto import _BOSS_FACTORY
from tests import replay

EXPECTED_DIR = Path(__file__).resolve().parent / "expected"
RUN_FIXTURES = ["sh", "dei", "adina"]

_cache = {}


def run_reference():
    """Rejoue le run de reference, une seule fois par execution."""
    if "run" not in _cache:
        _cache["run"] = replay.run(RUN_FIXTURES)
    return _cache["run"]


def _read(path):
    return path.read_text(encoding="utf-8").splitlines()


def _write(path, text):
    path.parent.mkdir(exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ############################### TESTS ###############################

def test_run_message_unchanged():
    """Le message produit pour un run connu ne change pas."""
    message, _ = run_reference()
    expected_path = EXPECTED_DIR / "run_message.txt"
    assert expected_path.exists(), "sortie de reference absente, lancer --update"
    assert message.splitlines() == _read(expected_path), (
        "le message a change ; verifier le diff puis --update si c'est voulu"
    )


def test_arxiv_is_keyed_by_account():
    """ARXIV est indexe par compte, pas par surnom d'affichage."""
    _, arxiv = run_reference()
    assert arxiv, "ARXIV est vide"
    for url, accounts in arxiv.items():
        assert url.startswith("https://dps.report/"), f"cle de log inattendue: {url}"
        for account in accounts:
            assert "." in account, f"{account!r} ne ressemble pas a un compte GW2"


def test_arxiv_stats_are_snapshots():
    """Chaque stat porte une valeur et une description, sans moyenne derivee.

    Les noms commencant par "avg" sont legitimes quand dps.report fournit
    deja un pourcentage (avgCritRate, avgBoons...). Ce qui n'a rien a faire
    ici, c'est un avgX double d'un X presente dans la meme categorie : la
    moyenne se calcule en aval, sur plusieurs logs.
    """
    _, arxiv = run_reference()
    for accounts in arxiv.values():
        for categories in accounts.values():
            for category, stats in categories.items():
                for name, stat in stats.items():
                    assert set(stat) == {"value", "description"}, (
                        f"{category}/{name} a des cles inattendues: {sorted(stat)}"
                    )
                    if name.startswith("avg"):
                        assert name[3:] not in stats, (
                            f"{category}/{name} double {category}/{name[3:]} : "
                            "les moyennes se calculent en aval, pas a l'ecriture"
                        )


def test_core_stats_have_descriptions():
    """Les stats decrites a la main dans ALL_MECHS ne perdent pas leur libelle."""
    _, arxiv = run_reference()
    for accounts in arxiv.values():
        for categories in accounts.values():
            for stats in categories.values():
                for name, stat in stats.items():
                    assert stat["description"], f"{name} n'a pas de description"


def test_every_boss_is_reachable():
    """Tout boss du factory est atteignable depuis un triggerID, et vice versa."""
    known = set(BOSS_DICT.values()) | set(EXTRA_BOSS_DICT.values())
    orphans = known - set(_BOSS_FACTORY)
    assert not orphans, f"triggerID sans classe (KeyError au parsing): {sorted(orphans)}"
    unreachable = set(_BOSS_FACTORY) - known
    assert not unreachable, (
        f"classes sans triggerID (boss ignore silencieusement): {sorted(unreachable)}"
    )


def test_languages_have_the_same_keys():
    """Une cle de message existe en francais et en anglais."""
    missing_en = sorted(set(french) - set(english))
    missing_fr = sorted(set(english) - set(french))
    assert not missing_en, f"absentes de english.py: {missing_en}"
    assert not missing_fr, f"absentes de french.py: {missing_fr}"


# ############################### RUNNER ###############################

TESTS = [
    test_run_message_unchanged,
    test_arxiv_is_keyed_by_account,
    test_arxiv_stats_are_snapshots,
    test_core_stats_have_descriptions,
    test_every_boss_is_reachable,
    test_languages_have_the_same_keys,
]


def update_expected():
    message, _ = replay.run(RUN_FIXTURES)
    _write(EXPECTED_DIR / "run_message.txt", message)
    print(f"sortie de reference mise a jour ({len(message.splitlines())} lignes)")


def main():
    if "--update" in sys.argv:
        update_expected()
        return 0

    if not replay.available():
        print("fixtures absentes. Les capturer avec :")
        print("  python -m tests.capture_fixture <url> [<url> ...]")
        return 1

    failures = 0
    for test in TESTS:
        try:
            test()
        except AssertionError as error:
            failures += 1
            print(f"ECHEC  {test.__name__}\n       {error}")
        except Exception as error:  # noqa: BLE001 - on veut voir l'erreur brute
            failures += 1
            print(f"ERREUR {test.__name__}\n       {type(error).__name__}: {error}")
        else:
            print(f"ok     {test.__name__}")

    print(f"\n{len(TESTS) - failures}/{len(TESTS)} tests passes")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
