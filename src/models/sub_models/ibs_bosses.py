from models.boss_class import Boss, Stats
from models.log_class import Log
from func import *

################################ ICEBROOD CONSTRUCT ################################

class ICE(Boss):
    
    last    = None
    name    = "ICEBROOD"
    boss_id = 22154
    wing    = "IBS"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        ICE.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
        
################################ KODANS ################################

class KODANS(Boss):
    
    last    = None
    name    = "KODANS"
    boss_id = 22343
    wing    = "IBS"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp    = self.get_mvp()
        self.lvp    = self.get_lvp()
        KODANS.last = self
        
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
        lvp_dps_name                    = self.players_to_string(i_players)
        dps                         = max_dmg / self.duration_ms 
        dmg_ratio                   = max_dmg / tot_dmg * 100
        self.add_lvps(i_players)
        return LANGUES["selected_language"]["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dps=dps, dmg_ratio=dmg_ratio)
    
    ################################ DATA MECHAS ################################
    
    def get_dmg_boss(self, i_player: int):
        boss1_dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][0][self.real_phase_id]['damage']
        boss2_dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][1][self.real_phase_id]['damage']
        return boss1_dmg + boss2_dmg
        
    
################################ FRAENIR ################################

class FRAENIR(Boss):
    
    last    = None
    name    = "FRAENIR"
    boss_id = 22492
    wing    = "IBS"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp     = self.get_mvp()
        self.lvp     = self.get_lvp()
        FRAENIR.last = self
        
    def get_mvp(self):
        msg_frozen = self.get_frozen_mvp()
        if msg_frozen:
            return msg_frozen
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        msg_sak = self.get_lvp_sak()
        if msg_sak:
            return msg_sak
        return self.get_lvp_dps()
    
    ################################ MVP ################################
    
    def get_frozen_mvp(self):
        i_players, max_frozen, _ = Stats.get_max_value(self, self.get_frozen)
        if max_frozen > 1:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) > 1:
                return LANGUES["selected_language"]["FRAENIR MVP FROZEN P"].format(mvp_names=mvp_names, max_frozen=max_frozen)
            return LANGUES["selected_language"]["FRAENIR MVP FROZEN S"].format(mvp_names=mvp_names, max_frozen=max_frozen)
        return
    
    ################################ LVP ################################
    
    def get_lvp_sak(self):
        i_players, max_dmg, tot_dmg = Stats.get_max_value(self, self.get_dmg_boss)
        sak_dmg                     = self.get_sak_dmg(i_players[0])
        sak_count                   = self.get_sak_count(i_players[0])
        lvp_dps_name                    = self.players_to_string(i_players)
        dps                         = max_dmg / self.duration_ms 
        dmg_ratio                   = max_dmg / tot_dmg * 100
        self.add_lvps(i_players)
        if sak_count:
            sak_ratio = sak_dmg/max_dmg*100
            return LANGUES["selected_language"]["FRAENIR LVP SAK"].format(lvp_dps_name=lvp_dps_name, sak_count=sak_count, sak_ratio=sak_ratio, dps=dps, dmg_ratio=dmg_ratio)
        return
    
    ################################ DATA MECHAS ################################
    
    def get_dmg_boss(self, i_player: int):
        boss1_dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][0][self.real_phase_id]['damage']
        boss2_dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][1][self.real_phase_id]['damage']
        return boss1_dmg + boss2_dmg
    
    def get_frozen(self, i_player: int):
        return self.get_mech_value(i_player, "Frozen")
    
    def get_sak_dmg(self, i_player: int):
        totalDamageDist = self.log.pjcontent["players"][i_player]["totalDamageDist"][0]
        for dmgSource in totalDamageDist:
            if dmgSource["id"] == 60448:
                return dmgSource["totalDamage"]
        return 0
    
    def get_sak_count(self, i_player: int):
        rota = self.get_player_rotation(i_player)
        for spell in rota:
            if spell["id"] == 60448:
                return len(spell["skills"])
        return 0
        
################################ WOJ ################################

class WOJ(Boss):
    
    last    = None
    name    = "WOJ"
    boss_id = 22711
    wing    = "IBS"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        WOJ.last = self
        
    def get_mvp(self):
        msg_chains = self.get_chain_mvp()
        if msg_chains:
            return msg_chains
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
    ################################ MVP ################################
    
    def get_chain_mvp(self):
        i_players, max_dmg, tot_dmg = Stats.get_max_value(self, self.get_chain_damage)
        mvp_name                    = self.players_to_string(i_players)
        ratio                       = max_dmg / tot_dmg * 100
        self.add_mvps(i_players) 
        if max_dmg > 10000:
            return LANGUES["selected_language"]["WOJ MVP CHAINS"].format(mvp_name=mvp_name, max_dmg=max_dmg, ratio=ratio)
        return
    
    ################################ DATA MECHAS ################################
    
    def get_chain_damage(self, i_player: int):
        chain_id = 59159
        dmgTaken = self.log.pjcontent['players'][i_player]["totalDamageTaken"][0]
        for dmg in dmgTaken:
            if dmg["id"] == chain_id:
                return dmg["totalDamage"]
        return 0
        
################################ BONESKINNER ################################

class BONESKINNER(Boss):
    
    last    = None
    name    = "BONESKINNER"
    boss_id = 22521
    wing    = "IBS"
    sak_id  = 60501
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp         = self.get_mvp()
        self.lvp         = self.get_lvp()
        BONESKINNER.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        msg_sak = self.get_lvp_sak()
        if msg_sak:
            return msg_sak
        return self.get_lvp_dps()
    
    ################################ LVP ################################
    
    def get_lvp_sak(self):
        i_players, max_dmg, tot_dmg = Stats.get_max_value(self, self.get_dmg_boss)
        sak_dmg                     = self.get_sak_dmg(i_players[0])
        sak_count                   = self.get_sak_count(i_players[0])
        lvp_dps_name                    = self.players_to_string(i_players)
        dps                         = max_dmg / self.duration_ms 
        dmg_ratio                   = max_dmg / tot_dmg * 100
        self.add_lvps(i_players)
        if sak_count:
            sak_ratio = sak_dmg/max_dmg*100
            return LANGUES["selected_language"]["FRAENIR LVP SAK"].format(lvp_dps_name=lvp_dps_name, sak_count=sak_count, sak_ratio=sak_ratio, dps=dps, dmg_ratio=dmg_ratio)
        return
    
    ################################ DATA MECHAS ################################
    
    def get_sak_dmg(self, i_player: int):
        dmgPath = self.log.pjcontent["players"][i_player]["targetDamageDist"][0][0]
        for dmg in dmgPath:
            if dmg["id"] == BONESKINNER.sak_id:
                return dmg["totalDamage"]
        return 0
    
    def get_sak_count(self, i_player: int):
        rota = self.get_player_rotation(i_player)
        for spell in rota:
            if spell["id"] == BONESKINNER.sak_id:
                return len(spell["skills"])
        return 0