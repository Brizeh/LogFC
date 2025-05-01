"""
Module contenant la classe représentant le boss Cerus de Secrets of the Obscure.
"""
from core.models.boss import Boss
from core.models.log import Log


class CERUS(Boss):
    """
    Classe représentant le boss Cerus de Secrets of the Obscure.
    
    Attributes:
        last (CERUS): Dernière instance créée de cette classe
        name (str): Nom du boss
        boss_id (int): Identifiant unique du boss
        wing (str): Type d'instance (ici "SOTO" pour Secrets of the Obscure)
        mvp (str): Message pour le joueur le plus performant
        lvp (str): Message pour le joueur avec le plus de dégâts
    """
    
    last = None
    name = "CERUS"
    boss_id = 25989
    wing = "SOTO"
    
    def __init__(self, log: Log):
        """
        Initialise une instance de Cerus.
        
        Args:
            log (Log): Objet contenant les données du journal de combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        CERUS.last = self  # Correction de DAGDA.last à CERUS.last
        
    def get_mvp(self):
        """
        Récupère le message pour le joueur le plus performant.
        
        Returns:
            str: Message pour le joueur le plus performant ou None
        """
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return None
    
    def get_lvp(self):
        """
        Récupère le message pour le joueur avec le plus de dégâts.
        
        Returns:
            str: Message pour le joueur avec le plus de dégâts
        """
        return self.get_lvp_dps()