from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class KO(Boss):
    """
    Minister Li (KO) from End of Dragons.
    """

    last = None
    name = "KO"
    boss_id = 24485
    wing = "EOD"

    def __init__(self, log):
        """
        Initializes an instance of KO with a specific log.

        Args:
            log: The Log object containing combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        KO.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the fight against Minister Li.

        First checks players with a high amount of debilitating effects,
        then those with significantly low DPS.

        Returns:
            str: Formatted message indicating the MVP and the reason, or None if no MVP
        """
        msg_debil = self.mvp_debil()
        if msg_debil:
            return msg_debil

        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the fight against Minister Li.

        Returns:
            str: Formatted message indicating the LVP and the reason, or None if no LVP
        """
        return self.get_lvp_dps()

    ################################ LVP ################################

    def get_lvp_dps(self):
        """
        Identifies LVPs based on their high DPS.

        This method is a specific implementation for Minister Li.

        Returns:
            str: Formatted LVP message or None if no player has high DPS
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)
        lvp_dps_name = self.players_to_string(i_players)
        dmg_ratio = max_dmg / tot_dmg * 100
        dps = max_dmg / self.duration_ms
        self.add_lvps(i_players)

        return language_config.selected_language["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps)

    ################################ MVP ################################

    def mvp_debil(self):
        """
        Identifies MVPs who suffered the most debilitating effects.

        Returns:
            str: Formatted MVP message or None if no player had many debilitating effects
        """
        i_players, max_debil, _ = Analyzer.get_max_value(self.player_list, self.get_max_debil, exclude=[self.is_heal])
        mvp_names = self.players_to_string(i_players)

        if max_debil > 1:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return language_config.selected_language["KO MVP DEBIL S"].format(mvp_names=mvp_names, max_debil=max_debil)
            else:
                return language_config.selected_language["KO MVP DEBIL P"].format(mvp_names=mvp_names, max_debil=max_debil)

        return None

    ################################ DATA MECHAS ################################

    def get_max_debil(self, i_player: int):
        """
        Retrieves the highest level of debilitation suffered by a player.

        Args:
            i_player (int): Index of the player

        Returns:
            int: Highest level of debilitation
        """
        buffUptimes = self.log.pjcontent["players"][i_player]["buffUptimes"]
        debil_id = 67972
        states = None

        for buff in buffUptimes:
            if buff["id"] == debil_id:
                states = buff["states"]

        debil = 0
        if states:
            for state in states:
                if state[1] > debil:
                    debil = state[1]

        return debil

    def get_dmg_boss(self, i_player: int):
        """
        Retrieves the total damage dealt by a player to Minister Li.

        Args:
            i_player (int): Index of the player

        Returns:
            int: Total damage dealt
        """
        return self.log.pjcontent["players"][i_player]["dpsAll"][0]["damage"]
