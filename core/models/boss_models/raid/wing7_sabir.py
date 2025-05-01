"""
Module contenant la classe SABIR pour l'analyse des logs du boss Cardinal Sabir.
"""

from core.models.boss import Boss


class SABIR(Boss):
    """
    Classe représentant le boss Cardinal Sabir de la septième aile de raid.

    Cette classe implémente des méthodes de base pour analyser les performances
    des joueurs contre Sabir, basées principalement sur le CC.

    Attributes:
        last (SABIR): Référence à la dernière instance créée
        name (str): Nom du boss "SABIR"
        wing (int): Numéro de l'aile (7)
        boss_id (int): Identifiant du boss (21964)
    """

    last = None
    name = "SABIR"
    wing = 7
    boss_id = 21964

    def __init__(self, log):
        """
        Initialise une instance de SABIR avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SABIR.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Sabir.

        Pour Sabir, le MVP est basé uniquement sur les joueurs avec peu de CC.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        return self.get_mvp_cc_boss()

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Sabir.

        Pour Sabir, le LVP est basé uniquement sur les joueurs avec beaucoup de CC.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_cc_boss()