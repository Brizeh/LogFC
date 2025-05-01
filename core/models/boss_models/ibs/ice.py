from core.models.boss import Boss
from core.models.log import Log


class ICE(Boss):
    """
    Icebrood Construct de la saga Icebrood.
    """
    
    last = None
    name = "ICEBROOD"
    boss_id = 22154
    wing = "IBS"
    
    def __init__(self, log: Log):
        """
        Initialise une instance de Icebrood Construct.
        
        Args:
            log (Log): Objet contenant les données du journal de combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        ICE.last = self
        
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