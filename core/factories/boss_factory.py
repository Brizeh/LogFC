from typing import Dict, Type, Optional

from config.settings import BOSS_DICT, EXTRA_BOSS_DICT, ALL_BOSSES
from core.models.boss import (Boss)
from core.models.boss_models import *
from core.models.log import Log


class BossFactory:
    """
    Boss factory that creates appropriate instances for each encounter.
    Uses the Factory Method pattern to instantiate the correct boss class.
    """

    # Dictionary that maps boss identifiers to corresponding classes
    _BOSS_CLASSES: Dict[str, Type[Boss]] = {
        # ============ RAID BOSSES ============
        # Wing 1
        "vg": VG,
        "gors": GORS,
        "sab": SABETHA,

        # Wing 2
        "sloth": SLOTH,
        "matt" : MATTHIAS,

        # Wing 3
        "esc"  : ESCORT,
        "kc"   : KC,
        "xera" : XERA,

        # Wing 4
        "cairn": CAIRN,
        "mo"   : MO,
        "sam"  : SAMAROG,
        "dei"  : DEIMOS,

        # Wing 5
        "sh"   : SH,
        "dhuum": DHUUM,

        # Wing 6
        "ca"   : CA,
        "twins": LARGOS,
        "qadim": Q1,

        # Wing 7
        "adina": ADINA,
        "sabir": SABIR,
        "qpeer": QTP,

        # Wing 8
        "greer": GREER,
        "deci" : DECIMA,
        "ura"  : URA,

        #  IBS BOSSES
        "ice"  : ICE,
        "falln": KODANS,
        "frae" : FRAENIR,
        "whisp": WOJ,
        "bone" : BONESKINNER,

        #  EOD BOSSES
        "trin" : AH,
        "ankka": XJ,
        "li"   : KO,
        "void" : HT,
        "olc"  : OLC,

        #  SOTO BOSSES
        "dagda": DAGDA,
        "cerus": CERUS,

        #  FRAC BOSSES
        "mama" : MAMA,
        "siax" : SIAX,
        "enso" : ENSOLYSS,

        "skor" : SKORVALD,
        "arriv": ARTSARIIV,
        "arkk" : ARKK,

        "ai"   : DARKAI,

        "kana" : KANAXAI,

        "eparc": EPARCH,

        #  YES
        "golem": GOLEM
    }

    @classmethod
    def create_boss(cls, log: Log) -> Optional[Boss]:
        """
        Creates the appropriate boss instance from a log.

        Args:
            log: The Log object containing the combat data

        Returns:
            The created boss instance or None if the boss is not recognized
        """
        trigger_id = log.jcontent.get('triggerID')
        boss_name = BOSS_DICT.get(trigger_id) or EXTRA_BOSS_DICT.get(trigger_id)

        if not boss_name:
            print(f"Boss not recognized for trigger ID: {trigger_id}")
            return None

        if boss_name not in cls._BOSS_CLASSES:
            print(f"Boss class not implemented for: {boss_name}")
            return None

        # Instantiate the appropriate boss class
        boss_instance = cls._BOSS_CLASSES[boss_name](log)
        ALL_BOSSES.append(boss_instance)

        return boss_instance

    @classmethod
    def register_boss_class(cls, boss_name: str, boss_class: Type[Boss]) -> None:
        """
        Registers a new boss class in the factory.
        Useful for extensions or tests.

        Args:
            boss_name: The boss identifier
            boss_class: The class to use for this boss
        """
        cls._BOSS_CLASSES[boss_name] = boss_class