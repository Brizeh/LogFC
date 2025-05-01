from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config
from utils.formatters import time_to_index
from utils.maths import get_dist


class XERA(Boss):
    """
    Xera
    """

    last = None
    name = "XERA"
    wing = 3
    boss_id = 16246
    real_phase = "Phase 1"

    # Coordinates of specific points
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
        Initializes a XERA instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        XERA.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Xera fight.

        First checks players who managed to skip the mini-game, then players
        who died while gliding, and finally players with low CC.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
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
        Determines the LVP (Least Valuable Player) for the Xera fight.

        First checks players who did the mini-game twice, then players
        with high CC.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        msg_minijeu = self.lvp_minijeu()
        if msg_minijeu:
            return msg_minijeu

        return self.get_lvp_cc_boss()

    def get_dps_ranking(self):
        """
        Calculates the DPS ranking of players for Xera excluding supports.

        Returns:
            dict: Dictionary associating players with their DPS score
        """
        return self._get_dps_contrib([self.is_support])

    ################################ MVP ################################

    def mvp_fdp_xera(self):
        """
        Identifies MVPs who managed to skip Xera's mini-game.

        Returns:
            str: Formatted MVP message or None if no player skipped the mini-game
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
        Identifies MVPs who died during the gliding phase.

        Returns:
            str: Formatted MVP message or None if no player died while gliding
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
        Identifies LVPs who did the mini-game twice.

        Returns:
            str: Formatted LVP message or None if no player did the mini-game twice
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
        Checks if a player managed to skip the mini-game.

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player skipped the mini-game, False otherwise
        """
        return i_player in self.get_fdp()

    ################################ DATA MECHAS ################################

    def get_tp_out(self, i_player: int):
        """
        Retrieves the number of teleports to the mini-game for a player.

        Args:
            i_player (int): Player index

        Returns:
            int: Number of teleports to the mini-game
        """
        return self.get_mech_value(i_player, 'TP')

    def get_tp_back(self, i_player: int):
        """
        Retrieves the number of returns from the mini-game for a player.

        Args:
            i_player (int): Player index

        Returns:
            int: Number of returns from the mini-game
        """
        return self.get_mech_value(i_player, 'TP back')

    def get_fdp(self):
        """
        Identifies players who skipped Xera's mini-game.

        This method analyzes player positions after their teleportation
        to determine if they managed to reach the center without going through the mini-game.

        Returns:
            list: List of indices of players who skipped the mini-game
        """
        # Retrieving teleportation data
        mecha_data = self.log.pjcontent['mechanics']
        tp_data = None
        for e in mecha_data:
            if e['name'] == "TP Out":
                tp_data = e['mechanicsData']
                break

        # Analyzing positions after teleportation
        fdp = []
        delta = 6000
        i_delta = time_to_index(delta, self.time_base)

        for e in tp_data:
            tp_time = e['time']
            player_name = e['actor']
            i_player = self.get_player_id(player_name)
            tp_time += 2000  # 2s delay to be sure
            i_time = time_to_index(tp_time, self.time_base)
            pos_player = self.get_player_pos(i_player, i_time, i_time + i_delta)

            for p in pos_player:
                if get_dist(p, XERA.centre) <= XERA.centre_radius:
                    fdp.append(i_player)
                    break

        return fdp

    def get_gliding_death(self):
        """
        Identifies players who died during the gliding phase.

        Returns:
            list: List of indices of players who died during the gliding phase
        """
        dead = []
        glide_phase = self.get_phase_id("Gliding")

        if glide_phase != 0:
            for i in self.player_list:
                if self.log.pjcontent['players'][i]['defenses'][glide_phase]['deadCount'] > 0:
                    dead.append(i)

        return dead