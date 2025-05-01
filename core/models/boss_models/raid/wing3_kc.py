from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class KC(Boss):
    """
    Keep Construct (KC) de la troisième aile de raid.
    """

    last = None
    name = "KC"
    wing = 3
    boss_id = 16235

    def __init__(self, log):
        """
        Initialise une instance de KC avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        KC.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Keep Construct.

        Vérifie d'abord les joueurs avec peu d'orbes gérées, puis les joueurs avec un DPS faible.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_orb = self.mvp_orb_kc()
        if msg_orb:
            return msg_orb

        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Keep Construct.

        Identifie les joueurs avec le nombre le plus élevé d'orbes gérées.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.lvp_orb_kc()

    ################################ MVP ################################

    def mvp_orb_kc(self):
        """
        Identifie les MVP basés sur la faible gestion des orbes.

        Returns:
            str: Message MVP formaté ou None si aucun joueur ne répond au critère
        """
        i_players, min_orb, _ = Analyzer.get_min_value(self.player_list, self.get_good_orb)
        mvp_names = self.players_to_string(i_players)

        if min_orb < 7:
            self.add_mvps(i_players)
            if min_orb < 0:
                return language_config.selected_language["KC MVP BAD ORBS"].format(mvp_names=mvp_names, min_orb=-min_orb)
            if min_orb == 0:
                return language_config.selected_language["KC MVP 0 ORB"].format(mvp_names=mvp_names)
            else:
                return language_config.selected_language["KC MVP ORB"].format(mvp_names=mvp_names, min_orb=min_orb)

        return None

    ################################ LVP ################################

    def lvp_orb_kc(self):
        """
        Identifie les LVP basés sur la gestion élevée des orbes.

        Returns:
            str: Message LVP formaté
        """
        i_players, max_orb, _ = Analyzer.get_max_value(self.player_list, self.get_good_orb)
        lvp_names = self.players_to_string(i_players)
        self.add_lvps(i_players)
        return language_config.selected_language["KC LVP ORB"].format(lvp_names=lvp_names, max_orb=max_orb)

    ################################ DATA MECHAS ################################

    def get_good_orb(self, i_player: int):
        """
        Calcule le score d'orbes pour un joueur donné, en tenant compte des orbes bien gérées
        et des orbes mal gérées.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Score d'orbes (positif pour une bonne gestion, négatif pour une mauvaise)
        """
        good_red_orbs = self.get_mech_value(i_player, 'Good Red Orb')
        good_white_orbs = self.get_mech_value(i_player, 'Good White Orb')
        bad_red_orbs = self.get_mech_value(i_player, 'Bad Red Orb')
        bad_white_orbs = self.get_mech_value(i_player, 'Bad White Orb')
        return good_red_orbs + good_white_orbs - bad_red_orbs - bad_white_orbs