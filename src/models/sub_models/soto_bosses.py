from ..boss_class import Boss, Stats
from ..log_class import Log
from ...func import *

################################ DAGDA ################################

class DAGDA(Boss):
    
    last    = None
    name    = "DAGDA"
    boss_id = 25705
    wing    = "SOTO"
    
    def __init__(self, log: Log):
        super().__init__(log)
        DAGDA.last = self
        
    def get_mvp(self):
        mvp = []
        msg_debil = self.mvp_debil()
        if msg_debil:
            mvp.append(msg_debil)
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
    
    ################################ MVP ################################
    
    def mvp_debil(self):
        i_players, max_debil, _ = Stats.get_max_value(self, self.get_max_debil, exclude=[self.is_heal])
        mvp_names               = self.players_to_string(i_players)
        if max_debil > 1:
            self.add_mvps(i_players)
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
    
################################ CERUS ################################

class CERUS(Boss):
    
    last    = None
    name    = "CERUS"
    boss_id = 25989
    wing    = "SOTO"
    
    def __init__(self, log: Log):
        super().__init__(log)
        CERUS.last = self
        
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
    
################################ KELA ################################

class KELA(Boss):
    
    last    = None
    name    = "KELA"
    boss_id = 27124
    wing    = "SOTO"
    
    def __init__(self, log: Log):
        super().__init__(log)
        KELA.last = self
        
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