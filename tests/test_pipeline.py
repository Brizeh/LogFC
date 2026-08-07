#!/usr/bin/env python3
"""Offline tests for LogFC.

    python -m tests.test_pipeline

No external dependency, no network access: the pipeline is replayed
against the fixtures in tests/fixtures (see tests/capture_fixture.py to
add more).

To regenerate the reference output after a deliberate change:

    python -m tests.test_pipeline --update
"""
import sys
from pathlib import Path

from src.languages_dict.english import english
from src.languages_dict.french import french
from src.models.boss_class import Boss
from src.models import boss_facto  # noqa: F401 - importing it populates Boss.registry
from src.models.boss_facto import BossFactory
from src import mechanics
from src import wingman
from tests import replay

EXPECTED_DIR = Path(__file__).resolve().parent / "expected"

# A coherent run from a single session, to cover wing grouping, the
# GRAND MVP/LVP lines and the total duration.
RUN_FIXTURES = ["sh", "dei", "adina"]

_cache = {}


def run_reference():
    """Replays the reference run, only once per execution."""
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
    """The message produced for a known run doesn't change."""
    message, _ = run_reference()
    expected_path = EXPECTED_DIR / "run_message.txt"
    assert expected_path.exists(), "reference output missing, run --update"
    assert message.splitlines() == _read(expected_path), (
        "the message changed; check the diff then --update if it's intentional"
    )


def test_each_boss_message_unchanged():
    """Each boss, replayed alone, produces the same message as before.

    Replaying boss by boss rather than as a batch: a failure then points
    straight at the faulty class.
    """
    changed = []
    for name in replay.available():
        expected_path = EXPECTED_DIR / f"{name}.txt"
        assert expected_path.exists(), f"reference missing for {name}, run --update"
        message, _ = replay.run([name])
        if message.splitlines() != _read(expected_path):
            changed.append(name)
    assert not changed, f"message changed for: {', '.join(changed)}"


def test_two_analyses_do_not_interfere():
    """Two interleaved analyses give the same result as run sequentially.

    This is the whole point of the Analysis object: as long as run state
    lived in module-level variables, two simultaneous analyses merged
    their bosses and players, which forced the bot to serialize them
    behind a lock.
    """
    left, right = ["sh", "dei"], ["gors", "qadim"]
    expected_left, _ = replay.run(left)
    expected_right, _ = replay.run(right)

    with replay.no_network():
        analysis_left, logs_left = replay.build(left)
        analysis_right, logs_right = replay.build(right)
        # alternate a log from each side to maximize the odds of a
        # collision if any state were still shared
        for log_left, log_right in zip(logs_left, logs_right):
            BossFactory.create_boss(log_left, analysis_left)
            BossFactory.create_boss(log_right, analysis_right)
        wingman.fetch_percentiles(analysis_left.bosses)
        wingman.fetch_percentiles(analysis_right.bosses)
        got_left = replay.message_of(analysis_left)
        got_right = replay.message_of(analysis_right)

    assert got_left == expected_left, "the left analysis was polluted by the other one"
    assert got_right == expected_right, "the right analysis was polluted by the other one"


def test_two_languages_do_not_interfere():
    """Two interleaved analyses in different languages coexist.

    The selected language used to be the last module-level variable
    mutated on every run: an English analysis would overwrite the
    language of a French analysis in progress.
    """
    expected_fr, _ = replay.run(["gors"], language="FR")
    expected_en, _ = replay.run(["gors"], language="EN")
    assert expected_fr != expected_en, "both languages render the same text"

    with replay.no_network():
        analysis_fr, logs_fr = replay.build(["gors"], language="FR")
        analysis_en, logs_en = replay.build(["gors"], language="EN")
        for log_fr, log_en in zip(logs_fr, logs_en):
            BossFactory.create_boss(log_fr, analysis_fr)
            BossFactory.create_boss(log_en, analysis_en)
        wingman.fetch_percentiles(analysis_fr.bosses)
        wingman.fetch_percentiles(analysis_en.bosses)
        got_fr = replay.message_of(analysis_fr)
        got_en = replay.message_of(analysis_en)

    assert got_fr == expected_fr, "the French analysis switched language"
    assert got_en == expected_en, "the English analysis switched language"


def test_icd_table_covers_the_fixtures():
    """No fixture mechanic is missing from mechanic_icd.json.

    A missing entry would make its internal cooldown fall back to zero
    and overestimate its value: LogFC flags this, this test forbids it
    for the bosses that are covered.
    """
    mechanics._warned.clear()
    for name in replay.available():
        replay.run([name])
    assert not mechanics._warned, (
        f"missing from mechanic_icd.json: {sorted(map(str, mechanics._warned))} "
        "(run python -m tools.update_mechanic_icd <url>)"
    )


def test_arxiv_is_keyed_by_account():
    """ARXIV is indexed by account, not by display nickname."""
    _, arxiv = run_reference()
    assert arxiv, "ARXIV is empty"
    for url, accounts in arxiv.items():
        assert url.startswith("https://dps.report/"), f"unexpected log key: {url}"
        for account in accounts:
            assert "." in account, f"{account!r} doesn't look like a GW2 account"


