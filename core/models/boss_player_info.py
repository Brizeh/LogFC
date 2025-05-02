from typing import ClassVar, List, Dict, Any, Optional

from core.models.boss_data_access import DataAccessMixin
from core.models.log import Log


class PlayerInfoMixin(DataAccessMixin):

    # Threshold values
    BUYER_DEATH_THRESHOLD: ClassVar[int] = 20000  # ms
    INSTANT_DEATH_TIME_DIFF: ClassVar[int] = 8000  # ms


    def __init__(self, log: Log, *args, **kwargs) -> None:
        super().__init__(log, *args, **kwargs)
        self.player_list: List[int] = self.get_player_list()

    def get_player_name(self, i_player: int) -> str:
        """
        Retrieves the name of the player.

        Args:
            i_player: Player index

        Returns:
            Player's name
        """
        return self.log.jcontent.get('players', [])[i_player].get('name', 'Unknown')

    def get_player_id(self, name: str) -> Optional[int]:
        """
        Retrieves the index of a player by their name.

        Args:
            name: Player name to search

        Returns:
            Player index or None if not found
        """
        players = self.log.pjcontent.get('players', [])

        return next((i for i, player in enumerate(players)
                     if player.get('name') == name), None)

    def get_player_account(self, i_player: int) -> str:
        """
        Retrieves the player's account name.

        Args:
            i_player: Player index

        Returns:
            Player's account name (format: name.1234)
        """
        return self.log.pjcontent.get('players', [])[i_player].get('account', 'Unknown')

    def get_player_group(self, i_player: int) -> int:
        """
        Retrieves the group number the player belongs to.

        Args:
            i_player: Player index

        Returns:
            Group number
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return 0

        return players[i_player].get('group', 0)

    def get_player_spe(self, i_player: int) -> str:
        """
        Retrieves the player's specialization.

        Args:
            i_player: Player index

        Returns:
            Name of the specialization
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return "Unknown"

        return players[i_player].get('profession', 'Unknown')

    def get_player_pos(self, i_player: int, start: int = 0, end: Optional[int] = None) -> List[List[float]]:
        """
        Retrieves the player's positions during the fight.

        Args:
            i_player: Player index
            start: Start index for positions
            end: End index for positions (None = until the end)

        Returns:
            List of [x, y, z] positions for the player
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return []

        combat_data = players[i_player].get('combatReplayData', {})
        positions = combat_data.get('positions', [])

        return positions[start:end]

    def get_player_list(self) -> List[int]:
        """
        Retrieves the list of player indices participating in the fight.

        Filters out players in special groups (50+) and those detected as buyers
        (for raid selling purposes).

        Returns:
            List of actual participant player indices
        """
        real_players = []
        players = self.log.pjcontent.get('players', [])

        for i_player, player in enumerate(players):
            if (player.get('group', 0) < 50 and
                    not self.is_buyer(i_player)):
                real_players.append(i_player)

        return real_players

    def is_buyer(self, i_player: int) -> bool:
        """
        Checks if the player is a buyer (raid sale).

        A player is considered a buyer if they:
        - Die within the first 20 seconds of the fight
        - Have no rotation data

        Args:
            i_player: Index of the player to check

        Returns:
            True if the player is a buyer, False otherwise
        """
        player_name = self.get_player_name(i_player)
        mechanics = self.log.pjcontent.get('mechanics', [])

        if mechanics:
            death_history = [
                death for mech in mechanics
                if mech.get('name') == "Dead"
                for death in mech.get('mechanicsData', [])
            ]

            for death in death_history:
                if (death.get('time', 0) < self.BUYER_DEATH_THRESHOLD and
                        death.get('actor') == player_name):
                    return True

        try:
            rotation = self.get_player_rotation(i_player)
            if not rotation:
                return True
        except (KeyError, IndexError):
            return True

        return False

    def get_player_rotation(self, i_player: int) -> List[Dict[str, Any]]:
        """
        Retrieves the player's skill rotation during the fight.

        Args:
            i_player: Player index

        Returns:
            List of skills used by the player
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return []

        return players[i_player].get('rotation', [])

    def get_player_mech_history(self, i_player: int, mechs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Retrieves the mechanic history for a player.

        Collects all mechanic events that affected the player during the fight,
        with optional filtering by specific mechanic names.

        Args:
            i_player: Player index
            mechs: List of mechanic names to filter (None = all)

        Returns:
            List of mechanic events for the player, sorted by time
        """
        history = []
        player_name = self.get_player_name(i_player)
        mech_history = self.log.pjcontent.get('mechanics', [])

        if mechs is None:
            mechs = []

        for mech in mech_history:
            mech_name = mech.get('name', '')

            for data in mech.get('mechanicsData', []):
                if data.get('actor') == player_name:
                    if not mechs or mech_name in mechs:
                        history.append({
                            "name": mech_name,
                            "time": data.get('time', 0)
                        })

        history.sort(key=lambda event: event.get("time", 0))
        return history

    def get_cc_boss(self, i_player: int) -> float:
        """
        Retrieves the defiance bar damage dealt to the boss by the player.

        Args:
            i_player: Player index

        Returns:
            Defiance bar damage to the boss
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return 0

        dps_targets = players[i_player].get('dpsTargets', [[]])
        if not dps_targets or not dps_targets[0]:
            return 0

        return dps_targets[0][0].get('breakbarDamage', 0)

    def get_cc_total(self, i_player: int) -> float:
        """
        Retrieves the total defiance bar damage dealt by the player.

        Args:
            i_player: Player index

        Returns:
            Total defiance bar damage
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return 0

        dps_all = players[i_player].get('dpsAll', [{}])
        if not dps_all:
            return 0

        return dps_all[0].get('breakbarDamage', 0)

    def time_entered_area(self, i_player: int, center: List[float], radius: float) -> Optional[int]:
        """
        Determines when the player entered a circular area.

        Args:
            i_player: Player index
            center: Coordinates [x, y, z] of the center of the area
            radius: Radius of the area

        Returns:
            Time in ms since the start of the fight, or None if never entered
        """
        from utils.maths import get_dist

        poses = self.get_player_pos(i_player)
        if not poses:
            return None

        position_interval = 150

        for i, pos in enumerate(poses):
            if get_dist(pos, center) < radius:
                return i * position_interval

        return None

    def time_exited_area(self, i_player: int, center: List[float], radius: float) -> Optional[int]:
        """
        Determines when the player exited a circular area after entering it.

        Args:
            i_player: Player index
            center: Coordinates [x, y, z] of the center of the area
            radius: Radius of the area

        Returns:
            Time in ms since the start of the fight, or None if never exited
        """
        from utils.maths import get_dist

        time_enter = self.time_entered_area(i_player, center, radius)
        if time_enter is None:
            return None

        # Delay between each position (ms)
        position_interval = 150
        i_enter = int(time_enter / position_interval)

        poses = self.get_player_pos(i_player, start=i_enter)
        if not poses:
            return None

        for i, pos in enumerate(poses):
            if get_dist(pos, center) > radius:
                return (i + i_enter) * position_interval

        return None