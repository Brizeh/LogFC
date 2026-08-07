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

from src.languages_dict.english import english
from src.languages_dict.french import french
from src.models.boss_class import Boss
from src.models import boss_facto  # noqa: F401 - son import peuple Boss.registry
from src.models.boss_facto import BossFactory
from tests import replay

EXPECTED_DIR = Path(__file__).resolve().parent / "expected"

# Un run coherent d'une meme soiree, pour couvrir le regroupement par aile,
# les GRAND MVP/LVP et la duree totale.
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


def test_each_boss_message_unchanged():
    """Chaque boss, rejoue seul, produit le meme message qu'avant.

    Rejouer boss par boss plutot qu'en bloc : un echec designe alors
    directement la classe fautive.
    """
    changed = []
    for name in replay.available():
        expected_path = EXPECTED_DIR / f"{name}.txt"
        assert expected_path.exists(), f"reference absente pour {name}, lancer --update"
        message, _ = replay.run([name])
        if message.splitlines() != _read(expected_path):
            changed.append(name)
    assert not changed, f"message modifie pour: {', '.join(changed)}"


def test_two_analyses_do_not_interfere():
    """Deux analyses entrelacees donnent le meme resultat qu'en sequentiel.

    C'est la raison d'etre de l'objet Analysis : tant que l'etat de run
    vivait dans des variables de module, deux analyses simultanees
    fusionnaient leurs boss et leurs joueurs, ce qui obligeait le bot a
    les serialiser derriere un verrou.
    """
    left, right = ["sh", "dei"], ["gors", "qadim"]
    expected_left, _ = replay.run(left)
    expected_right, _ = replay.run(right)

    with replay.no_network():
        analysis_left, logs_left = replay.build(left)
        analysis_right, logs_right = replay.build(right)
        # on alterne un log de chaque cote pour maximiser les chances de
        # collision si un etat etait encore partage
        for log_left, log_right in zip(logs_left, logs_right):
            BossFactory.create_boss(log_left, analysis_left)
            BossFactory.create_boss(log_right, analysis_right)
        got_left = replay.message_of(analysis_left)
        got_right = replay.message_of(analysis_right)

    assert got_left == expected_left, "l'analyse de gauche a ete polluee par l'autre"
    assert got_right == expected_right, "l'analyse de droite a ete polluee par l'autre"


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


def test_registry_is_populated():
    """Les classes de boss se sont enregistrees a l'import."""
    assert len(Boss.registry) >= 47, f"registre trop petit: {len(Boss.registry)} entrees"
    for boss_id, boss in Boss.registry.items():
        assert boss_id > 0, f"{boss.__name__} enregistre sous un triggerID invalide"
        assert boss.name, f"{boss.__name__} n'a pas de nom d'affichage"


def test_url_suffixes_are_unambiguous():
    """Deux boss ne peuvent pas partager un suffixe d'URL."""
    seen = {}
    for boss in set(Boss.registry.values()):
        if not boss.url_suffix:
            continue
        other = seen.setdefault(boss.url_suffix, boss)
        assert other is boss, (
            f"suffixe {boss.url_suffix!r} partage par {other.__name__} et {boss.__name__}"
        )


def test_wingman_id_is_not_a_trigger_id():
    """boss_id sert l'API wingman et differe parfois du triggerID du log.

    Aligner l'un sur l'autre casserait silencieusement soit la note
    wingman, soit la reconnaissance du log : ces quatre boss l'attestent.
    """
    for name, wingman_id in [("DARKAI", 232542), ("HT", 24375),
                             ("KO", 24485), ("OLC", 25413)]:
        boss = next(b for b in Boss.registry.values() if b.__name__ == name)
        assert boss.boss_id == wingman_id, f"{name}: id wingman modifie"
        assert wingman_id not in Boss.registry, (
            f"{name}: l'id wingman {wingman_id} ne doit pas identifier un log"
        )


def test_registry_rejects_a_duplicate_trigger_id():
    """Declarer un triggerID deja pris echoue au lieu d'ecraser l'autre boss."""
    taken = next(iter(Boss.registry))
    try:
        class Doublon(Boss):
            name    = "Doublon"
            boss_id = taken
    except ValueError:
        pass
    else:
        raise AssertionError(f"le triggerID {taken}, deja pris, a ete accepte")


def test_registry_rejects_a_missing_boss_id():
    """Un boss sans triggerID echoue a l'import plutot que d'etre ignore."""
    try:
        class SansId(Boss):
            name = "SansId"
    except ValueError:
        pass
    else:
        raise AssertionError("une classe sans boss_id a ete acceptee")


def test_languages_have_the_same_keys():
    """Une cle de message existe en francais et en anglais."""
    missing_en = sorted(set(french) - set(english))
    missing_fr = sorted(set(english) - set(french))
    assert not missing_en, f"absentes de english.py: {missing_en}"
    assert not missing_fr, f"absentes de french.py: {missing_fr}"


# ############################### RUNNER ###############################

TESTS = [
    test_run_message_unchanged,
    test_each_boss_message_unchanged,
    test_two_analyses_do_not_interfere,
    test_arxiv_is_keyed_by_account,
    test_arxiv_stats_are_snapshots,
    test_core_stats_have_descriptions,
    test_registry_is_populated,
    test_url_suffixes_are_unambiguous,
    test_wingman_id_is_not_a_trigger_id,
    test_registry_rejects_a_duplicate_trigger_id,
    test_registry_rejects_a_missing_boss_id,
    test_languages_have_the_same_keys,
]


def update_expected():
    message, _ = replay.run(RUN_FIXTURES)
    _write(EXPECTED_DIR / "run_message.txt", message)
    print(f"run_message.txt ({len(message.splitlines())} lignes)")
    for name in replay.available():
        message, _ = replay.run([name])
        _write(EXPECTED_DIR / f"{name}.txt", message)
        print(f"{name}.txt ({len(message.splitlines())} lignes)")


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
