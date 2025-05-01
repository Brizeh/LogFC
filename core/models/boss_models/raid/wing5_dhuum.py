from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class DHUUM(Boss):
    """
    Dhuum from the fifth raid wing.
    """

    last = None
    name = "DHUUM"
    wing = 5
    boss_id = 19450
    real_phase = "Dhuum Fight"

    def __init__(self, log):
        """
        Initializes a DHUUM instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        DHUUM.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Dhuum fight.

        First, check players with many cracks, then players
        with significantly low DPS (excluding green carriers).

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        msg_cracks = self.mvp_cracks()
        if msg_cracks:
            return msg_cracks

        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_green])
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the Dhuum fight.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.get_lvp_dps()

    def get_dps_ranking(self):
        """
        Calculates the DPS ranking of players for Dhuum excluding supports and green carriers.

        Returns:
            dict: Dictionary associating players with their DPS score
        """
        return self._get_dps_contrib([self.is_support, self.is_green])

    ################################ MVP ################################

    def mvp_cracks(self):
        """
        Identifies MVPs based on the high number of cracks handled.

        Returns:
            str: Formatted MVP message or None if no player handled many cracks
        """
        i_players, max_cracks, _ = Analyzer.get_max_value(self.player_list, self.get_cracks)
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)

        if len(i_players) == 1:
            return language_config.selected_language["DHUUM MVP CRACKS S"].format(mvp_names=mvp_names, max_cracks=max_cracks)
        if len(i_players) > 1:
            return language_config.selected_language["DHUUM MVP CRACKS P"].format(mvp_names=mvp_names, max_cracks=max_cracks)

        return None

    ################################ CONDITIONS ################################

    def is_green(self, i_player: int) -> bool:
        """
        Checks if a player performed a green port during the main phase.

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player performed a green port, False otherwise
        """
        return self.get_mech_value(i_player, "Green port", "Dhuum Fight") > 0

    ################################ DATA MECHAS ################################

    def get_cracks(self, i_player: int):
        """
        Retrieves the number of cracks handled by a player.

        Args:
            i_player (int): Player index

        Returns:
            int: Number of cracks handled
        """
        return self.get_mech_value(i_player, "Cracks")