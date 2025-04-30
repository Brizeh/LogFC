"""
Module contenant la classe XJ pour l'analyse des logs du boss Ankka.
"""

from core.models.boss import Boss


class XJ(Boss):
    """
    Classe représentant le boss Ankka d'End of Dragons.

    Cette classe implémente des méthodes de base pour analyser les performances
    des joueurs contre Ankka, basées principalement sur le CC et le DPS.

    Attributes:
        last (XJ): Référence à la dernière instance créée
        name (str): Nom du boss "ANKKA"
        boss_id (int): Identifiant du boss (23957)
        wing (str): Indication de l'expansion "EOD"
    """

    last = None
    name = "ANKKA"
    boss_id = 23957
    wing = "EOD"

    def __init__(self, log):
        """
        Initialise une instance de XJ avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        XJ.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Ankka.

        Vérifie d'abord les joueurs avec peu de CC, puis ceux avec un DPS significativement bas.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_cc = self.get_mvp_cc_total()
        if msg_cc:
            return msg_cc

        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Ankka.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_dps()