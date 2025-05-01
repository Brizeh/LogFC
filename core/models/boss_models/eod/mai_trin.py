from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class AH(Boss):
    """
    Mai Trin from End of Dragons.
    """

    last = None
    name = "MAI TRIN"
    boss_id = 24033
    wing = "EOD"

    def __init__(self, log):
        """
        Initializes an instance of AH with a specific log.

        Args:
            log: The Log object containing combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        AH.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the fight against Mai Trin.

        First checks players with a high level of exposure, then those
        with significantly low DPS.

        Returns:
            str: Formatted message indicating the MVP and the reason, or None if no MVP
        """
        msg_exposed = self.expose_mvp()
        if msg_exposed:
            return msg_exposed

        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the fight against Mai Trin.

        Returns:
            str: Formatted message indicating the LVP and the reason, or None if no LVP
        """
        return self.get_lvp_dps()

    ################################ MVP ################################

    def expose_mvp(self):
        """
        Identifies MVPs who suffered the most from the exposure effect.

        Returns:
            str: Formatted MVP message or None if no player was sufficiently exposed
        """
        i_players, max_exposed, _ = Analyzer.get_max_value(self.player_list, self.get_max_exposed,
                                                           exclude=[self.is_heal])
        mvp_names = self.players_to_string(i_players)

        if max_exposed > 2:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return language_config.selected_language["AH MVP EXPOSED S"].format(mvp_names=mvp_names, max_exposed=max_exposed)
            else:
                return language_config.selected_language["AH MVP EXPOSED P"].format(mvp_names=mvp_names, max_exposed=max_exposed)

        return None

    ################################ LVP ################################

    def get_lvp_dps(self):
        """
        Identifies LVPs based on their high DPS.

        This method is a specific implementation for Mai Trin.

        Returns:
            str: Formatted LVP message or None if no player has high DPS
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)
        ratio = max_dmg / tot_dmg * 100
        time = self.duration_ms
        dps = max_dmg / time
        lvp_dps_name = self.players_to_string(i_players)
        self.add_lvps(i_players)

        return language_config.selected_language["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dps=dps, dmg_ratio=ratio)

    ################################ DATA MECHAS ################################

    def get_max_exposed(self, i_player: int):
        """
        Retrieves the highest level of exposure suffered by a player.

        Args:
            i_player (int): Index of the player

        Returns:
            int: Highest level of exposure
        """
        buff_uptimes = self.log.pjcontent["players"][i_player]["buffUptimes"]
        expose_id = 64936
        expose_states = None

        for buff in buff_uptimes:
            if buff["id"] == expose_id:
                expose_states = buff["states"]

        exposed = 0
        if expose_states:
            for state in expose_states:
                if state[1] > exposed:
                    exposed = state[1]

        return exposed

    def get_dmg_boss(self, i_player: int):
        """
        Calculates the total damage dealt by a player to Mai Trin and Echo.

        Args:
            i_player (int): Index of the player

        Returns:
            int: Total damage dealt
        """
        target_dmg = self.log.pjcontent["players"][i_player]["dpsTargets"]
        mai_trin_dmg = target_dmg[0][0]["damage"]
        echo_dmg = target_dmg[1][0]["damage"]
        return mai_trin_dmg + echo_dmg
