from .boss_class import Boss
from .log_class import Log

# These imports look unused: they're essential. Loading the sub_models
# modules triggers __init_subclass__ on every boss class, which fills
# Boss.registry. Removing them would empty the registry and no log
# would be recognized anymore.
from .sub_models.raid_bosses import *
from .sub_models.ibs_bosses import *
from .sub_models.eod_bosses import *
from .sub_models.soto_bosses import *
from .sub_models.frac_bosses import *


class BossFactory:
    @staticmethod
    def create_boss(log: Log, analysis):
        boss = Boss.registry.get(log.pjcontent['triggerID'])
        if boss:
            analysis.bosses.append(boss(log, analysis))
