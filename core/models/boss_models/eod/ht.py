"""
Module contenant la classe HT pour l'analyse des logs du boss Harvest Temple.
"""

from core.models.boss import Boss


class HT(Boss):
    """
    Classe représentant le boss Harvest Temple (HT) d'End of Dragons.

    Cette classe implémente des méthodes de base pour analyser les performances
    des joueurs contre Harvest Temple, basées principalement sur le DPS.

    Attributes:
        last (HT): Référence à la dernière instance créée
        name (str): Nom du boss "HT"
        boss_id (int): Identifiant du boss (24375)
        wing (str): Indication de l'expansion "EOD"
    """

    last = None
    name = "HT"
    boss_id = 24375
    wing = "EOD"

    def __init__(self, log):
        """
        Initialise une instance de HT avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        HT.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Harvest Temple.

        Pour Harvest Temple, le MVP est basé uniquement sur les joueurs avec un DPS significativement bas.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Harvest Temple.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_dps()