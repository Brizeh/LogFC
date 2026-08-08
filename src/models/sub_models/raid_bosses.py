from ..boss_class import Boss, Stats
from ...combat_replay import contains, rectangles
from ...func import *
import numpy as np

################################ VG ################################

class VG(Boss):
    
    name       = "VG"
    wing       = 1
    boss_id    = 15438
    url_suffix = "vg"
    
    def get_mvp(self):
        mvp = []
        msg_bleu = self.mvp_bleu()
        if msg_bleu:
            mvp.append(msg_bleu)
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        return [self.get_lvp_dps()]

    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_condi])
        
    ################################ MVP ################################   
    
    def mvp_bleu(self):
        i_players, max_bleu, _ = Stats.get_max_value(self, self.get_bleu)
        mvp_names              = self.players_to_string(i_players)  
        if max_bleu > 1:
            self.add_mvps(i_players)
            nb_players = len(i_players)
            if nb_players == 1:
                return self.msg("VG MVP BLEU S", mvp_names=mvp_names, max_bleu=max_bleu)
            if nb_players > 1:
                return self.msg("VG MVP BLEU P", mvp_names=mvp_names, nb_players=nb_players, max_bleu=max_bleu)
        return
    
    ################################ LVP ################################
    


    ################################ CONDITIONS ###############################
    
    
    
    ################################ MECHANICS DATA ################################
    
    def get_bleu(self, i_player: int):
        bleu_split = self.get_mech_value(i_player, "Green Guard TP")
        bleu_boss  = self.get_mech_value(i_player, "Boss TP")
        return bleu_boss + bleu_split

################################ GORS ################################

class GORS(Boss):
    
    name       = "GORSEVAL"
    wing       = 1
    boss_id    = 15429
    url_suffix = "gors"
    
    def get_mvp(self):
        mvp = []
        msg_egg = self.mvp_egg()
        if msg_egg:
            mvp.append(msg_egg)
        
        msg_dmg_split = self.mvp_dmg_split()
        if msg_dmg_split:
            mvp.append(msg_dmg_split)
        
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_split = self.lvp_dmg_split()
        if msg_split:
            lvp.append(msg_split)
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
        
    ################################ MVP ################################
    
    def mvp_dmg_split(self):
        i_players, min_dmg, total_dmg = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support])
        dps_total_dmg                 = Stats.get_tot_value(self, self.get_dmg_split, exclude=[self.is_support])
        if min_dmg/dps_total_dmg < 1/6*0.75 and total_dmg:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            dmg_ratio = min_dmg / total_dmg * 100
            return self.msg("GORS MVP SPLIT", mvp_names=mvp_names, min_dmg=min_dmg, dmg_ratio=dmg_ratio)
    
    def mvp_egg(self):
        i_players = self.get_egged()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) == 1:
                return self.msg("GORS MVP EGG S", mvp_names=mvp_names)
            if len(i_players) > 1:
                return self.msg("GORS MVP EGG P", mvp_names=mvp_names)
        return 
    
    ################################ LVP ################################
    
    def lvp_dmg_split(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_split)
        lvp_names                     = self.players_to_string(i_players)
        if total_dmg:
            dmg_ratio = max_dmg / total_dmg * 100
            self.add_lvps(i_players)
            return self.msg("GORS LVP SPLIT", lvp_names=lvp_names, max_dmg=max_dmg, dmg_ratio=dmg_ratio)

    ################################ CONDITIONS ###############################
    
    def got_egged(self, i_player: int):
        return self.get_mech_value(i_player, "Egged") > 0
    
    ################################ MECHANICS DATA ################################
        
    def get_dmg_split(self, i_player: int):
        dmg_split   = 0
        split_1_id = self.get_phase_id("Split 1")
        split_2_id = self.get_phase_id("Split 2")
        dmg_split_1 = self.get_dmg_phase_targets(i_player, split_1_id)
        dmg_split_2 = self.get_dmg_phase_targets(i_player, split_2_id)
        for add_split1, add_split2 in zip(dmg_split_1,dmg_split_2):
            dmg_split += add_split1 + add_split2
        return dmg_split
    
    def get_egged(self):
        egged = []
        for i in self.player_list:
            if self.got_egged(i):
                egged.append(i)
        return egged
    
################################ SABETHA ################################

