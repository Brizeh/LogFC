from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class ADINA(Boss):
    """
    Cardinal Adina
    """

    last = None
    name = "ADINA"
    wing = 7
    boss_id = 22006

    def __init__(self, log):
        """
        Initializes an ADINA instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        ADINA.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Adina fight.

        First checks players with low DPS, then those who dealt
        the least damage during split phases.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return self.mvp_dmg_split()

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the Adina fight.

        Identifies players who dealt the most damage during split phases.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.lvp_dmg_split()

    ################################ MVP ################################

    def mvp_dmg_split(self):
        """
        Identifies MVPs who dealt the least damage during split phases.

        Returns:
            str: Formatted MVP message
        """
        i_players, min_dmg, total_dmg = Analyzer.get_min_value(self.player_list, self.get_dmg_split,
                                                               exclude=[self.is_support])
        mvp_names = self.players_to_string(i_players)
        dmg_ratio = min_dmg / total_dmg * 100
        self.add_mvps(i_players)
        return language_config.selected_language["ADINA MVP SPLIT"].format(mvp_names=mvp_names, dmg_ratio=dmg_ratio)

    ################################ LVP ################################

    def lvp_dmg_split(self):
        """
        Identifies LVPs who dealt the most damage during split phases.

        Returns:
            str: Formatted LVP message
        """
        i_players, max_dmg, total_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_split)
        lvp_names = self.players_to_string(i_players)
        dmg_ratio = max_dmg / total_dmg * 100
        self.add_lvps(i_players)
        return language_config.selected_language["ADINA LVP SPLIT"].format(lvp_names=lvp_names, dmg_ratio=dmg_ratio)

    ################################ DATA MECHAS ################################

    def get_dmg_split(self, i_player: int):
        """
        Calculates the total damage dealt by a player during split phases.

        Args:
            i_player (int): Player index

        Returns:
            int: Total damage dealt during split phases
        """
        dmg_split1 = self.log.jcontent['phases'][2]['dpsStats'][i_player][0]
        dmg_split2 = self.log.jcontent['phases'][4]['dpsStats'][i_player][0]
        dmg_split3 = self.log.jcontent['phases'][6]['dpsStats'][i_player][0]
        return dmg_split1 + dmg_split2 + dmg_split3