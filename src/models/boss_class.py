from datetime import datetime, timedelta, timezone
import requests
import pytz

from models.player_class import *
from const import ALL_PLAYERS, BOSS_DICT, CUSTOM_NAMES, BIG
from models.log_class import Log
import func
from languages import LANGUES

class Boss:  

    name       = None
    wing       = 0
    boss_id    = -1
    real_phase = "Full Fight"

    def __init__(self, log: Log):
        self.log                = log
        self.cm                 = self.is_cm()
        self.logName            = self.get_logName()
        self.mechanics          = self.get_mechanics()
        self.duration_ms        = self.get_duration_ms() 
        self.start_date         = self.get_start_date()
        self.end_date           = self.get_end_date()
        self.player_list        = self.get_player_list()
        self.wingman_time       = self.get_wingman_time()
        self.wingman_percentile = self.get_wingman_percentile()
        self.real_phase_id      = self.get_phase_id(self.real_phase)
        self.time_base          = self.get_time_base()
        self.mvp_accounts       = []
        self.lvp_accounts       = []
        for i in self.player_list:
            account = self.get_player_account(i)
            player  = ALL_PLAYERS.get(account)
            if not player:
                new_player           = Player(self, account)
                ALL_PLAYERS[account] = new_player
            else:
                player.add_boss(self)
                
    def __repr__(self) -> str:
        return self.log.url    
        
    ################################ Fonction pour attribus Boss ################################
    
    def is_cm(self):
        return self.log.pjcontent['isCM']
    
    def get_logName(self):
        return self.log.pjcontent['fightName']
    
    def get_mechanics(self):
        mechs        = []
        mechanic_map = self.log.jcontent['mechanicMap']
        for mechanic in mechanic_map:
            is_player_mechanic = mechanic['playerMech']
            if is_player_mechanic:
                mechs.append(mechanic)
                
        return mechs
    
    def get_duration_ms(self):
        return self.log.pjcontent['durationMS']
    
    def get_start_date(self):
        start_date_text = self.log.pjcontent['timeStartStd']
        date_format     = "%Y-%m-%d %H:%M:%S %z"
        start_date      = datetime.strptime(start_date_text, date_format)
        paris_timezone  = timezone(timedelta(hours=1))
        return start_date.astimezone(paris_timezone)
    
    def get_end_date(self):
        end_date_text  = self.log.pjcontent['timeEndStd']
        date_format    = "%Y-%m-%d %H:%M:%S %z"
        end_date       = datetime.strptime(end_date_text, date_format)
        paris_timezone = timezone(timedelta(hours=1))
        return end_date.astimezone(paris_timezone)

    def get_wingman_time(self):
        # return None
        w_boss_id = self.boss_id * (-1) ** self.cm
        url       = f"https://gw2wingman.nevermindcreations.de/api/boss?era=latest&bossID={w_boss_id}"
        r         = requests.get(url)
        if not r.ok:
            print("wingman faled")
            print(r.status_code)
            print(r.content)
            return None
        data = r.json()
        if data.get("error"):
            print("wingman failed")
            print(data["error"])
            return None
        return [data["duration_med"], data["duration_top"]]
    
    def get_player_list(self):
        real_players = []
        players      = self.log.pjcontent['players']
        for i_player, player in enumerate(players):
            if player['group'] < 50 and not self.is_buyer(i_player):
                real_players.append(i_player)
                
        return real_players
    
    def get_wingman_percentile(self):
        time_stamp = int(self.get_start_date().timestamp())
        requestUrl = f"https://gw2wingman.nevermindcreations.de/api/getPercentileByMetadata?bossID={self.boss_id}&isCM={self.cm}&duration={self.duration_ms}&timestamp={time_stamp}"
        infos      = requests.get(requestUrl).json()
        if infos.get("percentile"):
            return infos["percentile"]
        return                  
            
    ################################ CONDITIONS ################################

    def is_quick(self, i_player: int):
        min_quick_contrib    = 30
        quick_id             = 1187
        boon_path            = self.log.pjcontent['players'][i_player].get("groupBuffsActive")
        player_quick_contrib = 0
        if boon_path:
            for boon in boon_path:
                if boon["id"] == quick_id:
                    player_quick_contrib = boon["buffData"][self.real_phase_id]["generation"]
        return player_quick_contrib >= min_quick_contrib

    def is_alac(self, i_player: int):
        min_alac_contrib    = 30
        alac_id             = 30328
        boon_path           = self.log.pjcontent['players'][i_player].get("groupBuffsActive")
        player_alac_contrib = 0
        if boon_path:
            for boon in boon_path:
                if boon["id"] == alac_id:
                    player_alac_contrib = boon["buffData"][self.real_phase_id]["generation"]
        return player_alac_contrib >= min_alac_contrib

    def is_support(self, i_player: int):
        prof = self.log.pjcontent['players'][i_player]['profession']
        is_druid_supp = False
        delta = self.start_date - datetime(2022,7,17,23,0,0,tzinfo=pytz.FixedOffset(60))
        if prof == "Druid" and delta.total_seconds() < 0:
            is_druid_supp = True
        return self.is_quick(i_player) or self.is_alac(i_player) or is_druid_supp or self.is_bannerslave(i_player)
    
    def is_dps(self, i_player: int):
        return not self.is_support(i_player)
    
    def is_tank(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['toughness'] > 0
    
    def is_heal(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['healing'] > 0
    
    def is_dead(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['defenses'][0]['deadCount'] > 0
    
    def is_buyer(self, i_player: int):
        player_name = self.get_player_name(i_player)
        mechanics   = self.log.pjcontent.get('mechanics')
        if mechanics:
            death_history = [death for mech in mechanics if mech['name'] == "Dead" for death in mech['mechanicsData']]
            for death in death_history:
                if death['time'] < 20000 and death['actor'] == player_name:
                    return True
        try:
            rota = self.get_player_rotation(i_player)
        except:
            return True
        return False
    
    def is_buff_up(self, i_player: int, target_time: int, buff_name: str):
        buffmap = self.log.pjcontent['buffMap']
        buff_id = None
        for id, buff in buffmap.items():
            if buff['name'] == buff_name:
                buff_id = int(id[1:])
                break
        if buff_id is None:
            return False
        buffs = self.log.pjcontent['players'][i_player]['buffUptimes']
        for buff in buffs:
            if buff['id'] == buff_id:
                buffplot = buff['states']
                break
        xbuffplot = [pos[0] for pos in buffplot]
        ybuffplot = [pos[1] for pos in buffplot]
        
        left_value = None
        for time in xbuffplot:
            if time <= target_time:
                left_value = time
            else:
                break
        left_index = xbuffplot.index(left_value)
        if ybuffplot[left_index]:
            return True
        return False
    
    def is_dead_instant(self, i_player: int):
        downs_deaths = self.get_player_mech_history(i_player, ["Downed", "Dead"])
        if downs_deaths:
            if downs_deaths[-1]['name'] == "Dead":
                if len(downs_deaths) == 1:
                    return True
                if len(downs_deaths) > 1:
                    if downs_deaths[-2]['time'] < downs_deaths[-1]['time']-8000:
                        return True
        return False
    
    def is_condi(self, i_player: int):
        power_dmg = self.log.pjcontent['players'][i_player]['dpsAll'][0]['powerDamage']
        condi_dmg = self.log.pjcontent['players'][i_player]['dpsAll'][0]['condiDamage']
        return condi_dmg > power_dmg
    
    def is_power(self, i_player: int):
        return not self.is_condi(i_player)

    def is_bannerslave(self, i_player):
        delta = self.start_date - datetime(2022,7,17,23,0,0,tzinfo=pytz.FixedOffset(60))
        prof = self.log.pjcontent['players'][i_player]['profession']
        if prof == "Warrior" or prof == "Berserker" and delta.total_seconds() < 0:
            banner1 = 14449
            banner2 = 14417
            if self.log.pjcontent['players'][i_player].get('groupBuffs'):
                groupBuff = self.log.pjcontent['players'][i_player]['groupBuffs']
                for buff in groupBuff:
                    if buff['id'] == banner1 or buff['id'] == banner2:
                        return True
        return False
    
    ################################ DATA JOUEUR ################################
    
    def get_player_name(self, i_player: int):
        return self.log.jcontent['players'][i_player]['name']
    
    def get_player_account(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['account']
    
    def get_player_pos(self, i_player: int , start: int = 0, end: int = None):
        return self.log.pjcontent['players'][i_player]['combatReplayData']['positions'][start:end]
    
    def get_cc_boss(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['dpsTargets'][0][0]['breakbarDamage']
    
    def get_dmg_boss(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['dpsTargets'][0][self.real_phase_id]['damage']
    
    def get_cc_total(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['dpsAll'][0]['breakbarDamage']
    
    def get_player_id(self, name: str):
        players = self.log.pjcontent['players'] 
        for i_player, player in enumerate(players):
            if player['name'] == name:
                return i_player
        return None
    
    def get_player_spe(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['profession']
    
    def get_player_mech_history(self, i_player: int, mechs: list[str] = []):
        history      = []
        player_name  = self.get_player_name(i_player)
        mech_history = self.log.pjcontent['mechanics']
        for mech in mech_history:
            for data in mech['mechanicsData']:
                if data['actor'] == player_name:
                    if mechs:
                        if mech['name'] in mechs:
                            history.append({"name": mech['name'], "time": data['time']})
                    else:
                        history.append({"name": mech['name'], "time": data['time']})
        history.sort(key=lambda mech: mech["time"], reverse=False)
        return history
    
    def players_to_string(self, i_players: list[int]):
        name_list = []
        for i in i_players:
            account = self.get_player_account(i)
            custom_name = CUSTOM_NAMES.get(account)
            if custom_name:
                name_list.append(custom_name)
            else:
                name_list.append(self.get_player_name(i))
        return "__"+'__ / __'.join(name_list)+"__"
    
    def get_player_death_timer(self, i_player: int):
        if self.is_dead(i_player):
            mech_history = self.get_player_mech_history(i_player, ["Dead"])
            if mech_history:
                return mech_history[-1]['time']
        return
    
    def get_player_rotation(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['rotation']
    
    def time_entered_area(self, i_player: int, center: list[float], radius: float):
        poses = self.get_player_pos(i_player)
        for i, pos in enumerate(poses):
            if func.get_dist(pos, center) < radius:
                return i*150
        return
    
    def time_exited_area(self, i_player, center: list[float], radius: float):
        time_enter = self.time_entered_area(i_player, center, radius)
        if time_enter:
            i_enter = int(time_enter/150)
            poses   = self.get_player_pos(i_player)[i_enter:]
            for i, pos in enumerate(poses):
                if func.get_dist(pos, center) > radius:
                    return (i+i_enter) * 150
        return
    
    def add_mvps(self, players: list[int]):
        self.mvp_accounts = [self.get_player_account(i) for i in players]
        for i in players:
            account = self.get_player_account(i)
            ALL_PLAYERS[account].mvps += 1
                
    def add_lvps(self, players: list[int]):
        self.lvp_accounts = [self.get_player_account(i) for i in players]
        for i in players:
            account = self.get_player_account(i)
            ALL_PLAYERS[account].lvps += 1
            
    def _get_dps_contrib(self, exclude: list[classmethod]=[]):
        dps_ranking = {}
        max_dps     = 0
        for i in self.player_list:
            if any(filter_func(i) for filter_func in exclude):
                continue
            player_dps = self.log.pjcontent['players'][i]['dpsTargets'][0][self.real_phase_id]['damage']
            if player_dps > max_dps:
                max_dps = player_dps
            dps_ranking[self.log.pjcontent['players'][i]['account']] = player_dps
        for player in dps_ranking:
            dps_ranking[player] = 20 * dps_ranking[player] / max_dps
        return dps_ranking

    def get_dps_ranking(self):
        return self._get_dps_contrib([self.is_support])
    
    def get_player_group(self, i_player: int):
        return self.log.pjcontent["players"][i_player]["group"]
    
    def get_foodswap_count(self, i_player: int):
        foodSwapIcon  = "https://wiki.guildwars2.com/images/d/d6/Champion_of_the_Crown.png"
        foodSwapId    = []
        buffMap       = self.log.pjcontent["buffMap"]
        buffUptimes   = self.log.pjcontent["players"][i_player]["buffUptimes"]
        foodSwapCount = 0
        for buffName, data in buffMap.items():
            if data.get("icon") == foodSwapIcon:
                foodSwapId.append(int(buffName[1:]))
        for buff in buffUptimes:
            if buff["id"] in foodSwapId:
                for state in buff["states"]:
                    if state[1] == 1:
                        foodSwapCount += 1
        return foodSwapCount

    ################################ MVP ################################
    
    def get_mvp_cc_boss(self, extra_exclude: list[classmethod]=[]):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_boss, exclude=[*extra_exclude])
        if total_cc == 0:
            return
        self.add_mvps(i_players)  
        mvp_names  = self.players_to_string(i_players)
        cc_ratio   = min_cc / total_cc * 100
        number_mvp = len(i_players)  
        if min_cc == 0:
            if number_mvp == 1:
                return LANGUES["selected_language"]["MVP BOSS 0 CC S"].format(mvp_names=mvp_names)
            else:
                return LANGUES["selected_language"]["MVP BOSS 0 CC P"].format(mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return LANGUES["selected_language"]["MVP BOSS CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return LANGUES["selected_language"]["MVP BOSS CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
    
    def get_mvp_cc_total(self,extra_exclude: list[classmethod]=[]):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_total, exclude=[*extra_exclude])
        if total_cc == 0:
            return
        self.add_mvps(i_players)  
        mvp_names  = self.players_to_string(i_players)
        cc_ratio   = min_cc / total_cc * 100
        number_mvp = len(i_players)  
        if min_cc == 0:
            if number_mvp == 1:
                return LANGUES["selected_language"]["MVP TOTAL 0 CC S"].format(mvp_names=mvp_names)
            else:
                return LANGUES["selected_language"]["MVP TOTAL 0 CC P"].format(mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return LANGUES["selected_language"]["MVP TOTAL CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return LANGUES["selected_language"]["MVP TOTAL CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
    
    def get_bad_dps(self, extra_exclude: list[classmethod]=[]):
        i_sup, sup_max_dmg, _ = Stats.get_max_value(self, self.get_dmg_boss, exclude=[self.is_dps, self.is_bannerslave])
        sup_name              = self.players_to_string(i_sup)
        bad_dps               = []
        for i in self.player_list:   
            if any(filter_func(i) for filter_func in extra_exclude) or self.is_dead(i) or self.is_support(i) or self.is_bannerslave(i):
                continue
            dps = self.get_dmg_boss(i)
            if dps < sup_max_dmg:
                if not(self.name == "QUOIDIMM" and self.get_player_spe(i) == "Spellbreaker"): 
                    bad_dps.append(i)
        if bad_dps:
            self.add_mvps(bad_dps)
            bad_dps_name = self.players_to_string(bad_dps)
            if len(bad_dps) == 1:
                return LANGUES["selected_language"]["MVP BAD DPS S"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)
            else:
                return LANGUES["selected_language"]["MVP BAD DPS P"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)
    
    ################################ LVP ################################
    
    def get_lvp_cc_boss(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_boss)
        if total_cc == 0:
            return
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        cc_ratio  = max_cc / total_cc * 100
        return LANGUES["selected_language"]["LVP BOSS CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)
    
    def get_lvp_cc_total(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_total)
        if total_cc == 0:
            return
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        cc_ratio  = max_cc / total_cc * 100
        return LANGUES["selected_language"]["LVP TOTAL CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)
    
    def get_lvp_dps(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_boss)
        dmg_ratio                     = max_dmg / total_dmg * 100
        lvp_dps_name                  = self.players_to_string(i_players)
        dps                           = max_dmg / self.duration_ms
        foodSwapCount                 = self.get_foodswap_count(i_players[0])
        self.add_lvps(i_players) 
        if foodSwapCount:
            return LANGUES["selected_language"]["LVP DPS FOODSWAP"].format(lvp_dps_name=lvp_dps_name, max_dmg=max_dmg, dmg_ratio=dmg_ratio, dps=dps, foodSwapCount=foodSwapCount)
        return LANGUES["selected_language"]["LVP DPS"].format(lvp_dps_name=lvp_dps_name, max_dmg=max_dmg, dmg_ratio=dmg_ratio, dps=dps)
    ################################ DATA BOSS ################################
    
    def get_pos_boss(self, start: int = 0, end: int = None):
        targets = self.log.pjcontent['targets']
        for target in targets:
            if target['id'] in BOSS_DICT.keys():
                return target['combatReplayData']['positions'][start:end]
        raise ValueError('No Boss in targets')
    
    def get_phase_timers(self, target_phase: str, inMilliSeconds=False):
        phases = self.log.pjcontent['phases']
        for phase in phases:
            if phase['name'] == target_phase:  
                start = phase['start']
                end   = phase['end']
                if inMilliSeconds:
                    return start, end
                return func.time_to_index(start, self.time_base), func.time_to_index(end, self.time_base)
        raise ValueError(f'{target_phase} not found')
    
    def get_mech_value(self, i_player: int, mech_name: str, phase: str="Full Fight"):
        phase      = self.get_phase_id(phase)
        mechs_list = [mech['name'] for mech in self.mechanics]
        if mech_name in mechs_list:
            i_mech = mechs_list.index(mech_name)
            return self.log.jcontent['phases'][phase]['mechanicStats'][i_player][i_mech][0]
        return 0
    
    def bosshp_to_time(self, hp: float):
        hp_percents = self.log.pjcontent['targets'][0]['healthPercents']
        for timer in hp_percents:
            if timer[1] < hp:
                return timer[0]
        return
    
    def get_mechanic_history(self, name: str):
        mechanics = self.log.pjcontent['mechanics']
        for mech in mechanics:
            if mech['fullName'] == name:
                return mech['mechanicsData']
        return
    
    def get_phase_id(self, name: str):
        phases = self.log.pjcontent["phases"]
        for i, phase in enumerate(phases):
            if phase["name"] == name:
                return i
        return 0  
    
    def get_time_base(self):
        delta = self.log.pjcontent["players"][0]["combatReplayData"]["end"]-self.log.pjcontent["players"][0]["combatReplayData"]["start"]
        lpos  = len(self.log.pjcontent["players"][0]["combatReplayData"]["positions"])
        return int(delta/lpos) 
            
    
class Stats:
    @staticmethod
    def get_max_value(boss : Boss,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):  
        if exclude is None:
            exclude = []
        value_max = -1
        value_tot = 0
        i_maxs    = []
        for i in boss.player_list:
            value      = fnc(i)
            value_tot += value
            if any(filter_func(i) for filter_func in exclude):
                continue
            if value > value_max:
                value_max = value
                i_maxs = [i]
            elif value == value_max:
                i_maxs.append(i)
        if value_max == 0:
            return [], value_max, value_tot
        return i_maxs, value_max, value_tot
        
    @staticmethod
    def get_min_value(boss : Boss,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):

        if exclude is None:
            exclude = []
        value_min = BIG
        value_tot = 0
        i_mins    = []
        for i in boss.player_list:
            value      = fnc(i)
            value_tot += value
            if any(filter_func(i) for filter_func in exclude):
                continue
            if value < value_min:
                value_min = value
                i_mins = [i]
            elif value == value_min:
                i_mins.append(i)
        return i_mins, value_min, value_tot

    @staticmethod
    def get_tot_value(boss : Boss,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):
                
        if exclude is None:
            exclude = []
        value_tot = 0
        for i in boss.player_list:
            if any(filter_func(i) for filter_func in exclude):
                continue
            value_tot += fnc(i)
        return value_tot