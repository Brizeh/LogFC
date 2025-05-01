from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class SLOTH(Boss):
    """
    Slothasor de la seconde aile de raid.
    """
    
    last    = None
    name    = "SLOTH"
    wing    = 2
    boss_id = 16123
    
    def __init__(self, log):
        """
        Initialise une instance de SLOTH avec un log spécifique.
        
        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp   = self.get_mvp()
        self.lvp   = self.get_lvp()
        SLOTH.last = self
        
    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Slothasor.
        
        Vérifie différentes conditions dans l'ordre:
        1. Joueur avec le plus de tantrums
        2. Joueur avec le moins de CC
        3. Joueur avec un DPS significativement bas
        
        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_tantrum = self.mvp_tantrum()
        if msg_tantrum:
            return msg_tantrum
        
        msg_cc = self.mvp_cc_sloth()
        if msg_cc:
            return msg_cc
        
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_shroom])
        if msg_bad_dps:
            return msg_bad_dps
        
        return    
        
    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Slothasor.
        
        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_cc_boss()
        
    def get_dps_ranking(self):
        """
        Calcule le classement DPS des joueurs pour Slothasor en excluant les supports et porteurs de champignon.
        
        Returns:
            dict: Dictionnaire associant les joueurs à leur score DPS
        """
        return self._get_dps_contrib([self.is_support, self.is_shroom])

    ################################ MVP ################################
    
    def mvp_cc_sloth(self):
        """
        Identifie les MVP basés sur le faible nombre de CC appliqué sur Slothasor.
        
        Returns:
            str: Message MVP formaté ou None si aucun joueur ne correspond au critère
        """
        i_players, min_cc, total_cc = Analyzer.get_min_value(self.player_list, self.get_cc_boss, exclude=[self.is_shroom])
        if min_cc < 800:
            self.add_mvps(i_players)
            cc_ratio  = min_cc / total_cc * 100
            mvp_names = self.players_to_string(i_players)
            if min_cc == 0:
                if len(i_players) > 1:
                    return language_config.selected_language["SLOTH MVP 0 CC P"].format(mvp_names=mvp_names)
                return language_config.selected_language["SLOTH MVP 0 CC S"].format(mvp_names=mvp_names)
            if len(i_players) > 1:
                return language_config.selected_language["SLOTH MVP CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            return language_config.selected_language["SLOTH MVP CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
        return None

    def mvp_tantrum(self):
        """
        Identifie les MVP basés sur le nombre élevé de tantrums gérés.
        
        Returns:
            str: Message MVP formaté ou None si aucun joueur ne correspond au critère
        """
        i_players, max_tantrum, _ = Analyzer.get_max_value(self.player_list, self.get_tantrum)
        if max_tantrum > 1:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) > 1:
                return language_config.selected_language["SLOTH MVP TANTRUM P"].format(mvp_names=mvp_names, max_tantrum=max_tantrum)
            return language_config.selected_language["SLOTH MVP TANTRUM S"].format(mvp_names=mvp_names, max_tantrum=max_tantrum)
        return None

    ################################ CONDITIONS ###############################
    
    def is_shroom(self, i_player: int):
        """
        Vérifie si un joueur a porté le champignon pendant le combat.
        
        Args:
            i_player (int): Indice du joueur à vérifier
            
        Returns:
            bool: True si le joueur a porté le champignon, False sinon
        """
        rota = self.get_player_rotation(i_player)
        for skill in rota:
            if skill['id'] == 34408:
                return True
        return False
    
    ################################ DATA MECHAS ################################
    
    def get_tantrum(self, i_player: int):
        """
        Récupère le nombre de tantrums gérés par un joueur.
        
        Args:
            i_player (int): Indice du joueur
            
        Returns:
            int: Nombre de tantrums gérés
        """
        return self.get_mech_value(i_player, "Tantrum")