from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class CAIRN(Boss):
    """
    Cairn
    """

    last = None
    name = "CAIRN"
    wing = 4
    boss_id = 17194

    def __init__(self, log):
        """
        Initializes a CAIRN instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        CAIRN.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Cairn fight.

        First checks players with the most teleports, then players
        with significantly low DPS.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        msg_tp = self.mvp_tp()
        if msg_tp:
            return msg_tp

        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the Cairn fight.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.get_lvp_dps()

    ################################ MVP ################################

    def mvp_tp(self):
        """
        Identifies MVPs based on high number of teleports.

        Returns:
            str: Formatted MVP message or None if no player meets the criteria
        """
        i_players, max_tp, _ = Analyzer.get_max_value(self.player_list, self.get_tp)
        mvp_names = self.players_to_string(i_players)

        if max_tp > 2:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return language_config.selected_language["CAIRN MVP TP S"].format(mvp_names=mvp_names, max_tp=max_tp)
            if len(i_players) > 1:
                return language_config.selected_language["CAIRN MVP TP P"].format(mvp_names=mvp_names, max_tp=max_tp)

        return None

    ################################ DATA MECHAS ################################

    def get_tp(self, i_player: int):
        """
        Retrieves the number of orange teleports for a player.

        Args:
            i_player (int): Player index

        Returns:
            int: Number of orange teleports
        """
        return self.get_mech_value(i_player, 'Orange TP')