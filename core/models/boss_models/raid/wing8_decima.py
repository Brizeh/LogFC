"""
Module contenant la classe DECIMA pour l'analyse des logs du boss Keeper of Order (Decima).
"""

from core.models.boss import Boss


class DECIMA(Boss):
    """
    Classe représentant le boss Keeper of Order (Decima) de la huitième aile de raid.

    Cette classe implémente des méthodes de base pour analyser les performances
    des joueurs contre Decima, basées principalement sur le DPS.

    Attributes:
        last (DECIMA): Référence à la dernière instance créée
        name (str): Nom du boss "DECIMA"
        wing (int): Numéro de l'aile (8)
        boss_id (int): Identifiant du boss (26774)
    """

    last = None
    name = "DECIMA"
    wing = 8
    boss_id = 26774

    def __init__(self, log):
        """
        Initialise une instance de DECIMA avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        DECIMA.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Decima.

        Pour Decima, le MVP est basé uniquement sur les joueurs avec un DPS significativement bas.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        return self.get_bad_dps()

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Decima.

        Pour Decima, le LVP est basé uniquement sur les joueurs avec un DPS élevé.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_dps()