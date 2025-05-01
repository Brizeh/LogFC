"""
Module contenant la classe représentant le boss Voice of the Fallen (WOJ) de la saga Icebrood.
"""
from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class WOJ(Boss):
    """
    Classe représentant le boss Voice of the Fallen (WOJ) de la saga Icebrood.
    
    Attributes:
        last (WOJ): Dernière instance créée de cette classe
        name (str): Nom du boss
        boss_id (int): Identifiant unique du boss
        wing (str): Type d'instance (ici "IBS" pour Icebrood Saga)
        mvp (str): Message pour le joueur le plus performant
        lvp (str): Message pour le joueur avec le plus de dégâts
    """
    
    last = None
    name = "WOJ"
    boss_id = 22711
    wing = "IBS"
    
    def __init__(self, log: Log):
        """
        Initialise une instance de Voice of the Fallen (WOJ).
        
        Args:
            log (Log): Objet contenant les données du journal de combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        WOJ.last = self
        
    def get_mvp(self):
        """
        Récupère le message pour le joueur le plus performant.
        Vérifie d'abord les dégâts des chaînes, puis les joueurs avec de mauvais DPS.
        
        Returns:
            str: Message pour le joueur le plus performant ou None
        """
        msg_chains = self.get_chain_mvp()
        if msg_chains:
            return msg_chains
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
    
    def get_chain_mvp(self):
        """
        Détermine le MVP basé sur les dégâts des chaînes subis.
        
        Returns:
            str: Message formaté pour le MVP des chaînes ou None
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_chain_damage)
        mvp_name = self.players_to_string(i_players)
        ratio = max_dmg / tot_dmg * 100
        self.add_mvps(i_players) 
        
        if max_dmg > 10000:
            return language_config.selected_language["WOJ MVP CHAINS"].format(
                mvp_name=mvp_name, max_dmg=max_dmg, ratio=ratio
            )
        return None
    
    def get_chain_damage(self, i_player: int):
        """
        Récupère les dégâts subis par un joueur à cause des chaînes.
        
        Args:
            i_player (int): Index du joueur dans les données
            
        Returns:
            int: Dégâts totaux subis par les chaînes
        """
        chain_id = 59159
        dmgTaken = self.log.pjcontent['players'][i_player]["totalDamageTaken"][0]
        for dmg in dmgTaken:
            if dmg["id"] == chain_id:
                return dmg["totalDamage"]
        return 0