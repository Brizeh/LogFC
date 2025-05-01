from core.models.boss import Boss
from utils.maths import get_dist
from i18n.languages import language_config


class SH(Boss):
    """
    Soulless Horror (SH)
    """

    last = None
    name = "SH"
    wing = 5
    boss_id = 19767

    # Arena coordinates and radii
    center_arena = [375, 375]
    radius1 = 345.5
    radius2 = 304.2
    radius3 = 256.2
    radius4 = 208.5
    radius5 = 163

    def __init__(self, log):
        """
        Initializes an SH instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SH.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Soulless Horror fight.

        First checks players hit by a wall, then those who fell,
        and finally players with low CC.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
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
        Determines the LVP (Least Valuable Player) for the Soulless Horror fight.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.get_lvp_cc_boss()

    ################################ MVP ################################

    def mvp_wall(self):
        """
        Identifies MVPs hit by a wall.

        Returns:
            str: Formatted MVP message or None if no player was hit by a wall
        """
        i_players = self.get_walled_players()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)

        if i_players:
            return language_config.selected_language["SH MVP WALL"].format(mvp_names=mvp_names)

        return None

    def mvp_fall(self):
        """
        Identifies MVPs who fell from the arena.

        Note: There is probably an error in the original code as it uses
        get_walled_players() instead of get_fallen_players(). This implementation
        corrects this error.

        Returns:
            str: Formatted MVP message or None if no player fell
        """
        i_players = self.get_fallen_players()  # Correction of the called function
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)

        if i_players:
            return language_config.selected_language["SH MVP FALL"].format(mvp_names=mvp_names)

        return None

    ################################ CONDITIONS ################################

    def took_wall(self, i_player: int):
        """
        Checks if a player was hit by a wall (instant death not due to falling).

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player was hit by a wall, False otherwise
        """
        if self.is_dead_instant(i_player) and not self.has_fallen(i_player):
            return True
        return False

    def has_fallen(self, i_player: int):
        """
        Checks if a player fell from the arena.

        This method analyzes the player's position at death and the time of death
        to determine if they fell from one of the arena's edges.

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player fell from the arena, False otherwise
        """
        if self.is_dead_instant(i_player):
            last_pos = self.get_player_pos(i_player)[-1]
            death_time = self.get_player_death_timer(i_player)
            fell_at_begin = get_dist(SH.center_arena, last_pos) > SH.radius2
            fell_to_radius23 = self.boss_hp_to_time(90) + 2500 < death_time < self.boss_hp_to_time(
                66) + 2500 and get_dist(SH.center_arena, last_pos) > SH.radius3
            fell_to_radius34 = self.boss_hp_to_time(66) + 2500 < death_time < self.boss_hp_to_time(
                33) + 2500 and get_dist(SH.center_arena, last_pos) > SH.radius4
            fell_to_radius45 = death_time > self.boss_hp_to_time(33) + 2500 and get_dist(SH.center_arena,
                                                                                        last_pos) > SH.radius5

            if fell_at_begin or fell_to_radius23 or fell_to_radius34 or (self.cm and fell_to_radius45):
                return True

        return False

    ################################ DATA MECHAS ################################

    def get_walled_players(self):
        """
        Retrieves the list of players hit by a wall.

        Returns:
            list: List of indices of players hit by a wall
        """
        walled = []
        for i in self.player_list:
            if self.took_wall(i):
                walled.append(i)
        return walled

    def get_fallen_players(self):
        """
        Retrieves the list of players who fell from the arena.

        Returns:
            list: List of indices of players who fell from the arena
        """
        fallen = []
        for i in self.player_list:
            if self.has_fallen(i):
                fallen.append(i)
        return fallen