"""
Module contenant la classe AH pour l'analyse des logs du boss Mai Trin.
"""

from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class AH(Boss):
    """
    Classe représentant le boss Mai Trin d'End of Dragons.

    Cette classe implémente des méthodes spécifiques pour analyser les performances
    des joueurs contre Mai Trin, notamment concernant l'exposition et les dégâts.

    Attributes:
        last (AH): Référence à la dernière instance créée
        name (str): Nom du boss "MAI TRIN"
        boss_id (int): Identifiant du boss (24033)
        wing (str): Indication de l'expansion "EOD"
    """

    last = None
    name = "MAI TRIN"
    boss_id = 24033
    wing = "EOD"

    def __init__(self, log):
        """
        Initialise une instance de AH avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        AH.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Mai Trin.

        Vérifie d'abord les joueurs avec un niveau d'exposition élevé, puis ceux
        avec un DPS significativement bas.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_exposed = self.expose_mvp()
        if msg_exposed:
            return msg_exposed

        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Mai Trin.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_dps()

    ################################ MVP ################################

    def expose_mvp(self):
        """
        Identifie les MVP qui ont le plus souffert de l'effet d'exposition.

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'a été suffisamment exposé
        """
        i_players, max_exposed, _ = Analyzer.get_max_value(self.player_list, self.get_max_exposed,
                                                           exclude=[self.is_heal])
        mvp_names = self.players_to_string(i_players)

        if max_exposed > 2:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return language_config.selected_language["AH MVP EXPOSED S"].format(mvp_names=mvp_names, max_exposed=max_exposed)
            else:
                return language_config.selected_language["AH MVP EXPOSED P"].format(mvp_names=mvp_names, max_exposed=max_exposed)

        return None

    ################################ LVP ################################

    def get_lvp_dps(self):
        """
        Identifie les LVP basés sur leur DPS élevé.

        Cette méthode est une implémentation spécifique pour Mai Trin.

        Returns:
            str: Message LVP formaté ou None si aucun joueur n'a un DPS élevé
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)
        ratio = max_dmg / tot_dmg * 100
        time = self.duration_ms
        dps = max_dmg / time
        lvp_dps_name = self.players_to_string(i_players)
        self.add_lvps(i_players)

        return language_config.selected_language["LVP DPS"].format(lvp_dps_name=lvp_dps_name, dps=dps, dmg_ratio=ratio)

    ################################ DATA MECHAS ################################

    def get_max_exposed(self, i_player: int):
        """
        Récupère le niveau maximal d'exposition subi par un joueur.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Niveau maximal d'exposition
        """
        buffUptimes = self.log.pjcontent["players"][i_player]["buffUptimes"]
        expose_id = 64936
        expose_states = None

        for buff in buffUptimes:
            if buff["id"] == expose_id:
                expose_states = buff["states"]

        exposed = 0
        if expose_states:
            for state in expose_states:
                if state[1] > exposed:
                    exposed = state[1]

        return exposed

    def get_dmg_boss(self, i_player: int):
        """
        Calcule les dégâts totaux infligés par un joueur à Mai Trin et Echo.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Dégâts totaux infligés
        """
        targetDmg = self.log.pjcontent["players"][i_player]["dpsTargets"]
        mai_trin_dmg = targetDmg[0][0]["damage"]
        echo_dmg = targetDmg[1][0]["damage"]
        return mai_trin_dmg + echo_dmg