class SABETHA(Boss):
    
    name       = "SABETHA"
    wing       = 1
    boss_id    = 15375
    url_suffix = "sab"
    
    pos_sab             = [376.7,364.4]
    pos_canon1          = [346.9,706.7]
    pos_canon2          = [35.9,336.8]
    pos_canon3          = [403.3,36.0]
    pos_canon4          = [713.9,403.1]
    canon_detect_radius = 45
    bomb_radius         = 280  # Timed Bomb blast radius, per EI's Sabetha.cs (CircleDecoration(280, ...))
    
    def get_mvp(self):
        mvp = []
        msg_terrorists = self.mvp_terrorists()
        if msg_terrorists:
            mvp.append(msg_terrorists)
        
        msg_dmg_split = self.mvp_dmg_split()
        if msg_dmg_split:
            mvp.append(msg_dmg_split)
        
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_cannon])
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_split = self.lvp_dmg_split()
        if msg_split:
            lvp.append(msg_split)
        
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
    
    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_cannon])

    ################################ MVP ################################
    
    def mvp_dmg_split(self):
        i_players, min_dmg, total_dmg = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support,self.is_cannon])
        dps_total_dmg                 = Stats.get_tot_value(self, self.get_dmg_split, exclude=[self.is_support])
        if min_dmg/dps_total_dmg < 1/6*0.75 and total_dmg:
            self.add_mvps(i_players) 
            dmg_ratio = min_dmg / total_dmg * 100
            mvp_names = self.players_to_string(i_players)
            return self.msg("SABETHA MVP SPLIT", mvp_names=mvp_names, dmg_ratio=dmg_ratio)
        return
    
    def mvp_terrorists(self):
        i_players = self.get_terrorists()
        self.add_mvps(i_players)
        if i_players:
            mvp_names = self.players_to_string(i_players)
            return self.msg("SABETHA MVP BOMB", mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    def lvp_dmg_split(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_split)
        lvp_names                     = self.players_to_string(i_players)
        if total_dmg:
            dmg_ratio                     = max_dmg / total_dmg * 100
            self.add_lvps(i_players)
            return self.msg("SABETHA LVP SPLIT", lvp_names=lvp_names, dmg_ratio=dmg_ratio)

    ################################ CONDITIONS ###############################
    
    def is_cannon(self, i_player: int, n: int=0):
        pos_player = self.get_player_pos(i_player)
        match n:
            case 0: 
                canon_pos = [SABETHA.pos_canon1, SABETHA.pos_canon2, SABETHA.pos_canon3, SABETHA.pos_canon4]
            case 1:
                canon_pos = [SABETHA.pos_canon1]
            case 2:
                canon_pos = [SABETHA.pos_canon2]
            case 3:
                canon_pos = [SABETHA.pos_canon3]
            case 4:
                canon_pos = [SABETHA.pos_canon4]
            case _:
                canon_pos = []
        for pos in pos_player:
            for canon in canon_pos:
                if get_dist(pos, canon) <= SABETHA.canon_detect_radius:
                    return True
        return False
    
    def is_terrorist(self, i_player: int):
        bomb_history = self.get_player_mech_history(i_player, ["Timed Bomb"])
        if not bomb_history:
            return False
        poses         = self.get_player_pos(i_player)
        # the API exposes the exact map scale; no need to hand-calibrate
        # a scaler against a single replay, as was done before
        pixel_to_inch = 1 / self.log.pjcontent['combatReplayMetaData']['inchToPixel']
        players       = self.player_list
        for bomb in bomb_history:
            bomb_time  = bomb['time'] + 3000
            time_index = time_to_index(bomb_time, self.time_base)
            try:
                bomb_pos = poses[time_index]
            except IndexError:
                continue
            bombed_players = 0
            for i in players:
                if i == i_player:
                    continue
                try:
                    i_pos = self.get_player_pos(i)[time_index]
                except IndexError:
                    continue
                if get_dist(bomb_pos, i_pos)*pixel_to_inch <= SABETHA.bomb_radius:
                    bombed_players += 1
            if bombed_players > 1:
                return True
        return False
    
    ################################ MECHANICS DATA ################################
        
    def get_dmg_split(self,i_player: int):
        dmg_kernan   = self.get_dmg_phase_targets(i_player, 2)[0]
        dmg_mornifle = self.get_dmg_phase_targets(i_player, 5)[0]
        dmg_karde    = self.get_dmg_phase_targets(i_player, 7)[0]
        return dmg_kernan + dmg_mornifle + dmg_karde 
    
    def get_terrorists(self):
        terrotists = []
        for i in self.player_list:
            if self.is_terrorist(i):
                terrotists.append(i)
        return terrotists 

################################ SLOTH ################################

class SLOTH(Boss):
    
    name       = "SLOTH"
    wing       = 2
    boss_id    = 16123
    url_suffix = "sloth"
    
    def get_mvp(self):
        mvp = []
        msg_tantrum = self.mvp_tantrum()
        if msg_tantrum:
            mvp.append(msg_tantrum)
        
        msg_cc = self.mvp_cc_sloth()
        if msg_cc:
            mvp.append(msg_cc)
        
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_shroom])
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        
        return mvp  
        
    def get_lvp(self):
        lvp = []
        msg_cc = self.get_lvp_cc_boss()
        if msg_cc:
            lvp.append(msg_cc)
        
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps) 
            
        return lvp
        
    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_shroom])

    ################################ MVP ################################
    
    def mvp_cc_sloth(self):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_boss, exclude=[self.is_shroom])  
        if min_cc < 800 and total_cc:
            self.add_mvps(i_players)
            cc_ratio  = min_cc / total_cc * 100
            mvp_names = self.players_to_string(i_players)
            if min_cc == 0:
                if len(i_players) > 1:
                    return self.msg("SLOTH MVP 0 CC P", mvp_names=mvp_names)
                return self.msg("SLOTH MVP 0 CC S", mvp_names=mvp_names)
            if len(i_players) > 1:
                return self.msg("SLOTH MVP CC P", mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            return self.msg("SLOTH MVP CC S", mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
    
    def mvp_tantrum(self):
        i_players, max_tantrum, _ = Stats.get_max_value(self, self.get_tantrum)
        if max_tantrum > 1:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) > 1:
                return self.msg("SLOTH MVP TANTRUM P", mvp_names=mvp_names, max_tantrum=max_tantrum)
            return self.msg("SLOTH MVP TANTRUM S", mvp_names=mvp_names, max_tantrum=max_tantrum)
    
    ################################ LVP ################################
    
    

    ################################ CONDITIONS ###############################
    
    def is_shroom(self, i_player: int):
        rota = self.get_player_rotation(i_player)
        for skill in rota:
            if skill['id'] == 34408:
                return True
        return False
    
    ################################ MECHANICS DATA ################################
    
    def get_tantrum(self, i_player: int):
        return self.get_mech_value(i_player, "Tantrum")

################################ MATTHIAS ################################

class MATTHIAS(Boss):
    
    name       = "MATTHIAS"
    wing       = 2
    boss_id    = 16115
    url_suffix = "matt"
    
    def get_mvp(self):
        mvp = []
        msg_cc = self.mvp_cc_matthias()
        if msg_cc:
            mvp.append(msg_cc)
        
        msg_dps = self.get_bad_dps()
        if msg_dps:
            mvp.append(msg_dps) 
        return mvp
        
    def get_lvp(self):
        lvp = []
        msg_cc = self.lvp_cc_matthias()
        if msg_cc:
            lvp.append(msg_cc)
        
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
            
        return lvp
      
    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_sac])

    ################################ MVP ################################
    
    def mvp_cc_matthias(self):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_total, exclude=[self.is_sac])
        if total_cc:
            cc_ratio                    = min_cc / total_cc * 100
            mvp_names                   = self.players_to_string(i_players)
            self.add_mvps(i_players)
            if min_cc == 0:
                return self.msg("MATTHIAS MVP 0 CC", mvp_names=mvp_names)
            else:
                return self.msg("MATTHIAS MVP CC", mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
        
    ################################ LVP ################################
            
    def lvp_cc_matthias(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_total)
        if total_cc:    
            cc_ratio                    = max_cc / total_cc * 100
            lvp_names                   = self.players_to_string(i_players)
            self.add_lvps(i_players)
            return self.msg("MATTHIAS LVP CC", lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)
    
    ################################ CONDITIONS ###############################
    
    def is_sac(self, i_player: int):
        return self.get_nb_sac(i_player) > 0
    
    ################################ MECHANICS DATA ################################    
    
    def get_nb_sac(self, i_player: int):
        return self.get_mech_value(i_player, "Sacrifice")

################################ ESCORT ################################

class ESCORT(Boss):
    
    name       = "ESCORT"
    wing       = 3
    boss_id    = 16253
    url_suffix = "esc"
    
    towers = [
               [387,129.1],
               [304.1,115.7],
               [187.1,118.8],
               [226.1,252.3],
               [80.3,255.5]
              ]
    tower_radius = 19
    
    def get_mvp(self):
        mvp = []
        msg_mine = self.mvp_mine()
        if msg_mine:
            mvp.append(msg_mine)
            
        return mvp
       
    def get_lvp(self):
        lvp = []
        msg_tower = self.lvp_tower()
        if msg_tower:
            lvp.append(msg_tower)
            
        msg_glenna = self.lvp_glenna()
        if msg_glenna:
            lvp.append(msg_glenna)
            
        return lvp
    
    ################################ MVP ################################
    
    def mvp_mine(self):
        i_players = self.get_mined_players()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) == 1:
                return self.msg("ESCORT MVP MINE S", mvp_names=mvp_names)
            else:
                return self.msg("ESCORT MVP MINE P", mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    def lvp_glenna(self):
        i_players, max_call, _ = Stats.get_max_value(self, self.get_glenna_call)
        lvp_names              = self.players_to_string(i_players)
        self.add_lvps(i_players)
        return self.msg("ESCORT LVP GLENNA", lvp_names=lvp_names, max_call=max_call)
    
    def lvp_tower(self):
        towers    = self.get_towers()
        lvp_names = self.players_to_string(towers)
        for i in self.player_list:
            for n in range(1,6):
                if self.is_tower_n(i,n) and not self.is_tower(i):
                    return
        self.add_lvps(towers)
        if len(towers) == 1:
            return self.msg("ESCORT LVP TOWER S", lvp_names=lvp_names)
        return self.msg("ESCORT LVP TOWER P", lvp_names=lvp_names)
    
    ################################ CONDITIONS ################################
    
    def got_mined(self, i_player: int):
        return self.get_mech_value(i_player, "Mine Detonation Hit") > 0
    
    def is_tower_n(self, i_player: int, n: int):
        poses = self.get_player_pos(i_player)
        tower = ESCORT.towers[n-1]
        for pos in poses:
            if get_dist(pos, tower) < ESCORT.tower_radius:
                return True
        return False
    
    def is_tower(self, i_player: int):
        for n in range(1,6):
            if not self.is_tower_n(i_player, n):
                return False
        return True

    ################################ MECHANICS DATA ################################
    
    def get_mined_players(self):
        p = []
        for i in self.player_list:
            if self.got_mined(i):
                p.append(i)
        return p
            
    def get_glenna_call(self, i_player: int):
        return self.get_mech_value(i_player, "Over Here! Cast")
    
    def get_towers(self):
        towers = []
        for i in self.player_list:
            if self.is_tower(i):
                towers.append(i)
        return towers

################################ KC ################################

class KC(Boss):
    
    name       = "KC"
    wing       = 3
    boss_id    = 16235
    url_suffix = "kc"
    
    def get_mvp(self):
        mvp = []
        msg_orb = self.mvp_orb_kc()
        if msg_orb:
            mvp.append(msg_orb)
            
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
            
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_orb = self.lvp_orb_kc()
        if msg_orb:
            lvp.append(msg_orb)
        
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
            
        return lvp
        
    ################################ MVP ################################
            
    def mvp_orb_kc(self):
        i_players, min_orb, _ = Stats.get_min_value(self, self.get_good_orb)
        mvp_names             = self.players_to_string(i_players)
        if min_orb < 7:
            self.add_mvps(i_players)
            if min_orb < 0:
                return self.msg("KC MVP BAD ORB", mvp_names=mvp_names, min_orb=-min_orb)
            if min_orb == 0:
                return self.msg("KC MVP 0 ORB", mvp_names=mvp_names)
            else:
                return self.msg("KC MVP ORB", mvp_names=mvp_names, min_orb=min_orb)
            
    ################################ LVP ################################
    
    def lvp_orb_kc(self):
        i_players, max_orb, _ = Stats.get_max_value(self, self.get_good_orb)
        lvp_names             = self.players_to_string(i_players)
        self.add_lvps(i_players)
        return self.msg("KC LVP ORB", lvp_names=lvp_names, max_orb=max_orb)
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ MECHANICS DATA ################################

    def get_good_orb(self, i_player: int):
        good_red_orbs   = self.get_mech_value(i_player, 'Good Red Orb')
        good_white_orbs = self.get_mech_value(i_player, 'Good White Orb')
        bad_red_orbs    = self.get_mech_value(i_player, 'Bad Red Orb')
        bad_white_orbs  = self.get_mech_value(i_player, 'Bad White Orb')
        return good_red_orbs + good_white_orbs - bad_red_orbs - bad_white_orbs

################################ XERA ################################

class XERA(Boss):
    
    name       = "XERA"
    wing       = 3
    boss_id    = 16246
    url_suffix = "xera"
    real_phase = "Phase 1"
    
    debut         = [497.1,86.4]
    l1            = [663.0,314.9]
    l2            = [532.5,557.4]
    fin           = [268.3,586.4]
    r1            = [208.2,103.4]
    r2            = [87.0,346.8]
    centre        = [366.4,323.4]
    debut_radius  = 85
    centre_radius = 140

    def get_mvp(self):
        mvp = []
        msg_fdp = self.mvp_fdp_xera()
        if msg_fdp:
            mvp.append(msg_fdp)
            
        msg_glide = self.mvp_glide()
        if msg_glide:
            mvp.append(msg_glide)
            
        msg_cc = self.get_mvp_cc_boss()
        if msg_cc:
            mvp.append(msg_cc)  
            
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_minijeu = self.lvp_minijeu()
        if msg_minijeu:
            lvp.append(msg_minijeu)
            
        msg_cc = self.get_lvp_cc_boss()
        if msg_cc:
            lvp.append(msg_cc)
        
        return lvp
        
    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support])

    ################################ MVP ################################
    
    def mvp_fdp_xera(self):
        i_fdp     = self.get_fdp()
        fdp_names = self.players_to_string(i_fdp)
        self.add_mvps(i_fdp)
        if len(i_fdp) == 1:
            return self.msg("XERA MVP SKIP S", fdp_names=fdp_names)
        if len(i_fdp) > 1:
            return self.msg("XERA MVP SKIP P", fdp_names=fdp_names)
        return
    
    def mvp_glide(self):
        i_glide     = self.get_gliding_death()
        glide_names = self.players_to_string(i_glide)
        self.add_mvps(i_glide)
        if len(i_glide) == 1:
            return self.msg("XERA MVP GLIDE S", glide_names=glide_names)
        if len(i_glide) > 1:
            return self.msg("XERA MVP GLIDE P", glide_names=glide_names)
        return
    
    ################################ LVP ################################
    
    def lvp_minijeu(self):
        i_players, max_minijeu, _ = Stats.get_max_value(self, self.get_tp_back, exclude=[self.is_fdp])  
        lvp_names                 = self.players_to_string(i_players)
        self.add_lvps(i_players)
        if max_minijeu == 2:
            return self.msg("XERA LVP MINI-JEU", lvp_names=lvp_names)
        return
    
    ################################ CONDITIONS ################################
    
    def is_fdp(self, i_player: int):
        return i_player in self.get_fdp()
    
    ################################ MECHANICS DATA ################################

    def get_tp_out(self, i_player: int):
        return self.get_mech_value(i_player, 'TP')
    
    def get_tp_back(self, i_player: int):
        return self.get_mech_value(i_player, 'TP back')
    
    def get_fdp(self): # fdp = skip mini jeu XERA
        mecha_data = self.log.pjcontent['mechanics']
        tp_data    = None
        for e in mecha_data:
            if e['name'] == "TP Out":
                tp_data = e['mechanicsData']
                break
        fdp     = []
        delta   = 6000
        i_delta = time_to_index(delta, self.time_base)
        if not tp_data:
            return fdp
        for e in tp_data:
            tp_time     = e['time']
            
            player_name = e['actor']
            i_player    = self.player_name_to_id(player_name)
            tp_time    += 2000  # 1s de delais pour etre sur
            i_time      = time_to_index(tp_time, self.time_base)
            pos_player  = self.get_player_pos(i_player, i_time, i_time + i_delta)
            for p in pos_player:
                if get_dist(p, XERA.centre) <= XERA.centre_radius:
                    fdp.append(i_player)
                    break
        return fdp
    
    def get_gliding_death(self):
        dead = []
        glide_phase = self.get_phase_id("Gliding")
        if glide_phase != 0:
            for i in self.player_list:
                if self.log.pjcontent['players'][i]['defenses'][glide_phase]['deadCount'] > 0:
                    dead.append(i)
        return dead     

