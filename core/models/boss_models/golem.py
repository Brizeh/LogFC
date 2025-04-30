"""
Module contenant la classe GOLEM pour l'analyse des logs du boss d'entraînement Golem.
"""

from core.models.boss import Boss


class GOLEM(Boss):
    """
    Classe représentant le boss d'entraînement Golem.

    Cette classe implémente des méthodes minimales pour l'analyse des logs du Golem,
    principalement utilisé pour les tests de DPS.

    Attributes:
        last (GOLEM): Référence à la dernière instance créée
        name (str): Nom du boss "GOLEM CHAT STANDARD"
        boss_id (int): Identifiant du boss (16199)
    """

    last = None
    name = "GOLEM CHAT STANDARD"
    boss_id = 16199

    def __init__(self, log):
        """
        Initialise une instance de GOLEM avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        GOLEM.last = self