from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class MATTHIAS(Boss):
    """
    Matthias
    """

    last = None  # Reference to the last MATTHIAS instance
    name = "MATTHIAS"
    wing = 2
    boss_id = 16115

    def __init__(self, log):
        """
        Initializes a MATTHIAS instance with a specific log.

        Args:
            log: The Log object containing combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        MATTHIAS.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the fight against Matthias.

        Identifies players who applied the fewest CCs on Matthias.

        Returns:
            str: Formatted message indicating the MVP and the reason, or None if no MVP
        """
        return self.mvp_cc_matthias()

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the fight against Matthias.

        Identifies players who applied the most CCs on Matthias.

        Returns:
            str: Formatted message indicating the LVP and the reason, or None if no LVP
        """
        return self.lvp_cc_matthias()

    def get_dps_ranking(self):
        """
        Computes the DPS ranking of players for Matthias, excluding supports and sacrificed players.

        Returns:
            dict: Dictionary mapping players to their DPS score
        """
        return self._get_dps_contrib([self.is_support, self.is_sac])  # Exclude support and sacrificed players

    ################################ MVP ################################

    def mvp_cc_matthias(self):
        """
        Identifies MVPs based on the low number of CCs applied on Matthias.

        Returns:
            str: Formatted MVP message
        """
        i_players, min_cc, total_cc = Analyzer.get_min_value(
            self.player_list, self.get_cc_total, exclude=[self.is_sac]
        )
        cc_ratio = min_cc / total_cc * 100  # Percentage of total CCs
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)

        if min_cc == 0:
            return language_config.selected_language["MATTHIAS MVP 0 CC"].format(mvp_names=mvp_names)
        else:
            return language_config.selected_language["MATTHIAS MVP CC"].format(
                mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio
            )

    ################################ LVP ################################

    def lvp_cc_matthias(self):
        """
        Identifies LVPs based on the high number of CCs applied on Matthias.

        Returns:
            str: Formatted LVP message
        """
        i_players, max_cc, total_cc = Analyzer.get_max_value(self.player_list, self.get_cc_total)
        cc_ratio = max_cc / total_cc * 100  # Percentage of total CCs
        lvp_names = self.players_to_string(i_players)
        self.add_lvps(i_players)

        return language_config.selected_language["MATTHIAS LVP CC"].format(
            lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio
        )

    ################################ CONDITIONS ###############################

    def is_sac(self, i_player: int):
        """
        Checks whether a player was sacrificed during the fight.

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player was sacrificed, False otherwise
        """
        return self.get_nb_sac(i_player) > 0

    ################################ DATA MECHAS ################################

    def get_nb_sac(self, i_player: int):
        """
        Retrieves the number of times a player was sacrificed.

        Args:
            i_player (int): Index of the player

        Returns:
            int: Number of sacrifices
        """
        return self.get_mech_value(i_player, "Sacrifice")