def test_arxiv_stats_are_snapshots():
    """Every stat carries a value and a description, no derived average.

    Names starting with "avg" are legitimate when dps.report already
    provides a percentage (avgCritRate, avgBoons...). What has no place
    here is an avgX duplicating an X present in the same category: the
    average is computed downstream, across several logs.
    """
    _, arxiv = run_reference()
    for accounts in arxiv.values():
        for categories in accounts.values():
            for category, stats in categories.items():
                for name, stat in stats.items():
                    assert set(stat) == {"value", "description"}, (
                        f"{category}/{name} has unexpected keys: {sorted(stat)}"
                    )
                    if name.startswith("avg"):
                        assert name[3:] not in stats, (
                            f"{category}/{name} duplicates {category}/{name[3:]}: "
                            "averages are computed downstream, not at write time"
                        )


def test_core_stats_have_descriptions():
    """Stats hand-described in ALL_MECHS don't lose their label."""
    _, arxiv = run_reference()
    for accounts in arxiv.values():
        for categories in accounts.values():
            for stats in categories.values():
                for name, stat in stats.items():
                    assert stat["description"], f"{name} has no description"


def test_registry_is_populated():
    """Boss classes registered themselves at import time."""
    assert len(Boss.registry) >= 47, f"registry too small: {len(Boss.registry)} entries"
    for boss_id, boss in Boss.registry.items():
        assert boss_id > 0, f"{boss.__name__} registered under an invalid triggerID"
        assert boss.name, f"{boss.__name__} has no display name"


def test_url_suffixes_are_unambiguous():
    """Two bosses can't share a URL suffix."""
    seen = {}
    for boss in set(Boss.registry.values()):
        if not boss.url_suffix:
            continue
        other = seen.setdefault(boss.url_suffix, boss)
        assert other is boss, (
            f"suffix {boss.url_suffix!r} shared by {other.__name__} and {boss.__name__}"
        )


def test_wingman_id_is_not_a_trigger_id():
    """boss_id serves the wingman API and sometimes differs from the log's triggerID.

    Aligning the two would silently break either the wingman grade or
    log recognition, as these four bosses show.
    """
    for name, wingman_id in [("DARKAI", 232542), ("HT", 24375),
                             ("KO", 24485), ("OLC", 25413)]:
        boss = next(b for b in Boss.registry.values() if b.__name__ == name)
        assert boss.boss_id == wingman_id, f"{name}: wingman id changed"
        assert wingman_id not in Boss.registry, (
            f"{name}: wingman id {wingman_id} must not identify a log"
        )


def test_registry_rejects_a_duplicate_trigger_id():
    """Declaring an already-taken triggerID fails instead of overwriting the other boss."""
    taken = next(iter(Boss.registry))
    try:
        class Duplicate(Boss):
            name    = "Duplicate"
            boss_id = taken
    except ValueError:
        pass
    else:
        raise AssertionError(f"triggerID {taken}, already taken, was accepted")


def test_registry_rejects_a_missing_boss_id():
    """A boss without a triggerID fails at import instead of being ignored."""
    try:
        class NoId(Boss):
            name = "NoId"
    except ValueError:
        pass
    else:
        raise AssertionError("a class without boss_id was accepted")


def test_languages_have_the_same_keys():
    """A message key exists in both French and English."""
    missing_en = sorted(set(french) - set(english))
    missing_fr = sorted(set(english) - set(french))
    assert not missing_en, f"missing from english.py: {missing_en}"
    assert not missing_fr, f"missing from french.py: {missing_fr}"


# ############################### RUNNER ###############################

TESTS = [
    test_run_message_unchanged,
    test_each_boss_message_unchanged,
    test_two_analyses_do_not_interfere,
    test_two_languages_do_not_interfere,
    test_icd_table_covers_the_fixtures,
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
    print(f"run_message.txt ({len(message.splitlines())} lines)")
    for name in replay.available():
        message, _ = replay.run([name])
        _write(EXPECTED_DIR / f"{name}.txt", message)
        print(f"{name}.txt ({len(message.splitlines())} lines)")


def main():
    if "--update" in sys.argv:
        update_expected()
        return 0

    if not replay.available():
        print("no fixtures. Capture some with:")
        print("  python -m tests.capture_fixture <url> [<url> ...]")
        return 1

    failures = 0
    for test in TESTS:
        try:
            test()
        except AssertionError as error:
            failures += 1
            print(f"FAIL   {test.__name__}\n       {error}")
        except Exception as error:  # noqa: BLE001 - we want to see the raw error
            failures += 1
            print(f"ERROR  {test.__name__}\n       {type(error).__name__}: {error}")
        else:
            print(f"ok     {test.__name__}")

    print(f"\n{len(TESTS) - failures}/{len(TESTS)} tests passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
