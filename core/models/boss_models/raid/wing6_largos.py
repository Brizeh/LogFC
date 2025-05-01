from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class LARGOS(Boss):
    """
    Twin Largos from the sixth raid wing.
    """

    last = None
    name = "LARGOS"
    wing = 6
    boss_id = 21105

    def __init__(self, log):
        """
        Initializes a LARGOS instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        LARGOS.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Twin Largos fight.

        First checks players who suffered the most attack dashes.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        msg_dash = self.mvp_dash()
        if msg_dash:
            return msg_dash

        return None

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the Twin Largos fight.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.get_lvp_cc_total()

    ################################ MVP ################################

    def mvp_dash(self):
        """
        Identifies MVPs based on the high number of attack dashes suffered.

        Returns:
            str: Formatted MVP message, low DPS message, or None
        """
        i_players, max_dash, _ = Analyzer.get_max_value(self.player_list, self.get_dash,
                                                        exclude=[self.is_heal, self.is_tank])
        mvp_names = self.players_to_string(i_players)

        if max_dash < 7:
            return self.get_bad_dps()
        else:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return language_config.selected_language["LARGOS MVP DASH S"].format(mvp_names=mvp_names, max_dash=max_dash)
            if len(i_players) > 1:
                return language_config.selected_language["LARGOS MVP DASH P"].format(mvp_names=mvp_names, max_dash=max_dash)

        return None

    def get_bad_dps(self, extra_exclude=None):
        """
        Identifies DPS players whose damage is lower than that of a support.

        This method is a specific override for LARGOS.

        Args:
            extra_exclude (list, optional): Additional list of filter functions.

        Returns:
            str: Formatted message or None if no player has low DPS
        """
        if extra_exclude is None:
            extra_exclude = []

        i_sup, sup_max_dmg, _ = Analyzer.get_max_value(self.player_list, self.get_dmg_boss, exclude=[self.is_dps])
        sup_name = self.players_to_string(i_sup)
        bad_dps = []

        for i in self.player_list:
            if any(filter_func(i) for filter_func in extra_exclude) or self.is_dead(i) or self.is_support(i):
                continue
            dps = self.get_dmg_boss(i)
            if dps < sup_max_dmg:
                if not (self.name == "QUOIDIMM" and self.get_player_spe(i) == "Spellbreaker"):
                    bad_dps.append(i)

        if bad_dps:
            self.add_mvps(bad_dps)
            bad_dps_name = self.players_to_string(bad_dps)
            if len(bad_dps) == 1:
                return language_config.selected_language["MVP BAD DPS S"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)
            else:
                return language_config.selected_language["MVP BAD DPS P"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)

        return None

    ################################ LVP ################################

    ################################ CONDITIONS ################################

    ################################ DATA MECHAS ################################

    def get_dash(self, i_player: int):
        """
        Retrieves the number of attack dashes suffered by a player.

        Args:
            i_player (int): Player index

        Returns:
            int: Number of attack dashes suffered
        """
        return self.get_mech_value(i_player, "Vapor Rush Charge")

    def get_dmg_boss(self, i_player: int):
        """
        Calculates the total damage dealt by a player against both Largos.

        Args:
            i_player (int): Player index

        Returns:
            int: Total damage dealt
        """
        dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][0][self.real_phase_id]['damage']
        dmg += self.log.pjcontent['players'][i_player]['dpsTargets'][1][self.real_phase_id]['damage']
        return dmg