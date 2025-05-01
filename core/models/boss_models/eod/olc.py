from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class OLC(Boss):
    """
    Old Lion's Court (OLC) from End of Dragons.
    """

    last = None
    name = "OLC"
    boss_id = 25413
    wing = "EOD"

    def __init__(self, log):
        """
        Initializes an instance of OLC with a specific log.

        Args:
            log: The Log object containing combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        OLC.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the fight against Old Lion's Court.

        For Old Lion's Court, the MVP is based solely on players with significantly low DPS.

        Returns:
            str: Formatted message indicating the MVP and the reason, or None if no MVP
        """
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the fight against Old Lion's Court.

        Returns:
            str: Formatted message indicating the LVP and the reason, or None if no LVP
        """
        return self.get_lvp_dps()

    ################################ LVP ################################

    def get_lvp_dps(self):
        """
        Identifies LVPs based on their high DPS.

        This method is a specific implementation for Old Lion's Court.

        Returns:
            str: Formatted LVP message or None if no player has high DPS
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)
        lvp_dps_name = self.players_to_string(i_players)
        dmg_ratio = max_dmg / tot_dmg * 100
        dps = max_dmg / self.duration_ms
        self.add_lvps(i_players)

        return language_config.selected_language["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps)

    ################################ DATA MECHAS ################################

    def get_dmg_boss(self, i_player: int):
        """
        Retrieves the total damage dealt by a player to Old Lion's Court.

        Args:
            i_player (int): Index of the player

        Returns:
            int: Total damage dealt
        """
        return self.log.pjcontent["players"][i_player]["dpsAll"][0]["damage"]
