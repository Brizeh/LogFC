from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class SLOTH(Boss):
    """
    Slothasor
    """

    last = None  # Reference to the last SLOTH instance
    name = "SLOTH"
    wing = 2
    boss_id = 16123

    def __init__(self, log):
        """
        Initializes a SLOTH instance with a specific log.

        Args:
            log: The Log object containing combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SLOTH.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the fight against Slothasor.

        Checks multiple conditions in order:
        1. Player with the most tantrums handled
        2. Player with the fewest CCs applied
        3. Player with significantly low DPS

        Returns:
            str: Formatted message indicating the MVP and the reason, or None if no MVP
        """
        msg_tantrum = self.mvp_tantrum()
        if msg_tantrum:
            return msg_tantrum

        msg_cc = self.mvp_cc_sloth()
        if msg_cc:
            return msg_cc

        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_shroom])
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the fight against Slothasor.

        Returns:
            str: Formatted message indicating the LVP and the reason, or None if no LVP
        """
        return self.get_lvp_cc_boss()

    def get_dps_ranking(self):
        """
        Computes the DPS ranking of players for Slothasor, excluding supports and mushroom carriers.

        Returns:
            dict: Dictionary mapping players to their DPS score
        """
        return self._get_dps_contrib([self.is_support, self.is_shroom])

    ################################ MVP ################################

    def mvp_cc_sloth(self):
        """
        Identifies MVPs based on the low number of CCs applied on Slothasor.

        Returns:
            str: Formatted MVP message or None if no player meets the criteria
        """
        i_players, min_cc, total_cc = Analyzer.get_min_value(self.player_list, self.get_cc_boss,
                                                             exclude=[self.is_shroom])
        if min_cc < 800:
            self.add_mvps(i_players)
            cc_ratio = min_cc / total_cc * 100
            mvp_names = self.players_to_string(i_players)
            if min_cc == 0:
                if len(i_players) > 1:
                    return language_config.selected_language["SLOTH MVP 0 CC P"].format(mvp_names=mvp_names)
                return language_config.selected_language["SLOTH MVP 0 CC S"].format(mvp_names=mvp_names)
            if len(i_players) > 1:
                return language_config.selected_language["SLOTH MVP CC P"].format(mvp_names=mvp_names, min_cc=min_cc,
                                                                                  cc_ratio=cc_ratio)
            return language_config.selected_language["SLOTH MVP CC S"].format(mvp_names=mvp_names, min_cc=min_cc,
                                                                              cc_ratio=cc_ratio)
        return None

    def mvp_tantrum(self):
        """
        Identifies MVPs based on the highest number of tantrums handled.

        Returns:
            str: Formatted MVP message or None if no player meets the criteria
        """
        i_players, max_tantrum, _ = Analyzer.get_max_value(self.player_list, self.get_tantrum)
        if max_tantrum > 1:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) > 1:
                return language_config.selected_language["SLOTH MVP TANTRUM P"].format(mvp_names=mvp_names,
                                                                                       max_tantrum=max_tantrum)
            return language_config.selected_language["SLOTH MVP TANTRUM S"].format(mvp_names=mvp_names,
                                                                                   max_tantrum=max_tantrum)
        return None

    ################################ CONDITIONS ###############################

    def is_shroom(self, i_player: int):
        """
        Checks whether a player carried the mushroom during the fight.

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player carried the mushroom, False otherwise
        """
        rota = self.get_player_rotation(i_player)
        for skill in rota:
            if skill['id'] == 34408:
                return True
        return False

    ################################ DATA MECHAS ################################

    def get_tantrum(self, i_player: int):
        """
        Retrieves the number of tantrums handled by a player.

        Args:
            i_player (int): Index of the player

        Returns:
            int: Number of tantrums handled
        """
        return self.get_mech_value(i_player, "Tantrum")