################################ CAIRN ################################

class CAIRN(Boss):
    
    name       = "CAIRN"
    wing       = 4
    boss_id    = 17194
    url_suffix = "cairn"
    
    def get_mvp(self):
        mvp = []
        msg_tp = self.mvp_tp()
        if msg_tp:
            mvp.append(msg_tp)
             
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
    
    def mvp_tp(self):
        i_players, max_tp, _ = Stats.get_max_value(self, self.get_tp)
        mvp_names            = self.players_to_string(i_players)
        if max_tp > 2:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return self.msg("CAIRN MVP TP S", mvp_names=mvp_names, max_tp=max_tp)
            if len(i_players) > 1:
                return self.msg("CAIRN MVP TP P", mvp_names=mvp_names, max_tp=max_tp)
        return
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ MECHANICS DATA ################################

    def get_tp(self, i_player: int):
        return self.get_mech_value(i_player, 'Orange TP')

################################ MO ################################

class MO(Boss):
    
    name       = "MO"
    wing       = 4
    boss_id    = 17172
    url_suffix = "mo"
    
    def get_mvp(self):
        mvp = []
        msg_pic = self.mvp_pic()
        if msg_pic:
            mvp.append(msg_pic)
            
        msg_dps = self.get_bad_dps()
        if msg_dps:
            mvp.append(msg_dps)
        
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()   
        if msg_dps:
            lvp.append(msg_dps)
            
        return lvp
        
    ################################ MVP ################################
    
    def mvp_pic(self):
        i_players = self.get_piced()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return self.msg("MO MVP PICS S", mvp_names=mvp_names) 
        if len(i_players) > 1:
            return self.msg("MO MVP PICS P", mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ MECHANICS DATA ################################

    def get_piced(self):
        piced = []
        for i in self.player_list:
            if self.is_dead_instant(i):
                piced.append(i)
        return piced

################################ SAMAROG ################################

class SAMAROG(Boss):
    
    name       = "SAMAROG"
    wing       = 4
    boss_id    = 17188
    url_suffix = "sam"
    
    top_left_corn  = [278.0,645.2]
    top_right_corn = [667.6,660.7]
    bot_left_corn  = [299.4,58.6]
    bot_right_corn = [690.7,73.6]
    scaler         = 5.4621
    
    def get_mvp(self):
        mvp = []
        msg_impaled = self.mvp_impaled()
        if msg_impaled:
            mvp.append(msg_impaled)
        
        msg_bisou = self.mvp_traitors()
        if msg_bisou:
            mvp.append(msg_bisou)
        
        msg_cc = self.get_mvp_cc_boss(extra_exclude=[self.is_fix])
        if msg_cc:
            mvp.append(msg_cc)
            
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_cc = self.get_lvp_cc_boss()
        if msg_cc:
            lvp.append(msg_cc)
            
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        
        return lvp
        
        
    
    ################################ MVP ################################ 
    
    def mvp_impaled(self):
        i_players = self.get_impaled()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return self.msg("SAMAROG MVP IMPALED S", mvp_names=mvp_names) 
        if len(i_players) > 1:
            return self.msg("SAMAROG MVP IMPALED P", mvp_names=mvp_names)
        return 
    
    def mvp_traitors(self):
        i_trait, i_vict = self.get_traitors()
        trait_names     = self.players_to_string(i_trait)
        vict_names      = self.players_to_string(i_vict)
        self.add_mvps(i_trait)
        if len(i_trait) == 1:
            return self.msg("SAMAROG MVP BISOU S", trait_names=trait_names, vict_names=vict_names)
        if len(i_trait) > 1:
            return self.msg("SAMAROG MVP BISOU P", trait_names=trait_names, vict_names=vict_names)
        return  
    
    ################################ LVP ################################ 
    
    
    
    ################################ CONDITIONS ################################
    
    def got_impaled(self, i_player: int):
        if self.is_dead_instant(i_player):
            mech_history = self.get_player_mech_history(i_player)
            for mech in mech_history:
                if mech['name'] == "DC":
                    mech_history.remove(mech)
            if len(mech_history) > 1:
                if (mech_history[-2]['name'] == "Swp" or mech_history[-2]['name'] == "Schk.Wv") and mech_history[-1]['name'] == "Dead":
                    return True
        return False
    
    def is_fix(self, i_player: int):
        return self.get_mech_value(i_player, "Fixate: Samarog") >= 3
    
    ################################ MECHANICS DATA ################################
    
    def get_impaled(self):
        i_players = []
        for i in self.player_list:
            if self.got_impaled(i):
                  i_players.append(i)
        return i_players
    
    def get_traitors(self):
        traitors, victims = [], []
        big_greens        = self.get_mechanic_history("Big Green")
        small_greens      = self.get_mechanic_history("Small Green")
        failed_greens     = self.get_mechanic_history("Failed Green")
        last_fail_time    = None
        if failed_greens:
            for fail_green in failed_greens:
                if fail_green['time'] == last_fail_time:
                    continue
                last_fail_time = fail_green['time']
                fail_actor     = fail_green['actor']
                fail_time      = fail_green['time']
                for small, big in zip(small_greens, big_greens):
                    small_actor = small['actor']
                    big_actor   = big['actor']
                    green_time  = small['time']
                    if fail_actor in [big_actor, small_actor] and np.abs(fail_time - green_time) < 7000:
                        victims.append(self.player_name_to_id(big_actor))
                        traitors.append(self.player_name_to_id(small_actor))
        return traitors, victims 

################################ DEIMOS ################################

class DEIMOS(Boss):
    
    name       = "DEIMOS"
    wing       = 4
    boss_id    = 17154
    url_suffix = "dei"
    
    def get_mvp(self):
        mvp = []
        msg_black = self.mvp_black()
        if msg_black:
            mvp.append(msg_black)
        msg_pizza = self.mvp_pizza()
        if msg_pizza:
            mvp.append(msg_pizza)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_tears = self.lvp_tears()
        if msg_tears:
            lvp.append(msg_tears)
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp

    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_sac])

    ################################ MVP ################################
    
    def mvp_black(self):
        i_players, max_black, _ = Stats.get_max_value(self, self.get_black_trigger)
        mvp_names               = self.players_to_string(i_players)
        nb_players              = len(i_players)
        self.add_mvps(i_players)
        if nb_players == 1:
            return self.msg("DEIMOS MVP BLACK S", mvp_names=mvp_names, max_black=max_black)
        if nb_players > 1:
            return self.msg("DEIMOS MVP BLACK P", mvp_names=mvp_names, nb_players=nb_players, max_black=max_black)
        return
    
    def mvp_pizza(self):
        i_players = self.get_pizzaed()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return self.msg("DEIMOS MVP PIZZA", mvp_names=mvp_names)
        return
    
    ################################ LVP ################################ 
    
    def lvp_tears(self):
        i_players, max_tears, _ = Stats.get_max_value(self, self.get_tears)
        lvp_names               = self.players_to_string(i_players)
        if i_players and max_tears > 2:
            self.add_lvps(i_players)
            return self.msg("DEIMOS LVP TEARS", lvp_names=lvp_names, max_tears=max_tears)
        return
    
    ################################ CONDITIONS ################################
    
    def got_pizzaed(self, i_player: int):
        if self.is_dead_instant(i_player):
            mech_history = self.get_player_mech_history(i_player)
            for mech in mech_history:
                if mech['name'] == "DC":
                    mech_history.remove(mech)
            if mech_history[-2]['name'] == "Pizza" and mech_history[-1]['name'] == "Dead":
                return True
        return False

    def is_sac(self, i_player: int):
        greens = self.get_mechanic_history('Chosen (Green)')
        if not greens:
            return False
        return greens[-1]['actor'] == self.get_player_name(i_player)

    ################################ MECHANICS DATA ################################

    def get_black_trigger(self, i_player: int):
        return self.get_mech_value(i_player, "Black Oil Trigger")
    
    def get_tears(self, i_player: int):
        return self.get_mech_value(i_player, "Tear")
    
    def get_pizzaed(self):
        pizzaed = []
        for i in self.player_list:
            if self.got_pizzaed(i):
                pizzaed.append(i)
        return pizzaed
    
    def get_dmg_boss(self, i_player: int):
        p10010id = self.get_phase_id("100% - 10%")
        p100id   = self.get_phase_id("10% - 0%") 
        d10010   = self.log.pjcontent['players'][i_player]['dpsTargets'][0][p10010id]['damage']
        d100     = self.log.pjcontent['players'][i_player]['dpsTargets'][0][p100id]['damage']
        return d10010 + d100

