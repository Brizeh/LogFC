"""
Module contenant la classe ADINA pour l'analyse des logs du boss Cardinal Adina.
"""

from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class ADINA(Boss):
    """
    Classe représentant le boss Cardinal Adina de la septième aile de raid.

    Cette classe implémente des méthodes spécifiques pour analyser les performances
    des joueurs contre Adina, notamment concernant les phases de split.

    Attributes:
        last (ADINA): Référence à la dernière instance créée
        name (str): Nom du boss "ADINA"
        wing (int): Numéro de l'aile (7)
        boss_id (int): Identifiant du boss (22006)
    """

    last = None
    name = "ADINA"
    wing = 7
    boss_id = 22006

    def __init__(self, log):
        """
        Initialise une instance de ADINA avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        ADINA.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Adina.

        Vérifie d'abord les joueurs avec un DPS faible, puis ceux qui ont fait
        le moins de dégâts pendant les phases de split.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return self.mvp_dmg_split()

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Adina.

        Identifie les joueurs qui ont fait le plus de dégâts pendant les phases de split.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.lvp_dmg_split()

    ################################ MVP ################################

    def mvp_dmg_split(self):
        """
        Identifie les MVP qui ont fait le moins de dégâts pendant les phases de split.

        Returns:
            str: Message MVP formaté
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
        Identifie les LVP qui ont fait le plus de dégâts pendant les phases de split.

        Returns:
            str: Message LVP formaté
        """
        i_players, max_dmg, total_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_split)
        lvp_names = self.players_to_string(i_players)
        dmg_ratio = max_dmg / total_dmg * 100
        self.add_lvps(i_players)
        return language_config.selected_language["ADINA LVP SPLIT"].format(lvp_names=lvp_names, dmg_ratio=dmg_ratio)

    ################################ DATA MECHAS ################################

    def get_dmg_split(self, i_player: int):
        """
        Calcule les dégâts totaux infligés par un joueur pendant les phases de split.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Dégâts totaux infligés pendant les phases de split
        """
        dmg_split1 = self.log.jcontent['phases'][2]['dpsStats'][i_player][0]
        dmg_split2 = self.log.jcontent['phases'][4]['dpsStats'][i_player][0]
        dmg_split3 = self.log.jcontent['phases'][6]['dpsStats'][i_player][0]
        return dmg_split1 + dmg_split2 + dmg_split3