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
        AH.last  = self
        
    def get_mvp(self):
        mvp = []
        msg_exposed = self.expose_mvp()
        if msg_exposed:
            mvp.append(msg_exposed)
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
        XJ.last  = self
        
    def get_mvp(self):
        mvp = []
        msg_cc = self.get_mvp_cc_total()
        if msg_cc:
            mvp.append(msg_cc)
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
    
################################ KO ################################

class KO(Boss):
    
    last    = None
    name    = "KO"
    boss_id = 24485
    wing    = "EOD"
    
    def __init__(self, log: Log):
        super().__init__(log)
        KO.last  = self
        
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
        HT.last  = self
        
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
    
################################ OLC ################################

class OLC(Boss):
    
    last    = None
    name    = "OLC"
    boss_id = 25413
    wing    = "EOD"
    
    def __init__(self, log: Log):
        super().__init__(log)
        OLC.last = self
        
    def get_mvp(self):
        mvp = []
        msg_olc = self.get_mvp_olc()
        if msg_olc:
            mvp.append(msg_olc)
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
        dmg_ratio                   = max_dmg / tot_dmg * 100
        dps                         = max_dmg / self.duration_ms
        self.add_lvps(i_players)
        return LANGUES["selected_language"]["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps)
    
    ################################ MVP ################################
    
    def get_mvp_olc(self):
        red_timers     = self.get_mechanic_history("DualHrz.C")
        green_timers   = self.get_mechanic_history("PrnVrx.C")
        blue_timers    = self.get_mechanic_history("CrckWind.C")
        exposed_timers = self.get_mechanic_history("Exposed")
        mvps           = {}
        max_mvps       = {}
        for event in exposed_timers:
            player_id = self.player_name_to_id(event["actor"])
            rgb = {"red":0, "green":0, "blue":0}
            for red in red_timers:
                if abs(event["time"]-red["time"]) < 10000:
                    rgb["red"] += 1
            for green in green_timers:
                if abs(event["time"]-green["time"]) < 10000:
                    rgb["green"] += 1
            for blue in blue_timers:
                if abs(event["time"]-blue["time"]) < 10000:
                    rgb["blue"] += 1
            if rgb["red"] == 0 and rgb["green"] == 0 and rgb["blue"] == 0:
                continue
            else:
                mvps[player_id] = rgb
        max_rgb = 0
        for player_id, rgb in mvps.items():
            if rgb["red"] + rgb["green"] + rgb["blue"] > max_rgb:
                max_rgb = rgb["red"] + rgb["green"] + rgb["blue"]
        if max_rgb != 0:
            for player_id, rgb in mvps.items():
                if rgb["red"] + rgb["green"] + rgb["blue"] == max_rgb:
                    max_mvps[player_id] = rgb
        self.add_mvps(list(max_mvps.keys()))
        msg = ""
        for player_id, rgb in max_mvps.items():
            mvp_name = self.players_to_string([player_id])
            msg += LANGUES["selected_language"]["OLC MVP EXPOSED"].format(mvp_name=mvp_name, red=rgb["red"], green=rgb["green"], blue=rgb["blue"])+"\n"           
        return msg[:-1]
    
    ################################ DATA MECHAS ################################
    
    def get_dmg_boss(self, i_player: int):
        return self.log.pjcontent["players"][i_player]["dpsAll"][0]["damage"]
    