################################ SH ################################

class SH(Boss):
    
    name       = "SH"
    wing       = 5
    boss_id    = 19767
    url_suffix = "sh"
    needs_replay_data = True

    center_arena = [375,375]
    radius1      = 345.5
    radius2      = 304.2
    radius3      = 256.2
    radius4      = 208.5
    radius5      = 163

    def get_mvp(self):
        mvp = []
        msg_cc = self.get_mvp_cc_boss()
        if msg_cc:
            mvp.append(msg_cc)
        msg_wall = self.mvp_wall()
        if msg_wall:
            mvp.append(msg_wall)
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp

    def get_lvp(self):
        lvp = []
        msg_cc = self.get_lvp_cc_boss()
        if msg_cc:
            lvp.append(msg_cc)
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp

    def mvp_wall(self):
        i_players = self.get_walled_players()
        if not i_players:
            return
        self.add_mvps(i_players)
        mvp_names = self.players_to_string(i_players)
        return self.msg("SH MVP WALL", mvp_names=mvp_names)

    def get_walled_players(self):
        """Players who died while standing inside a moving wall.

        Elite Insights' walls ("SurgingSoul") carry no combat stats and
        are absent from the JSON API; their position only exists in the
        page's HTML combat replay data (self.log.replay_data, fetched by
        combat_replay.fetch_replay_data for bosses that need it).
        Empirically the position sample matching a recorded death
        sometimes lags the wall's own sample grid by one polling step
        (~300ms), hence checking a small window of frames around the
        death instead of only the exact one.

        Deaths after duration_ms are excluded: arcdps keeps logging a
        little past a successful kill, and a "death" there is a
        post-encounter artifact rather than a wall hit (confirmed on a
        real log where two players' final "death" landed after the
        fight's own recorded end and coincided to the same millisecond,
        the signature of something else entirely).
        """
        crdata = self.log.replay_data
        if not crdata:
            return []
        walls = rectangles(crdata, "255, 100, 0")
        if not walls:
            return []
        polling = crdata["pollingRate"]

        walled = []
        for i in self.player_list:
            crd = self.log.pjcontent['players'][i]['combatReplayData']
            deaths = [t for interval in crd['dead'] if (t := interval[0]) <= self.duration_ms]
            if any(self._died_in_a_wall(crd['positions'], t, polling, walls) for t in deaths):
                walled.append(i)
        return walled

    def _died_in_a_wall(self, positions, death_time, polling, walls):
        base = (death_time // polling) * polling
        for t in (base, base + polling, base + 2 * polling, base - polling):
            index = t // polling
            if not (0 <= index < len(positions)):
                continue
            if any(contains(wall, positions[index], t) for wall in walls):
                return True
        return False

    ################################ MVP ################################
    # Work in progress, not sure if I will keep it in the final version of the bot
    """def mvp_wall(self):
        i_players = self.get_walled_players()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return self.msg("SH MVP WALL", mvp_names=mvp_names)
        return
    
    def mvp_fall(self):
        i_players = self.get_walled_players()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return self.msg("SH MVP FALL", mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    def took_wall(self, i_player: int):
        if self.is_dead_instant(i_player) and not self.has_fallen(i_player):
            return True
        return False
        
    def has_fallen(self, i_player: int):
        if self.is_dead_instant(i_player):
            last_pos         = self.get_player_pos(i_player)[-1]
            death_time       = self.get_player_death_timer(i_player)
            fell_at_begin    = get_dist(SH.center_arena, last_pos) > SH.radius2
            fell_to_radius23 = death_time > self.bosshp_to_time(90)+2500 and death_time < self.bosshp_to_time(66)+2500 and get_dist(SH.center_arena, last_pos) > SH.radius3
            fell_to_radius34 = death_time > self.bosshp_to_time(66)+2500 and death_time < self.bosshp_to_time(33)+2500 and get_dist(SH.center_arena, last_pos) > SH.radius4
            fell_to_radius45 = death_time > self.bosshp_to_time(33)+2500 and get_dist(SH.center_arena, last_pos) > SH.radius5
            if fell_at_begin or fell_to_radius23 or fell_to_radius34 or (self.cm and fell_to_radius45):
                return True
        return False
    
    ################################ MECHANICS DATA ################################

    def get_walled_players(self):
        walled = []
        for i in self.player_list:
            if self.took_wall(i):
                walled.append(i)
        return walled
    
    def get_fallen_players(self):
        fallen = []
        for i in self.player_list:
            if self.has_fallen(i):
                fallen.append(i)
        return fallen"""

################################ DHUUM ################################

class DHUUM(Boss):
    
    name       = "DHUUM"
    wing       = 5
    boss_id    = 19450
    url_suffix = "dhuum"
    real_phase = "Dhuum Fight"

    def mechanic_exclusions(self, mech_name):
        # A pick-up right around the Shielded Dhuum transition isn't
        # counted: personal counting choice, not an Elite Insights bug.
        if mech_name != "Ender's Pick up":
            return []
        for phase in self.log.pjcontent['phases']:
            if phase['name'] == "Shielded Dhuum":
                return [(phase['start'] - 5000, phase['start'] + 5000)]
        return []

    def get_mvp(self):
        mvp = []
        msg_cracks = self.mvp_cracks()
        if msg_cracks:
            mvp.append(msg_cracks)
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_green])
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp

    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_green])
   
    ################################ MVP ################################
    
    def mvp_cracks(self):
        i_players, max_cracks, _ = Stats.get_max_value(self, self.get_cracks)
        mvp_names                = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return self.msg("DHUUM MVP CRACKS S", mvp_names=mvp_names, max_cracks=max_cracks)
        if len(i_players) > 1:
            return self.msg("DHUUM MVP CRACKS P", mvp_names=mvp_names, max_cracks=max_cracks)
        return

    
    ################################ LVP ################################
    
     
    
    ################################ CONDITIONS ################################
    
    def is_green(self, i_player: int) -> bool:
        return self.get_mech_value(i_player, "Green port", "Dhuum Fight") > 0
    
    ################################ MECHANICS DATA ################################

    def get_cracks(self, i_player: int):
        return self.get_mech_value(i_player, "Cracks")    

