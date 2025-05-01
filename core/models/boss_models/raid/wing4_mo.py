from core.models.boss import Boss
from i18n.languages import language_config


class MO(Boss):
    """
    Mursaat Overseer (MO)
    """

    last = None
    name = "MO"
    wing = 4
    boss_id = 17172

    def __init__(self, log):
        """
        Initializes a MO instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        MO.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Mursaat Overseer fight.

        First checks players hit by spikes, then players with low DPS.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        msg_pic = self.mvp_pic()
        if msg_pic:
            return msg_pic

        return self.get_bad_dps()

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the Mursaat Overseer fight.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.get_lvp_dps()

        ################################ MVP ################################

    def mvp_pic(self):
        """
        Identifies MVPs who were hit by spikes.

        Returns:
            str: Formatted MVP message or None if no player was hit by spikes
        """
        i_players = self.get_piced()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)

        if len(i_players) == 1:
            return language_config.selected_language["MO MVP PICS S"].format(mvp_names=mvp_names)
        if len(i_players) > 1:
            return language_config.selected_language["MO MVP PICS P"].format(mvp_names=mvp_names)

        return None

    ################################ DATA MECHAS ################################

    def get_piced(self):
        """
        Retrieves the list of players killed instantly (probably by spikes).

        Returns:
            list: List of indices of players killed by spikes
        """
        piced = []
        for i in self.player_list:
            if self.is_dead_instant(i):
                piced.append(i)
        return piced