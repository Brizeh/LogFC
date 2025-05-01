from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class DAGDA(Boss):
    """
    Dagda from Secrets of the Obscure.
    """

    last = None
    name = "DAGDA"
    boss_id = 25705
    wing = "SOTO"

    def __init__(self, log: Log):
        """
        Initializes a Dagda instance.

        Args:
            log (Log): Object containing the combat log data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        DAGDA.last = self

    def get_mvp(self):
        """
        Retrieves the message for the best performing player.
        First checks players with debilitations, then those with bad DPS.

        Returns:
            str: Message for the best performing player or None
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
        Retrieves the message for the player with the most damage.

        Returns:
            str: Message for the player with the most damage
        """
        return self.get_lvp_dps()

    def mvp_debil(self):
        """
        Determines the MVP based on the maximum number of debilitations applied.
        Excludes healer players.

        Returns:
            str: Formatted message for the debilitation MVP or None
        """
        i_players, max_debil, _ = Analyzer.get_max_value(self.player_list, self.get_max_debil, exclude=[self.is_heal])
        mvp_names = self.players_to_string(i_players)

        if max_debil > 1:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return language_config.selected_language["KO MVP DEBIL S"].format(
                    mvp_names=mvp_names, max_debil=max_debil
                )
            else:
                return language_config.selected_language["KO MVP DEBIL P"].format(
                    mvp_names=mvp_names, max_debil=max_debil
                )
        return None

    def get_max_debil(self, i_player: int):
        """
        Retrieves the maximum number of debilitations applied by a player.

        Args:
            i_player (int): Player index in the data

        Returns:
            int: Maximum number of debilitations applied
        """
        buff_uptimes = self.log.pjcontent["players"][i_player]["buffUptimes"]
        debil_id = 67972
        states = None

        for buff in buff_uptimes:
            if buff["id"] == debil_id:
                states = buff["states"]

        debil = 0
        if states:
            for state in states:
                if state[1] > debil:
                    debil = state[1]

        return debil