################################ CA ################################

class CA(Boss):
    
    name       = "CA"
    wing       = 6
    boss_id    = 43974
    url_suffix = "ca"

    def get_mvp(self):
        mvp = []
        msg_dps = self.get_bad_dps()
        if msg_dps:
            mvp.append(msg_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
  
    ################################ MVP ################################
    
    
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ MECHANICS DATA ################################  

################################ LARGOS ################################

class LARGOS(Boss):
    
    name       = "LARGOS"
    wing       = 6
    boss_id    = 21105
    url_suffix = "twins"

    def get_mvp(self):
        mvp = []
        msg_dash = self.mvp_dash()
        if msg_dash:
            mvp.append(msg_dash)
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_cc = self.get_lvp_cc_total()
        if msg_cc:
            lvp.append(msg_cc)
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp

    ################################ MVP ################################
        
    def mvp_dash(self):
        i_players, max_dash, _ = Stats.get_max_value(self, self.get_dash, exclude=[self.is_heal, self.is_tank])
        mvp_names              = self.players_to_string(i_players)
        if max_dash < 7:
            return self.get_bad_dps()
        else:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return self.msg("LARGOS MVP DASH S", mvp_names=mvp_names, max_dash=max_dash)
            if len(i_players) > 1:
                return self.msg("LARGOS MVP DASH P", mvp_names=mvp_names, max_dash=max_dash)
        return
    
    def get_bad_dps(self, extra_exclude: list[classmethod]=[]):
        i_sup, sup_max_dmg, _ = Stats.get_max_value(self, self.get_dmg_boss, exclude=[self.is_dps])
        sup_name              = self.players_to_string(i_sup)
        bad_dps               = []
        for i in self.player_list:   
            if any(filter_func(i) for filter_func in extra_exclude) or self.is_dead(i) or self.is_support(i):
                continue
            dps = self.get_dmg_boss(i)
            if dps < sup_max_dmg:
                if not(self.name == "QUOIDIMM" and self.get_player_spe(i) == "Spellbreaker"): 
                    bad_dps.append(i)
        if bad_dps:
            self.add_mvps(bad_dps)
            bad_dps_name = self.players_to_string(bad_dps)
            if len(bad_dps) == 1:
                return self.msg("MVP BAD DPS S", bad_dps_name=bad_dps_name, sup_name=sup_name)
            else:
                return self.msg("MVP BAD DPS P", bad_dps_name=bad_dps_name, sup_name=sup_name)
    
    ################################ LVP ################################ 
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ MECHANICS DATA ################################

    def get_dash(self, i_player: int):
        return self.get_mech_value(i_player, "Vapor Rush Charge")
    
    def get_dmg_boss(self, i_player: int):
        dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][0][self.real_phase_id]['damage']
        dmg += self.log.pjcontent['players'][i_player]['dpsTargets'][1][self.real_phase_id]['damage']
        return dmg

