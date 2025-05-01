from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class KC(Boss):
    """
    Keep Construct (KC)
    """

    last = None
    name = "KC"
    wing = 3
    boss_id = 16235

    def __init__(self, log):
        """
        Initializes a KC instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        KC.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Keep Construct fight.

        First checks players with few orbs handled, then players with low DPS.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        msg_orb = self.mvp_orb_kc()
        if msg_orb:
            return msg_orb

        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the Keep Construct fight.

        Identifies players with the highest number of orbs handled.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.lvp_orb_kc()

    ################################ MVP ################################

    def mvp_orb_kc(self):
        """
        Identifies MVPs based on low orb handling.

        Returns:
            str: Formatted MVP message or None if no player meets the criteria
        """
        i_players, min_orb, _ = Analyzer.get_min_value(self.player_list, self.get_good_orb)
        mvp_names = self.players_to_string(i_players)

        if min_orb < 7:
            self.add_mvps(i_players)
            if min_orb < 0:
                return language_config.selected_language["KC MVP BAD ORBS"].format(mvp_names=mvp_names, min_orb=-min_orb)
            if min_orb == 0:
                return language_config.selected_language["KC MVP 0 ORB"].format(mvp_names=mvp_names)
            else:
                return language_config.selected_language["KC MVP ORB"].format(mvp_names=mvp_names, min_orb=min_orb)

        return None

    ################################ LVP ################################

    def lvp_orb_kc(self):
        """
        Identifies LVPs based on high orb handling.

        Returns:
            str: Formatted LVP message
        """
        i_players, max_orb, _ = Analyzer.get_max_value(self.player_list, self.get_good_orb)
        lvp_names = self.players_to_string(i_players)
        self.add_lvps(i_players)
        return language_config.selected_language["KC LVP ORB"].format(lvp_names=lvp_names, max_orb=max_orb)

    ################################ DATA MECHAS ################################

    def get_good_orb(self, i_player: int):
        """
        Calculates the orb score for a given player, taking into account well-handled orbs
        and poorly handled orbs.

        Args:
            i_player (int): Player index

        Returns:
            int: Orb score (positive for good handling, negative for poor handling)
        """
        good_red_orbs = self.get_mech_value(i_player, 'Good Red Orb')
        good_white_orbs = self.get_mech_value(i_player, 'Good White Orb')
        bad_red_orbs = self.get_mech_value(i_player, 'Bad Red Orb')
        bad_white_orbs = self.get_mech_value(i_player, 'Bad White Orb')
        return good_red_orbs + good_white_orbs - bad_red_orbs - bad_white_orbs