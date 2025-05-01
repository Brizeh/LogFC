from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config
from utils.formatters import time_to_index
from utils.maths import get_dist


class XERA(Boss):
    """
    Xera de la troisième aile de raid.
    """

    last = None
    name = "XERA"
    wing = 3
    boss_id = 16246
    real_phase = "Phase 1"

    # Coordonnées des points spécifiques
    debut = [497.1, 86.4]
    l1 = [663.0, 314.9]
    l2 = [532.5, 557.4]
    fin = [268.3, 586.4]
    r1 = [208.2, 103.4]
    r2 = [87.0, 346.8]
    centre = [366.4, 323.4]
    debut_radius = 85
    centre_radius = 140

    def __init__(self, log):
        """
        Initialise une instance de XERA avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        XERA.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Xera.

        Vérifie d'abord les joueurs qui ont pu skip le mini-jeu, puis les joueurs
        qui sont morts en volant, et enfin les joueurs avec peu de CC.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_fdp = self.mvp_fdp_xera()
        if msg_fdp:
            return msg_fdp

        msg_glide = self.mvp_glide()
        if msg_glide:
            return msg_glide

        return self.get_mvp_cc_boss()

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Xera.

        Vérifie d'abord les joueurs qui ont fait le mini-jeu deux fois, puis les
        joueurs avec beaucoup de CC.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        msg_minijeu = self.lvp_minijeu()
        if msg_minijeu:
            return msg_minijeu

        return self.get_lvp_cc_boss()

    def get_dps_ranking(self):
        """
        Calcule le classement DPS des joueurs pour Xera en excluant les supports.

        Returns:
            dict: Dictionnaire associant les joueurs à leur score DPS
        """
        return self._get_dps_contrib([self.is_support])

    ################################ MVP ################################

    def mvp_fdp_xera(self):
        """
        Identifie les MVP qui ont réussi à esquiver le mini-jeu de Xera.

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'a esquivé le mini-jeu
        """
        i_fdp = self.get_fdp()
        fdp_names = self.players_to_string(i_fdp)
        self.add_mvps(i_fdp)

        if len(i_fdp) == 1:
            return language_config.selected_language["XERA MVP SKIP S"].format(fdp_names=fdp_names)
        if len(i_fdp) > 1:
            return language_config.selected_language["XERA MVP SKIP P"].format(fdp_names=fdp_names)

        return None

    def mvp_glide(self):
        """
        Identifie les MVP qui sont morts pendant la phase de vol.

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'est mort en vol
        """
        i_glide = self.get_gliding_death()
        glide_names = self.players_to_string(i_glide)
        self.add_mvps(i_glide)

        if len(i_glide) == 1:
            return language_config.selected_language["XERA MVP GLIDE S"].format(glide_names=glide_names)
        if len(i_glide) > 1:
            return language_config.selected_language["XERA MVP GLIDE P"].format(glide_names=glide_names)

        return None

    ################################ LVP ################################

    def lvp_minijeu(self):
        """
        Identifie les LVP qui ont fait le mini-jeu deux fois.

        Returns:
            str: Message LVP formaté ou None si aucun joueur n'a fait le mini-jeu deux fois
        """
        i_players, max_minijeu, _ = Analyzer.get_max_value(self.player_list, self.get_tp_back, exclude=[self.is_fdp])
        lvp_names = self.players_to_string(i_players)
        self.add_lvps(i_players)

        if max_minijeu == 2:
            return language_config.selected_language["XERA LVP MINI-JEU"].format(lvp_names=lvp_names)

        return None

    ################################ CONDITIONS ################################

    def is_fdp(self, i_player: int):
        """
        Vérifie si un joueur a réussi à esquiver le mini-jeu.

        Args:
            i_player (int): Indice du joueur à vérifier

        Returns:
            bool: True si le joueur a esquivé le mini-jeu, False sinon
        """
        return i_player in self.get_fdp()

    ################################ DATA MECHAS ################################

    def get_tp_out(self, i_player: int):
        """
        Récupère le nombre de téléportations vers le mini-jeu pour un joueur.

        Args:
            i_player (int) : Indice du joueur

        Returns:
            int: Nombre de téléportations vers le mini-jeu
        """
        return self.get_mech_value(i_player, 'TP')

    def get_tp_back(self, i_player: int):
        """
        Récupère le nombre de retours du mini-jeu pour un joueur.

        Args:
            i_player (int) : Indice du joueur

        Returns:
            int: Nombre de retours du mini-jeu
        """
        return self.get_mech_value(i_player, 'TP back')

    def get_fdp(self):
        """
        Identifie les joueurs qui ont esquivé le mini-jeu de Xera.

        Cette méthode analyse les positions des joueurs après leur téléportation
        pour déterminer s'ils ont réussi à atteindre le centre sans passer par le mini-jeu.

        Returns:
            list: Liste des indices des joueurs qui ont esquivé le mini-jeu
        """
        # Récupération des données de téléportation
        mecha_data = self.log.pjcontent['mechanics']
        tp_data = None
        for e in mecha_data:
            if e['name'] == "TP Out":
                tp_data = e['mechanicsData']
                break

        # Analyse des positions après téléportation
        fdp = []
        delta = 6000
        i_delta = time_to_index(delta, self.time_base)

        for e in tp_data:
            tp_time = e['time']
            player_name = e['actor']
            i_player = self.get_player_id(player_name)
            tp_time += 2000  # 2s de délai pour être sûr
            i_time = time_to_index(tp_time, self.time_base)
            pos_player = self.get_player_pos(i_player, i_time, i_time + i_delta)

            for p in pos_player:
                if get_dist(p, XERA.centre) <= XERA.centre_radius:
                    fdp.append(i_player)
                    break

        return fdp

    def get_gliding_death(self):
        """
        Identifie les joueurs qui sont morts pendant la phase de vol.

        Returns:
            list: Liste des indices des joueurs morts durant la phase de vol
        """
        dead = []
        glide_phase = self.get_phase_id("Gliding")

        if glide_phase != 0:
            for i in self.player_list:
                if self.log.pjcontent['players'][i]['defenses'][glide_phase]['deadCount'] > 0:
                    dead.append(i)

        return dead