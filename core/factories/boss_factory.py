# core/factories/boss_factory.py
from typing import Dict, Type, Optional

from config.settings import BOSS_DICT, EXTRA_BOSS_DICT, ALL_BOSSES
from core.models.log import Log
from core.models.boss import Boss

# Import des classes spécifiques de boss
from core.models.boss_models.raid_wing1_vg import VG
from core.models.boss_models.raid_wing1_gors import GORS
from core.models.boss_models.raid_wing1_sabetha import SABETHA


class BossFactory:
    """
    Usine à boss qui crée les instances appropriées pour chaque rencontre.
    Utilise le pattern Factory Method pour instancier la bonne classe de boss.
    """

    # Dictionnaire qui mappe les identifiants de boss aux classes correspondantes
    _BOSS_CLASSES: Dict[str, Type[Boss]] = {
        # ============ RAID BOSSES ============
        # Wing 1
        "vg": VG,
        "gors": GORS,
        "sab": SABETHA,
        #
        # "sloth": SLOTH,
        # "matt" : MATTHIAS,
        #
        # "esc"  : ESCORT,
        # "kc"   : KC,
        # "xera" : XERA,
        #
        # "cairn": CAIRN,
        # "mo"   : MO,
        # "sam"  : SAMAROG,
        # "dei"  : DEIMOS,
        #
        # "sh"   : SH,
        # "dhuum": DHUUM,
        #
        # "ca"   : CA,
        # "twins": LARGOS,
        # "qadim": Q1,
        #
        # "adina": ADINA,
        # "sabir": SABIR,
        # "qpeer": QTP,
        #
        # "greer": GREER,
        # "deci" : DECIMA,
        # "ura"  : URA,
        #
        # #  IBS BOSSES
        # "ice"  : ICE,
        # "falln": KODANS,
        # "frae" : FRAENIR,
        # "whisp": WOJ,
        # "bone" : BONESKINNER,
        #
        # #  EOD BOSSES
        # "trin" : AH,
        # "ankka": XJ,
        # "li"   : KO,
        # "void" : HT,
        # "olc"  : OLC,
        #
        # #  SOTO BOSSES
        # "dagda": DAGDA,
        # "cerus": CERUS,
        #
        # #  FRAC BOSSES
        # "mama" : MAMA,
        # "siax" : SIAX,
        # "enso" : ENSOLYSS,
        #
        # "skor" : SKORVALD,
        # "arriv": ARTSARIIV,
        # "arkk" : ARKK,
        #
        # "ai"   : DARKAI,
        #
        # "kana" : KANAXAI,
        #
        # "eparc": EPARCH,
        #
        # #  YES
        # "golem": GOLEM
    }

    @classmethod
    def create_boss(cls, log: Log) -> Optional[Boss]:
        """
        Crée l'instance de boss appropriée à partir d'un log.

        Args:
            log: L'objet Log contenant les données du combat

        Returns:
            L'instance de boss créée ou None si le boss n'est pas reconnu
        """
        trigger_id = log.jcontent.get('triggerID')
        boss_name = BOSS_DICT.get(trigger_id) or EXTRA_BOSS_DICT.get(trigger_id)

        if not boss_name:
            print(f"Boss non reconnu pour le trigger ID: {trigger_id}")
            return None

        if boss_name not in cls._BOSS_CLASSES:
            print(f"Classe de boss non implémentée pour: {boss_name}")
            return None

        # Instancier la classe de boss appropriée
        boss_instance = cls._BOSS_CLASSES[boss_name](log)
        ALL_BOSSES.append(boss_instance)

        return boss_instance

    @classmethod
    def register_boss_class(cls, boss_name: str, boss_class: Type[Boss]) -> None:
        """
        Enregistre une nouvelle classe de boss dans la factory.
        Utile pour les extensions ou les tests.

        Args:
            boss_name: L'identifiant du boss
            boss_class: La classe à utiliser pour ce boss
        """
        cls._BOSS_CLASSES[boss_name] = boss_class