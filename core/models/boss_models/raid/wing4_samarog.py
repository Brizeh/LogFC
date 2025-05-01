import numpy as np

from core.models.boss import Boss
from i18n.languages import language_config


class SAMAROG(Boss):
    """
    Samarog
    """

    last = None
    name = "SAMAROG"
    wing = 4
    boss_id = 17188

    # Arena corner coordinates
    top_left_corn = [278.0, 645.2]
    top_right_corn = [667.6, 660.7]
    bot_left_corn = [299.4, 58.6]
    bot_right_corn = [690.7, 73.6]
    scaler = 5.4621

    def __init__(self, log):
        """
        Initializes a SAMAROG instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SAMAROG.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Samarog fight.

        First checks impaled players, then traitors, and finally players
        with low CC (excluding fixated players).

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        msg_impaled = self.mvp_impaled()
        if msg_impaled:
            return msg_impaled

        msg_bisou = self.mvp_traitors()
        if msg_bisou:
            return msg_bisou

        return self.get_mvp_cc_boss(extra_exclude=[self.is_fix])

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the Samarog fight.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.get_lvp_cc_boss()

    ################################ MVP ################################

    def mvp_impaled(self):
        """
        Identifies MVPs who were impaled.

        Returns:
            str: Formatted MVP message or None if no player was impaled
        """
        i_players = self.get_impaled()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)

        if len(i_players) == 1:
            return language_config.selected_language["SAMAROG MVP IMPALED S"].format(mvp_names=mvp_names)
        if len(i_players) > 1:
            return language_config.selected_language["SAMAROG MVP IMPALED P"].format(mvp_names=mvp_names)

        return None

    def mvp_traitors(self):
        """
        Identifies MVPs who betrayed other players (with greens).

        Returns:
            str: Formatted MVP message or None if no betrayal occurred
        """
        i_trait, i_vict = self.get_traitors()
        trait_names = self.players_to_string(i_trait)
        vict_names = self.players_to_string(i_vict)
        self.add_mvps(i_trait)

        if len(i_trait) == 1:
            return language_config.selected_language["SAMAROG MVP BISOU S"].format(trait_names=trait_names, vict_names=vict_names)
        if len(i_trait) > 1:
            return language_config.selected_language["SAMAROG MVP BISOU P"].format(trait_names=trait_names, vict_names=vict_names)

        return None

    ################################ CONDITIONS ################################

    def got_impaled(self, i_player: int):
        """
        Checks if a player was impaled.

        A player is considered impaled if they died instantly after
        being hit by Sweep or Shock Wave.

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player was impaled, False otherwise
        """
        if self.is_dead_instant(i_player):
            mech_history = self.get_player_mech_history(i_player)
            for mech in mech_history:
                if mech['name'] == "DC":
                    mech_history.remove(mech)
            if len(mech_history) > 1:
                if (mech_history[-2]['name'] == "Swp" or mech_history[-2]['name'] == "Schk.Wv") and mech_history[-1][
                    'name'] == "Dead":
                    return True
        return False

    def is_fix(self, i_player: int):
        """
        Checks if a player was fixated by Samarog at least 3 times.

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player was fixated at least 3 times, False otherwise
        """
        return self.get_mech_value(i_player, "Fixate: Samarog") >= 3

    ################################ DATA MECHAS ################################

    def get_impaled(self):
        """
        Retrieves the list of players who were impaled.

        Returns:
            list: List of indices of impaled players
        """
        i_players = []
        for i in self.player_list:
            if self.got_impaled(i):
                i_players.append(i)
        return i_players

    def get_traitors(self):
        """
        Identifies players who betrayed other players with green mechanics.

        Returns:
            tuple: Tuple containing (traitors, victims)
        """
        traitors, victims = [], []
        big_greens = self.get_mechanic_history("Big Green")
        small_greens = self.get_mechanic_history("Small Green")
        failed_greens = self.get_mechanic_history("Failed Green")
        last_fail_time = None

        if failed_greens:
            for fail_green in failed_greens:
                if fail_green['time'] == last_fail_time:
                    continue
                last_fail_time = fail_green['time']
                fail_actor = fail_green['actor']
                fail_time = fail_green['time']

                for small, big in zip(small_greens, big_greens):
                    small_actor = small['actor']
                    big_actor = big['actor']
                    green_time = small['time']

                    if fail_actor in [big_actor, small_actor] and np.abs(fail_time - green_time) < 7000:
                        victims.append(self.get_player_id(big_actor))
                        traitors.append(self.get_player_id(small_actor))

        return traitors, victims