################################ QADIM ################################

class Q1(Boss):
    
    name       = "QADIM"
    wing       = 6
    boss_id    = 20934
    url_suffix = "qadim"
    
    center     = [411.5,431.1]
    fdp_radius = 70

    def get_mvp(self):
        mvp = []
        msg_fdp = self.mvp_fdp()
        if msg_fdp:
            mvp.append(msg_fdp)
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        msg_wave = self.mvp_wave()
        if msg_wave:
            mvp.append(msg_wave)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps) 
        return lvp
        
    ################################ MVP ################################
    
    def mvp_fdp(self):
        i_players = self.get_fdp()
        fdp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return self.msg("QADIM MVP PYRE S", fdp_names=fdp_names)
        if len(i_players) > 1:
            return self.msg("QADIM MVP PYRE P", fdp_names=fdp_names)
    
    def mvp_wave(self):
        i_players, max_waves, _ = Stats.get_max_value(self, self.get_wave)    
        mvp_names               = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return self.msg("QADIM MVP WAVE S", mvp_names=mvp_names, max_waves=max_waves)
        if len(i_players) > 1:
            return self.msg("QADIM MVP WAVE P", mvp_names=mvp_names, max_waves=max_waves)
        return
    
    ################################ LVP ################################ 
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ MECHANICS DATA ################################

    def get_fdp(self):
        fdp              = []
        start_p1, end_p1 = self.get_phase_timers("Qadim P1")
        start_p2, end_p2 = self.get_phase_timers("Qadim P2")
        if start_p1 is None or start_p2 is None:
            return fdp
        for i in self.player_list:
            if not self.is_tank(i):
                add_fdp = True
                pos_p1  = self.get_player_pos(i, start=start_p1, end=end_p1)
                pos_p2  = self.get_player_pos(i, start=start_p2, end=end_p2)
                for pos in pos_p1:
                    dist = get_dist(pos, Q1.center)
                    if dist > Q1.fdp_radius:
                        add_fdp = False
                        break        
                for pos in pos_p2:
                    dist = get_dist(pos, Q1.center)
                    if dist > Q1.fdp_radius:
                        add_fdp = False
                        break 
                if add_fdp:
                    fdp.append(i)
        return fdp
    
    def get_wave(self, i_player: int):
        return self.get_mech_value(i_player, "Mace Shockwave")

