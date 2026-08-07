from ..boss_class import Boss, Stats
from ...func import *

################################ MAMA ################################

class MAMA(Boss):
    
    name       = "MAMA"
    boss_id    = 17021
    url_suffix = "mama"
    wing       = "FRAC"
    
    def get_mvp(self):
        mvp = []
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
    
################################ SIAX ################################

class SIAX(Boss):
    
    name       = "SIAX"
    boss_id    = 17028
    url_suffix = "siax"
    wing       = "FRAC"
    
    def get_mvp(self):
        mvp = []
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
    
################################ ENSOLYSS ################################

class ENSOLYSS(Boss):
    
    name       = "ENSOLYSS"
    boss_id    = 16948
    url_suffix = "enso"
    wing       = "FRAC"
    
    def get_mvp(self):
        mvp = []
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
    
################################ SKORVALD ################################

class SKORVALD(Boss):
    
    name       = "SKORVALD"
    boss_id    = 17632
    url_suffix = "skor"
    wing       = "FRAC"
    
    def get_mvp(self):
        mvp = []
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
    
################################ ARTSARIIV ################################

class ARTSARIIV(Boss):
    
    name       = "ARTSARIIV"
    boss_id    = 17949
    url_suffix = "arriv"
    wing       = "FRAC"
    
    def get_mvp(self):
        mvp = []
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp  
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
    
################################ ARKK ################################

class ARKK(Boss):
    
    name       = "ARKK"
    boss_id    = 17759
    url_suffix = "arkk"
    wing       = "FRAC"
    
    def get_mvp(self):
        mvp = []
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
    
################################ DARK AI ################################

class DARKAI(Boss):
    
    name       = "DARK AI"
    boss_id    = 232542
    url_suffix = "ai"
    trigger_ids = (23254,)
    wing       = "FRAC"
    
    def get_mvp(self):
        mvp = []
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
    
################################ KANAXAI ################################

class KANAXAI(Boss):
    
    name       = "KANAXAI"
    boss_id    = 25577
    url_suffix = "kana"
    wing       = "FRAC"
    
    def get_mvp(self):
        mvp = []
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
    
    ################################ LVP ################################
    
    def get_lvp_dps(self):
        i_players, max_dmg, tot_dmg = Stats.get_max_value(self, self.get_dmg_boss)
        lvp_dps_name                = self.players_to_string(i_players)
        linkCount                   = self.get_links(i_players[0])
        dmg_ratio                   = max_dmg / tot_dmg * 100
        dps                         = max_dmg / self.duration_ms
        if linkCount:
            return self.msg("KANAXAI LVP DPS", lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps, linkCount=linkCount)
        else:
            return self.msg("LVP DPS", lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps)
    
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
    
    name       = "EPARCH"
    boss_id    = 26231
    url_suffix = "eparc"
    wing       = "FRAC"
    
    def get_mvp(self):
        mvp = []
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
    
################################ WS ################################

class WS(Boss):
    
    name       = "WS"
    boss_id    = 27010
    url_suffix = "ws"
    wing       = "FRAC"
    
    def get_mvp(self):
        mvp = []
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
