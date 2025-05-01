from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class DEIMOS(Boss):
    """
    Deimos de la quatrième aile de raid.
    """

    last = None
    name = "DEIMOS"
    wing = 4
    boss_id = 17154
    real_phase = "100% - 10%"

    def __init__(self, log):
        """
        Initialise une instance de DEIMOS avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        DEIMOS.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Deimos.

        Vérifie d'abord les joueurs avec le plus d'huiles noires déclenchées,
        puis les joueurs touchés par des pizzas.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
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
        Détermine le LVP (Least Valuable Player) pour le combat contre Deimos.

        Vérifie d'abord les joueurs avec beaucoup de larmes, puis les joueurs avec un DPS élevé.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        msg_tears = self.lvp_tears()
        if msg_tears:
            return msg_tears

        return self.get_lvp_dps()

    def get_dps_ranking(self):
        """
        Calcule le classement DPS des joueurs pour Deimos en excluant les supports et sacrifiés.

        Returns:
            dict: Dictionnaire associant les joueurs à leur score DPS
        """
        return self._get_dps_contrib([self.is_support, self.is_sac])

    ################################ MVP ################################

    def mvp_black(self):
        """
        Identifie les MVP basés sur le déclenchement d'huiles noires.

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'a déclenché beaucoup d'huiles
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
        Identifie les MVP qui ont été touchés par des pizzas.

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'a été touché par des pizzas
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
        Identifie les LVP basés sur le nombre élevé de larmes reçues.

        Returns:
            str: Message LVP formaté ou None si aucun joueur n'a reçu beaucoup de larmes
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
        Vérifie si un joueur est mort à cause d'une pizza.

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur est mort à cause d'une pizza, False sinon
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
        Vérifie si un joueur a été sacrifié (vert choisi).

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur a été sacrifié, False sinon
        """
        greens = self.get_mechanic_history('Chosen (Green)')
        if not greens:
            return False
        return greens[-1]['actor'] == self.get_player_name(i_player)

    ################################ DATA MECHAS ################################

    def get_black_trigger(self, i_player: int):
        """
        Récupère le nombre d'huiles noires déclenchées par un joueur.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Nombre d'huiles noires déclenchées
        """
        return self.get_mech_value(i_player, "Black Oil Trigger")

    def get_tears(self, i_player: int):
        """
        Récupère le nombre de larmes reçues par un joueur.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Nombre de larmes reçues
        """
        return self.get_mech_value(i_player, "Tear")

    def get_pizzaed(self):
        """
        Récupère la liste des joueurs tués par des pizzas.

        Returns:
            list: Liste des indices des joueurs tués par des pizzas
        """
        pizzaed = []
        for i in self.player_list:
            if self.got_pizzaed(i):
                pizzaed.append(i)
        return pizzaed