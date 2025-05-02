from typing import List, Dict, Any, Optional, Tuple, Callable

from config.settings import ALL_PLAYERS, BOSS_DICT
from core.models.boss_encounter import BossEncounterMixin
from core.models.boss_player_gameplay import PlayerGameplayMixin
from core.models.boss_player_lvp import PlayerLvpMixin
from core.models.boss_player_mvp import PlayerMvpMixin
from core.models.log import Log
from utils.formatters import time_to_index

# Type for player filtering functions
PlayerFilter = Callable[[int], bool]


class Boss(PlayerLvpMixin, PlayerMvpMixin, PlayerGameplayMixin, BossEncounterMixin):
    """
    Base class representing a boss encounter in Guild Wars 2.

    This class encapsulates common logic for all boss encounters,
    including log parsing, player tracking, and performance evaluation.
    """

    def __init__(self, log: Log) -> None:
        """
        Initializes a boss encounter from a Log object.

        Args:
            log: The Log object containing the encounter data
        """
        super().__init__(log)

        # Lists to track MVP and LVP players
        self.mvp_accounts: List[str] = []
        self.lvp_accounts: List[str] = []

        # Initialize players in the global dictionary
        self._initialize_players()

    def _initialize_players(self) -> None:
        """
        Initializes the players involved in this encounter in the global dictionary.

        For each player, if they already exist in the ALL_PLAYERS dictionary,
        add this boss to their history. Otherwise, create a new player.
        """
        for i in self.player_list:
            account = self.get_player_account(i)
            player = ALL_PLAYERS.get(account)

            if not player:
                # Create a new player if not already present
                from core.models.player import Player
                new_player = Player(self, account)
                ALL_PLAYERS[account] = new_player
            else:
                # Add this boss to the player's history
                player.add_boss(self)

    def __repr__(self) -> str:
        """
        String representation of the boss for debugging.

        Returns:
            Log URL
        """
        return self.log.url

    # -------------------------------------------------------------------------
    # TODO: A trier
    # -------------------------------------------------------------------------

    def get_dmg_boss(self, i_player: int) -> int:
        """
        Retrieves the damage dealt to the boss by the player.

        Args:
            i_player: Player index

        Returns:
            Damage dealt to the boss
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return 0

        dps_targets = players[i_player].get('dpsTargets', [[]])
        if not dps_targets or not dps_targets[0]:
            return 0

        if self.real_phase_id >= len(dps_targets[0]):
            return 0

        return dps_targets[0][self.real_phase_id].get('damage', 0)

    def get_pos_boss(self, start: int = 0, end: Optional[int] = None) -> List[List[float]]:
        """
        Retrieves the main boss's positions during the fight.

        Iterates through the targets to find one that matches a known boss
        and returns its positions.

        Args:
            start: Starting index for positions (default = 0)
            end: Ending index for positions (None = until the end)

        Returns:
            List of [x, y, z] positions of the boss

        Raises:
            ValueError: If no boss is found among the targets
        """
        targets = self.log.pjcontent.get('targets', [])

        for target in targets:
            target_id = target.get('id')
            if target_id in BOSS_DICT:
                combat_data = target.get('combatReplayData', {})
                positions = combat_data.get('positions', [])
                return positions[start:end]

        raise ValueError('No Boss found in targets')

    def get_phase_timers(self, target_phase: str, in_milliseconds: bool = False) -> Tuple[int, int]:
        """
        Retrieves the start and end times of a specific fight phase.

        Args:
            target_phase: Name of the phase to look for
            in_milliseconds: If True, returns times in milliseconds;
                             otherwise, in position indices

        Returns:
            Tuple (start, end) representing the phase times or indices

        Raises:
            ValueError: If the phase is not found
        """
        phases = self.log.pjcontent.get('phases', [])

        for phase in phases:
            if phase.get('name') == target_phase:
                start = phase.get('start', 0)
                end = phase.get('end', 0)

                if in_milliseconds:
                    return start, end

                # Convert to position indices
                return time_to_index(start, self.time_base), time_to_index(end, self.time_base)

        raise ValueError(f'Phase "{target_phase}" not found')

    def get_mech_value(self, i_player: int, mech_name: str, phase: str = "Full Fight") -> int:
        """
        Retrieves the number of occurrences of a mechanic for a player during a specific phase.

        Args:
            i_player: Player index
            mech_name: Name of the mechanic to look for
            phase: Name of the phase (default = "Full Fight")

        Returns:
            Number of mechanic occurrences for this player
        """
        phase_id = self.get_phase_id(phase)

        # Create the list of mechanic names
        mechs_list = []
        for mech in self.mechanics:
            mechs_list.append(mech.get('name', ''))

        # Check if the mechanic exists
        if mech_name in mechs_list:
            i_mech = mechs_list.index(mech_name)

            try:
                # Access mechanic stats with index checks
                phases = self.log.jcontent.get('phases', [])
                if phase_id < len(phases):
                    mech_stats = phases[phase_id].get('mechanicStats', [])

                    if i_player < len(mech_stats) and i_mech < len(mech_stats[i_player]):
                        return mech_stats[i_player][i_mech][0]
            except (IndexError, KeyError, TypeError):
                # Return 0 in case of any error
                pass

        return 0

    def boss_hp_to_time(self, hp: float) -> Optional[int]:
        """
        Converts a boss HP percentage to the time elapsed since the start of the fight.

        This method finds the first moment when the boss's HP fell below the given percentage.

        Args:
            hp: Boss health percentage (0-100)

        Returns:
            Time in ms when the boss had this HP percentage, or None if not found
        """
        targets = self.log.pjcontent.get('targets', [])
        if not targets:
            return None

        hp_percents = targets[0].get('healthPercents', [])

        for timer in hp_percents:
            # Ensure timer is a list with at least 2 elements
            if isinstance(timer, list) and len(timer) > 1:
                if timer[1] < hp:
                    return timer[0]

        return None

    def get_mechanic_history(self, name: str) -> List[Dict[str, Any]]:
        """
        Retrieves the full history of a specific mechanic during the fight.

        Args:
            name: Full name of the mechanic

        Returns:
            List of occurrences of the mechanic, or an empty list if not found
        """
        mechanics = self.log.pjcontent.get('mechanics', [])

        for mech in mechanics:
            if mech.get('fullName') == name:
                return mech.get('mechanicsData', [])

        return []

    def get_dps_ranking(self) -> Dict[str, float]:
        """
        Retrieves the DPS ranking of players based on damage contribution.

        Support players are excluded from this ranking.

        Returns:
            Dictionary mapping player accounts to their normalized contribution
        """
        return self._get_dps_contrib([self.is_support])

    def _get_dps_contrib(self, exclude: List[PlayerFilter] = None) -> Dict[str, float]:
        """
        Computes each player's DPS contribution, normalized on a scale from 0 to 20.

        This method gives a relative performance measure in terms of damage dealt,
        with the top DPS player scoring 20 points and others proportionally less.

        Args:
            exclude: List of filtering functions to exclude certain players

        Returns:
            Dictionary mapping player accounts to their normalized contribution
        """
        if exclude is None:
            exclude = []

        dps_ranking = {}
        max_dps = 0

        for i in self.player_list:
            if any(filter_func(i) for filter_func in exclude):
                continue

            try:
                player_dps = self.get_dmg_boss(i)

                if player_dps > max_dps:
                    max_dps = player_dps

                dps_ranking[self.get_player_account(i)] = player_dps
            except (KeyError, IndexError):
                continue

        if max_dps > 0:
            for player in dps_ranking:
                dps_ranking[player] = 20.0 * dps_ranking[player] / max_dps

        return dps_ranking