"""
Module contenant la classe représentant le boss KANAXAI des fractales.
"""
from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class KANAXAI(Boss):
    """
    Classe représentant le boss KANAXAI des fractales.
    
    Attributes:
        last (KANAXAI): Dernière instance créée de cette classe
        name (str): Nom du boss
        boss_id (int): Identifiant unique du boss
        wing (str): Type d'instance (ici "FRAC" pour fractale)
        mvp (str): Message pour le joueur le plus performant
        lvp (str): Message pour le joueur avec le plus de dégâts
    """
    
    last = None
    name = "KANAXAI"
    boss_id = 25577
    wing = "FRAC"
    
    def __init__(self, log: Log):
        """
        Initialise une instance de KANAXAI.
        
        Args:
            log (Log): Objet contenant les données du journal de combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        KANAXAI.last = self
        
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
            str: Message pour le joueur avec le plus de dégâts spécifique à KANAXAI
        """
        return self.get_lvp_dps()
    
    def get_lvp_dps(self):
        """
        Récupère le message spécifique pour le joueur avec le plus de dégâts sur KANAXAI.
        Inclut le nombre de liens si présent.
        
        Returns:
            str: Message formaté pour le joueur avec le plus de dégâts
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)
        lvp_dps_name = self.players_to_string(i_players)
        link_count = self.get_links(i_players[0])
        dmg_ratio = max_dmg / tot_dmg * 100
        dps = max_dmg / self.duration_ms
        
        if link_count:
            return language_config.selected_language["KANAXAI LVP DPS"].format(
                lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps, linkCount=link_count
            )
        else:
            return language_config.selected_language["LVP DPS"].format(
                lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps
            )
    
    def get_links(self, i_player: int):
        """
        Calcule le nombre de liens pour un joueur spécifique pendant les phases du combat.
        
        Args:
            i_player (int): Index du joueur à analyser
            
        Returns:
            int: Nombre de liens détectés
        """
        link_id = 69206
        start1, end1 = self.get_phase_timers("Phase 1", in_milliseconds=True)
        start2, end2 = self.get_phase_timers("Phase 2", in_milliseconds=True)
        start3, end3 = self.get_phase_timers("Phase 3", in_milliseconds=True)
        buff_uptimes = self.log.pjcontent["players"][i_player]["buffUptimes"]
        link_count = 0
        
        # Ajustement des temps pour les phases
        start2 += 8000
        start3 += 8000
        end1 -= 8000
        end2 -= 8000
        
        for buff in buff_uptimes:
            if buff["id"] == link_id:
                for state in buff["states"]:
                    buff_time = state[0]
                    if (
                        state[1] == 1 and
                        ((buff_time > start1 and buff_time < end1) or
                         (buff_time > start2 and buff_time < end2) or
                         (buff_time > start3 and buff_time < end3))
                    ):
                        link_count += 1
        
        return link_count