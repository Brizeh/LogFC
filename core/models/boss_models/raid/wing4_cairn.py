from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class CAIRN(Boss):
    """
    Cairn de la quatrième aile de raid.
    """

    last = None
    name = "CAIRN"
    wing = 4
    boss_id = 17194

    def __init__(self, log):
        """
        Initialise une instance de CAIRN avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        CAIRN.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Cairn.

        Vérifie d'abord les joueurs avec le plus de téléportations, puis les joueurs
        avec un DPS significativement bas.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_tp = self.mvp_tp()
        if msg_tp:
            return msg_tp

        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Cairn.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_dps()

    ################################ MVP ################################

    def mvp_tp(self):
        """
        Identifie les MVP basés sur le nombre élevé de téléportations.

        Returns:
            str: Message MVP formaté ou None si aucun joueur ne répond au critère
        """
        i_players, max_tp, _ = Analyzer.get_max_value(self.player_list, self.get_tp)
        mvp_names = self.players_to_string(i_players)

        if max_tp > 2:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return language_config.selected_language["CAIRN MVP TP S"].format(mvp_names=mvp_names, max_tp=max_tp)
            if len(i_players) > 1:
                return language_config.selected_language["CAIRN MVP TP P"].format(mvp_names=mvp_names, max_tp=max_tp)

        return None

    ################################ DATA MECHAS ################################

    def get_tp(self, i_player: int):
        """
        Récupère le nombre de téléportations oranges pour un joueur.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Nombre de téléportations oranges
        """
        return self.get_mech_value(i_player, 'Orange TP')