from typing import Optional, List, Dict, ClassVar

from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config
from utils.formatters import time_to_index
from utils.maths import get_dist


class SABETHA(Boss):
    """
    Sabetha
    """

    # Class attributes
    last: Optional['SABETHA'] = None  # Reference to the last created instance
    name: ClassVar[str] = "SABETHA"
    wing: ClassVar[int] = 1
    boss_id: ClassVar[int] = 15375
    real_phase: ClassVar[str] = "Full Fight"

    # Positions and constants for mechanics
    pos_sab: List[float] = [376.7, 364.4]
    pos_canon1: List[float] = [346.9, 706.7]
    pos_canon2: List[float] = [35.9, 336.8]
    pos_canon3: List[float] = [403.3, 36.0]
    pos_canon4: List[float] = [713.9, 403.1]
    canon_detect_radius: float = 45.0
    scaler: float = 9.34179

    def __init__(self, log: Log) -> None:
        """
        Initializes a Sabetha object.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SABETHA.last = self  # Updates the reference to the last instance

    def get_mvp(self) -> Optional[str]:
        """
        Determines the MVP player for Sabetha.
        Priority: proper use of bombs > good damage on adds > bad DPS (excluding the cannons)

        Returns:
            MVP reward message or None if no player stands out
        """
        # First, check if players have properly used the bombs
        msg_terrorists = self.mvp_terrorists()
        if msg_terrorists:
            return msg_terrorists

        # Next, check the damage during the split phases
        msg_dmg_split = self.mvp_dmg_split()
        if msg_dmg_split:
            return msg_dmg_split

        # Finally, check for underperforming DPS (excluding players on cannons)
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_cannon])
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self) -> str:
        """
        Determines the LVP player for Sabetha, based on damage during the split phases.

        Returns:
            LVP penalty message
        """
        return self.lvp_dmg_split()

    def get_dps_ranking(self) -> Dict[str, float]:
        """
        Calculates the DPS ranking for Sabetha.
        Excludes supports and players on cannons because they have a specific role.

        Returns:
            Dictionary of normalized DPS contributions
        """
        return self._get_dps_contrib([self.is_support, self.is_cannon])

    ################################ MVP ################################

    def mvp_dmg_split(self) -> Optional[str]:
        """
        Identifies the players who did the least damage during the add phases.
        These players are considered MVP because they focused on the mechanics.

        Returns:
            MVP message for good damage on adds or None if no one stands out
        """
        # Get the players who did the least damage in the add phases
        i_players, min_dmg, total_dmg = Analyzer.get_min_value(
            self.player_list,
            self.get_dmg_split,
            exclude=[self.is_support, self.is_cannon]
        )

        # Calculate the total damage of DPS players
        dps_total_dmg = Analyzer.get_tot_value(
            self.player_list,
            self.get_dmg_split,
            exclude=[self.is_support]
        )

        # If the damage is significantly low (less than 75% of the expected share)
        if min_dmg / dps_total_dmg < 1 / 6 * 0.75:
            # Add these players to the MVP list
            self.add_mvps(i_players)

            # Prepare variables for the message
            mvp_names = self.players_to_string(i_players)
            dmg_ratio = min_dmg / total_dmg * 100

            # Generate the message
            return language_config.selected_language["SABETHA MVP SPLIT"].format(
                mvp_names=mvp_names,
                dmg_ratio=dmg_ratio
            )

        return None

    def mvp_terrorists(self) -> Optional[str]:
        """
        Identifies the players who properly handled the bombs during the fight.
        The "terrorists" are the players who kept the bombs away from others.

        Returns:
            MVP message for good bomb users or None if no one stands out
        """
        # Get the list of players who handled the bombs well
        i_players = self.get_terrorists()

        # Add these players to the MVP list
        self.add_mvps(i_players)

        if i_players:
            # Prepare the message
            mvp_names = self.players_to_string(i_players)

            # Generate the message
            return language_config.selected_language["SABETHA MVP BOMB"].format(mvp_names=mvp_names)

        return None

    ################################ LVP ################################

    def lvp_dmg_split(self) -> str:
        """
        Identifies the players who did the most damage during the add phases.
        These players are considered LVP because they focused on damage at the expense of mechanics.

        Returns:
            LVP message for the players with the highest damage on the adds
        """
        # Get the players who did the most damage in the add phases
        i_players, max_dmg, total_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_split)

        # Prepare variables for the message
        lvp_names = self.players_to_string(i_players)
        dmg_ratio = max_dmg / total_dmg * 100

        # Add these players to the LVP list
        self.add_lvps(i_players)

        # Generate the message
        return language_config.selected_language["SABETHA LVP SPLIT"].format(
            lvp_names=lvp_names,
            dmg_ratio=dmg_ratio
        )

    ################################ CONDITIONS ###############################

    def is_cannon(self, i_player: int, n: int = 0) -> bool:
        """
        Checks if a player handled a cannon during the fight.

        Args:
            i_player: The player index
            n: The cannon number to check (0 = all, 1-4 = specific cannon)

        Returns:
            True if the player handled the specified cannon(s), False otherwise
        """
        # Retrieve the player's positions during the fight
        pos_player = self.get_player_pos(i_player)

        # Determine which cannons to check
        if n == 0:
            canon_pos = [
                SABETHA.pos_canon1,
                SABETHA.pos_canon2,
                SABETHA.pos_canon3,
                SABETHA.pos_canon4
            ]
        elif n == 1:
            canon_pos = [SABETHA.pos_canon1]
        elif n == 2:
            canon_pos = [SABETHA.pos_canon2]
        elif n == 3:
            canon_pos = [SABETHA.pos_canon3]
        elif n == 4:
            canon_pos = [SABETHA.pos_canon4]
        else:
            canon_pos = []

        # Check if the player was near a cannon
        for pos in pos_player:
            for canon in canon_pos:
                # Use the get_dist function to calculate the distance between two points
                if get_dist(pos, canon) <= SABETHA.canon_detect_radius:
                    return True

        return False

    def is_terrorist(self, i_player: int) -> bool:
        """
        Checks if a player properly handled the bombs (by staying away from other players).

        Args:
            i_player: The player index

        Returns:
            True if the player properly handled the bombs, False otherwise
        """
        # Retrieve the player's bomb history
        bomb_history = self.get_player_mech_history(i_player, ["Timed Bomb"])

        if bomb_history:
            # Get the player's positions and the list of other players
            poses = self.get_player_pos(i_player)
            players = self.player_list

            # Check each bomb
            for bomb in bomb_history:
                # The player has 3 seconds after the bomb appears to move away
                bomb_time = bomb['time'] + 3000
                time_index = time_to_index(bomb_time, self.time_base)

                try:
                    # Player's position at the time of the explosion
                    bomb_pos = poses[time_index]
                except IndexError:
                    # If the index is out of bounds, move to the next bomb
                    continue

                # Count how many players are near the explosion
                bombed_players = 0
                for i in players:
                    # Do not count the player themselves or dead players
                    if i == i_player or self.is_dead(i):
                        continue

                    # Position of this player at the time of the explosion
                    i_pos = self.get_player_pos(i)[time_index]

                    # Check if the player is within the explosion radius (270 units after scaling)
                    if get_dist(bomb_pos, i_pos) * SABETHA.scaler <= 270:
                        bombed_players += 1

                # If the player hit more than one other player, they're not a good terrorist
                if bombed_players > 1:
                    return True

        return False

    ################################ DATA MECHAS ################################

    def get_dmg_split(self, i_player: int) -> int:
        """
        Calculates the total damage done by a player during the add phases.

        Args:
            i_player: The player index

        Returns:
            Total damage done during the add phases
        """
        try:
            # Get the damage for each of the three important adds
            dmg_kernan = self.log.jcontent['phases'][2]['dpsStatsTargets'][i_player][0][0]
            dmg_mornifle = self.log.jcontent['phases'][5]['dpsStatsTargets'][i_player][0][0]
            dmg_karde = self.log.jcontent['phases'][7]['dpsStatsTargets'][i_player][0][0]

            # Sum the damage from the three adds
            return dmg_kernan + dmg_mornifle + dmg_karde

        except (IndexError, KeyError, TypeError):
            # If there's an error accessing the data
            return 0

    def get_terrorists(self) -> List[int]:
        """
        Identifies all players who properly handled the bombs during the fight.

        Returns:
            List of indices of players who properly handled the bombs
        """
        terrorists = []

        for i in self.player_list:
            if self.is_terrorist(i):
                terrorists.append(i)

        return terrorists
