"""
Package contenant les modèles de boss pour l'analyse des logs de raid.
"""

# Import des classes de l'aile 1
from core.models.boss_models.raid.raid_wing1_vg import VG
from core.models.boss_models.raid.raid_wing1_gors import GORS
from core.models.boss_models.raid.raid_wing1_sabetha import SABETHA

# Import des classes de l'aile 2
from core.models.boss_models.raid.raid_wing2_sloth import SLOTH
from core.models.boss_models.raid.raid_wing2_matthias import MATTHIAS

# Import des classes de l'aile 3
from core.models.boss_models.raid.raid_wing3_escort import ESCORT
from core.models.boss_models.raid.raid_wing3_kc import KC
from core.models.boss_models.raid.raid_wing3_xera import XERA

# Import des classes de l'aile 4
from core.models.boss_models.raid.raid_wing4_cairn import CAIRN
from core.models.boss_models.raid.raid_wing4_mo import MO
from core.models.boss_models.raid.raid_wing4_samarog import SAMAROG
from core.models.boss_models.raid.raid_wing4_deimos import DEIMOS

# Import des classes de l'aile 5
from core.models.boss_models.raid.raid_wing5_sh import SH
from core.models.boss_models.raid.raid_wing5_dhuum import DHUUM

# Import des classes de l'aile 6
from core.models.boss_models.raid.raid_wing6_ca import CA
from core.models.boss_models.raid.raid_wing6_largos import LARGOS
from core.models.boss_models.raid.raid_wing6_q1 import Q1

# Import des classes de l'aile 7
from core.models.boss_models.raid.raid_wing7_adina import ADINA
from core.models.boss_models.raid.raid_wing7_sabir import SABIR
from core.models.boss_models.raid.raid_wing7_qtp import QTP

# Import des classes de l'aile 8
from core.models.boss_models.raid.raid_wing8_greer import GREER
from core.models.boss_models.raid.raid_wing8_decima import DECIMA
from core.models.boss_models.raid.raid_wing8_ura import URA

# IBS
from core.models.boss_models.ibs.ice import ICE
from core.models.boss_models.ibs.kodans import KODANS
from core.models.boss_models.ibs.fraenir import FRAENIR
from core.models.boss_models.ibs.woj import WOJ
from core.models.boss_models.ibs.boneskinner import BONESKINNER

# End of Dragon
from core.models.boss_models.eod.mai_trin import AH
from core.models.boss_models.eod.ankka import XJ
from core.models.boss_models.eod.ko import KO
from core.models.boss_models.eod.ht import HT
from core.models.boss_models.eod.olc import OLC

# SOTO
from core.models.boss_models.soto.dagda import DAGDA
from core.models.boss_models.soto.cerus import CERUS

# Fractacls
from core.models.boss_models.fractals.mama import MAMA
from core.models.boss_models.fractals.siax import SIAX
from core.models.boss_models.fractals.ensolyss import ENSOLYSS
from core.models.boss_models.fractals.skorvald import SKORVALD
from core.models.boss_models.fractals.artsariiv import ARTSARIIV
from core.models.boss_models.fractals.arkk import ARKK
from core.models.boss_models.fractals.dark_ai import DARKAI
from core.models.boss_models.fractals.kanaxai import KANAXAI
from core.models.boss_models.fractals.eparch import EPARCH


# Import de la classe Golem
from core.models.boss_models.golem import GOLEM

# Définir les classes disponibles à l'importation
__all__ = [
    # Raids
    'VG', 'GORS', 'SABETHA',
    'SLOTH', 'MATTHIAS',
    'ESCORT', 'KC', 'XERA',
    'CAIRN', 'MO', 'SAMAROG', 'DEIMOS',
    'SH', 'DHUUM',
    'CA', 'LARGOS', 'Q1',
    'ADINA', 'SABIR', 'QTP',
    'GREER', 'DECIMA', 'URA',

    # IBS
    'ICE', 'KODANS', 'FRAENIR', 'WOJ', 'BONESKINNER',

    # EOD
    'AH', 'XJ', 'KO', 'HT', 'OLC',

    # SOTO
    'DAGDA', 'CERUS',

    # Fractals
    'MAMA', 'SIAX', 'ENSOLYSS',
    'SKORVALD', 'ARTSARIIV', 'ARKK',
    'DARKAI',
    'KANAXAI',
    'EPARCH',

    # Golem
    'GOLEM',
]
