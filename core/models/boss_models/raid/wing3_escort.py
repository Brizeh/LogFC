from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config
from utils.maths import get_dist


class ESCORT(Boss):
    """
    Escort de la troisième aile de raid.
    """

    last = None
    name = "ESCORT"
    wing = 3
    boss_id = 16253

    towers = [
        [387, 129.1],
        [304.1, 115.7],
        [187.1, 118.8],
        [226.1, 252.3],
        [80.3, 255.5]
    ]
    tower_radius = 19

    def __init__(self, log):
        """
        Initialise une instance de ESCORT avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        ESCORT.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour l'escorte.

        Vérifie si des joueurs ont été touchés par les mines.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_mine = self.mvp_mine()
        if msg_mine:
            return msg_mine
        return

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour l'escorte.

        Vérifie d'abord les problèmes avec les tours, puis les appels excessifs de Glenna.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        msg_tower = self.lvp_tower()
        if msg_tower:
            return msg_tower
        return self.lvp_glenna()

    ################################ MVP ################################

    def mvp_mine(self):
        """
        Identifie les MVP basés sur le déclenchement de mines.

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'a déclenché de mine
        """
        i_players = self.get_mined_players()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) == 1:
                return language_config.selected_language["ESCORT MVP MINE S"].format(mvp_names=mvp_names)
            else:
                return language_config.selected_language["ESCORT MVP MINE P"].format(mvp_names=mvp_names)
        return

    ################################ LVP ################################

    def lvp_glenna(self):
        """
        Identifie les LVP basés sur le nombre d'appels à Glenna.

        Returns:
            str: Message LVP formaté
        """
        i_players, max_call, _ = Analyzer.get_max_value(self.player_list, self.get_glenna_call)
        lvp_names = self.players_to_string(i_players)
        self.add_lvps(i_players)
        return language_config.selected_language["ESCORT LVP GLENNA"].format(lvp_names=lvp_names, max_call=max_call)

    def lvp_tower(self):
        """
        Identifie les LVP basés sur l'activation incorrecte des tours.

        Returns:
            str: Message LVP formaté ou None si les tours ont été correctement activées
        """
        towers = self.get_towers()
        lvp_names = self.players_to_string(towers)
        for i in self.player_list:
            for n in range(1, 6):
                if self.is_tower_n(i, n) and not self.is_tower(i):
                    return
        self.add_lvps(towers)
        if len(towers) == 1:
            return language_config.selected_language["ESCORT LVP TOWER S"].format(lvp_names=lvp_names)
        return language_config.selected_language["ESCORT LVP TOWER P"].format(lvp_names=lvp_names)

    ################################ CONDITIONS ################################

    def got_mined(self, i_player: int):
        """
        Vérifie si un joueur a été touché par une mine.

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur a été touché, False sinon
        """
        return self.get_mech_value(i_player, "Mine Detonation Hit") > 0

    def is_tower_n(self, i_player: int, n: int):
        """
        Vérifie si un joueur a activé une tour spécifique.

        Args:
            i_player (int): Indice du joueur à vérifier
            n (int): Numéro de la tour (1-5)

        Returns:
            bool: True si le joueur a activé la tour, False sinon
        """
        poses = self.get_player_pos(i_player)
        tower = ESCORT.towers[n - 1]
        for pos in poses:
            if get_dist(pos, tower) < ESCORT.tower_radius:
                return True
        return False

    def is_tower(self, i_player: int):
        """
        Vérifie si un joueur a activé toutes les tours.

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur a activé toutes les tours, False sinon
        """
        for n in range(1, 6):
            if not self.is_tower_n(i_player, n):
                return False
        return True

    ################################ DATA MECHAS ################################

    def get_mined_players(self):
        """
        Récupère la liste des joueurs touchés par des mines.

        Returns:
            list: Liste des indices des joueurs touchés par des mines
        """
        p = []
        for i in self.player_list:
            if self.got_mined(i):
                p.append(i)
        return p

    def get_glenna_call(self, i_player: int):
        """
        Récupère le nombre d'appels "Over Here!" lancés par un joueur.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Nombre d'appels
        """
        return self.get_mech_value(i_player, "Over Here! Cast")

    def get_towers(self):
        """
        Récupère la liste des joueurs ayant activé toutes les tours.

        Returns:
            list: Liste des indices des joueurs ayant activé toutes les tours
        """
        towers = []
        for i in self.player_list:
            if self.is_tower(i):
                towers.append(i)
        return towers