################################ ADINA ################################

class ADINA(Boss):
    
    name       = "ADINA"
    wing       = 7
    boss_id    = 22006
    url_suffix = "adina"
    
    def get_mvp(self):
        mvp = []
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
            
        msg_split = self.mvp_dmg_split()
        if msg_split:
            mvp.append(msg_split)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_split = self.lvp_dmg_split()
        if msg_split:
            lvp.append(msg_split)
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp
        
    ################################ MVP ################################

    def mvp_dmg_split(self):
        i_players, min_dmg, total_dmg = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support])
        mvp_names                     = self.players_to_string(i_players)
        if total_dmg:
            dmg_ratio                     = min_dmg / total_dmg * 100
            self.add_mvps(i_players)
            return self.msg("ADINA MVP SPLIT", mvp_names=mvp_names, dmg_ratio=dmg_ratio)
    
    ################################ LVP ################################    
    
    def lvp_dmg_split(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_split) 
        lvp_names                     = self.players_to_string(i_players)
        if total_dmg:
            dmg_ratio                     = max_dmg / total_dmg * 100
            self.add_lvps(i_players)
            return self.msg("ADINA LVP SPLIT", lvp_names=lvp_names, dmg_ratio=dmg_ratio)
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ MECHANICS DATA ################################
    
    def get_dmg_split(self, i_player: int):
        dmg_split1 = self.get_dmg_phase(i_player, 2)
        dmg_split2 = self.get_dmg_phase(i_player, 4)
        dmg_split3 = self.get_dmg_phase(i_player, 6)
        return dmg_split1 + dmg_split2 + dmg_split3    

