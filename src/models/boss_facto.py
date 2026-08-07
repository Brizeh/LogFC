from .boss_class import Boss
from .log_class import Log
from ..const import ALL_BOSSES

# Ces imports paraissent inutilises : ils sont indispensables. Charger les
# modules de sub_models declenche __init_subclass__ sur chaque classe de
# boss, ce qui remplit Boss.registry. Les retirer viderait le registre et
# plus aucun log ne serait reconnu.
from .sub_models.raid_bosses import *
from .sub_models.ibs_bosses import *
from .sub_models.eod_bosses import *
from .sub_models.soto_bosses import *
from .sub_models.frac_bosses import *


class BossFactory:
    @staticmethod
    def create_boss(log: Log):
        boss = Boss.registry.get(log.jcontent['triggerID'])
        if boss:
            ALL_BOSSES.append(boss(log))
