"""
Module contenant la classe CA pour l'analyse des logs du boss Conjured Amalgamate.
"""

from core.models.boss import Boss


class CA(Boss):
    """
    Classe représentant le boss Conjured Amalgamate (CA) de la sixième aile de raid.

    Cette classe implémente des méthodes de base pour analyser les performances
    des joueurs contre Conjured Amalgamate.

    Attributes:
        last (CA): Référence à la dernière instance créée
        name (str): Nom du boss "CA"
        wing (int): Numéro de l'aile (6)
        boss_id (int): Identifiant du boss (43974)
    """

    last = None
    name = "CA"
    wing = 6
    boss_id = 43974

    def __init__(self, log):
        """
        Initialise une instance de CA avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        CA.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Conjured Amalgamate.

        Pour CA, le MVP est basé uniquement sur les joueurs avec un DPS significativement bas.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        return self.get_bad_dps()

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Conjured Amalgamate.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_dps()

    ################################ MVP ################################

    ################################ LVP ################################

    ################################ CONDITIONS ################################

    ################################ DATA MECHAS ################################
    