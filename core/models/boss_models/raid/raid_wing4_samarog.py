"""
Module contenant la classe SAMAROG pour l'analyse des logs du boss Samarog.
"""

import numpy as np

from core.models.boss import Boss
from i18n.languages import language_config


class SAMAROG(Boss):
    """
    Classe représentant le boss Samarog de la quatrième aile de raid.

    Cette classe implémente des méthodes spécifiques pour analyser les performances
    des joueurs contre Samarog, notamment concernant les joueurs empalés et les traîtres.

    Attributes:
        last (SAMAROG): Référence à la dernière instance créée
        name (str): Nom du boss "SAMAROG"
        wing (int): Numéro de l'aile (4)
        boss_id (int): Identifiant du boss (17188)
        top_left_corn, top_right_corn, bot_left_corn, bot_right_corn (list): Coordonnées des coins de l'arène
        scaler (float): Facteur d'échelle pour les coordonnées
    """

    last = None
    name = "SAMAROG"
    wing = 4
    boss_id = 17188

    # Coordonnées des coins de l'arène
    top_left_corn = [278.0, 645.2]
    top_right_corn = [667.6, 660.7]
    bot_left_corn = [299.4, 58.6]
    bot_right_corn = [690.7, 73.6]
    scaler = 5.4621

    def __init__(self, log):
        """
        Initialise une instance de SAMAROG avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SAMAROG.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Samarog.

        Vérifie d'abord les joueurs empalés, puis les traîtres, et enfin les joueurs
        avec peu de CC (excluant les joueurs fixés).

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
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
        Détermine le LVP (Least Valuable Player) pour le combat contre Samarog.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_cc_boss()

    ################################ MVP ################################

    def mvp_impaled(self):
        """
        Identifie les MVP qui ont été empalés.

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'a été empalé
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
        Identifie les MVP qui ont trahi d'autres joueurs (avec des verts).

        Returns:
            str: Message MVP formaté ou None si aucune trahison n'a eu lieu
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
        Vérifie si un joueur a été empalé.

        Un joueur est considéré comme empalé s'il est mort instantanément après
        avoir été touché par Sweep ou Shock Wave.

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur a été empalé, False sinon
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
        Vérifie si un joueur a été fixé par Samarog au moins 3 fois.

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur a été fixé au moins 3 fois, False sinon
        """
        return self.get_mech_value(i_player, "Fixate: Samarog") >= 3

    ################################ DATA MECHAS ################################

    def get_impaled(self):
        """
        Récupère la liste des joueurs qui ont été empalés.

        Returns:
            list: Liste des indices des joueurs empalés
        """
        i_players = []
        for i in self.player_list:
            if self.got_impaled(i):
                i_players.append(i)
        return i_players

    def get_traitors(self):
        """
        Identifie les joueurs qui ont trahi d'autres joueurs avec des mécaniques vertes.

        Returns:
            tuple: Tuple contenant (traîtres, victimes)
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