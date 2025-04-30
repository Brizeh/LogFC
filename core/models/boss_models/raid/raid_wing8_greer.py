"""
Module contenant la classe GREER pour l'analyse des logs du boss Voice of the Fallen (Greer).
"""

from core.models.boss import Boss


class GREER(Boss):
    """
    Classe représentant le boss Voice of the Fallen (Greer) de la huitième aile de raid.

    Cette classe implémente des méthodes de base pour analyser les performances
    des joueurs contre Greer, basées principalement sur le DPS.

    Attributes:
        last (GREER): Référence à la dernière instance créée
        name (str): Nom du boss "GREER"
        wing (int): Numéro de l'aile (8)
        boss_id (int): Identifiant du boss (26725)
    """

    last = None
    name = "GREER"
    wing = 8
    boss_id = 26725

    def __init__(self, log):
        """
        Initialise une instance de GREER avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        GREER.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Greer.

        Pour Greer, le MVP est basé uniquement sur les joueurs avec un DPS significativement bas.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        return self.get_bad_dps()

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Greer.

        Pour Greer, le LVP est basé uniquement sur les joueurs avec un DPS élevé.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_dps()