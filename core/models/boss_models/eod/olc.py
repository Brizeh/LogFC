"""
Module contenant la classe OLC pour l'analyse des logs du boss Old Lion's Court.
"""

from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class OLC(Boss):
    """
    Classe représentant le boss Old Lion's Court (OLC) d'End of Dragons.

    Cette classe implémente des méthodes de base pour analyser les performances
    des joueurs contre Old Lion's Court, basées principalement sur le DPS.

    Attributes:
        last (OLC): Référence à la dernière instance créée
        name (str): Nom du boss "OLC"
        boss_id (int): Identifiant du boss (25413)
        wing (str): Indication de l'expansion "EOD"
    """

    last = None
    name = "OLC"
    boss_id = 25413
    wing = "EOD"

    def __init__(self, log):
        """
        Initialise une instance de OLC avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        OLC.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Old Lion's Court.

        Pour Old Lion's Court, le MVP est basé uniquement sur les joueurs avec un DPS significativement bas.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Old Lion's Court.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_dps()

    ################################ LVP ################################

    def get_lvp_dps(self):
        """
        Identifie les LVP basés sur leur DPS élevé.

        Cette méthode est une implémentation spécifique pour Old Lion's Court.

        Returns:
            str: Message LVP formaté ou None si aucun joueur n'a un DPS élevé
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)
        lvp_dps_name = self.players_to_string(i_players)
        dmg_ratio = max_dmg / tot_dmg * 100
        dps = max_dmg / self.duration_ms
        self.add_lvps(i_players)

        return language_config.selected_language["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps)

    ################################ DATA MECHAS ################################

    def get_dmg_boss(self, i_player: int):
        """
        Récupère les dégâts totaux infligés par un joueur à Old Lion's Court.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Dégâts totaux infligés
        """
        return self.log.pjcontent["players"][i_player]["dpsAll"][0]["damage"]