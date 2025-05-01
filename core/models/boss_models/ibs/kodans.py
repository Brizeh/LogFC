
"""
from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class KODANS(Boss):
    """
    Kodans de la saga Icebrood.
    """
    
    last = None
    name = "KODANS"
    boss_id = 22343
    wing = "IBS"
    
    def __init__(self, log: Log):
        """
        Initialise une instance de Kodans.
        
        Args:
            log (Log): Objet contenant les données du journal de combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        KODANS.last = self
        
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
    
    def get_lvp_dps(self):
        """
        Calcule et formate le message pour le joueur avec le plus de dégâts.
        Prend en compte les dégâts combinés des deux cibles.
        
        Returns:
            str: Message formaté pour le joueur avec le plus de dégâts
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)
        lvp_dps_name = self.players_to_string(i_players)
        dps = max_dmg / self.duration_ms 
        dmg_ratio = max_dmg / tot_dmg * 100
        self.add_lvps(i_players)
        return language_config.selected_language["LVP DPS"].format(
            lvp_dps_name=lvp_dps_name, dps=dps, dmg_ratio=dmg_ratio
        )
    
    def get_dmg_boss(self, i_player: int):
        """
        Calcule les dégâts totaux infligés par un joueur aux deux cibles du boss.
        
        Args:
            i_player (int): Index du joueur dans les données
            
        Returns:
            int: Somme des dégâts infligés aux deux cibles
        """
        boss1_dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][0][self.real_phase_id]['damage']
        boss2_dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][1][self.real_phase_id]['damage']
        return boss1_dmg + boss2_dmg