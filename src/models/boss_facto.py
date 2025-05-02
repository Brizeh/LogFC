from models.log_class import Log
from const import BOSS_DICT, EXTRA_BOSS_DICT, ALL_BOSSES
from .sub_models.raid_bosses import *
from .sub_models.ibs_bosses import *
from .sub_models.eod_bosses import *
from .sub_models.soto_bosses import *
from .sub_models.frac_bosses import *

_BOSS_FACTORY = {
    #  RAID BOSSES
    "vg"   : VG,
    "gors" : GORS,
    "sab"  : SABETHA,   
                    
    "sloth": SLOTH,
    "matt" : MATTHIAS,    
                    
    "esc"  : ESCORT,
    "kc"   : KC,
    "xera" : XERA,

    "cairn": CAIRN,
    "mo"   : MO,
    "sam"  : SAMAROG,
    "dei"  : DEIMOS,   
                    
    "sh"   : SH,
    "dhuum": DHUUM,   
                    
    "ca"   : CA,
    "twins": LARGOS,
    "qadim": Q1,      

    "adina": ADINA,
    "sabir": SABIR,
    "qpeer": QTP,
    
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
class BossFactory:
    @staticmethod
    def create_boss(log : Log):
        boss_name = BOSS_DICT.get(log.jcontent['triggerID']) or EXTRA_BOSS_DICT.get(log.jcontent['triggerID'])
        if boss_name:
            ALL_BOSSES.append(_BOSS_FACTORY[boss_name](log))