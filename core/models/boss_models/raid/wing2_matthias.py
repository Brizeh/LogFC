from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class MATTHIAS(Boss):
    """
    Classe représentant le boss Matthias de la seconde aile de raid.

    Cette classe implémente des méthodes spécifiques pour analyser les performances
    des joueurs contre Matthias, en particulier concernant les contrôles et les sacrifices.

    Attributes:
        last (MATTHIAS): Référence à la dernière instance créée
        name (str): Nom du boss "MATTHIAS"
        wing (int): Numéro de l'aile (2)
        boss_id (int): Identifiant du boss (16115)
    """

    last = None
    name = "MATTHIAS"
    wing = 2
    boss_id = 16115

    def __init__(self, log):
        """
        Initialise une instance de MATTHIAS avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        MATTHIAS.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Matthias.

        Identifie les joueurs ayant appliqué le moins de CC sur Matthias.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        return self.mvp_cc_matthias()

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Matthias.

        Identifie les joueurs ayant appliqué le plus de CC sur Matthias.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.lvp_cc_matthias()

    def get_dps_ranking(self):
        """
        Calcule le classement DPS des joueurs pour Matthias en excluant les supports et sacrifiés.

        Returns:
            dict: Dictionnaire associant les joueurs à leur score DPS
        """
        return self._get_dps_contrib([self.is_support, self.is_sac])

    ################################ MVP ################################

    def mvp_cc_matthias(self):
        """
        Identifie les MVP basés sur le faible nombre de CC appliqué sur Matthias.

        Returns:
            str: Message MVP formaté
        """
        i_players, min_cc, total_cc = Analyzer.get_min_value(self.player_list, self.get_cc_total, exclude=[self.is_sac])
        cc_ratio = min_cc / total_cc * 100
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if min_cc == 0:
            return language_config.selected_language["MATTHIAS MVP 0 CC"].format(mvp_names=mvp_names)
        else:
            return language_config.selected_language["MATTHIAS MVP CC"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)

    ################################ LVP ################################

    def lvp_cc_matthias(self):
        """
        Identifie les LVP basés sur le nombre élevé de CC appliqué sur Matthias.

        Returns:
            str: Message LVP formaté
        """
        i_players, max_cc, total_cc = Analyzer.get_max_value(self.player_list, self.get_cc_total)
        cc_ratio = max_cc / total_cc * 100
        lvp_names = self.players_to_string(i_players)
        self.add_lvps(i_players)
        return language_config.selected_language["MATTHIAS LVP CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)

    ################################ CONDITIONS ###############################

    def is_sac(self, i_player: int):
        """
        Vérifie si un joueur a été sacrifié pendant le combat.

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur a été sacrifié, False sinon
        """
        return self.get_nb_sac(i_player) > 0

    ################################ DATA MECHAS ################################    

    def get_nb_sac(self, i_player: int):
        """
        Récupère le nombre de fois qu'un joueur a été sacrifié.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Nombre de sacrifices
        """
        return self.get_mech_value(i_player, "Sacrifice")