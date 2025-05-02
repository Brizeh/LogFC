from models.boss_class import Boss, Stats
from models.log_class import Log
from func import *

################################ MAMA ################################

class MAMA(Boss):
    
    last    = None
    name    = "MAMA"
    boss_id = 17021
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp  = self.get_mvp()
        self.lvp  = self.get_lvp()
        MAMA.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ SIAX ################################

class SIAX(Boss):
    
    last    = None
    name    = "SIAX"
    boss_id = 17028
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SIAX.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ ENSOLYSS ################################

class ENSOLYSS(Boss):
    
    last    = None
    name    = "ENSOLYSS"
    boss_id = 16948
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp      = self.get_mvp()
        self.lvp      = self.get_lvp()
        ENSOLYSS.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ SKORVALD ################################

class SKORVALD(Boss):
    
    last    = None
    name    = "SKORVALD"
    boss_id = 17632
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp      = self.get_mvp()
        self.lvp      = self.get_lvp()
        SKORVALD.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ ARTSARIIV ################################

class ARTSARIIV(Boss):
    
    last    = None
    name    = "ARTSARIIV"
    boss_id = 17949
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp       = self.get_mvp()
        self.lvp       = self.get_lvp()
        ARTSARIIV.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ ARKK ################################

class ARKK(Boss):
    
    last    = None
    name    = "ARKK"
    boss_id = 17759
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp  = self.get_mvp()
        self.lvp  = self.get_lvp()
        ARKK.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ DARK AI ################################

class DARKAI(Boss):
    
    last    = None
    name    = "DARK AI"
    boss_id = 232542
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp    = self.get_mvp()
        self.lvp    = self.get_lvp()
        DARKAI.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ KANAXAI ################################

class KANAXAI(Boss):
    
    last    = None
    name    = "KANAXAI"
    boss_id = 25577
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp     = self.get_mvp()
        self.lvp     = self.get_lvp()
        KANAXAI.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
    ################################ LVP ################################
    
    def get_lvp_dps(self):
        i_players, max_dmg, tot_dmg = Stats.get_max_value(self, self.get_dmg_boss)
        lvp_dps_name                = self.players_to_string(i_players)
        linkCount                   = self.get_links(i_players[0])
        dmg_ratio                   = max_dmg / tot_dmg * 100
        dps                         = max_dmg / self.duration_ms
        if linkCount:
            return LANGUES["selected_language"]["KANAXAI LVP DPS"].format(lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps, linkCount=linkCount)
        else:
            return LANGUES["selected_language"]["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps)
    
    ################################ DATA MECHAS ################################
    
    def get_links(self, i_player: int):
        link_id      = 69206
        start1, end1 = self.get_phase_timers("Phase 1", inMilliSeconds=True)
        start2, end2 = self.get_phase_timers("Phase 2", inMilliSeconds=True)
        start3, end3 = self.get_phase_timers("Phase 3", inMilliSeconds=True)
        buffUptimes  = self.log.pjcontent["players"][i_player]["buffUptimes"]
        linkCount    = 0
        start2      += 8000
        start3      += 8000
        end1        -= 8000
        end2        -= 8000
        for buff in buffUptimes:
            if buff["id"] == link_id:
                for state in buff["states"]:
                    buffTime = state[0]
                    if(
                       state[1] == 1 and
                       ((buffTime > start1 and buffTime < end1) or
                        (buffTime > start2 and buffTime < end2) or
                        (buffTime > start3 and buffTime < end3))
                      ):
                        linkCount += 1
        return linkCount
                
        
################################ EPARCH ################################

class EPARCH(Boss):
    
    last    = None
    name    = "EPARCH"
    boss_id = 26231
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp    = self.get_mvp()
        self.lvp    = self.get_lvp()
        EPARCH.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()