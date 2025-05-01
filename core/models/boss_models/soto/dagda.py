"""
Module contenant la classe représentant le boss Dagda de Secrets of the Obscure.
"""
from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class DAGDA(Boss):
    """
    Classe représentant le boss Dagda de Secrets of the Obscure.
    
    Attributes:
        last (DAGDA): Dernière instance créée de cette classe
        name (str): Nom du boss
        boss_id (int): Identifiant unique du boss
        wing (str): Type d'instance (ici "SOTO" pour Secrets of the Obscure)
        mvp (str): Message pour le joueur le plus performant
        lvp (str): Message pour le joueur avec le plus de dégâts
    """
    
    last = None
    name = "DAGDA"
    boss_id = 25705
    wing = "SOTO"
    
    def __init__(self, log: Log):
        """
        Initialise une instance de Dagda.
        
        Args:
            log (Log): Objet contenant les données du journal de combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        DAGDA.last = self
        
    def get_mvp(self):
        """
        Récupère le message pour le joueur le plus performant.
        Vérifie d'abord les joueurs avec des affaiblissements, puis ceux avec mauvais DPS.
        
        Returns:
            str: Message pour le joueur le plus performant ou None
        """
        msg_debil = self.mvp_debil()
        if msg_debil:
            return msg_debil
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
    
    def mvp_debil(self):
        """
        Détermine le MVP basé sur le nombre maximum d'affaiblissements appliqués.
        Exclut les joueurs soigneurs.
        
        Returns:
            str: Message formaté pour le MVP d'affaiblissements ou None
        """
        i_players, max_debil, _ = Analyzer.get_max_value(self.player_list, self.get_max_debil, exclude=[self.is_heal])
        mvp_names = self.players_to_string(i_players)
        
        if max_debil > 1:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return language_config.selected_language["KO MVP DEBIL S"].format(
                    mvp_names=mvp_names, max_debil=max_debil
                )
            else:
                return language_config.selected_language["KO MVP DEBIL P"].format(
                    mvp_names=mvp_names, max_debil=max_debil
                )
        return None
    
    def get_max_debil(self, i_player: int):
        """
        Récupère le nombre maximum d'affaiblissements appliqués par un joueur.
        
        Args:
            i_player (int): Index du joueur dans les données
            
        Returns:
            int: Nombre maximum d'affaiblissements appliqués
        """
        buffUptimes = self.log.pjcontent["players"][i_player]["buffUptimes"]
        debil_id = 67972
        states = None
        
        for buff in buffUptimes:
            if buff["id"] == debil_id:
                states = buff["states"]
                
        debil = 0
        if states:
            for state in states:
                if state[1] > debil:
                    debil = state[1]
                    
        return debil