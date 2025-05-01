from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config
from utils.maths import get_dist


class ESCORT(Boss):
    """
    Escort
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
        Initializes an ESCORT instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        ESCORT.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the escort.

        Checks if players have been hit by mines.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        msg_mine = self.mvp_mine()
        if msg_mine:
            return msg_mine
        return None

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the escort.

        First checks for issues with towers, then excessive Glenna calls.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        msg_tower = self.lvp_tower()
        if msg_tower:
            return msg_tower
        return self.lvp_glenna()

    ################################ MVP ################################

    def mvp_mine(self):
        """
        Identifies MVPs based on mine triggering.

        Returns:
            str: Formatted MVP message or None if no player triggered a mine
        """
        i_players = self.get_mined_players()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) == 1:
                return language_config.selected_language["ESCORT MVP MINE S"].format(mvp_names=mvp_names)
            else:
                return language_config.selected_language["ESCORT MVP MINE P"].format(mvp_names=mvp_names)
        return None

    ################################ LVP ################################

    def lvp_glenna(self):
        """
        Identifies LVPs based on the number of Glenna calls.

        Returns:
            str: Formatted LVP message
        """
        i_players, max_call, _ = Analyzer.get_max_value(self.player_list, self.get_glenna_call)
        lvp_names = self.players_to_string(i_players)
        self.add_lvps(i_players)
        return language_config.selected_language["ESCORT LVP GLENNA"].format(lvp_names=lvp_names, max_call=max_call)

    def lvp_tower(self):
        """
        Identifies LVPs based on incorrect tower activation.

        Returns:
            str: Formatted LVP message or None if towers were correctly activated
        """
        towers = self.get_towers()
        lvp_names = self.players_to_string(towers)
        for i in self.player_list:
            for n in range(1, 6):
                if self.is_tower_n(i, n) and not self.is_tower(i):
                    return None
        self.add_lvps(towers)
        if len(towers) == 1:
            return language_config.selected_language["ESCORT LVP TOWER S"].format(lvp_names=lvp_names)
        return language_config.selected_language["ESCORT LVP TOWER P"].format(lvp_names=lvp_names)

    ################################ CONDITIONS ################################

    def got_mined(self, i_player: int):
        """
        Checks if a player was hit by a mine.

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player was hit, False otherwise
        """
        return self.get_mech_value(i_player, "Mine Detonation Hit") > 0

    def is_tower_n(self, i_player: int, n: int):
        """
        Checks if a player activated a specific tower.

        Args:
            i_player (int): Index of the player to check
            n (int): Tower number (1-5)

        Returns:
            bool: True if the player activated the tower, False otherwise
        """
        poses = self.get_player_pos(i_player)
        tower = ESCORT.towers[n - 1]
        for pos in poses:
            if get_dist(pos, tower) < ESCORT.tower_radius:
                return True
        return False

    def is_tower(self, i_player: int):
        """
        Checks if a player activated all towers.

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player activated all towers, False otherwise
        """
        for n in range(1, 6):
            if not self.is_tower_n(i_player, n):
                return False
        return True

    ################################ DATA MECHAS ################################

    def get_mined_players(self):
        """
        Retrieves the list of players hit by mines.

        Returns:
            list: List of indices of players hit by mines
        """
        p = []
        for i in self.player_list:
            if self.got_mined(i):
                p.append(i)
        return p

    def get_glenna_call(self, i_player: int):
        """
        Retrieves the number of "Over Here!" calls made by a player.

        Args:
            i_player (int): Player index

        Returns:
            int: Number of calls
        """
        return self.get_mech_value(i_player, "Over Here! Cast")

    def get_towers(self):
        """
        Retrieves the list of players who activated all towers.

        Returns:
            list: List of indices of players who activated all towers
        """
        towers = []
        for i in self.player_list:
            if self.is_tower(i):
                towers.append(i)
        return towers