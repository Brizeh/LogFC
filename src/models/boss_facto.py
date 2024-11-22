from models.log_class import Log
from const import *
from .sub_models.raid_bosses import *
from .sub_models.ibs_bosses import *
from .sub_models.eod_bosses import *
from .sub_models.soto_bosses import *
from .sub_models.frac_bosses import *

class BossFactory:
    @staticmethod
    def create_boss(log : Log):
        boss = None
        factory = {#  RAID BOSSES
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
                   
                   "golem": GOLEM}
        boss_name = boss_dict.get(log.jcontent['triggerID']) or extra_boss_dict.get(log.jcontent['triggerID'])
        if boss_name:
            all_bosses.append(factory[boss_name](log))
                 
    
    

