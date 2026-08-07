"""Notes de performance issues de gw2wingman.

Chaque boss se voit attribuer un percentile : la position de son temps
de kill par rapport aux autres logs du meme boss. C'est un appel HTTP
par boss, autrefois lance depuis le constructeur de Boss, donc un a la
suite de l'autre. Sur un run de cinq logs, cette attente sequentielle
representait 80% du temps total.

Ces appels sont maintenant groupes en une passe, apres la creation des
boss et avant la mise en forme du message. On emploie des threads
plutot que grequests : ce module est destine a etre importe par le bot
Discord, et grequets applique le monkey-patching de gevent a tout le
processus, ce qui cohabite mal avec asyncio.
"""
from concurrent.futures import ThreadPoolExecutor

import requests

API_URL = "https://gw2wingman.nevermindcreations.de/api/getPercentileByMetadata"
MAX_PARALLEL = 10


def url_for(boss):
    timestamp = int(boss.start_date.timestamp())
    return (f"{API_URL}?bossID={boss.boss_id}&isCM={boss.cm}"
            f"&duration={boss.duration_ms}&timestamp={timestamp}")


def _percentile(boss):
    try:
        infos = requests.get(url_for(boss)).json()
    except Exception:
        print("wingman percentile failed")
        return None
    # un percentile nul est traite comme absent, la note disparait alors
    # du message : c'est le comportement historique
    return infos.get("percentile") or None


def fetch_percentiles(bosses):
    """Renseigne wingman_percentile de chaque boss, en une seule passe."""
    if not bosses:
        return
    with ThreadPoolExecutor(max_workers=min(len(bosses), MAX_PARALLEL)) as pool:
        for boss, percentile in zip(bosses, pool.map(_percentile, bosses)):
            boss.wingman_percentile = percentile