################################ SABIR ################################

class SABIR(Boss):
    
    name       = "SABIR"
    wing       = 7
    boss_id    = 21964
    url_suffix = "sabir"
    
    def get_mvp(self):
        mvp = []
        msg_cc = self.get_mvp_cc_boss()
        if msg_cc:
            mvp.append(msg_cc)
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_cc = self.get_lvp_cc_boss()
        if msg_cc:
            lvp.append(msg_cc)
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp

    ################################ MVP ################################
    
    
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ MECHANICS DATA ################################

################################ QTP ################################

class QTP(Boss):
    
    name       = "QTP"
    wing       = 7
    boss_id    = 22000
    url_suffix = "qpeer"

    def get_mvp(self):
        mvp = []
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_pylon])
        if msg_bad_dps:
            mvp.append(msg_bad_dps)
        msg_cc = self.get_mvp_cc_total(extra_exclude=[self.is_pylon])
        if msg_cc:
            mvp.append(msg_cc)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_cc = self.get_lvp_cc_total()
        if msg_cc:
            lvp.append(msg_cc)
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp

    def is_alac(self, i_player: int):
        min_alac_contrib     = 30
        alac_id              = 30328
        boon_path            = self.log.pjcontent['players'][i_player].get("groupBuffsActive")
        player_alac_contrib  = 0
        pylon_players_in_sub = []
        if boon_path:
            for boon in boon_path:
                if boon["id"] == alac_id:
                    player_alac_contrib = boon["buffData"][self.real_phase_id]["generation"]
            pylon_players_in_sub = [i for i in self.player_list if self.is_pylon(i) and self.get_player_group(i_player) == self.get_player_group(i)]
        corrected_uptime = player_alac_contrib * 5 / (4 - len(pylon_players_in_sub))
        return corrected_uptime >= min_alac_contrib

    def is_quick(self, i_player: int):
        min_quick_contrib    = 30
        quick_id             = 1187
        boon_path            = self.log.pjcontent['players'][i_player].get("groupBuffsActive")
        player_quick_contrib = 0
        pylon_players_in_sub = []
        if boon_path:
            for boon in boon_path:
                if boon["id"] == quick_id:
                    player_quick_contrib = boon["buffData"][self.real_phase_id]["generation"]
            pylon_players_in_sub = [i for i in self.player_list if self.is_pylon(i) and self.get_player_group(i_player) == self.get_player_group(i)]
        corrected_uptime = player_quick_contrib * 5 / (4 - len(pylon_players_in_sub))
        return corrected_uptime >= min_quick_contrib

    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support, self.is_pylon])

    ################################ MVP ################################
    
    
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    def is_pylon(self, i_player: int):
        return self.get_orb_caught(i_player) > 1
    
    ################################ MECHANICS DATA ################################

    def get_orb_caught(self, i_player: int):
        return self.get_mech_value(i_player, "Critical Mass")
    
################################ GREER ################################

class GREER(Boss):
    
    name       = "GREER"
    wing       = 8
    boss_id    = 26725
    url_suffix = "greer"

    def get_mvp(self):
        mvp = []
        msg_dps = self.get_bad_dps()
        if msg_dps:
            mvp.append(msg_dps)
        msg_cc = self.get_mvp_cc_boss()
        if msg_cc:
            mvp.append(msg_cc)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_cc = self.get_lvp_cc_boss()
        if msg_cc:
            lvp.append(msg_cc)
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp

    ################################ MVP ################################
    
    
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ MECHANICS DATA ################################
    
################################ GREER ################################

class DECIMA(Boss):
    
    name       = "DECIMA"
    wing       = 8
    boss_id    = 26774
    url_suffix = "deci"
    trigger_ids = (26774, 26867)

    def get_mvp(self):
        mvp = []
        msg_dps = self.get_bad_dps()
        if msg_dps:
            mvp.append(msg_dps)
        msg_cc = self.get_mvp_cc_boss()
        if msg_cc:
            mvp.append(msg_cc)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_cc = self.get_lvp_cc_boss()
        if msg_cc:
            lvp.append(msg_cc)
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp

    ################################ MVP ################################
    
    
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ MECHANICS DATA ################################
    
################################ GREER ################################

class URA(Boss):
    
    name       = "URA"
    wing       = 8
    boss_id    = 26712
    url_suffix = "ura"

    def get_mvp(self):
        mvp = []
        msg_dps = self.get_bad_dps()
        if msg_dps:
            mvp.append(msg_dps)
        return mvp
    
    def get_lvp(self):
        lvp = []
        msg_dps = self.get_lvp_dps()
        if msg_dps:
            lvp.append(msg_dps)
        return lvp

    ################################ MVP ################################
    
    
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ MECHANICS DATA ################################
    
################################ GOLEM CHAT STANDARD ################################

class GOLEM(Boss):
    
    name    = "GOLEM CHAT STANDARD"
    boss_id = 16199
    trigger_ids = (16199, 19645)
