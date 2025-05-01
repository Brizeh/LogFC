"""
Module contenant la classe représentant le boss ENSOLYSS des fractales.
"""
from core.models.boss import Boss
from core.models.log import Log


class ENSOLYSS(Boss):
    """
    Classe représentant le boss ENSOLYSS des fractales.
    
    Attributes:
        last (ENSOLYSS): Dernière instance créée de cette classe
        name (str): Nom du boss
        boss_id (int): Identifiant unique du boss
        wing (str): Type d'instance (ici "FRAC" pour fractale)
        mvp (str): Message pour le joueur le plus performant
        lvp (str): Message pour le joueur avec le plus de dégâts
    """
    
    last = None
    name = "ENSOLYSS"
    boss_id = 16948
    wing = "FRAC"
    
    def __init__(self, log: Log):
        """
        Initialise une instance de ENSOLYSS.
        
        Args:
            log (Log): Objet contenant les données du journal de combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        ENSOLYSS.last = self
        
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