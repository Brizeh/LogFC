"""Reproduction du tableau de mecaniques d'Elite Insights.

dps.report expose deux choses : une API JSON, et une page HTML dont on
peut extraire une structure plus riche. Cette derniere contient un
tableau `mechanicStats` deja agrege par joueur et par phase, que LogFC
lisait autrefois en scrapant le HTML.

Ce module recalcule ce tableau a partir des seuls evenements bruts de
l'API JSON. La regle, retrouvee en comparant 7676 cellules de reference
puis confirmee dans le source d'Elite Insights, tient en trois points :

- la valeur est une **somme de poids** (`weight`), pas un nombre
  d'evenements : un "Breakbar Damage" pese la quantite de degats infligee
- chaque mecanique porte un **temps de grace** (icd) pendant lequel un
  nouvel evenement ne compte pas
- cette fenetre demarre a t=0 et **se rearme a chaque evenement**, meme
  ignore : une rafale d'evenements rapproches ne vaut donc que le premier

L'icd n'existe que dans la page HTML : il est fige dans
`mechanic_icd.json`, alimente par `tools/update_mechanic_icd.py`.
"""
import json
from pathlib import Path

_ICD_PATH = Path(__file__).resolve().parent / "mechanic_icd.json"

try:
    with open(_ICD_PATH, encoding="utf-8") as _file:
        ICD_TABLE = json.load(_file)
except FileNotFoundError:
    ICD_TABLE = {}

# Mecaniques de statut, que le HTML ne compte pas parmi les mecaniques
# joueur alors que leurs acteurs en sont. On les ecarte explicitement.
STATUS_MECHANICS = {"Dead", "Downed", "Got up", "Res"}

_warned = set()


def _warn_once(key, message):
    if key not in _warned:
        _warned.add(key)
        print(message)


def get_icd(trigger_id: int, mech_name: str):
    """Temps de grace d'une mecanique, 0 si inconnu (avec avertissement)."""
    boss = ICD_TABLE.get(str(trigger_id))
    if boss is None:
        _warn_once(trigger_id,
                   f"mechanic icd: boss {trigger_id} absent de mechanic_icd.json, "
                   "icd suppose nul (voir tools/update_mechanic_icd.py)")
        return 0
    if mech_name not in boss:
        _warn_once((trigger_id, mech_name),
                   f"mechanic icd: {mech_name!r} inconnu pour le boss {trigger_id}, "
                   "icd suppose nul (voir tools/update_mechanic_icd.py)")
        return 0
    return boss[mech_name]


def player_mechanics(pjcontent):
    """Mecaniques subies par les joueurs, dans l'ordre de la page HTML."""
    players = {player["name"] for player in pjcontent["players"]}
    mechanics = []
    for mechanic in pjcontent["mechanics"]:
        if mechanic["fullName"] in STATUS_MECHANICS:
            continue
        actors = {data["actor"] for data in mechanic["mechanicsData"]}
        if actors and actors <= players:
            mechanics.append(mechanic)
    return mechanics


def mech_value(mechanic, actor: str, icd: int, start: int, end: int):
    """Valeur d'une mecanique pour un joueur sur un intervalle de temps."""
    events = sorted(
        (data["time"], data.get("weight", 1))
        for data in mechanic["mechanicsData"]
        if data["actor"] == actor and start <= data["time"] <= end
    )
    total, last = 0, 0
    for time, weight in events:
        if time - last >= icd:
            total += weight
        last = time
    return total
