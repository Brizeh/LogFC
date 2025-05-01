from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config
from utils.maths import get_dist


class Q1(Boss):
    """
    Qadim (first)
    """

    last = None
    name = "QADIM"
    wing = 6
    boss_id = 20934

    center = [411.5, 431.1]
    fdp_radius = 70

    def __init__(self, log):
        """
        Initializes a Q1 instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        Q1.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Qadim fight.

        First checks players who stayed in the center, then those with low DPS,
        and finally those hit by the mace shockwaves.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
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
        Determines the LVP (Least Valuable Player) for the Qadim fight.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.get_lvp_dps()

    ################################ MVP ################################

    def mvp_fdp(self):
        """
        Identifies MVPs who stayed in the center of the arena (FDP = Fire Door Protocol).

        Returns:
            str: Formatted MVP message or None if no player stayed in the center
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
        Identifies MVPs hit by the most mace shockwaves.

        Returns:
            str: Formatted MVP message or None if no player was hit by many waves
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
        Identifies players who stayed in the center of the arena during P1 and P2 phases.

        Returns:
            list: List of indices of players who stayed in the center
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
        Retrieves the number of mace shock waves suffered by a player.

        Args:
            i_player (int): Player index

        Returns:
            int: Number of shock waves suffered
        """
        return self.get_mech_value(i_player, "Mace Shockwave")