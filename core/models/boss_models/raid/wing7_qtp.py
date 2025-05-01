"""
Module contenant la classe QTP pour l'analyse des logs du boss Qadim the Peerless.
"""

from core.models.boss import Boss


class QTP(Boss):
    """
    Classe représentant le boss Qadim the Peerless (QTP) de la septième aile de raid.

    Cette classe implémente des méthodes spécifiques pour analyser les performances
    des joueurs contre QTP, notamment concernant les pylônes et les buffs.

    Attributes:
        last (QTP): Référence à la dernière instance créée
        name (str): Nom du boss "QTP"
        wing (int): Numéro de l'aile (7)
        boss_id (int): Identifiant du boss (22000)
    """

    last = None
    name = "QTP"
    wing = 7
    boss_id = 22000

    def __init__(self, log):
        """
        Initialise une instance de QTP avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        QTP.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre QTP.

        Vérifie d'abord les joueurs avec un DPS faible (en excluant les joueurs de pylône),
        puis ceux avec peu de CC (également en excluant les joueurs de pylône).

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_pylon])
        if msg_bad_dps:
            return msg_bad_dps

        msg_cc = self.get_mvp_cc_total(extra_exclude=[self.is_pylon])
        if msg_cc:
            return msg_cc

        return None

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre QTP.

        Vérifie d'abord les joueurs avec beaucoup de CC, puis ceux avec un DPS élevé.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        msg_cc = self.get_lvp_cc_total()
        if msg_cc:
            return msg_cc

        return self.get_lvp_dps()

    def is_alac(self, i_player: int):
        """
        Vérifie si un joueur fournit suffisamment d'alacrité à son sous-groupe.

        Cette méthode prend en compte le nombre de joueurs qui gèrent les pylônes
        dans le sous-groupe pour ajuster l'exigence de génération d'alacrité.

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur fournit suffisamment d'alacrité, False sinon
        """
        min_alac_contrib = 30
        alac_id = 30328
        boon_path = self.log.pjcontent['players'][i_player].get("groupBuffsActive")
        player_alac_contrib = 0
        pylon_players_in_sub = []

        if boon_path:
            for boon in boon_path:
                if boon["id"] == alac_id:
                    player_alac_contrib = boon["buffData"][self.real_phase_id]["generation"]
            pylon_players_in_sub = [i for i in self.player_list if
                                    self.is_pylon(i) and self.get_player_group(i_player) == self.get_player_group(i)]

        corrected_uptime = player_alac_contrib * 5 / (4 - len(pylon_players_in_sub))
        return corrected_uptime >= min_alac_contrib

    def is_quick(self, i_player: int):
        """
        Vérifie si un joueur fournit suffisamment de célérité à son sous-groupe.

        Cette méthode prend en compte le nombre de joueurs qui gèrent les pylônes
        dans le sous-groupe pour ajuster l'exigence de génération de célérité.

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur fournit suffisamment de célérité, False sinon
        """
        min_quick_contrib = 30
        quick_id = 1187
        boon_path = self.log.pjcontent['players'][i_player].get("groupBuffsActive")
        player_quick_contrib = 0
        pylon_players_in_sub = []

        if boon_path:
            for boon in boon_path:
                if boon["id"] == quick_id:
                    player_quick_contrib = boon["buffData"][self.real_phase_id]["generation"]
            pylon_players_in_sub = [i for i in self.player_list if
                                    self.is_pylon(i) and self.get_player_group(i_player) == self.get_player_group(i)]

        corrected_uptime = player_quick_contrib * 5 / (4 - len(pylon_players_in_sub))
        return corrected_uptime >= min_quick_contrib

    def get_dps_ranking(self):
        """
        Calcule le classement DPS des joueurs pour QTP en excluant les supports et joueurs de pylône.

        Returns:
            dict: Dictionnaire associant les joueurs à leur score DPS
        """
        return self._get_dps_contrib([self.is_support, self.is_pylon])

    ################################ CONDITIONS ################################

    def is_pylon(self, i_player: int):
        """
        Vérifie si un joueur est un 'joueur de pylône' (a attrapé plus d'une orbe).

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur a attrapé plus d'une orbe, False sinon
        """
        return self.get_orb_caught(i_player) > 1

    ################################ DATA MECHAS ################################

    def get_orb_caught(self, i_player: int):
        """
        Récupère le nombre d'orbes (Critical Mass) attrapées par un joueur.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Nombre d'orbes attrapées
        """
        return self.get_mech_value(i_player, "Critical Mass")