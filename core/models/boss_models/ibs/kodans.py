from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class KODANS(Boss):
    """
    Kodans from the Icebrood Saga.
    """

    last = None
    name = "KODANS"
    boss_id = 22343
    wing = "IBS"

    def __init__(self, log: Log):
        """
        Initializes an instance of Kodans.

        Args:
            log (Log): Object containing the combat log data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        KODANS.last = self

    def get_mvp(self):
        """
        Retrieves the message for the most effective player.

        Returns:
            str: Message for the most effective player or None
        """
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return None

    def get_lvp(self):
        """
        Retrieves the message for the player with the most damage.

        Returns:
            str: Message for the player with the most damage
        """
        return self.get_lvp_dps()

    def get_lvp_dps(self):
        """
        Calculates and formats the message for the player with the most damage.
        Takes into account the combined damage to both targets.

        Returns:
            str: Formatted message for the player with the most damage
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)
        lvp_dps_name = self.players_to_string(i_players)
        dps = max_dmg / self.duration_ms
        dmg_ratio = max_dmg / tot_dmg * 100
        self.add_lvps(i_players)
        return language_config.selected_language["LVP DPS"].format(
            lvp_dps_name=lvp_dps_name, dps=dps, dmg_ratio=dmg_ratio
        )

    def get_dmg_boss(self, i_player: int):
        """
        Calculates the total damage inflicted by a player to both boss targets.

        Args:
            i_player (int): Player index in the data

        Returns:
            int: Sum of damage inflicted to both targets
        """
        boss1_dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][0][self.real_phase_id]['damage']
        boss2_dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][1][self.real_phase_id]['damage']
        return boss1_dmg + boss2_dmg
