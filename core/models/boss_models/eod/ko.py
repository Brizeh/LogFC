"""
Module contenant la classe KO pour l'analyse des logs du boss Minister Li.
"""

from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class KO(Boss):
    """
    Classe représentant le boss Minister Li (KO) d'End of Dragons.

    Cette classe implémente des méthodes spécifiques pour analyser les performances
    des joueurs contre Minister Li, notamment concernant les affaiblissements.

    Attributes:
        last (KO): Référence à la dernière instance créée
        name (str): Nom du boss "KO"
        boss_id (int): Identifiant du boss (24485)
        wing (str): Indication de l'expansion "EOD"
    """

    last = None
    name = "KO"
    boss_id = 24485
    wing = "EOD"

    def __init__(self, log):
        """
        Initialise une instance de KO avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        KO.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Minister Li.

        Vérifie d'abord les joueurs avec beaucoup d'affaiblissements, puis ceux
        avec un DPS significativement bas.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_debil = self.mvp_debil()
        if msg_debil:
            return msg_debil

        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Minister Li.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_dps()

    ################################ LVP ################################

    def get_lvp_dps(self):
        """
        Identifie les LVP basés sur leur DPS élevé.

        Cette méthode est une implémentation spécifique pour Minister Li.

        Returns:
            str: Message LVP formaté ou None si aucun joueur n'a un DPS élevé
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)
        lvp_dps_name = self.players_to_string(i_players)
        dmg_ratio = max_dmg / tot_dmg * 100
        dps = max_dmg / self.duration_ms
        self.add_lvps(i_players)

        return language_config.selected_language["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps)

    ################################ MVP ################################

    def mvp_debil(self):
        """
        Identifie les MVP qui ont subi le plus d'affaiblissements (debilitation).

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'a subi beaucoup d'affaiblissements
        """
        i_players, max_debil, _ = Analyzer.get_max_value(self.player_list, self.get_max_debil, exclude=[self.is_heal])
        mvp_names = self.players_to_string(i_players)

        if max_debil > 1:
            self.add_lvps(i_players)  # Erreur possible : devrait probablement être add_mvps
            if len(i_players) == 1:
                return language_config.selected_language["KO MVP DEBIL S"].format(mvp_names=mvp_names, max_debil=max_debil)
            else:
                return language_config.selected_language["KO MVP DEBIL P"].format(mvp_names=mvp_names, max_debil=max_debil)

        return None

    ################################ DATA MECHAS ################################

    def get_max_debil(self, i_player: int):
        """
        Récupère le niveau maximal d'affaiblissement subi par un joueur.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Niveau maximal d'affaiblissement
        """
        buffUptimes = self.log.pjcontent["players"][i_player]["buffUptimes"]
        debil_id = 67972
        states = None

        for buff in buffUptimes:
            if buff["id"] == debil_id:
                states = buff["states"]

        debil = 0
        if states:
            for state in states:
                if state[1] > debil:
                    debil = state[1]

        return debil

    def get_dmg_boss(self, i_player: int):
        """
        Récupère les dégâts totaux infligés par un joueur à Minister Li.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Dégâts totaux infligés
        """
        return self.log.pjcontent["players"][i_player]["dpsAll"][0]["damage"]