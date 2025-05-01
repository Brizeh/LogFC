from core.models.boss import Boss
from i18n.languages import language_config


class MO(Boss):
    """
    Mursaat Overseer (MO) de la quatrième aile de raid.
    """

    last = None
    name = "MO"
    wing = 4
    boss_id = 17172

    def __init__(self, log):
        """
        Initialise une instance de MO avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        MO.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Mursaat Overseer.

        Vérifie d'abord les joueurs touchés par les pics, puis les joueurs avec un DPS faible.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_pic = self.mvp_pic()
        if msg_pic:
            return msg_pic

        return self.get_bad_dps()

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Mursaat Overseer.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_dps()

        ################################ MVP ################################

    def mvp_pic(self):
        """
        Identifie les MVP qui ont été touchés par les pics.

        Returns:
            str: Message MVP formaté ou None si aucun joueur n'a été touché par les pics
        """
        i_players = self.get_piced()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)

        if len(i_players) == 1:
            return language_config.selected_language["MO MVP PICS S"].format(mvp_names=mvp_names)
        if len(i_players) > 1:
            return language_config.selected_language["MO MVP PICS P"].format(mvp_names=mvp_names)

        return None

    ################################ DATA MECHAS ################################

    def get_piced(self):
        """
        Récupère la liste des joueurs tués instantanément (probablement par des pics).

        Returns:
            list: Liste des indices des joueurs tués par des pics
        """
        piced = []
        for i in self.player_list:
            if self.is_dead_instant(i):
                piced.append(i)
        return piced