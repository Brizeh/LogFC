from datetime import datetime, timedelta, timezone
import pytz

from .player_class import *
from ..const import CUSTOM_NAMES, BIG, ALL_MECHS
from .log_class import Log
from .. import func
from ..mechanics import get_icd, mech_value, player_mechanics

class Boss:

    # Each subclass registers itself at import time via its boss_id: no
    # lookup table needs to be kept in sync elsewhere.
    registry   = {}

    name        = None
    wing        = 0
    boss_id     = -1    # wingman API identifier
    trigger_ids = ()    # log triggerIDs; defaults to (boss_id,).
                        # Declare when the two differ (DARKAI, HT,
                        # KO, OLC) or a boss has several triggerIDs.
    url_suffix  = None  # dps.report URL suffix; None = not detected
                        # in a pasted list of logs (the golem's case)
    real_phase  = "Full Fight"
    needs_replay_data = False  # set True by a boss whose MVP/LVP logic
                                # reads self.log.replay_data (see combat_replay.py)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.boss_id < 0:
            raise ValueError(f"{cls.__name__} has no boss_id: it would be silently ignored")
        boss_ids = cls.trigger_ids or (cls.boss_id,)
        # validate everything before registering anything, so an error
        # never leaves a partial registration behind
        for boss_id in boss_ids:
            known = Boss.registry.get(boss_id)
            if known is not None:
                raise ValueError(f"triggerID {boss_id} already taken by {known.__name__}, redeclared by {cls.__name__}")
        for boss_id in boss_ids:
            Boss.registry[boss_id] = cls

    @classmethod
    def url_suffixes(cls):
        """Suffixes detectable in a pasted list of logs."""
        return {boss.url_suffix for boss in cls.registry.values() if boss.url_suffix}

    def mechanic_exclusions(self, mech_name: str):
        """Time ranges (start_ms, end_ms) to drop from a mechanic's events.

        Empty by default. A boss overrides this for one-off counting
        adjustments (e.g. DHUUM discards "Ender's Pick up" events fired
        near the start of "Shielded Dhuum") without touching the shared
        aggregation logic in mechanics.mech_value.
        """
        return []

    def __init__(self, log: Log, analysis):
        self.log                = log
        self.analysis           = analysis
        self.cm                 = self.is_cm()
        self.logName            = self.get_logName()
        self.mechanics          = self.get_mechanics()
        self.duration_ms        = self.get_duration_ms() 
        self.start_date         = self.get_start_date()
        self.end_date           = self.get_end_date()
        self.player_list        = self.get_player_list()
        self.wingman_percentile = None  # renseigne par wingman.fetch_percentiles
        self.real_phase_id      = self.get_phase_id(self.real_phase)
        self.time_base          = self.get_time_base()
        self.mvp_accounts       = []
        self.lvp_accounts       = []
        for i in self.player_list:
            account = self.get_player_account(i)
            player  = self.analysis.players.get(account)
            if not player:
                self.analysis.players[account] = Player(self, account)
            else:
                player.add_boss(self)
        self.mvp     = self.get_mvp()
        self.lvp     = self.get_lvp()
        self.box     = None #self.get_box()
        self.outputs = [self.mvp, self.lvp, self.box]
        self.add_players_mechs()
                
    def __repr__(self) -> str:
        return self.log.url

    def msg(self, key: str, **kwargs) -> str:
        """Localized message, in the current analysis' language."""
        template = self.analysis.language.get(key)
        if template is None:
            raise KeyError(f"message key missing from both language dictionaries: {key!r}")
        return template.format(**kwargs)

    ################################ Boss attribute functions ################################
    
    def is_cm(self):
        return self.log.pjcontent['isCM']
    
    def get_logName(self):
        return self.log.pjcontent['fightName']
    
    def get_mechanics(self):
        return player_mechanics(self.log.pjcontent)
    
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

    def get_player_list(self):
        real_players = []
        players      = self.log.pjcontent['players']
        for i_player, player in enumerate(players):
            if player['group'] < 50 and not self.is_buyer(i_player):
                real_players.append(i_player)
                
        return real_players
    
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
    
    ################################ PLAYER DATA ################################
    
    def get_player_name(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['name']
    
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
    
    def player_name_to_id(self, name: str):
        players = self.log.pjcontent['players'] 
        for i_player, player in enumerate(players):
            if player['name'] == name:
                return i_player
        return None
    
    def player_account_to_id(self, account: str):
        players = self.log.pjcontent['players'] 
        for i_player, player in enumerate(players):
            if player['account'] == account:
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
                            history.append({"name": mech['name'], "time": data['time'], "fullName": mech['fullName'], "description": mech['description']})
                    else:
                        history.append({"name": mech['name'], "time": data['time'], "fullName": mech['fullName'], "description": mech['description']})
        history.sort(key=lambda mech: mech["time"], reverse=False)
        return history
    
    def players_to_string(self, i_players: list[int]):
        name_list = []
        for i in i_players:
            account = self.get_player_account(i)
            custom_name = CUSTOM_NAMES.get(account)
            if custom_name:
                if type(custom_name) == str:
                    name_list.append(custom_name)
                else:
                    discord_name = custom_name.get("discord")
                    if discord_name:
                        name_list.append(discord_name)
                    else:
                        name_list.append(custom_name.get("nickname"))
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
                return i*self.time_base
        return
    
    def time_exited_area(self, i_player, center: list[float], radius: float):
        time_enter = self.time_entered_area(i_player, center, radius)
        if time_enter:
            i_enter = int(time_enter/150)
            poses   = self.get_player_pos(i_player)[i_enter:]
            for i, pos in enumerate(poses):
                if func.get_dist(pos, center) > radius:
                    return (i+i_enter) * self.time_base
        return
    
    def add_mvps(self, players: list[int]):
        self.mvp_accounts = [self.get_player_account(i) for i in players]
        for i in players:
            account = self.get_player_account(i)
            self.add_player_stat("Titles", "MVP", 1, account, description="Number of MVP titles")
            self.analysis.players[account].mvps += 1

    def add_lvps(self, players: list[int]):
        self.lvp_accounts = [self.get_player_account(i) for i in players]
        for i in players:
            account = self.get_player_account(i)
            self.add_player_stat("Titles", "LVP", 1, account, description="Number of LVP titles")
            self.analysis.players[account].lvps += 1
            
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
    
    def get_box(self):
        player1_acc = "Ravi.5812"
        player2_acc = "endymion.3162"
        player1 = self.analysis.players.get(player1_acc)
        player2 = self.analysis.players.get(player2_acc)
        if player1 and player2:
            if player1.boxWins is None:
                player1.boxWins = 0
            if player2.boxWins is None:
                player2.boxWins = 0
            box_class = "Catalyst"
            player1_id = self.player_account_to_id(player1_acc)
            player2_id = self.player_account_to_id(player2_acc)
            if player1_id is not None and player2_id is not None:
                player1_class = self.log.pjcontent["players"][player1_id]["profession"]
                player2_class = self.log.pjcontent["players"][player2_id]["profession"]
                if player1_class == box_class and player2_class == box_class:
                    player1_dmg = self.get_dmg_boss(player1_id)
                    player2_dmg = self.get_dmg_boss(player2_id)
                    if player1_dmg > player2_dmg:
                        player1.boxWins += 1
                        return f"# :boxing_glove: *__{player1.nickname}__ a battu __{player2.nickname}__* :boxing_glove:"
                    else:
                        player2.boxWins += 1
                        return f"# :boxing_glove: *__{player2.nickname}__ a battu __{player1.nickname}__* :boxing_glove:"
        return

    ################################ MVP ################################
    
    def get_mvp(self):
        return
    
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
                return self.msg("MVP BOSS 0 CC S", mvp_names=mvp_names)
            else:
                return self.msg("MVP BOSS 0 CC P", mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return self.msg("MVP BOSS CC S", mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return self.msg("MVP BOSS CC P", mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
    
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
                return self.msg("MVP TOTAL 0 CC S", mvp_names=mvp_names)
            else:
                return self.msg("MVP TOTAL 0 CC P", mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return self.msg("MVP TOTAL CC S", mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return self.msg("MVP TOTAL CC P", mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
    
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
                return self.msg("MVP BAD DPS S", bad_dps_name=bad_dps_name, sup_name=sup_name)
            else:
                return self.msg("MVP BAD DPS P", bad_dps_name=bad_dps_name, sup_name=sup_name)
            
    def add_player_stat(self, category: str, stat: str, value, account: str, description: str = None):
        extra_mechs = self.analysis.extra_mechs
        if description:
            extra_mechs.setdefault(category, {}).setdefault(stat, description)
        # ALL_MECHS is shared configuration: derived labels go into the
        # analysis instead, or they'd pile up from one run to the next
        if ALL_MECHS.get(category) and "avg" not in stat:
            extra_mechs.setdefault(category, {}).setdefault("avg" + stat, f"Average {stat} uptime")

        stat_description = ALL_MECHS.get(category, {}).get(stat) or extra_mechs.get(category, {}).get(stat)
        arxiv_stats = self.analysis.arxiv.setdefault(self.log.url, {}).setdefault(account, {}).setdefault(category, {})
        arxiv_stats[stat] = {"value": value, "description": stat_description}
        
                    
    def add_players_mechs(self):
        for i in self.player_list:
            account = self.get_player_account(i)
            # Damage stats
            dmgTarget = self.log.pjcontent['players'][i]['dpsTargets'][0][0]
            dmgAll = self.log.pjcontent['players'][i]['dpsAll'][0]
            self.add_player_stat("Damage Stats", "DmgTarget", dmgTarget["damage"], account)
            self.add_player_stat("Damage Stats", "DmgPowerTarget", dmgTarget["powerDamage"], account)
            self.add_player_stat("Damage Stats", "DmgCondiTarget", dmgTarget["condiDamage"], account)
            self.add_player_stat("Damage Stats", "CcTarget", dmgTarget["breakbarDamage"], account)
            self.add_player_stat("Damage Stats", "DmgAll", dmgAll["damage"], account)
            self.add_player_stat("Damage Stats", "DmgPowerAll", dmgAll["powerDamage"], account)
            self.add_player_stat("Damage Stats", "DmgCondiAll", dmgAll["condiDamage"], account)
            self.add_player_stat("Damage Stats", "CcAll", dmgAll["breakbarDamage"], account)

            # Gameplay stats
            statsAll = self.log.pjcontent['players'][i]['statsAll'][0]
            self.add_player_stat("Gameplay Stats", "TimeWasted", statsAll["timeWasted"], account)
            self.add_player_stat("Gameplay Stats", "BadCancels", statsAll["wasted"], account)
            self.add_player_stat("Gameplay Stats", "TimeSaved", statsAll["timeSaved"], account)
            self.add_player_stat("Gameplay Stats", "GoodCancels", statsAll["saved"], account)
            self.add_player_stat("Gameplay Stats", "WeaponSwaps", statsAll["swapCount"], account)
            self.add_player_stat("Gameplay Stats", "avgCombatUptime", statsAll["skillCastUptime"], account)
            self.add_player_stat("Gameplay Stats", "avgCombatNoAAUptime", statsAll["skillCastUptimeNoAA"], account)
            self.add_player_stat("Gameplay Stats", "avgDistSqd", statsAll["stackDist"], account)
            self.add_player_stat("Gameplay Stats", "avgDistCom", statsAll["distToCom"], account)

            # Offensive stats
            statsTarget = self.log.pjcontent['players'][i]['statsTargets'][0][0]
            critHit, critableHit = statsTarget["criticalRate"], statsTarget["critableDirectDamageCount"]
            if critableHit == 0:
                critableHit = 1
            self.add_player_stat("Offensive Stats", "avgCritRate", critHit/critableHit*100, account)
            flankHit, allHit = statsTarget["flankingRate"], statsTarget["connectedDirectDamageCount"]
            if allHit == 0:
                allHit = 1
            self.add_player_stat("Offensive Stats", "avgFlankRate", flankHit/allHit*100, account)
            power90Hit, powerHit = statsTarget["connectedPowerAbove90HPCount"], statsTarget["connectedPowerCount"]
            if powerHit == 0:
                powerHit = 1
            self.add_player_stat("Offensive Stats", "avgWritPower", power90Hit/powerHit*100, account)
            condi90Hit, condiHit = statsTarget["connectedConditionAbove90HPCount"], statsTarget["connectedConditionCount"]
            if condiHit == 0:
                condiHit = 1
            self.add_player_stat("Offensive Stats", "avgWritCondi", condi90Hit/condiHit*100, account)
            glanceHit = statsTarget["glanceRate"]
            self.add_player_stat("Offensive Stats", "avgGlanceRate", glanceHit/allHit*100, account)

            # Defensive stats
            defenses = self.log.pjcontent['players'][i]['defenses'][0]
            self.add_player_stat("Defensive Stats", "DmgTaken", defenses["damageTaken"], account)
            self.add_player_stat("Defensive Stats", "PowerDmgTaken", defenses["powerDamageTaken"], account)
            self.add_player_stat("Defensive Stats", "CondiDmgTaken", defenses["conditionDamageTaken"], account)
            self.add_player_stat("Defensive Stats", "BreakbarDmgTaken", defenses["breakbarDamageTaken"], account)
            self.add_player_stat("Defensive Stats", "DmgBarrier", defenses["damageBarrier"], account)
            self.add_player_stat("Defensive Stats", "Interrupted", defenses["interruptedCount"], account)
            self.add_player_stat("Defensive Stats", "Cced", defenses["receivedCrowdControl"], account)
            self.add_player_stat("Defensive Stats", "CcTime", defenses["receivedCrowdControlDuration"]/1000, account)
            self.add_player_stat("Defensive Stats", "Evaded", defenses["evadedCount"], account)
            self.add_player_stat("Defensive Stats", "Blocked", defenses["blockedCount"], account)
            self.add_player_stat("Defensive Stats", "Dodged", defenses["dodgeCount"], account)
            self.add_player_stat("Defensive Stats", "Downed", defenses["downCount"], account)
            self.add_player_stat("Defensive Stats", "DownedTime", defenses["downDuration"]/1000, account)
            self.add_player_stat("Defensive Stats", "Dead", defenses["deadCount"], account)
            self.add_player_stat("Defensive Stats", "DeadTime", defenses["deadDuration"]/1000, account)

            # Support stats
            support = self.log.pjcontent['players'][i]['support'][0]
            self.add_player_stat("Support Stats", "CondiCleans", support["condiCleanse"], account)
            self.add_player_stat("Support Stats", "CondiCleansTime", support["condiCleanseTime"], account)
            self.add_player_stat("Support Stats", "SelfCleans", support["condiCleanseSelf"], account)
            self.add_player_stat("Support Stats", "SelfCleansTime", support["condiCleanseTimeSelf"], account)
            self.add_player_stat("Support Stats", "BoonStrips", support["boonStrips"], account)
            self.add_player_stat("Support Stats", "BoonStripsTime", support["boonStripsTime"], account)
            self.add_player_stat("Support Stats", "StunBreak", support["stunBreak"], account)
            self.add_player_stat("Support Stats", "StunBreakTime", support["removedStunDuration"]/1000, account)
            self.add_player_stat("Support Stats", "Resurrects", support["resurrects"], account)
            self.add_player_stat("Support Stats", "ResurrectTime", support["resurrectTime"], account)
            self.add_player_stat("Support Stats", "avgBoons", statsAll["avgBoons"], account)

            # Buffs
            buffUptimesActive = self.log.pjcontent["players"][i]["buffUptimesActive"]
            for buff in buffUptimesActive:
                data = self.getBuff(buff["id"])
                uptime = buff["buffData"][0]["uptime"]
                if data:
                    name = data["name"].replace(" ", "").replace("'", "").replace(":", "")
                    description = data['name']
                    category = data["classification"]
                    # Add EXTRA MECH
                    extra_mechs = self.analysis.extra_mechs
                    if category not in extra_mechs.keys():
                        extra_mechs[category] = {}
                    if name not in extra_mechs[category].keys():
                        extra_mechs[category][name] = f"{description} Total Usage"
                        extra_mechs[category]["avg"+name] = f"Average {description} Uptime"
                    # Add player mech
                    self.add_player_stat(category, name, uptime, account)

            # Mechanics
            player_name = self.get_player_name(i)
            start, end  = self.get_phase_bounds(0)
            trigger_id  = self.log.pjcontent['triggerID']
            for mechanic in self.mechanics:
                icd = get_icd(trigger_id, mechanic['fullName'])
                exclude = self.mechanic_exclusions(mechanic['fullName'])
                value = mech_value(mechanic, player_name, icd, start, end, exclude)
                description = f"{mechanic['fullName']} : {mechanic['description']}"
                self.add_player_stat("Mechanics", mechanic['name'], value, account, description=description)
    
    ################################ LVP ################################
    
    def get_lvp(self):
        return 
    
    def get_lvp_cc_boss(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_boss)
        if total_cc == 0:
            return
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        cc_ratio  = max_cc / total_cc * 100
        return self.msg("LVP BOSS CC", lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)
    
    def get_lvp_cc_total(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_total)
        if total_cc == 0:
            return
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        cc_ratio  = max_cc / total_cc * 100
        return self.msg("LVP TOTAL CC", lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)
    
    def get_lvp_dps(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_boss)
        if total_dmg == 0:
            return
        dmg_ratio                     = max_dmg / total_dmg * 100
        lvp_dps_name                  = self.players_to_string(i_players)
        dps                           = max_dmg / self.duration_ms
        foodSwapCount                 = self.get_foodswap_count(i_players[0])
        self.add_lvps(i_players) 
        if foodSwapCount:
            return self.msg("LVP DPS FOODSWAP", lvp_dps_name=lvp_dps_name, max_dmg=max_dmg, dmg_ratio=dmg_ratio, dps=dps, foodSwapCount=foodSwapCount)
        return self.msg("LVP DPS", lvp_dps_name=lvp_dps_name, max_dmg=max_dmg, dmg_ratio=dmg_ratio, dps=dps)
    ################################ BOSS DATA ################################
    
    def get_phase_timers(self, target_phase: str, inMilliSeconds=False):
        phases = self.log.pjcontent['phases']
        for phase in phases:
            if phase['name'] == target_phase:  
                start = phase['start']
                end   = phase['end']
                if inMilliSeconds:
                    return start, end
                return func.time_to_index(start, self.time_base), func.time_to_index(end, self.time_base)
        print(f'{target_phase} not found')
        return None, None
    
    def get_phase_bounds(self, phase_id: int):
        phase = self.log.pjcontent['phases'][phase_id]
        return phase['start'], phase['end']

    def get_dmg_phase_targets(self, i_player: int, phase_id: int):
        """Player's damage to each target involved in a phase.

        The HTML page indexed these columns by the phase's targets, the
        JSON API indexes them by the global target list: hence going
        through targets + secondaryTargets.
        """
        phase       = self.log.pjcontent['phases'][phase_id]
        indexes     = phase.get('targets', []) + phase.get('secondaryTargets', [])
        dps_targets = self.log.pjcontent['players'][i_player]['dpsTargets']
        return [dps_targets[i][phase_id]['damage'] for i in indexes]

    def get_dmg_phase(self, i_player: int, phase_id: int):
        """Player's damage to every target of a phase."""
        return self.log.pjcontent['players'][i_player]['dpsAll'][phase_id]['damage']

    def get_mech_value(self, i_player: int, mech_name: str, phase: str="Full Fight"):
        phase_id = self.get_phase_id(phase)
        for mechanic in self.mechanics:
            if mechanic['fullName'] == mech_name:
                start, end = self.get_phase_bounds(phase_id)
                icd = get_icd(self.log.pjcontent['triggerID'], mech_name)
                exclude = self.mechanic_exclusions(mech_name)
                return mech_value(mechanic, self.get_player_name(i_player), icd, start, end, exclude)
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
            if mech['fullName'] == name or mech['name'] == name:
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
    
    def getBuff(self, buffId: int):
        if not hasattr(self, "_buff_by_id"):
            self._buff_by_id = {
                int(id_[1:]): buff for id_, buff in self.log.pjcontent["buffMap"].items()
            }
        return self._buff_by_id.get(buffId)
    
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