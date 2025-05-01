from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class BONESKINNER(Boss):
    """
    Boneskinner de la saga Icebrood.
    """
    
    last = None
    name = "BONESKINNER"
    boss_id = 22521
    wing = "IBS"
    sak_id = 60501
    
    def __init__(self, log: Log):
        """
        Initialise une instance de Boneskinner.
        
        Args:
            log (Log): Objet contenant les données du journal de combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        BONESKINNER.last = self
        
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
        Vérifie d'abord les joueurs avec des statistiques SAK, puis utilise le DPS standard.
        
        Returns:
            str: Message pour le joueur avec le plus de dégâts
        """
        msg_sak = self.get_lvp_sak()
        if msg_sak:
            return msg_sak
        return self.get_lvp_dps()
    
    def get_lvp_sak(self):
        """
        Calcule le LVP basé sur les statistiques SAK (Shatter Assault Kill).
        
        Returns:
            str: Message formaté pour le LVP avec statistiques SAK ou None
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)
        sak_dmg = self.get_sak_dmg(i_players[0])
        sak_count = self.get_sak_count(i_players[0])
        lvp_dps_name = self.players_to_string(i_players)
        dps = max_dmg / self.duration_ms 
        dmg_ratio = max_dmg / tot_dmg * 100
        self.add_lvps(i_players)
        
        if sak_count:
            sak_ratio = sak_dmg / max_dmg * 100
            return language_config.selected_language["FRAENIR LVP SAK"].format(
                lvp_dps_name=lvp_dps_name, 
                sak_count=sak_count, 
                sak_ratio=sak_ratio, 
                dps=dps, 
                dmg_ratio=dmg_ratio
            )
        return None
    
    def get_sak_dmg(self, i_player: int):
        """
        Récupère les dégâts infligés par l'attaque Shatter Assault Kill.
        
        Args:
            i_player (int): Index du joueur dans les données
            
        Returns:
            int: Dégâts totaux infligés par SAK
        """
        dmgPath = self.log.pjcontent["players"][i_player]["targetDamageDist"][0][0]
        for dmg in dmgPath:
            if dmg["id"] == BONESKINNER.sak_id:
                return dmg["totalDamage"]
        return 0
    
    def get_sak_count(self, i_player: int):
        """
        Récupère le nombre d'utilisations de l'attaque Shatter Assault Kill.
        
        Args:
            i_player (int): Index du joueur dans les données
            
        Returns:
            int: Nombre d'utilisations de SAK
        """
        rota = self.get_player_rotation(i_player)
        for spell in rota:
            if spell["id"] == BONESKINNER.sak_id:
                return len(spell["skills"])
        return 0