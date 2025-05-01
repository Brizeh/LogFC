from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class FRAENIR(Boss):
    """
    Fraenir from the Icebrood Saga.
    """

    last = None
    name = "FRAENIR"
    boss_id = 22492
    wing = "IBS"

    def __init__(self, log: Log):
        """
        Initializes a Fraenir instance.

        Args:
            log (Log): Object containing combat log data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        FRAENIR.last = self

    def get_mvp(self):
        """
        Retrieves the message for the most valuable player.
        Checks frozen players first, then players with poor DPS.

        Returns:
            str: Message for the top-performing player, or None
        """
        msg_frozen = self.get_frozen_mvp()
        if msg_frozen:
            return msg_frozen
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return None

    def get_lvp(self):
        """
        Retrieves the message for the least valuable player.
        First checks players with SAK stats, then falls back to standard DPS.

        Returns:
            str: Message for the least effective player
        """
        msg_sak = self.get_lvp_sak()
        if msg_sak:
            return msg_sak
        return self.get_lvp_dps()

    def get_frozen_mvp(self):
        """
        Determines the MVP based on how many times a player was frozen.

        Returns:
            str: Formatted MVP message based on freeze count, or None
        """
        i_players, max_frozen, _ = Analyzer.get_max_value(self.player_list, self.get_frozen)
        if max_frozen > 1:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) > 1:
                return language_config.selected_language["FRAENIR MVP FROZEN P"].format(
                    mvp_names=mvp_names, max_frozen=max_frozen
                )
            return language_config.selected_language["FRAENIR MVP FROZEN S"].format(
                mvp_names=mvp_names, max_frozen=max_frozen
            )
        return None

    def get_lvp_sak(self):
        """
        Calculates the LVP based on SAK (Shatter Assault Kill) statistics.

        Returns:
            str: Formatted LVP message based on SAK stats, or None
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)
        sak_dmg = self.get_sak_dmg(i_players[0])
        sak_count = self.get_sak_count(i_players[0])
        lvp_dps_name = self.players_to_string(i_players)
        dps = max_dmg / self.duration_ms
        dmg_ratio = max_dmg / tot_dmg * 100
        self.add_lvps(i_players)

        if sak_count:
            sak_ratio = sak_dmg / max_dmg * 100
            return language_config.selected_language["FRAENIR LVP SAK"].format(
                lvp_dps_name=lvp_dps_name,
                sak_count=sak_count,
                sak_ratio=sak_ratio,
                dps=dps,
                dmg_ratio=dmg_ratio
            )
        return None

    def get_dmg_boss(self, i_player: int):
        """
        Calculates the total damage dealt by a player to the boss's two targets.

        Args:
            i_player (int): Index of the player in the data

        Returns:
            int: Total damage dealt to both targets
        """
        boss1_dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][0][self.real_phase_id]['damage']
        boss2_dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][1][self.real_phase_id]['damage']
        return boss1_dmg + boss2_dmg

    def get_frozen(self, i_player: int):
        """
        Retrieves how many times a player was frozen.

        Args:
            i_player (int): Index of the player in the data

        Returns:
            int: Number of times the player was frozen
        """
        return self.get_mech_value(i_player, "Frozen")

    def get_sak_dmg(self, i_player: int):
        """
        Retrieves the damage dealt by the Shatter Assault Kill attack.

        Args:
            i_player (int): Index of the player in the data

        Returns:
            int: Total damage dealt using SAK
        """
        totalDamageDist = self.log.pjcontent["players"][i_player]["totalDamageDist"][0]
        for dmgSource in totalDamageDist:
            if dmgSource["id"] == 60448:
                return dmgSource["totalDamage"]
        return 0

    def get_sak_count(self, i_player: int):
        """
        Retrieves how many times the Shatter Assault Kill attack was used.

        Args:
            i_player (int): Index of the player in the data

        Returns:
            int: Number of SAK usages
        """
        rota = self.get_player_rotation(i_player)
        for spell in rota:
            if spell["id"] == 60448:
                return len(spell["skills"])
        return 0
