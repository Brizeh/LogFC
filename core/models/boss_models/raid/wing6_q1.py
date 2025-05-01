"""
Module contenant la classe Q1 pour l'analyse des logs du boss Qadim.
"""

from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config
from utils.maths import get_dist


class Q1(Boss):
    """
    Classe représentant le boss Qadim (premier) de la sixième aile de raid.

    Cette classe implémente des méthodes spécifiques pour analyser les performances
    des joueurs contre Qadim, notamment concernant le positionnement au centre et les ondes de choc.

    Attributes:
        last (Q1): Référence à la dernière instance créée
        name (str): Nom du boss "QADIM"
        wing (int): Numéro de l'aile (6)
        boss_id (int): Identifiant du boss (20934)
        center (list): Coordonnées du centre de l'arène
        fdp_radius (float): Rayon de la zone considérée comme "centre"
    """

    last = None
    name = "QADIM"
    wing = 6
    boss_id = 20934

    center = [411.5, 431.1]
    fdp_radius = 70

    def __init__(self, log):
        """
        Initialise une instance de Q1 avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        Q1.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Qadim.

        Vérifie d'abord les joueurs restés au centre, puis ceux avec un DPS faible,
        et enfin ceux touchés par les ondes de choc de la masse.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_fdp = self.mvp_fdp()
        if msg_fdp:
            return msg_fdp

        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        msg_wave = self.mvp_wave()
        if msg_wave:
            return msg_wave

        return None

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Qadim.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_dps()

    ################################ MVP ################################

    def mvp_fdp(self):
        """
        Identifie les MVP qui sont restés au centre de l'arène (FDP = Fire Door Protocol).

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'est resté au centre
        """
        i_players = self.get_fdp()
        fdp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)

        if len(i_players) == 1:
            return language_config.selected_language["QADIM MVP PYRE S"].format(fdp_names=fdp_names)
        if len(i_players) > 1:
            return language_config.selected_language["QADIM MVP PYRE P"].format(fdp_names=fdp_names)

        return None

    def mvp_wave(self):
        """
        Identifie les MVP touchés par le plus d'ondes de choc de la masse.

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'a été touché par beaucoup d'ondes
        """
        i_players, max_waves, _ = Analyzer.get_max_value(self.player_list, self.get_wave)
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)

        if len(i_players) == 1:
            return language_config.selected_language["QADIM MVP WAVE S"].format(mvp_names=mvp_names, max_waves=max_waves)
        if len(i_players) > 1:
            return language_config.selected_language["QADIM MVP WAVE P"].format(mvp_names=mvp_names, max_waves=max_waves)

        return None

    ################################ DATA MECHAS ################################

    def get_fdp(self):
        """
        Identifie les joueurs qui sont restés au centre de l'arène pendant les phases P1 et P2.

        Returns:
            list: Liste des indices des joueurs restés au centre
        """
        fdp = []
        start_p1, end_p1 = self.get_phase_timers("Qadim P1")
        start_p2, end_p2 = self.get_phase_timers("Qadim P2")

        for i in self.player_list:
            if not self.is_tank(i):
                add_fdp = True
                pos_p1 = self.get_player_pos(i, start=start_p1, end=end_p1)
                pos_p2 = self.get_player_pos(i, start=start_p2, end=end_p2)

                for pos in pos_p1:
                    dist = get_dist(pos, Q1.center)
                    if dist > Q1.fdp_radius:
                        add_fdp = False
                        break

                for pos in pos_p2:
                    dist = get_dist(pos, Q1.center)
                    if dist > Q1.fdp_radius:
                        add_fdp = False
                        break

                if add_fdp:
                    fdp.append(i)

        return fdp

    def get_wave(self, i_player: int):
        """
        Récupère le nombre d'ondes de choc de la masse subies par un joueur.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Nombre d'ondes de choc subies
        """
        return self.get_mech_value(i_player, "Mace Shockwave")