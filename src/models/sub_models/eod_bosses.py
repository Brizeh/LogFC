from models.boss_class import Boss, Stats
from models.log_class import Log
from func import *

################################ MAI TRIN ################################

class AH(Boss):
    
    last    = None
    name    = "MAI TRIN"
    boss_id = 24033
    wing    = "EOD"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        AH.last  = self
        
    def get_mvp(self):
        msg_exposed = self.expose_mvp()
        if msg_exposed:
            return msg_exposed
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
    ################################ MVP ################################
    
    def expose_mvp(self):
        i_players, max_exposed, _ = Stats.get_max_value(self, self.get_max_exposed, exclude=[self.is_heal])
        mvp_names                 = self.players_to_string(i_players)
        if max_exposed > 2:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return LANGUES["selected_language"]["AH MVP EXPOSED S"].format(mvp_names=mvp_names, max_exposed=max_exposed)
            else:
                return LANGUES["selected_language"]["AH MVP EXPOSED P"].format(mvp_names=mvp_names, max_exposed=max_exposed)
        return
    
    ################################ LVP ################################
    
    def get_lvp_dps(self):
        i_players, max_dmg, tot_dmg = Stats.get_max_value(self, self.get_dmg_boss)
        ratio                       = max_dmg / tot_dmg * 100
        time                        = self.duration_ms
        dps                         = max_dmg / time
        lvp_dps_name                = self.players_to_string(i_players)
        self.add_lvps(i_players)
        return LANGUES["selected_language"]["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dps=dps, dmg_ratio=ratio)
    
    ################################ DATA MECHAS ################################
    
    def get_max_exposed(self, i_player: int):
        buffUptimes   = self.log.pjcontent["players"][i_player]["buffUptimes"]
        expose_id     = 64936
        expose_states = None
        for buff in buffUptimes:
            if buff["id"] == expose_id:
                expose_states = buff["states"]
        exposed = 0
        if expose_states:
            for state in expose_states:
                if state[1] > exposed:
                    exposed = state[1]
        return exposed
    
    def get_dmg_boss(self, i_player: int):
        targetDmg    = self.log.pjcontent["players"][i_player]["dpsTargets"]
        mai_trin_dmg = targetDmg[0][0]["damage"]
        echo_dmg     = targetDmg[1][0]["damage"]
        return mai_trin_dmg + echo_dmg 
                
    
################################ ANKKA ################################

class XJ(Boss):
    
    last    = None
    name    = "ANKKA"
    boss_id = 23957
    wing    = "EOD"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        XJ.last  = self
        
    def get_mvp(self):
        msg_cc = self.get_mvp_cc_total()
        if msg_cc:
            return msg_cc
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ KO ################################

class KO(Boss):
    
    last    = None
    name    = "KO"
    boss_id = 24485
    wing    = "EOD"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        KO.last  = self
        
    def get_mvp(self):
        msg_debil = self.mvp_debil()
        if msg_debil:
            return msg_debil
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
        dmg_ratio                   = max_dmg / tot_dmg * 100
        dps                         = max_dmg / self.duration_ms
        self.add_lvps(i_players)
        return LANGUES["selected_language"]["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps)
    
    ################################ MVP ################################
    
    def mvp_debil(self):
        i_players, max_debil, _ = Stats.get_max_value(self, self.get_max_debil, exclude=[self.is_heal])
        mvp_names               = self.players_to_string(i_players)
        if max_debil > 1:
            self.add_lvps(i_players)
            if len(i_players) == 1:
                return LANGUES["selected_language"]["KO MVP DEBIL S"].format(mvp_names=mvp_names, max_debil=max_debil)
            else:
                return LANGUES["selected_language"]["KO MVP DEBIL P"].format(mvp_names=mvp_names, max_debil=max_debil)
        return
    
    ################################ DATA MECHAS ################################
    
    def get_max_debil(self, i_player: int):
        buffUptimes = self.log.pjcontent["players"][i_player]["buffUptimes"]
        debil_id    = 67972
        states      = None
        for buff in buffUptimes:
            if buff["id"] == debil_id:
                states = buff["states"]
        debil = 0
        if states:
            for state in states:
                if state[1] > debil:
                    debil = state[1]
        return debil
    
    def get_dmg_boss(self, i_player: int):
        return self.log.pjcontent["players"][i_player]["dpsAll"][0]["damage"]
    
################################ HT ################################

class HT(Boss):
    
    last    = None
    name    = "HT"
    boss_id = 24375
    wing    = "EOD"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        HT.last  = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ OLC ################################

class OLC(Boss):
    
    last    = None
    name    = "OLC"
    boss_id = 25413
    wing    = "EOD"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        OLC.last = self
        
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
        dmg_ratio                   = max_dmg / tot_dmg * 100
        dps                         = max_dmg / self.duration_ms
        self.add_lvps(i_players)
        return LANGUES["selected_language"]["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps)
    
    ################################ DATA MECHAS ################################
    
    def get_dmg_boss(self, i_player: int):
        return self.log.pjcontent["players"][i_player]["dpsAll"][0]["damage"]