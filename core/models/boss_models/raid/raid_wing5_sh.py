"""
Module contenant la classe SH pour l'analyse des logs du boss Soulless Horror.
"""

from core.models.boss import Boss
from utils.maths import get_dist
from i18n.languages import language_config


class SH(Boss):
    """
    Classe représentant le boss Soulless Horror (SH) de la cinquième aile de raid.

    Cette classe implémente des méthodes spécifiques pour analyser les performances
    des joueurs contre Soulless Horror, notamment concernant les chutes et les murs.

    Attributes:
        last (SH): Référence à la dernière instance créée
        name (str): Nom du boss "SH"
        wing (int): Numéro de l'aile (5)
        boss_id (int): Identifiant du boss (19767)
        center_arena (list): Coordonnées du centre de l'arène
        radius1, radius2, radius3, radius4, radius5 (float): Rayons des différentes sections de l'arène
    """

    last = None
    name = "SH"
    wing = 5
    boss_id = 19767

    # Coordonnées et rayons de l'arène
    center_arena = [375, 375]
    radius1 = 345.5
    radius2 = 304.2
    radius3 = 256.2
    radius4 = 208.5
    radius5 = 163

    def __init__(self, log):
        """
        Initialise une instance de SH avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SH.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Soulless Horror.

        Vérifie d'abord les joueurs touchés par un mur, puis ceux qui sont tombés,
        et enfin les joueurs avec peu de CC.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_wall = self.mvp_wall()
        if msg_wall:
            return msg_wall

        msg_fall = self.mvp_fall()
        if msg_fall:
            return msg_fall

        return self.get_mvp_cc_boss()

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Soulless Horror.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_cc_boss()

    ################################ MVP ################################

    def mvp_wall(self):
        """
        Identifie les MVP qui ont été touchés par un mur.

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'a été touché par un mur
        """
        i_players = self.get_walled_players()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)

        if i_players:
            return language_config.selected_language["SH MVP WALL"].format(mvp_names=mvp_names)

        return None

    def mvp_fall(self):
        """
        Identifie les MVP qui sont tombés de l'arène.

        Note: Il y a probablement une erreur dans le code original car il utilise
        get_walled_players() au lieu de get_fallen_players(). Cette implémentation
        corrige cette erreur.

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'est tombé
        """
        i_players = self.get_fallen_players()  # Correction de la fonction appelée
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)

        if i_players:
            return language_config.selected_language["SH MVP FALL"].format(mvp_names=mvp_names)

        return None

    ################################ CONDITIONS ################################

    def took_wall(self, i_player: int):
        """
        Vérifie si un joueur a été touché par un mur (mort instantanée non due à une chute).

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur a été touché par un mur, False sinon
        """
        if self.is_dead_instant(i_player) and not self.has_fallen(i_player):
            return True
        return False

    def has_fallen(self, i_player: int):
        """
        Vérifie si un joueur est tombé de l'arène.

        Cette méthode analyse la position du joueur à sa mort et le moment de sa mort
        pour déterminer s'il est tombé d'une des bordures de l'arène.

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur est tombé de l'arène, False sinon
        """
        if self.is_dead_instant(i_player):
            last_pos = self.get_player_pos(i_player)[-1]
            death_time = self.get_player_death_timer(i_player)
            fell_at_begin = get_dist(SH.center_arena, last_pos) > SH.radius2
            fell_to_radius23 = death_time > self.boss_hp_to_time(90) + 2500 and death_time < self.boss_hp_to_time(
                66) + 2500 and get_dist(SH.center_arena, last_pos) > SH.radius3
            fell_to_radius34 = death_time > self.boss_hp_to_time(66) + 2500 and death_time < self.boss_hp_to_time(
                33) + 2500 and get_dist(SH.center_arena, last_pos) > SH.radius4
            fell_to_radius45 = death_time > self.boss_hp_to_time(33) + 2500 and get_dist(SH.center_arena,
                                                                                        last_pos) > SH.radius5

            if fell_at_begin or fell_to_radius23 or fell_to_radius34 or (self.cm and fell_to_radius45):
                return True

        return False

    ################################ DATA MECHAS ################################

    def get_walled_players(self):
        """
        Récupère la liste des joueurs touchés par un mur.

        Returns:
            list: Liste des indices des joueurs touchés par un mur
        """
        walled = []
        for i in self.player_list:
            if self.took_wall(i):
                walled.append(i)
        return walled

    def get_fallen_players(self):
        """
        Récupère la liste des joueurs tombés de l'arène.

        Returns:
            list: Liste des indices des joueurs tombés de l'arène
        """
        fallen = []
        for i in self.player_list:
            if self.has_fallen(i):
                fallen.append(i)
        return fallen