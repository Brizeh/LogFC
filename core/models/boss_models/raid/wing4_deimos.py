from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class DEIMOS(Boss):
    """
    Deimos
    """

    last = None
    name = "DEIMOS"
    wing = 4
    boss_id = 17154
    real_phase = "100% - 10%"

    def __init__(self, log):
        """
        Initializes a DEIMOS instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        DEIMOS.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Deimos fight.

        First checks players with the most triggered black oils,
        then players hit by pizzas.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        msg_black = self.mvp_black()
        if msg_black:
            return msg_black

        msg_pizza = self.mvp_pizza()
        if msg_pizza:
            return msg_pizza

        return None

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the Deimos fight.

        First checks players with many tears, then players with high DPS.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        msg_tears = self.lvp_tears()
        if msg_tears:
            return msg_tears

        return self.get_lvp_dps()

    def get_dps_ranking(self):
        """
        Calculates the DPS ranking of players for Deimos excluding supports and sacrificed players.

        Returns:
            dict: Dictionary associating players with their DPS score
        """
        return self._get_dps_contrib([self.is_support, self.is_sac])

    ################################ MVP ################################

    def mvp_black(self):
        """
        Identifies MVPs based on black oil triggering.

        Returns:
            str: Formatted MVP message or None if no player triggered many oils
        """
        i_players, max_black, _ = Analyzer.get_max_value(self.player_list, self.get_black_trigger)
        mvp_names = self.players_to_string(i_players)
        nb_players = len(i_players)
        self.add_mvps(i_players)

        if nb_players == 1:
            return language_config.selected_language["DEIMOS MVP BLACK S"].format(mvp_names=mvp_names, max_black=max_black)
        if nb_players > 1:
            return language_config.selected_language["DEIMOS MVP BLACK P"].format(mvp_names=mvp_names, nb_players=nb_players,
                                                          max_black=max_black)

        return None

    def mvp_pizza(self):
        """
        Identifies MVPs who were hit by pizzas.

        Returns:
            str: Formatted MVP message or None if no player was hit by pizzas
        """
        i_players = self.get_pizzaed()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)

        if i_players:
            return language_config.selected_language["DEIMOS MVP PIZZA"].format(mvp_names=mvp_names)

        return None

    ################################ LVP ################################

    def lvp_tears(self):
        """
        Identifies LVPs based on high number of tears received.

        Returns:
            str: Formatted LVP message or None if no player received many tears
        """
        i_players, max_tears, _ = Analyzer.get_max_value(self.player_list, self.get_tears)
        lvp_names = self.players_to_string(i_players)

        if i_players and max_tears > 2:
            self.add_lvps(i_players)
            return language_config.selected_language["DEIMOS LVP TEARS"].format(lvp_names=lvp_names, max_tears=max_tears)

        return None

    ################################ CONDITIONS ################################

    def got_pizzaed(self, i_player: int):
        """
        Checks if a player died due to a pizza.

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player died due to a pizza, False otherwise
        """
        if self.is_dead_instant(i_player):
            mech_history = self.get_player_mech_history(i_player)
            for mech in mech_history:
                if mech['name'] == "DC":
                    mech_history.remove(mech)
            if mech_history[-2]['name'] == "Pizza" and mech_history[-1]['name'] == "Dead":
                return True
        return False

    def is_sac(self, i_player: int):
        """
        Checks if a player was sacrificed (chosen green).

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player was sacrificed, False otherwise
        """
        greens = self.get_mechanic_history('Chosen (Green)')
        if not greens:
            return False
        return greens[-1]['actor'] == self.get_player_name(i_player)

    ################################ DATA MECHAS ################################

    def get_black_trigger(self, i_player: int):
        """
        Retrieves the number of black oils triggered by a player.

        Args:
            i_player (int): Player index

        Returns:
            int: Number of black oils triggered
        """
        return self.get_mech_value(i_player, "Black Oil Trigger")

    def get_tears(self, i_player: int):
        """
        Retrieves the number of tears received by a player.

        Args:
            i_player (int): Player index

        Returns:
            int: Number of tears received
        """
        return self.get_mech_value(i_player, "Tear")

    def get_pizzaed(self):
        """
        Retrieves the list of players killed by pizzas.

        Returns:
            list: List of indices of players killed by pizzas
        """
        pizzaed = []
        for i in self.player_list:
            if self.got_pizzaed(i):
                pizzaed.append(i)
        return pizzaed