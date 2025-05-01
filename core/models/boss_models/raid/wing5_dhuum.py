"""
Module contenant la classe DHUUM pour l'analyse des logs du boss Dhuum.
"""

from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class DHUUM(Boss):
    """
    Classe représentant le boss Dhuum de la cinquième aile de raid.

    Cette classe implémente des méthodes spécifiques pour analyser les performances
    des joueurs contre Dhuum, en particulier concernant les fissures.

    Attributes:
        last (DHUUM): Référence à la dernière instance créée
        name (str): Nom du boss "DHUUM"
        wing (int): Numéro de l'aile (5)
        boss_id (int): Identifiant du boss (19450)
        real_phase (str): Phase principale du combat
    """

    last = None
    name = "DHUUM"
    wing = 5
    boss_id = 19450
    real_phase = "Dhuum Fight"

    def __init__(self, log):
        """
        Initialise une instance de DHUUM avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        DHUUM.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Dhuum.

        Vérifie d'abord les joueurs avec beaucoup de fissures, puis les joueurs
        avec un DPS significativement bas (en excluant les porteurs de vert).

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_cracks = self.mvp_cracks()
        if msg_cracks:
            return msg_cracks

        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_green])
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Dhuum.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_dps()

    def get_dps_ranking(self):
        """
        Calcule le classement DPS des joueurs pour Dhuum en excluant les supports et porteurs de vert.

        Returns:
            dict: Dictionnaire associant les joueurs à leur score DPS
        """
        return self._get_dps_contrib([self.is_support, self.is_green])

    ################################ MVP ################################

    def mvp_cracks(self):
        """
        Identifie les MVP basés sur le nombre élevé de fissures gérées.

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'a géré beaucoup de fissures
        """
        i_players, max_cracks, _ = Analyzer.get_max_value(self.player_list, self.get_cracks)
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)

        if len(i_players) == 1:
            return language_config.selected_language["DHUUM MVP CRACKS S"].format(mvp_names=mvp_names, max_cracks=max_cracks)
        if len(i_players) > 1:
            return language_config.selected_language["DHUUM MVP CRACKS P"].format(mvp_names=mvp_names, max_cracks=max_cracks)

        return None

    ################################ CONDITIONS ################################

    def is_green(self, i_player: int) -> bool:
        """
        Vérifie si un joueur a effectué un port vert pendant la phase principale.

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur a effectué un port vert, False sinon
        """
        return self.get_mech_value(i_player, "Green port", "Dhuum Fight") > 0

    ################################ DATA MECHAS ################################

    def get_cracks(self, i_player: int):
        """
        Récupère le nombre de fissures gérées par un joueur.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Nombre de fissures gérées
        """
        return self.get_mech_value(i_player, "Cracks")